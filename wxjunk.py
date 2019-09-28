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
#    sizer.Add(sizer2)
    frame.Show()
    app.MainLoop()


main()
