import re

import wx


def dump(h, obj):
    print(h)
    print(obj)
    print('self:')
    for k, v in obj.__dict__.items():
        if k == '__doc__':
            pass
        else:
            print('  ', k, '--->>>', v, 'type: ', type(v))
    # If obj is a type, call mro on it directly.
    if isinstance(obj, type):
        mro = obj.mro()
    else:
        mro = obj.__class__.mro()
    for c in mro:
        print('  c: ', c)
        for k, v in c.__dict__.items():
            if k == '__doc__':
                pass
            else:
                print('    ', k, '--->>>', v, 'type: ', type(v))


class XObjects:
    def __init__(self):
        super().__init__()
        self.current_xobjid = None
        self.variable_counter = 0
        self.variable_name = ''
        self.last_names = {}
        self.output_codegen = False

        self.xenv = {
            'wx': wx,
            'x': self,
            '__builtins__': {}
        }

    def codegen_output_line(self, s):
        if self.output_codegen:
            print(s)

    def codegen_set_current_variable_name(self, xobjid):
        if xobjid is None:
            self.variable_name = 'self.var{n}'.format(n=self.variable_counter)
            self.variable_counter += 1
            return
        self.variable_name = 'self.' + xobjid

    def codegen_get_current_variable_name(self):
        return self.variable_name

    def codegen_set_replace_variable_name(self, name):
        self.last_names[name] = self.variable_name

    def codegen_get_replace_variable_name(self, name):
        if name in self.last_names:
            return self.last_names[name]
        return 'self.' + name

    def codegen_xname_replacement(self, s):
        # fullx is everything that ends in x. x is just the end part.
        # If they are the same, it's a single x.name
        pattern = r"""(?P<fullx>[a-zA-z]*(?P<x>x\.(?P<name>[a-zA-Z_]+)))"""
        new = ''
        remainder = s
        while True:
            result = re.match(pattern, remainder)
            if result is None:
                return new + remainder

            # Not a "real" x name.  Skip over it.
            if result['fullx'] != result['x']:
                skip_end = result.span('fullx')[1]
                additional = remainder[0:skip_end]
                new = new + additional
                remainder = remainder[skip_end:]
                continue

            # Got a real x match, do the replacement.
            replace_start = result.span('x')[0]
            replace_end = result.span('x')[1]
            old_name = result['name']
            additional = remainder[0:replace_start] + self.codegen_get_replace_variable_name(old_name)
            new = new + additional
            remainder = remainder[replace_end:]

    def codegen_functioncall(self, s, args, kwargs, needs_var):
        positional_args_string = ''
        have_positional = False
        for a in args:
            if have_positional:
                positional_args_string += ', '
            have_positional = True
            if a.startswith('*'):
                stripped = a[2:-1]  # get rid of asterisk and leading and trailing paren. Fragile.
                positional_args_string += self.codegen_xname_replacement(stripped)
            else:
                positional_args_string += self.codegen_xname_replacement(a)
        kwargs_string = ''
        have_kw = False
        for k, v in kwargs.items():
            if have_kw:
                kwargs_string += ', '
            have_kw = True
            vs = self.codegen_xname_replacement(v)
            kwargs_string += k + '=' + vs
        separator = ',' if have_positional and have_kw else ''

        function_call_template = '{variable}{s}({positional}{separator}{kw})'
        function_call_string = function_call_template.format(
            variable=self.codegen_get_current_variable_name() + '=' if needs_var else '',
            s=self.codegen_xname_replacement(s),
            positional=positional_args_string,
            separator=separator,
            kw=kwargs_string)
        self.codegen_output_line(function_call_string)

    def codegen_property(self, obj, name, value):
        property_template = '{obj_name}.{property_name}={value}'
        property_string = property_template.format(
            obj_name=self.codegen_xname_replacement(obj),
            property_name=name,
            value=self.codegen_xname_replacement(value)
        )
        self.codegen_output_line(property_string)

    def save_object(self, name, obj):
        self.__setattr__(name, obj)

    def xeval(self, s):
        return eval(s, self.xenv, {})

    def xcall(self, s, *args, needs_var=True, **kwargs):
        args_eval = ()
        for a in args:
            if a.startswith('*'):
                args_eval += self.xeval(a[1:])
            else:
                args_eval += (self.xeval(a),)
        kwargs_eval = {}
        for k, v in kwargs.items():
            kwargs_eval[k] = self.xeval(v)
        #        args = None
        #        kwargs = None

        funcorprop = self.xeval(s)
        part_names = s.split('.')
        last = part_names[-1]
        if callable(funcorprop):
            thing = funcorprop(*args_eval, **kwargs_eval)

            if needs_var:
                self.__setattr__(last, thing)

            self.codegen_set_current_variable_name(self.current_xobjid)
            self.codegen_functioncall(s, args, kwargs, needs_var)
            # Name updates must come AFTER function call generation so
            # that the name replacement is correct in the function code.
            if needs_var:
                self.codegen_set_replace_variable_name(last)

            return thing
        # else try it as a property.
        if len(args_eval) == 0:
            # No positional args, so multiple properties are in the kwargs.
            # The entire function string is the object.
            for k, v in kwargs_eval.items():
                obj = self.xeval(s)
                obj.__setattr__(k, v)
                self.codegen_property(s, k, kwargs[k])
        else:
            # Got positional arg so assume property value is the first positional arg.
            # The object is the first part of the function string and the property s is the last part.
            objstr = '.'.join(part_names[0:-1])
            obj = self.xeval(objstr)
            obj.__setattr__(last, args_eval[0])
            self.codegen_property(objstr, last, args[0])

        return None  # TODO: is there anything more useful to return?

    def xcall_attribs(self, s, attribs):
        attribs_copy = attribs.copy()
        id_str = 'xobj.id'
        xobjid = None
        if id_str in attribs_copy:
            xobjid = attribs_copy[id_str]
            del attribs_copy[id_str]
        self.current_xobjid = xobjid
        kwargs = {}
        for k, v in attribs_copy.items():
            if k.find('.') < 0:
                kwargs[k] = v
            else:
                pass  # It's a dotted attribute to process after.
        for k in kwargs.keys():  # Remove undotted attributes.
            del attribs_copy[k]
        thing = self.xcall(s, **kwargs)
        if xobjid is not None:
            self.__setattr__(xobjid, thing)
        for k, v in attribs_copy.items():
            self.xcall(k, v, needs_var=False)

    def on_element(self, element, namespace, prefix, name):
        #        print('Got element:', element, namespace, prefix, name)
        #        for k, v in element.attrib.items():
        #            print(k, v)
        self.xcall_attribs(prefix + '.' + name, element.attrib)


