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
            self.main_panel = None
            self.main_sizer = None
            self.panel1 = None
            self.panel2 = None
            self.statictext1 = None
            self.statictext2 = None
            self.statictext3 = None
            self.statictext2_1 = None
            self.statictext2_2 = None
            self.statictext2_3 = None


    def main():
        my_module = sys.modules[__name__]
        file = my_module.__file__
        own_dir = os.path.dirname(file)
        file1 = os.path.join(own_dir, 'sizerdemo.xml')
        ui = ThisUi()
        wxo = wxobject.WxObjects(ui)
        xobj_parser = xobj.XobjParser(all_namespaces, wxo)
        app = wx.App()
        xobj_parser.instantiate_from_file(file1)
        wxo.output_codegen('sizerdemo_generated.py')
        ui.main_frame.Show()
        app.MainLoop()


    main()
