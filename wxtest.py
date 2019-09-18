import sys
import os

import wx

import xobj
import wxobject

wx_namespace = "http://namespace.xobj.org/xobj/wx"

all_namespaces = {'': wx_namespace,
                  }

if __name__ == '__main__':
    def main():
        my_module = sys.modules[__name__]
        file = my_module.__file__
        own_dir = os.path.dirname(file)
        file1 = os.path.join(own_dir, 'wx1.xml')
        file2 = os.path.join(own_dir, 'wx2.xml')
        wxobjects1 = wxobject.WxObjects()
        wxobjects2 = wxobject.WxObjects()
        # xobjects.output_codegen = True
        ui1 = xobj.XobjParser(all_namespaces, wxobjects1)
        ui2 = xobj.XobjParser(all_namespaces, wxobjects2)
        app = wx.App()

        ui1.instantiate_from_file(file1)
        ui2.instantiate_from_file(file2)

        wxobjects1.main_frame.Show()
        wxobjects2.main_frame.Show()

        app.MainLoop()


    main()
