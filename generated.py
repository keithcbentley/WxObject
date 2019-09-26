import sys
import os

import wx


class ThisUI:
    def __init__(self):
        super().__init__()
        self.main_frame = wx.Frame(parent=None, title='sizerdemo')
        self.main_panel = wx.Panel(parent=self.main_frame)
        self.main_panel.BackgroundColour = wx.Colour(255, 255, 0)
        self.panel1 = wx.Panel(style=wx.BORDER_RAISED, parent=self.main_panel)
        self.statictext1 = wx.StaticText(label='StaticText1', style=wx.BORDER_SIMPLE, parent=self.panel1)
        self.statictext1.BackgroundColour = wx.Colour(0, 255, 0)
        self.statictext2 = wx.StaticText(label='StaticText2', style=wx.BORDER_SIMPLE, parent=self.panel1)
        self.statictext2.BackgroundColour = wx.Colour(0, 255, 0)
        self.statictext3 = wx.StaticText(label='StaticText3', style=wx.BORDER_SIMPLE, parent=self.panel1)
        self.statictext3.BackgroundColour = wx.Colour(0, 255, 0)
        self.main_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        wx.Window.SetSizer(self.main_frame, self.main_sizer)
        self.main_sizer_setsizer = self.main_panel.SetSizer(sizer=self.main_sizer)
        self.sizer1 = wx.BoxSizer()
        wx.Sizer.Add(self.main_sizer, self.sizer1)
        self.panel1_setsizer = self.panel1.SetSizer(sizer=self.sizer1)
        self.sizeritem_statictext1 = wx.SizerItem(window=self.statictext1, proportion=0, flag=wx.TOP | wx.CENTER,
                                                  border=10)
        wx.Sizer.Add(self.sizer1, self.sizeritem_statictext1)
        self.sizeritem_statictext2 = wx.SizerItem(window=self.statictext2, proportion=0,
                                                  flag=wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, border=20)
        wx.Sizer.Add(self.sizer1, self.sizeritem_statictext2)
        self.sizeritem_statictext3 = wx.SizerItem(window=self.statictext3, proportion=0, flag=wx.ALIGN_RIGHT)
        wx.Sizer.Add(self.sizer1, self.sizeritem_statictext3)
        self.sizeritem_panel1 = wx.SizerItem(window=self.panel1, flag=wx.EXPAND)
        wx.Sizer.Add(self.main_sizer, self.sizeritem_panel1)
        self.var6 = self.main_panel.Fit()


if __name__ == '__main__':
    def main():
        app = wx.App()
        ui = ThisUI()
        ui.main_frame.Show()
        app.MainLoop()


    main()
