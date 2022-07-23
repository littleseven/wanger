#! /usr/bin/env python 
# -*- encoding: utf-8 -*-
# author 王二

import wx
import wx.adv
import wx.grid
import wx.html2

from gui.constants import USE_WIT
from gui.frames.Main import MainFrame

AppBaseClass = wx.App
if USE_WIT:
    from wx.lib.mixins.inspection import InspectableApp
    AppBaseClass = InspectableApp


class GuiManager:
    def __init__(self):
        displaySize = wx.DisplaySize()  # (1920, 1080)
        MIN_DISPLAYSIZE = 1024, 800
        if (displaySize[0] < MIN_DISPLAYSIZE[0]) or (displaySize[1] < MIN_DISPLAYSIZE[1]):
            self.msg_dialog(f"由于您的显示器分辨率过低(低于{MIN_DISPLAYSIZE[0]},{MIN_DISPLAYSIZE[1]})，会导致部分控件显示异常！\
                           请调整显示器设置的【缩放比例】及【分辨率】")
            self.displaySize = MIN_DISPLAYSIZE[0], MIN_DISPLAYSIZE[1]
        else:
            self.displaySize = 1280, 800

    @staticmethod
    def msg_dialog(info):
        # 提示一些使用注意事项的对话框
        dlg_msg = wx.MessageDialog(None, info, u"温馨提示", wx.YES_NO | wx.ICON_INFORMATION)
        dlg_msg.ShowModal()
        dlg_msg.Destroy()


class WeApp(AppBaseClass):
    frame = None
    manager = None

    def __init__(self, redirect=False, filename=None, useBestVisual=True, clearSigInt=True):
        super().__init__(redirect, filename, useBestVisual, clearSigInt)

    def OnInit(self):
        self.manager = GuiManager()
        self.frame = MainFrame(None)
        # self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.SetTopWindow(self.frame)
        self.frame.Center()
        if USE_WIT:
            print("Press Ctrl-Alt-I (Cmd-Opt-I on Mac) to launch the WITH.")
            self.InitInspection()
        self.frame.Show()
        return True
