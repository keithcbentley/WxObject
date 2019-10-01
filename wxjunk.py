import typing
import wx


def dump(header, obj):
    print(header)
    print(obj)
    print('self:')
    for key, val in obj.__dict__.items():
        if key == '__doc__':
            pass
        else:
            print('  ', key, '--->>>', val, 'type: ', type(val))
    # If obj is a type, call mro on it directly.
    if type(obj) == type:
        mro = obj.mro(type)
    elif isinstance(obj, type):
        mro = obj.mro()
    else:
        mro = obj.__class__.mro()
    for clazz in mro:
        print('  c: ', clazz)
        for key, val in clazz.__dict__.items():
            if key == '__doc__':
                pass
            else:
                print('    ', key, '--->>>', val, 'type: ', type(val))


class SpyMixin:
    def Layout(self, *args, **kwargs):
        print('Before Layout', self)
        ret = super().Layout(*args, **kwargs)
        print('After Layout', self)
        return ret

    def Show(self, *args, **kwargs):
        print('Before Show', self)
        ret = super().Show(*args, **kwargs)
        print('After Show', self)
        return ret

    def BeginRepositioningChildren(self, *args, **kwargs):
        print('Before BeginRepositioningChildren', self)
        ret = super().BeginRepositioningChildren(*args, **kwargs)
        print('After BeginRepositioningChildren', self)
        return ret

    def EndRepositioningChildren(self, *args, **kwargs):
        print('Before EndRepositioningChildren', self)
        ret = super().EndRepositioningChildren(*args, **kwargs)
        print('After EndRepositioningChildren', self)
        return ret

    def DoGetBestSize(self, *args, **kwargs):
        print('Before DoGetBestSize', self)
        ret = super().DoGetBestSize(*args, **kwargs)
        print('After DoGetBestSize', self, ret)
        return ret

    def DoGetBestClientSize(self, *args, **kwargs):
        print('Before DoGetBestClientSize', self)
        ret = super().DoGetBestClientSize(*args, **kwargs)
        print('After DoGetBestClientSize', self, ret)
        return ret

    def Fit(self, *args, **kwargs):
        print('Before Fit', self)
        ret = super().Fit(*args, **kwargs)
        print('After Fit', self)
        return ret

    def FitInside(self, *args, **kwargs):
        print('Before FitInisde', self)
        ret = super().FitInside(*args, **kwargs)
        print('After FitInside', self)
        return ret

    def GetBestHeight(self, *args, **kwargs):
        print('Before GetBestHeight')
        ret = super().GetBestHeight(*args, **kwargs)
        print('After GetBestHeight', ret)
        return ret

    def GetBestSize(self, *args, **kwargs):
        print('Before GetBestSize')
        ret = super().GetBestSize(*args, **kwargs)
        print('After GetBestSize', ret)
        return ret

    def GetBestVirtualSize(self, *args, **kwargs):
        print('Before GetBestVirtualSize')
        ret = super().GetBestVirtualSize(*args, **kwargs)
        print('After GetBestVirtualSize', ret)
        return ret

    def GetBestWidth(self, *args, **kwargs):
        print('Before GetBestWidth')
        ret = super().GetBestWidth(*args, **kwargs)
        print('After GetBestWidth', ret)
        return ret

    def GetMaxClientSize(self, *args, **kwargs):
        print('Before GetMaxClientSize')
        ret = super().GetMaxClientSize(*args, **kwargs)
        print('After GetMaxClientSize', ret)
        return ret

    def GetMaxHeight(self, *args, **kwargs):
        print('Before GetMaxHeight')
        ret = super().GetMaxHeight(*args, **kwargs)
        print('After GetMaxHeight', ret)
        return ret

    def GetMaxSize(self, *args, **kwargs):
        print('Before GetMaxSize')
        ret = super().GetMaxSize(*args, **kwargs)
        print('After GetMaxSize', ret)
        return ret

    def GetMaxWidth(self, *args, **kwargs):
        print('Before GetMaxWidth')
        ret = super().GetMaxWidth(*args, **kwargs)
        print('After GetMaxWidth', ret)
        return ret

    def GetMinClientSize(self, *args, **kwargs):
        print('Before GetMinClientSize')
        ret = super().GetMinClientSize(*args, **kwargs)
        print('After GetMinClientSize', ret)
        return ret

    def GetMinHeight(self, *args, **kwargs):
        print('Before GetMinHeight')
        ret = super().GetMinHeight(*args, **kwargs)
        print('After GetMinHeight', ret)
        return ret

    def GetMinSize(self, *args, **kwargs):
        print('Before GetMinSize')
        ret = super().GetMinSize(*args, **kwargs)
        print('After GetMinSize', ret)
        return ret

    def GetMinWidth(self, *args, **kwargs):
        print('Before GetMinWidth')
        ret = super().GetMinWidth(*args, **kwargs)
        print('After GetMinWidth', ret)
        return ret

    def SetClientRect(self, *args, **kwargs):
        print('Before SetClientRect')
        ret = super().SetClientRect(*args, **kwargs)
        print('After SetClientRect')
        return ret

    def SetClientSize(self, *args, **kwargs):
        print('Before SetClientSize')
        ret = super().SetClientSize(*args, **kwargs)
        print('After SetClientSize')
        return ret

    def SetRect(self, *args, **kwargs):
        print('Before SetRect')
        ret = super().SetRect(*args, **kwargs)
        print('After SetRect')
        return ret

    def SetSize(self, *args, **kwargs):
        print('Before SetSize')
        ret = super().SetSize(*args, **kwargs)
        print('After SetSize')
        return ret


