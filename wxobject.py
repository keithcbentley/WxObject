from typing import NewType, Optional, Type, Iterable, Union
from re import search as re_search, match as re_match, fullmatch as re_fullmatch
import wx

RealVarName = NewType('RealVarName', str)
TransientVarName = NewType('TransientVarName', str)
AnyVarName = Union[RealVarName, TransientVarName]
CodegenVarName = NewType('CodegenVarName', str)


def dump(header, obj):
    print(header)
    print(obj)
    print('self:')
    for key, val in obj.__dict__.items():
        if key == '__doc__':
            pass
        else:
            print('  ', key, '--->>>', val, 'type: ', type(val))
    # If obj is a type, call mro on it directly.
    if type(obj) == type:
        mro = obj.mro(type)
    elif isinstance(obj, type):
        mro = obj.mro()
    else:
        mro = obj.__class__.mro()
    for clazz in mro:
        print('  c: ', clazz)
        for key, val in clazz.__dict__.items():
            if key == '__doc__':
                pass
            else:
                print('    ', key, '--->>>', val, 'type: ', type(val))


class UI:
    pass


class WxObjectError(Exception):
    pass


class WindowAlreadyHasSizer(WxObjectError):
    pass


class SizerAlreadyHasWindow(WxObjectError):
    pass


class WxPythonEnhancements:
    set_sizer_original = wx.Window.SetSizer

    @staticmethod
    def wxpe_set_sizer(*args, **kwargs):
        window: Optional[wx.Window] = None
        sizer: Optional[wx.Sizer] = None
        if len(args) > 0:
            window = args[0]
        if len(args) > 1:
            sizer = args[1]
        if window is None:
            window = kwargs['window']
        if sizer is None:
            sizer = kwargs['sizer']

        if window.GetSizer() is not None:
            raise WindowAlreadyHasSizer
        # Call this before calling the original so that the
        # sizer can check if it's already been attached.
        sizer.sizer_attaching_to_window(window)
        WxPythonEnhancements.set_sizer_original(*args, **kwargs)

    @staticmethod
    def wxpe_sizer_attaching_to_window(sizer: wx.Sizer, window: wx.Window):
        try:
            old_window = sizer.attaching_window
            if old_window is not None:
                raise SizerAlreadyHasWindow
        except AttributeError:
            pass
        setattr(sizer, 'attaching_window', window)

    @staticmethod
    def attach_sizer_to_window(sizer: wx.Sizer, window: wx.Window):
        window.SetSizer(sizer)


class WxPythonEnhancer:
    wx.Window.SetSizer = WxPythonEnhancements.wxpe_set_sizer
    setattr(wx.Sizer, 'sizer_attaching_to_window', WxPythonEnhancements.wxpe_sizer_attaching_to_window)
    setattr(wx.Sizer, 'attach_sizer_to_window', WxPythonEnhancements.attach_sizer_to_window)


class FrameEntry:
    def __init__(self, any_var_name: AnyVarName, real_var_name: RealVarName, obj):
        super().__init__()
        self.any_var_name = any_var_name
        self.real_var_name = real_var_name
        self.obj = obj

    def __str__(self) -> str:
        return self.real_var_name + '  ' + str(self.obj)


class FrameMatchingIsinstanceResult:
    def __init__(self, clazz: Type, frame_entry: FrameEntry):
        super().__init__()
        self.clazz = clazz
        self.frame_entry = frame_entry

    def __str__(self) -> str:
        self_str = ''
        self_str += str(self.clazz)
        self_str += ' ' + str(self.frame_entry)
        return self_str


class Frame:
    def __init__(self):
        super().__init__()
        self.frame_entries = {}

    def __str__(self) -> str:
        self_str = ''
        self_str += 'Context Frame:\n'
        for key, val in self.frame_entries.items():
            self_str += key + '  ' + str(val) + '\n'
        return self_str

    def add_entry(self, any_var_name: AnyVarName, real_var_name: RealVarName, obj) -> None:
        r"""
        Adds a new entry to this frame.

        :param any_var_name:    a real or transient name for the object
        :param real_var_name:   the (unique) real name for the object
        :param obj:             the object
        :return: None
        """
        # TODO check if entry already exists.  If it already exists, it's probably an error.
        self.frame_entries[any_var_name] = FrameEntry(any_var_name, real_var_name, obj)

    def find_matching_isinstance(self, clazzes: Iterable[Type]) -> Optional[FrameMatchingIsinstanceResult]:
        r"""
        Searches through the entries in this frame to see if any of the objects
        is an instance of any of the classes given.  isinstance is used for the check
        so an object matches if it is an instance of the class or an instance of a subclass
        of the class.  (This is the normal behavior of isinstance.)  There is no guaranteed search
        order of either the entries or the classes so there is no guaranteed result if there are
        multiple matches.  Only the first matching result is returned.

        :param clazzes: an iterable of classes
        :return: a FrameMatchingInstanceResult if there is a match, otherwise None
        """
        for name, frame_entry in self.frame_entries.items():
            for clazz in clazzes:
                if isinstance(frame_entry.obj, clazz):
                    return FrameMatchingIsinstanceResult(clazz, frame_entry)
        return None


