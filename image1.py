import sys
import os

import wx

import xobj
import wxobject

wx_namespace = "http://namespace.xobj.org/xobj/wx"

all_namespaces = {'': wx_namespace,
                  }


class ThisUI(wxobject.UI):
    def __init__(self):
        super().__init__()
        self.main_frame = None


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

        ui.main_frame.Show()
        app.MainLoop()


    main()
