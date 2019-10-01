import wx
import WxPythonEnhancements


class ThisUI:
    def __init__(self):
        super().__init__()
        self.internal_yellow = wx.Colour(red=255, green=255, blue=0)
        self.internal_pink = wx.Colour(red=255, green=200, blue=200)
        self.internal_lightgreen = wx.Colour(red=200, green=255, blue=200)
        self.current_image = wx.Image(width=100, height=100)
        self.main_frame = wx.Frame(parent=None, title='image1')
        self.main_panel = wx.Panel(parent=self.main_frame)
        self.image_panel = wx.Panel(parent=self.main_panel)
        self.display_bitmap_panel = wx.Panel(parent=self.image_panel)
        self.display_bitmap = wx.StaticBitmap(bitmap=wx.Bitmap(self.current_image), parent=self.display_bitmap_panel)
        self.control_panel = wx.Panel(parent=self.main_panel)
        self.browse_button = wx.Button(label='Browse', parent=self.control_panel)
        self.file_path_ctrl = wx.TextCtrl(size=(200,-1), parent=self.control_panel)
        self.main_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.main_sizer.attach_sizer_to_window(self.main_panel)
        self.internal_var1 = wx.SizerItem(window=self.image_panel, flag=wx.EXPAND, proportion=1)
        wx.Sizer.Add(self.main_sizer, self.internal_var1)
        self.internal_var3 = wx.SizerItem(window=self.control_panel, flag=wx.EXPAND)
        wx.Sizer.Add(self.main_sizer, self.internal_var3)
        self.internal_var5 = wx.BoxSizer()
        self.internal_var5.attach_sizer_to_window(self.image_panel)
        self.internal_var7 = wx.SizerItem(window=self.display_bitmap_panel, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        wx.Sizer.Add(self.internal_var5, self.internal_var7)
        self.internal_var9 = wx.BoxSizer()
        self.internal_var9.attach_sizer_to_window(self.control_panel)
        self.internal_var11 = wx.SizerItem(window=self.browse_button, proportion=0, flag=wx.ALL, border=5)
        wx.Sizer.Add(self.internal_var9, self.internal_var11)
        self.internal_var13 = wx.SizerItem(window=self.file_path_ctrl, proportion=1, flag=wx.ALL, border=7)
        wx.Sizer.Add(self.internal_var9, self.internal_var13)


if __name__ == '__main__':
    def main():
        app = wx.App()
        ui = ThisUI()
        ui.main_frame.Show()
        app.MainLoop()


    main()