class Context:
    def __init__(self):
        super().__init__()
        self.frames = []

    def __str__(self) -> str:
        self_str = ''
        self_str += 'Context:\n'
        for frame in self.frames:
            self_str += str(frame)
        return self_str

    def push_frame(self) -> None:
        r"""
        Pushes a new empty frame onto the context.

        :return: None
        """
        self.frames.append(Frame())

    def pop_frame(self) -> None:
        r"""
        Pops the top (most recent) frame from the context.

        :return: None
        """
        self.frames.pop()

    def add_entry(self, any_var_name: AnyVarName, real_var_name: RealVarName, obj) -> None:
        r"""
        Adds a new entry to the topmost (most recent) frame on the context.

        :param any_var_name:    any var name for the frame entry
        :param real_var_name:   real var name for the frame entry
        :param obj:             object for the frame entry
        :return: None
        """
        self.frames[len(self.frames) - 1].add_entry(any_var_name, real_var_name, obj)

    def lookup_real_variable_name(self, name: AnyVarName) -> Optional[RealVarName]:
        r"""
        Search in reverse chronological order (most recent to least recent) to try
        to find the real name of a variable.

        :param name:    a real or transient variable name
        :return:        the real variable name or None if not found
        """
        # Search backwards.  Remember that -1 is the non-inclusive lower limit, not 0.
        for i in range(len(self.frames) - 1, -1, -1):
            if name in self.frames[i].frame_entries:
                return self.frames[i].frame_entries[name].real_var_name
        return None

    def find_nearest_isinstance(
            self,
            clazzes: Iterable[Type],
            skip_current=False
    ) -> Optional[FrameMatchingIsinstanceResult]:
        r"""
        Search in reverse chronological order (most recent to least recent) to try
        to find an object that is an instance of any of the classes given.

        :param clazzes:     classes to look for
        :param skip_current: skip the current (most recent) frame
        :return: a FrameMatchingIsinstanceResult or None if not found
        """
        start_index = len(self.frames) - 1
        if skip_current:
            start_index -= 1
        for i in range(start_index, -1, -1):
            frame_matching_instance_result = self.frames[i].find_matching_isinstance(clazzes)
            if frame_matching_instance_result is not None:
                return frame_matching_instance_result
        return None


