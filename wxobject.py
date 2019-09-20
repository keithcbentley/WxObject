from typing import *
import re
import wx

AnyVarName = NewType('AnyVarName', str)
RealVarName = NewType('RealVarName', AnyVarName)
UsableVarName = NewType('UsableVarName', str)
CodegenVarName = NewType('CodegenVarName', str)


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


class UI:
    pass


class FrameEntryValue:
    def __init__(self, real_var_name: RealVarName, obj):
        super().__init__()
        self.real_var_name = real_var_name
        self.obj = obj

    def __str__(self):
        s = ''
        s += self.real_var_name + '  ' + str(self.obj)
        return s


class Frame:
    def __init__(self):
        super().__init__()
        self.frame_entries = {}

    def __str__(self):
        s = ''
        s += 'Context Frame:\n'
        for k, v in self.frame_entries.items():
            s += k + '  ' + str(v) + '\n'
        return s

    def add_entry(self, var_name: AnyVarName, real_var_name: RealVarName, obj):
        # TODO check if entry already exists.
        self.frame_entries[var_name] = FrameEntryValue(real_var_name, obj)

    def get_matching_instance(self, c) -> Optional[FrameEntryValue]:
        for k, v in self.frame_entries.items():
            if isinstance(v.obj, c):
                return self.frame_entries[k]
        return None


class Context:
    def __init__(self):
        super().__init__()
        self.frames = []

    def __str__(self):
        s = ''
        s += 'Context:\n'
        for frame in self.frames:
            s += str(frame)
        return s

    def push_frame(self):
        self.frames.append(Frame())

    def pop_frame(self):
        self.frames.pop()

    def add_entry(self, var_name: AnyVarName, real_var_name: RealVarName, obj):
        self.frames[len(self.frames) - 1].add_entry(var_name, real_var_name, obj)

    def lookup_real_variable_name(self, name: AnyVarName) -> Optional[RealVarName]:
        for i in range(len(self.frames) - 1, -1, -1):
            if name in self.frames[i].frame_entries:
                return self.frames[i].frame_entries[name].real_var_name
        return None

    def get_real_variable_name(self, name):
        real_name = self.lookup_real_variable_name(name)
        if real_name is not None:
            return real_name
        return name

    def find_nearest_instance(self, c):
        for i in range(len(self.frames) - 1, -1, -1):
            matching_instance = self.frames[i].get_matching_instance(c)
            if matching_instance is not None:
                return matching_instance
        return None


