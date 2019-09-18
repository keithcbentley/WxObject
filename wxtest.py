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
        xobj_file = os.path.join(own_dir, 'wx1.xml')
        xobjects = wxobject.XObjects()
        # xobjects.output_codegen = True
        xobj = xobj2.Xobj2(all_namespaces, xobjects)
        app = wx.App()
        xobj.instantiate_from_file(xobj_file)

        xobjects.main_frame.Show()

        app.MainLoop()


    main()
