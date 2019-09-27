class WxObjectError(Exception):
    pass


class WindowAlreadyHasSizer(WxObjectError):
    pass


class SizerAlreadyHasParentWindow(WxObjectError):
    pass


class SizerAlreadyHasParentSizer(WxObjectError):
    pass


class UiAttributeNotFound(WxObjectError):
    def __init__(self, attribute_name):
        super().__init__('UI Attribute Not Found: ' + attribute_name)


class UiAttributeAlreadyInUse(WxObjectError):
    def __init__(self, attribute_name):
        super().__init__('UI Attribute Already In Use: ' + attribute_name)
