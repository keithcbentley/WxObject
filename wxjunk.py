import wx

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