class WxObjects:
    def __init__(self, ui: UI):
        super().__init__()
        self.ui = ui
        self.context = Context()
        self.variable_counter = 0
        self.real_variable_name: RealVarName = RealVarName('')
        self.output_codegen = False

        self.xenv = {
            'wx': wx,
            'x': self.ui,
            '__builtins__': {}
        }

    def set_new_runtime_variable_name(self, uiid: Optional[str]) -> None:
        r"""
        Sets the (current) runtime variable name.
        If uiid is not None, the uiid itself is used as the variable name.
        If uiid is None, a new variable name is autogenerated.
        Note that uiid is not an optional parameter but it may be None.
        """
        if uiid is not None:
            self.real_variable_name = uiid
            return
        self.real_variable_name = 'var{n}'.format(n=self.variable_counter)
        self.variable_counter += 1

    def codegen_output_line(self, output_string: str) -> None:
        if self.output_codegen:
            print(output_string)

    def codegen_get_current_variable_name(self) -> CodegenVarName:
        return CodegenVarName('self.' + self.real_variable_name)

    def codegen_get_replace_variable_name(self, name: AnyVarName) -> CodegenVarName:
        lookup_name = self.context.lookup_real_variable_name(name)
        if lookup_name is not None:
            return CodegenVarName('self.' + lookup_name)
        # TODO validate that the name is actually on the ui object.
        return CodegenVarName('self.' + name)

    def runtime_get_replace_variable_name(self, name: AnyVarName) -> RealVarName:
        # See if the name is a transient name and replace if necessary.
        # For runtime replacements, we put the x. prefix back on the variable.
        lookup_name = self.context.lookup_real_variable_name(name)
        if lookup_name is not None:
            return RealVarName('x.' + lookup_name)
        # TODO validate that the name is actually on the ui object.
        return RealVarName('x.' + name)

    @staticmethod
    def xname_replacement(original_str: str, replacement_method) -> str:
        # fullx is everything that ends in x. x is just the end part.
        # If they are the same, it's a single x.name
        # pattern
        #    grab everything that looks like: prefix_ends_in_x.name
        #    inside the prefix_ends_in_x part, grab just the x part.
        pattern = r"""(?P<fullx>[a-zA-z0-9_]*(?P<x>x\.(?P<name>[a-zA-Z0-9_]+)))"""
        # Build up the new string by skipping or replacing items.
        new = ''
        remainder = original_str
        while True:
            # IMPORTANT be sure to use search, not match.
            # match only matches at the beginning of the string.
            result = re_search(pattern, remainder)
            if result is None:
                # Nothing (remaining) to skip or replace.
                return new + remainder

            # Not a "real" x name.  Skip over it.
            if result['fullx'] != result['x']:
                skip_end = result.span('fullx')[1]
                skipped = remainder[0:skip_end]
                new = new + skipped
                remainder = remainder[skip_end:]
            else:
                # Got a real x match, do the replacement.
                replace_start = result.span('x')[0]
                replace_end = result.span('x')[1]
                old_name = TransientVarName(result['name'])  # assume it's transient.
                new_name = replacement_method(old_name)
                replaced = remainder[0:replace_start] + new_name
                new = new + replaced
                remainder = remainder[replace_end:]

    def codegen_xname_replacement(self, original_str: str) -> str:
        return WxObjects.xname_replacement(original_str, self.codegen_get_replace_variable_name)

    def runtime_xname_replacement(self, original_str: str) -> str:
        return WxObjects.xname_replacement(original_str, self.runtime_get_replace_variable_name)

    def codegen_functioncall(self, function_name_string, args, kwargs, needs_var):
        positional_args_string = ''
        have_positional = False
        for arg in args:
            if have_positional:
                positional_args_string += ', '
            have_positional = True
            if arg.startswith('*'):
                stripped = arg[2:-1]  # get rid of asterisk and leading and trailing paren. Fragile.
                positional_args_string += self.codegen_xname_replacement(stripped)
            else:
                positional_args_string += self.codegen_xname_replacement(arg)
        kwargs_string = ''
        have_kw = False
        for arg_name, arg_val in kwargs.items():
            if have_kw:
                kwargs_string += ', '
            have_kw = True
            vs = self.codegen_xname_replacement(arg_val)
            kwargs_string += arg_name + '=' + vs
        separator = ',' if have_positional and have_kw else ''

        function_call_template = '{variable}{s}({positional}{separator}{kw})'
        function_call_string = function_call_template.format(
            variable=self.codegen_get_current_variable_name() + '=' if needs_var else '',
            s=self.codegen_xname_replacement(function_name_string),
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

    def xeval(self, str_to_eval):
        replacement_string = self.runtime_xname_replacement(str_to_eval)
        return eval(replacement_string, self.xenv, {})

    class XCallResult:
        def __init__(self, real_var_name, result):
            super().__init__()
            self.real_var_name = real_var_name
            self.result = result

    def xcall(self, s, *args_strings, needs_var=True, uiid=None, **kwargs_strings):
        args_eval = ()
        for a in args_strings:
            if a.startswith('*'):
                args_eval += self.xeval(a[1:])
            else:
                args_eval += (self.xeval(a),)
        kwargs_eval = {}
        for k, v in kwargs_strings.items():
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
            self.set_new_runtime_variable_name(uiid)
            thing = funcorprop(*args_eval, **kwargs_eval)
            if needs_var:
                self.save_ui_object(self.real_variable_name, thing)
                self.context.add_entry(TransientVarName(last), self.real_variable_name, thing)
                self.context.add_entry(TransientVarName('this'), self.real_variable_name, thing)

            self.codegen_functioncall(s, args_strings, kwargs_strings, needs_var)
            return self.XCallResult(self.real_variable_name, thing)
        # else try it as a property.
        if not args_eval:
            # No positional args, so multiple properties are in the kwargs.
            # The entire function string is the object.
            obj = self.xeval(s)
            for property_name, property_value in kwargs_eval.items():
                # Set the property on the object itself, not the ui object.
                obj.__setattr__(property_name, property_value)
                self.codegen_property(s, property_name, kwargs_strings[property_name])
            return None
        # Got positional arg so assume property value is the first positional arg.
        # The object is the first part of the function string and the property s is the last part.
        objstr = '.'.join(part_names[0:-1])
        obj = self.xeval(objstr)
        obj.__setattr__(last, args_eval[0])  # Set the property on the object itself, not the ui object.
        self.codegen_property(objstr, last, args_strings[0])
        return None  # TODO: is there anything more useful to return?

    def xcall_attribs(self, s, attribs):
        attribs_copy = attribs.copy()
        id_str = 'ui.id'
        uiid = None
        if id_str in attribs_copy:
            uiid = attribs_copy[id_str]
            del attribs_copy[id_str]
        if 'xobj_id' in attribs_copy:
            del attribs_copy['xobj_id']
        if 'xobj_id_ref' in attribs_copy:
            del attribs_copy['xobj_id_ref']
        kwargs = {}
        for k, v in attribs_copy.items():
            if k.find('.') < 0:
                kwargs[k] = v
            else:
                pass  # It's a dotted attribute to process after.
        for k in kwargs.keys():  # Remove undotted attributes.
            del attribs_copy[k]
        xcall_result = self.xcall(s, uiid=uiid, **kwargs)
        for k, v in attribs_copy.items():
            self.xcall(k, v, needs_var=False)
            self.context.pop_frame()
        return xcall_result

    @staticmethod
    def get_classname(clazz: Type):
        python_class_name_string = str(clazz)
        pattern = r""".* \'(?P<classname>.*)\'.*"""
        result = re_match(pattern, python_class_name_string)
        if result is None:
            return None
        name = result['classname']
        return name

    @staticmethod
    def get_param_map(obj):
        params = {}
        if isinstance(obj, type):
            mro = obj.mro()
        else:
            mro = obj.__class__.mro()
        # Scan classes in reverse order so that derived classes
        # can override base classes.
        mro.reverse()
        for clazz in mro:
            class_name = WxObjects.get_classname(clazz)
            if class_name in param_map:
                # TODO use a class/type here to clean up naming.
                param_entry = param_map[class_name][0]
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
        post_calls = None
        # Scan classes in reverse order so that derived classes
        # can override base classes.
        for clazz in mro:
            class_name = self.get_classname(clazz)
            if class_name in post_call_map:
                post_calls = post_call_map[class_name]
        return post_calls

    @staticmethod
    def is_constructorlike(element_string: str):
        pattern = r"[a-zA-z0-9_]*.[a-zA-z0-9_]*"
        if re_fullmatch(pattern, element_string):
            return True
        if element_string.endswith('.Create'):
            return True
        return False

    def on_element_start(self, element, namespace, prefix, name):
        #        print('Got element:', element, namespace, prefix, name)
        #        for k, v in element.attrib.items():
        #            print(k, v)
        call_attribs = element.attrib.copy()
        if prefix == 'wx':
            c = wx.__getattribute__(name)
            param_map = WxObjects.get_param_map(c)
            for param_name, target_class in param_map.items():
                if target_class is not None:  # param map uses None to disable attribute
                    nearest_matching_result = self.context.find_nearest_isinstance((target_class,))
                    if nearest_matching_result is not None:
                        varname = 'x.' + nearest_matching_result.frame_entry.real_var_name
                        if param_name not in call_attribs:
                            call_attribs[param_name] = varname
        xcall_result = self.xcall_attribs(prefix + '.' + name, call_attribs)
        if xcall_result is not None and WxObjects.is_constructorlike(prefix + '.' + name):
            post_calls = self.get_post_call(xcall_result.result)
            if post_calls is not None:
                classes = ()
                for post_call in post_calls:
                    classes += (post_call.clazz,)
                nearest_matching_result = self.context.find_nearest_isinstance(classes, skip_current=True)
                if nearest_matching_result is not None:
                    function_name = None
                    for post_call in post_calls:
                        if nearest_matching_result.clazz == post_call.clazz:
                            function_name = post_call.function_name
                    # Need to use xcall mechanism so that code is generated for the call.
                    self.xcall(
                        function_name,
                        'x.' + nearest_matching_result.frame_entry.real_var_name,
                        'x.' + xcall_result.real_var_name,
                        needs_var=False)
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
class PostCallEntry:
    def __init__(self, function_name: str, clazz: Type):
        super().__init__()
        self.function_name = function_name
        self.clazz = clazz


post_call_map = {
    'wx._core.StatusBar': [PostCallEntry('wx.Frame.SetStatusBar', wx.Frame)],
    'wx._core.MenuBar': [PostCallEntry('wx.Frame.SetMenuBar', wx.Frame)],
    'wx._core.MenuItem': [PostCallEntry('wx.Menu.Append', wx.Menu)],
    'wx._core.SizerItem': [PostCallEntry('wx.Sizer.Add', wx.Sizer)],
    'wx._core.GBSizerItem': [PostCallEntry('wx.GridBagSizer.Add', wx.GridBagSizer)]
}

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