class WxObjects:
    def __init__(self, ui: UI):
        super().__init__()
        self.ui = ui
        self.context = Context()
        self.current_uiid: RealVarName = None
        self.variable_counter = 0
        self.runtime_variable_name: RealVarName = None
        self.output_codegen = False

        self.xenv = {
            'wx': wx,
            'x': self.ui,
            '__builtins__': {}
        }

    def set_new_runtime_variable_name(self) -> None:
        if self.current_uiid is not None:
            self.runtime_variable_name = self.current_uiid
            return
        self.runtime_variable_name = 'var{n}'.format(n=self.variable_counter)
        self.variable_counter += 1

    def codegen_output_line(self, s) -> None:
        if self.output_codegen:
            print(s)

    def codegen_get_current_variable_name(self) -> CodegenVarName:
        return 'self.' + self.runtime_variable_name

    def codegen_get_replace_variable_name(self, name) -> CodegenVarName:
        return 'self.' + self.context.get_real_variable_name(name)

    def codegen_xname_replacement(self, s: str) -> str:
        # fullx is everything that ends in x. x is just the end part.
        # If they are the same, it's a single x.name
        pattern = r"""(?P<fullx>[a-zA-z0-9_]*(?P<x>x\.(?P<name>[a-zA-Z0-9_]+)))"""
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

    def save_ui_object(self, name, obj):
        self.ui.__setattr__(name, obj)

    def xeval(self, s):
        return eval(s, self.xenv, {})

    class XCallResult:
        def __init__(self, real_var_name, result):
            super().__init__()
            self.real_var_name = real_var_name
            self.result = result

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

        # Callers can't tell if this is a function call or property set.
        # Always push a frame so that callers can always pop the frame.
        # This will result in unused frames being pushed and popped but it's
        # cleaner for now.
        self.context.push_frame()
        funcorprop = self.xeval(s)
        part_names = s.split('.')
        last = part_names[-1]
        if callable(funcorprop):
            self.set_new_runtime_variable_name()
            thing = funcorprop(*args_eval, **kwargs_eval)
            if needs_var:
                self.save_ui_object(self.runtime_variable_name, thing)
                self.save_ui_object(last, thing)  # this is the 'magic' last name
                self.context.add_entry(self.runtime_variable_name, self.runtime_variable_name, thing)
                self.context.add_entry(last, self.runtime_variable_name, thing)

            self.codegen_functioncall(s, args, kwargs, needs_var)
            #            if needs_var:
            #                self.set_replace_variable_name(last)
            self.current_uiid = None  # safety, make sure we don't accidentally reuse
            return self.XCallResult(self.runtime_variable_name, thing)
        # else try it as a property.
        if len(args_eval) == 0:
            # No positional args, so multiple properties are in the kwargs.
            # The entire function string is the object.
            for k, v in kwargs_eval.items():
                obj = self.xeval(s)
                obj.__setattr__(k, v)  # Set the property on the object itself, not the ui object.
                self.codegen_property(s, k, kwargs[k])
            return None
        # Got positional arg so assume property value is the first positional arg.
        # The object is the first part of the function string and the property s is the last part.
        objstr = '.'.join(part_names[0:-1])
        obj = self.xeval(objstr)
        obj.__setattr__(last, args_eval[0])  # Set the property on the object itself, not the ui object.
        self.codegen_property(objstr, last, args[0])
        return None  # TODO: is there anything more useful to return?

    def xcall_attribs(self, s, attribs):
        attribs_copy = attribs.copy()
        id_str = 'ui.id'
        self.current_uiid = None
        if id_str in attribs_copy:
            self.current_uiid = attribs_copy[id_str]
            del attribs_copy[id_str]
        kwargs = {}
        for k, v in attribs_copy.items():
            if k.find('.') < 0:
                kwargs[k] = v
            else:
                pass  # It's a dotted attribute to process after.
        for k in kwargs.keys():  # Remove undotted attributes.
            del attribs_copy[k]
        xcall_result = self.xcall(s, **kwargs)
        for k, v in attribs_copy.items():
            self.xcall(k, v, needs_var=False)
            self.context.pop_frame()
        return xcall_result

    def get_classname(self, c):
        sname = str(c)
        pattern = r""".* \'(?P<classname>.*)\'.*"""
        result = re.match(pattern, sname)
        if result is None:
            return None
        name = result['classname']
        return name

    def get_param_map(self, obj):
        params = {}
        if isinstance(obj, type):
            mro = obj.mro()
        else:
            mro = obj.__class__.mro()
        # Scan classes in reverse order so that derived classes
        # can override base classes.
        mro.reverse()
        for c in mro:
            cname = self.get_classname(c)
            if cname in param_map:
                # TODO use a class/type here to clean up naming.
                param_entry = param_map[cname][0]
                param_name = param_entry[0]
                param_value = param_entry[1]
                params[param_name] = param_value
        return params

    def get_post_call(self, obj):
        if isinstance(obj, type):
            mro = obj.mro()
        else:
            mro = obj.__class__.mro()
        mro.reverse()
        post_call = None
        # Scan classes in reverse order so that derived classes
        # can override base classes.
        for c in mro:
            cname = self.get_classname(c)
            if cname in post_call_map:
                post_call = post_call_map[cname]
        return post_call

    def on_element_start(self, element, namespace, prefix, name):
        #        print('Got element:', element, namespace, prefix, name)
        #        for k, v in element.attrib.items():
        #            print(k, v)
        call_attribs = element.attrib.copy()
        if prefix == 'wx':
            c = wx.__getattribute__(name)
            param_map = self.get_param_map(c)
            for param_name, target_class in param_map.items():
                if target_class is not None:  # param map uses None to disable attribute
                    nearest = self.context.find_nearest_instance(target_class)
                    if nearest is not None:
                        varname = 'x.' + nearest.real_var_name
                        if param_name not in call_attribs:
                            call_attribs[param_name] = varname
        xcall_result = self.xcall_attribs(prefix + '.' + name, call_attribs)
        if xcall_result is not None:
            dump('thing:', xcall_result.result)
            post_call = self.get_post_call(xcall_result.result)
            if post_call is not None:
                fname, c = post_call
                nearest1 = self.context.find_nearest_instance(c)
                if nearest1 is not None:
                    # Need to use xcall mechanism so that code is generated for the call.
                    self.xcall(fname, 'x.' + nearest1.real_var_name, 'x.' + xcall_result.real_var_name)
                    self.context.pop_frame()

    def on_element_end(self, element, namespace, prefix, name):
        self.context.pop_frame()


# IMPORTANT Be sure to get the string case correct.
# wxPython uses a wrapper around the _core class.
# Getting an object's class name programmatically returns
# wx._core.name so in the tables below, you have to use this
# name for the class name string.  In the Python code itself,
# the class can be referenced as wx.name since Python handles the wrapper.
# class_name: [(param, param_class)]
# If you are an instance of class, use the closest instance of param_class as
# the argument for param.  (If param is not explicitly specified in the attribute list.
# Use None for param_class to disable the attribute.
param_map = {'wx._core.Window': [('parent', wx.Window)],
             'wx._core.MenuBar': [('parent', None)]
             }
# class_name: (method_name, target_class)
# method_name is a single argument method in the target_class
# If you are an instance of class_name, call method_name
# on the nearest instance of target_object_class with yourself
# # as the argument i.e.,
#       target_class instance.method_name(class_name instance)
# internally, it's actually called as
#       method_name(target_class instance, class_name instance)
post_call_map = {
    'wx._core.StatusBar': ('wx.Frame.SetStatusBar', wx.Frame),
    'wx._core.MenuBar': ('wx.Frame.SetMenuBar', wx.Frame),
    'wx._core.MenuItem': ('wx.Menu.Append', wx.Menu),
    'wx._core.SizerItem': ('wx.Sizer.Add', wx.Sizer),
    'wx._core.GBSizerItem': ('wx.GridBagSizer.Add', wx.GridBagSizer)}

if __name__ == '__main__':
    class ThisUi(UI):
        def __init__(self):
            super().__init__()
            self.main_window = None


    def main():
        app = wx.App(redirect=False)
        ui = ThisUi()
        xobjects = WxObjects(ui)
        xobjects.output_codegen = True

        # BEGIN FRAME
        attribs = {'ui.id': 'main_frame', 'parent': 'None', 'title': '"Hello Frame"'}
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
        attribs = {'ui.id': 'button1', 'parent': 'x.Panel', 'x.this.Label': '"Label from attribute"'}
        xobjects.xcall_attribs('wx.Button', attribs)

        attribs = {'ui.id': 'button2', 'parent': 'x.Panel', 'label': '"label2"'}
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
