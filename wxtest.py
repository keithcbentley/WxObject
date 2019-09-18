import sys
import os

import wx

import xobj2
import wxobject

wx_namespace = "http://namespace.xobj.org/xobj/wx"

all_namespaces = {'': wx_namespace,
                  }

if __name__ == '__main__':
    def main():
        my_module = sys.modules[__name__]
        file = my_module.__file__
        own_dir = os.path.dirname(file)
        xobj_file1 = os.path.join(own_dir, 'wx1.xml')
        xobj_file2 = os.path.join(own_dir, 'wx2.xml')
        xobjects1 = wxobject.XObjects()
        xobjects2 = wxobject.XObjects()
        # xobjects.output_codegen = True
        ui1 = xobj2.Xobj2(all_namespaces, xobjects1)
        ui2 = xobj2.Xobj2(all_namespaces, xobjects2)
        app = wx.App()

        ui1.instantiate_from_file(xobj_file1)
        ui2.instantiate_from_file(xobj_file2)

        xobjects1.main_frame.Show()
        xobjects2.main_frame.Show()

        app.MainLoop()


    main()
