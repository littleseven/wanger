import wx


class MainPanel(wx.Panel):
    """
    Just a simple derived panel where we override Freeze and Thaw to work
    around an issue on wxGTK.
    """
    def Freeze(self):
        if 'wxMSW' in wx.PlatformInfo:
            return super(MainPanel, self).Freeze()

    def Thaw(self):
        if 'wxMSW' in wx.PlatformInfo:
            return super(MainPanel, self).Thaw()