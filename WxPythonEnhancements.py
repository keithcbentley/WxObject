from typing import Optional

import wx
import WxObjectException


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
            raise WxObjectException.WindowAlreadyHasSizer
        # Call this before calling the original so that the
        # sizer can check if it's already been attached.
        sizer.sizer_attaching_to_window(window)
        WxPythonEnhancements.set_sizer_original(*args, **kwargs)

    @staticmethod
    def wxpe_sizer_attaching_to_window(sizer: wx.Sizer, parent_window: wx.Window):
        try:
            old_parent_window = sizer.parent_window
            if old_parent_window is not None:
                raise WxObjectException.SizerAlreadyHasParentWindow
        except AttributeError:
            pass
        try:
            old_parent_sizer = sizer.parent_sizer
            if old_parent_sizer is not None:
                raise WxObjectException.SizerAlreadyHasParentSizer
        except AttributeError:
            pass
        setattr(sizer, 'parent_window', parent_window)

    @staticmethod
    def wxpe_attach_sizer_to_window(sizer: wx.Sizer, window: wx.Window):
        window.SetSizer(sizer)

    @staticmethod
    def wxpe_add_to_parent_sizer(this_sizer: wx.Sizer, parent_sizer: wx.Sizer):
        try:
            old_parent_window = this_sizer.parent_window
            if old_parent_window is not None:
                raise WxObjectException.SizerAlreadyHasParentWindow
        except AttributeError:
            pass
        try:
            old_parent_sizer = this_sizer.parent_sizer
            if old_parent_sizer is not None:
                raise WxObjectException.SizerAlreadyHasParentSizer
        except AttributeError:
            pass

        setattr(this_sizer, 'parent_sizer', parent_sizer)
        parent_sizer.Add(this_sizer)


class WxPythonEnhancer:
    wx.Window.SetSizer = WxPythonEnhancements.wxpe_set_sizer
    setattr(wx.Sizer, 'sizer_attaching_to_window', WxPythonEnhancements.wxpe_sizer_attaching_to_window)
    setattr(wx.Sizer, 'attach_sizer_to_window', WxPythonEnhancements.wxpe_attach_sizer_to_window)
    setattr(wx.Sizer, 'add_to_parent_sizer', WxPythonEnhancements.wxpe_add_to_parent_sizer)
