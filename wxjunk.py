import typing
import wx


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


class WxPythonEnhancements:
    set_sizer_old = wx.Window.SetSizer

    @staticmethod
    def my_set_sizer(*args, **kwargs):
        print('my_set_sizer', args, kwargs)
        window = args[0]
        sizer = args[1]
        if window.GetSizer() is not None:
            print('Window already has sizer')
            return
        try:
            old_window = sizer.window
            if old_window is not None:
                print('window is already set on sizer')
                return
        except AttributeError:
            pass
        sizer.sizer_set_to(window)
        WxPythonEnhancements.set_sizer_old(*args, **kwargs)

    @staticmethod
    def sizer_set_to(sizer, window):
        print('sizer_set_to:', sizer, window)
        setattr(sizer, 'window', window)


class WxPythonEnhancer:
    wx.Window.SetSizer = WxPythonEnhancements.my_set_sizer
    setattr(wx.Sizer, 'sizer_set_to', WxPythonEnhancements.sizer_set_to)


def main():
    app = wx.App()
    frame = wx.Frame(parent=None, title='wxjunk')
    panel = wx.Panel(parent=frame)
    panel.SetBackgroundColour(wx.Colour(255, 255, 0))
    panel2 = wx.Panel(parent=panel, style=wx.BORDER_RAISED)

    panel2.SetBackgroundColour(wx.Colour(200, 200, 255))
    radio1 = wx.RadioButton(parent=panel2, style=wx.RB_GROUP, label='radio1')
    radio2 = wx.RadioButton(parent=panel2, label='radio2')

    sizer = wx.BoxSizer()
    panel.SetSizer(sizer)
    sizer.Add(panel2, flag=wx.EXPAND)
    sizer2 = wx.BoxSizer(orient=wx.VERTICAL)
    panel2.SetSizer(sizer2)
    sizer2.Add(radio1)
    sizer2.Add(radio2)
    frame.Show()
    app.MainLoop()


main()