if __name__ == '__main__':
    def main():
        app = wx.App(redirect=False)
        xobjects = XObjects()
        xobjects.output_codegen = True

        # BEGIN FRAME
        attribs = {'xobj.id': 'main_frame', 'parent': 'None', 'title': '"Hello Frame"'}
        xobjects.xcall_attribs('wx.Frame', attribs)

        # BEGIN STATUS BAR
        attribs = {'parent': 'x.Frame', 'id': '1', 'x.Frame.StatusBar': 'x.this'}
        xobjects.xcall_attribs('wx.StatusBar', attribs)
        attribs = {'StatusText': '"New Status"'}
        xobjects.xcall_attribs('x.this', attribs)
        # END STATUS BAR

        # BEGIN MENU BAR
        attribs = {'x.Frame.MenuBar': 'x.this'}
        xobjects.xcall_attribs('wx.MenuBar', attribs)

        attribs = {'x.MenuBar.Append': '*(x.this, "Menu&1")'}
        xobjects.xcall_attribs('wx.Menu', attribs)

        attribs = {'parentMenu': 'None', 'id': '1', 'text': '"Menu item 1 1"', 'x.Menu.Append': 'x.this'}
        xobjects.xcall_attribs('wx.MenuItem', attribs)

        attribs = {'parentMenu': 'None', 'id': '1', 'text': '"Menu item 1 2"', 'x.Menu.Append': 'x.this'}
        xobjects.xcall_attribs('wx.MenuItem', attribs)

        attribs = {'x.MenuBar.Append': '*(x.this, "Menu&2")'}
        xobjects.xcall_attribs('wx.Menu', attribs)

        attribs = {'parentMenu': 'None', 'id': '1', 'text': '"Menu item 2 1"', 'x.Menu.Append': 'x.this'}
        xobjects.xcall_attribs('wx.MenuItem', attribs)

        attribs = {'parentMenu': 'None', 'id': '1', 'text': '"Menu item 2 2"', 'x.Menu.Append': 'x.this'}
        xobjects.xcall_attribs('wx.MenuItem', attribs)
        # END MENU BAR

        # END FRAME

        # BEGIN PANEL
        attribs = {'parent': 'x.Frame'}
        xobjects.xcall_attribs('wx.Panel', attribs)
        # END PANEL

        # BEGIN BUTTONS
        attribs = {'xobj.id': 'button1', 'parent': 'x.Panel', 'x.this.Label': '"Label from attribute"'}
        xobjects.xcall_attribs('wx.Button', attribs)

        attribs = {'xobj.id': 'button2', 'parent': 'x.Panel', 'label': '"label2"'}
        xobjects.xcall_attribs('wx.Button', attribs)
        # END BUTTONS

        # BEGIN SIZER
        attribs = {'vgap': '0', 'hgap': '0', 'x.Panel.Sizer': 'x.this'}
        xobjects.xcall_attribs('wx.GridBagSizer', attribs)
        attribs = {'HGap': '100', 'VGap': '50'}
        xobjects.xcall_attribs('x.this', attribs)

        attribs = {'window': 'x.button1', 'pos': '(0, 0)', 'x.GridBagSizer.Add': 'x.this'}
        xobjects.xcall_attribs('wx.GBSizerItem', attribs)
        attribs = {'Proportion': '1', 'Flag': 'wx.ALL | wx.CENTER', 'Border': '10'}
        xobjects.xcall_attribs('x.this', attribs)

        attribs = {'window': 'x.button2', 'pos': '(1, 1)', 'x.GridBagSizer.Add': 'x.this'}
        xobjects.xcall_attribs('wx.GBSizerItem', attribs)
        attribs = {'Proportion': '1', 'Flag': 'wx.ALL', 'Border': '20'}
        xobjects.xcall_attribs('x.this', attribs)
        # END SIZER

        xobjects.main_frame.Show()

        #    xobjects.button1.Label = 'New Label'
        #    xobjects.xcall('x.button2.Label', ('Label from xcall'), {})

        app.MainLoop()


    main()
