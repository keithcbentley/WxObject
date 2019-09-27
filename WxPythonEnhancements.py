import wx

class WxPythonEnhancements:
    set_sizer_original = wx.Window.SetSizer

    @staticmethod
    def wxpe_set_sizer(*args, **kwargs):
        window: Optional[wx.Window] = None
        sizer: Optional[wx.Sizer] = None
        if len(args) > 0:
            window = args[0]
        if len(args) > 1:
            sizer = args[1]
        if window is None:
            window = kwargs['window']
        if sizer is None:
            sizer = kwargs['sizer']

        if window.GetSizer() is not None:
            raise WindowAlreadyHasSizer
        # Call this before calling the original so that the
        # sizer can check if it's already been attached.
        sizer.sizer_attaching_to_window(window)
        WxPythonEnhancements.set_sizer_original(*args, **kwargs)

    @staticmethod
    def wxpe_sizer_attaching_to_window(sizer: wx.Sizer, window: wx.Window):
        try:
            old_window = sizer.attaching_window
            if old_window is not None:
                raise SizerAlreadyHasWindow
        except AttributeError:
            pass
        setattr(sizer, 'attaching_window', window)

    @staticmethod
    def attach_sizer_to_window(sizer: wx.Sizer, window: wx.Window):
        window.SetSizer(sizer)


class WxPythonEnhancer:
    wx.Window.SetSizer = WxPythonEnhancements.wxpe_set_sizer
    setattr(wx.Sizer, 'sizer_attaching_to_window', WxPythonEnhancements.wxpe_sizer_attaching_to_window)
    setattr(wx.Sizer, 'attach_sizer_to_window', WxPythonEnhancements.attach_sizer_to_window)
