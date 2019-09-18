import sys
import os

import wx

import xobj
import wxobject

wx_namespace = "http://namespace.xobj.org/xobj/wx"

all_namespaces = {'': wx_namespace,
                  }

if __name__ == '__main__':
    # subclassing is not strictly necessary but it gets rid of warnings.
    class MyObjects(wxobject.WxObjects):
        def __init(self):
            super().__init__()
            self.main_frame = None
            self.helloItem = None
            self.aboutItem = None
            self.exitItem = None


    def OnHello(event):
        wx.MessageBox("Hello again from wxPython")


    def OnExit(frame, event):
        frame.Close(True)


    def OnAbout(event):
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK | wx.ICON_INFORMATION)


    def main():
        my_module = sys.modules[__name__]
        file = my_module.__file__
        own_dir = os.path.dirname(file)
        file1 = os.path.join(own_dir, 'hello2.xml')
        wxobjects1 = MyObjects()
        # xobjects.output_codegen = True
        ui1 = xobj.XobjParser(all_namespaces, wxobjects1)
        app = wx.App()

        ui1.instantiate_from_file(file1)
        main_frame = wxobjects1.main_frame
        main_frame.Bind(wx.EVT_MENU, OnHello, wxobjects1.helloItem)
        main_frame.Bind(wx.EVT_MENU, lambda event: OnExit(main_frame, event), wxobjects1.exitItem)
        main_frame.Bind(wx.EVT_MENU, OnAbout, wxobjects1.aboutItem)

        main_frame.Show()

        app.MainLoop()


    main()
