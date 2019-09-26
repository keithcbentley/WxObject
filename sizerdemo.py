import sys
import os

import wx

import xobj
import wxobject

wx_namespace = "local/xobj/wxobject"

all_namespaces = {'': wx_namespace,
                  }

if __name__ == '__main__':
    class ThisUi(wxobject.UI):
        def __init__(self):
            super().__init__()
            self.main_frame = None


    def main():
        my_module = sys.modules[__name__]
        file = my_module.__file__
        own_dir = os.path.dirname(file)
        file1 = os.path.join(own_dir, 'sizerdemo.xml')
        ui = ThisUi()
        wxobjects = wxobject.WxObjects(ui)
        wxobjects.output_codegen = True
        xobj_parser = xobj.XobjParser(all_namespaces, wxobjects)
        app = wx.App()
        xobj_parser.instantiate_from_file(file1)
        ui.main_frame.Show()
        app.MainLoop()


    main()