from typing import Optional

import sys
import os

import wx

import xobj
import wxobject

wx_namespace = "local/xobj/wxobject"

all_namespaces = {'': wx_namespace,
                  }


class ThisUI(wxobject.UI):
    def __init__(self):
        super().__init__()
        self.image_size = 240
        self.current_image = wx.Image(width=self.image_size, height=self.image_size)
        self.main_frame: Optional[wx.Frame] = None
        self.main_panel: Optional[wx.Panel] = None
        self.image_panel: Optional[wx.Panel] = None
        self.control_panel: Optional[wx.Panel] = None
        self.browse_button: Optional[wx.Button] = None
        self.file_path_ctrl: Optional[wx.TextCtrl] = None
        self.display_bitmap: Optional[wx.StaticBitmap] = None

    def load_image(self):
        file_path = self.file_path_ctrl.GetValue()
        image = wx.Image(file_path, wx.BITMAP_TYPE_ANY)
        iwidth = image.GetWidth()
        iheight = image.GetHeight()
        if iwidth > iheight:
            NewW = self.image_size
            NewH = self.image_size * iheight / iwidth
        else:
            NewW = self.image_size * iwidth / iheight
            NewH = self.image_size
        simage = image.Scale(NewW, NewH)
        self.display_bitmap.SetBitmap(wx.Bitmap(simage))
        self.main_panel.Refresh()

    def on_browse_button(self, event):
        wildcard = "JPEG files (*.jpg) |*.jpg"
        with wx.FileDialog(
                parent=None,
                message="Choose a file",
                wildcard=wildcard,
                style=wx.FD_OPEN) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.file_path_ctrl.SetValue(dialog.GetPath())
                self.load_image()


if __name__ == '__main__':
    def main():
        my_module = sys.modules[__name__]
        file = my_module.__file__
        own_dir = os.path.dirname(file)
        file1 = os.path.join(own_dir, 'image1.xml')
        ui = ThisUI()
        wxobjects = wxobject.WxObjects(ui)
        # wxobjects.output_codegen = True
        xobj_parser = xobj.XobjParser(all_namespaces, wxobjects)
        app = wx.App()
        xobj_parser.instantiate_from_file(file1)

        ui.browse_button.Bind(wx.EVT_BUTTON, ui.on_browse_button)
        ui.main_frame.Layout()
        ui.main_frame.Show()
        app.MainLoop()


    main()
