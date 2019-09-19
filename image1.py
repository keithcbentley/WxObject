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
        file1 = os.path.join(own_dir, 'image1.xml')
        wxobjects = wxobject.WxObjects()
        wxobjects.output_codegen = True
        ui1 = xobj.XobjParser(all_namespaces, wxobjects)
        app = wx.App()

        ui1.instantiate_from_file(file1)

        wxobjects.ui.main_frame.Show()
        app.MainLoop()


    main()