class MyPanel(SpyMixin, wx.Panel):
    pass


class MyFrame(SpyMixin, wx.Frame):
    pass


class MyRadioButton(SpyMixin, wx.RadioButton):
    pass


class MyBoxSizer(SpyMixin, wx.BoxSizer):
    def SetContainingWindow(self, *args, **kwargs):
        print('Before SetContainingWindow')
        ret = super().SetContainingWindow(*args, **kwargs)
        print('After SetContainingWindow', ret)
        return ret


def on_frame_size(event: wx.SizeEvent):
    print('on_frame_size', event, event.EventObject, event.Size)
    event.Skip()


def on_panel_size(event: wx.SizeEvent):
    print('on_panel_size:', event, event.EventObject, event.Size)
    #    dump("event", event)
    event.Skip()


def on_panel2_size(event: wx.SizeEvent):
    print('on_panel2_size:', event, event.EventObject, event.Size)
    event.Skip()


def main():
    app = wx.App()
    frame = MyFrame(parent=None, title='wxjunk')
    frame.Bind(wx.EVT_SIZE, on_frame_size)
    panel = MyPanel(parent=frame)
    print('panel', panel)
    panel.Bind(wx.EVT_SIZE, on_panel_size)
    panel.SetBackgroundColour(wx.Colour(255, 255, 0))
    panel2 = MyPanel(parent=panel, style=wx.BORDER_RAISED)
    print('panel2', panel2)
    panel2.Bind(wx.EVT_SIZE, on_panel2_size)

    panel2.SetBackgroundColour(wx.Colour(200, 200, 255))
    radio1 = MyRadioButton(parent=panel2, style=wx.RB_GROUP, label='radio1')
    radio2 = MyRadioButton(parent=panel2, label='radio2', style=wx.EXPAND)

    sizer = MyBoxSizer()
    print('sizer:', sizer)
    # sizer.SetContainingWindow(panel)
    # print('sizer:', sizer, 'panel.GetSizer(): ', panel.GetSizer())
    # print('sizer:', sizer, 'sizer.GetWindow():', sizer.GetContainingWindow())
    panel.SetSizer(sizer)
    sizer.Add(panel2)
    sizer2 = MyBoxSizer(orient=wx.VERTICAL)
    print('sizer2:', sizer2)
    #    print('panel2.GetSizer(): ', panel2.GetSizer())
    #    sizer2.SetContainingWindow(panel2)
    #    print('sizer2:', sizer2, 'panel2.GetSizer(): ', panel2.GetSizer())
    panel2.SetSizer(sizer2)
    sizer2.Add(radio1)
    sizer2.Add(radio2)
    frame.Show()

    app.MainLoop()


main()
