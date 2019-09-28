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
        self.available_bitmap_dimension = None
        self.current_image = None
        self.main_frame: Optional[wx.Frame] = None
        self.main_panel: Optional[wx.Panel] = None
        self.image_panel: Optional[wx.Panel] = None
        self.control_panel: Optional[wx.Panel] = None
        self.browse_button: Optional[wx.Button] = None
        self.file_path_ctrl: Optional[wx.TextCtrl] = None
        self.display_bitmap_panel: Optional[wx.Panel] = None
        self.display_bitmap: Optional[wx.StaticBitmap] = None
        self.main_sizer: Optional[wx.BoxSizer] = None

        # A separate panel around the bitmap is used to make resizing
        # the image easier.  If you try to use the bitmap directly, it
        # leads to recursion issues that complicate things.


class AppUI(ThisUI):
    def __init__(self):
        super().__init__()

    def load_scaled_image_to_display_bitmap(self):
        bitmap_width = self.available_bitmap_dimension[0]
        bitmap_height = self.available_bitmap_dimension[1]
        image_width = self.current_image.GetWidth()
        image_height = self.current_image.GetHeight()

        image_aspect = image_width / image_height
        bitmap_aspect = bitmap_width / bitmap_height
        if bitmap_aspect < image_aspect:
            # bitmap is relatively narrower than image
            # set width, scale height
            new_width = bitmap_width
            new_height = bitmap_height * bitmap_aspect / image_aspect
        else:
            # bitmap is relatively wider than image
            # set height, scale width
            new_height = bitmap_height
            new_width = bitmap_width * image_aspect / bitmap_aspect
        #        print('new_width, new_height:', new_width, new_height)
        scaled_image = self.current_image.Scale(new_width, new_height)
        new_bitmap = wx.Bitmap(scaled_image)
        self.display_bitmap.SetBitmap(new_bitmap)
        self.image_panel.Refresh()

    def load_image(self):
        file_path = self.file_path_ctrl.GetValue()
        self.current_image = wx.Image(file_path, wx.BITMAP_TYPE_ANY)
        self.load_scaled_image_to_display_bitmap()

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

    def on_display_bitmap_panel_size(self, event: wx.SizeEvent):
        self.available_bitmap_dimension = event.Size
        self.load_scaled_image_to_display_bitmap()


if __name__ == '__main__':
    def main():
        my_module = sys.modules[__name__]
        file = my_module.__file__
        own_dir = os.path.dirname(file)
        file1 = os.path.join(own_dir, 'image1.xml')
        ui = AppUI()
        wxo = wxobject.WxObjects(ui)
        xobj_parser = xobj.XobjParser(all_namespaces, wxo)
        app = wx.App()
        xobj_parser.instantiate_from_file(file1)
        wxo.output_codegen('image1_generated.py')
        ui.browse_button.Bind(wx.EVT_BUTTON, ui.on_browse_button)
        ui.display_bitmap_panel.Bind(wx.EVT_SIZE, ui.on_display_bitmap_panel_size)
        ui.main_frame.Show()
        app.MainLoop()


    main()
