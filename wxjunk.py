import wx

app = wx.App()
frame = wx.Frame(parent=None, title='wxjunk')
panel = wx.Panel(parent=frame)
sizer = wx.BoxSizer(orient=wx.VERTICAL)
panel.SetSizer(sizer)
radio1 = wx.RadioButton(parent=panel, style=wx.RB_GROUP, label='radio1')
radio2 = wx.RadioButton(parent=panel, label='radio2')
sizer.Add(radio1)
sizer.Add(radio2)
frame.Show()
app.MainLoop()
