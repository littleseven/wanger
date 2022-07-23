#! /usr/bin/env python 
# -*- encoding: utf-8 -*-
# author 王二
import os

import wx
import wx.adv
import wx.grid
import wx.html2

from gui.frames.MainFrame import MainFrame
from gui.frames.QuantFrame import QuantFrame

from gui.frames.ConfFrame import ConfFrame
from gui.frames.DataFrame import DataFrame

USE_WIT = True

AppBaseClass = wx.App
if USE_WIT:
    from wx.lib.mixins.inspection import InspectableApp
    AppBaseClass = InspectableApp

root_path = os.path.dirname(os.path.dirname(__file__))
config_path = root_path + '/config/'
data_path = root_path + '/datafiles/'

class GuiManager():
    def __init__(self, Fun_SwFrame):
        self.fun_swframe = Fun_SwFrame
        self.frameDict = {}  # 用来装载已经创建的Frame对象
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
        dlg_msg = wx.MessageDialog(None, info, u"温馨提示",
                                   wx.YES_NO | wx.ICON_INFORMATION)
        dlg_msg.ShowModal()
        dlg_msg.Destroy()

    def get_frame(self, type):
        frame = self.frameDict.get(type)
        if frame is None:
            frame = self.return_frame(type)
            self.frameDict[type] = frame
        return frame

    def return_frame(self, type):
        if type == 0:  # 主界面
            return MainFrame(parent=None, id=type,
                             displaySize=self.displaySize, switchFrame=self.fun_swframe)
        elif type == 1:  # 量化分析界面
            return QuantFrame(parent=None, id=type,
                              displaySize=self.displaySize, Fun_SwFrame=self.fun_swframe)
        elif type == 2:  # 数据管理界面
            return DataFrame(parent=None, id=type,
                             displaySize=wx.DisplaySize(), Fun_SwFrame=self.fun_swframe)
        elif type == 3:  #
            pass
        elif type == 4:  # 系统配置界面
            return ConfFrame(parent=None, id=type,
                             displaySize=wx.DisplaySize(), Fun_SwFrame=self.fun_swframe)


class MainApp(AppBaseClass):
    frame = None
    manager = None

    def __init__(self, redirect=False, filename=None, useBestVisual=True, clearSigInt=True):
        super().__init__(redirect, filename, useBestVisual, clearSigInt)

    def OnInit(self):
        self.manager = GuiManager(self.SwitchFrame)
        self.frame = self.manager.get_frame(0)
        # self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.SetTopWindow(self.frame)
        self.frame.Center()
        if USE_WIT:
            print("Press Ctrl-Alt-I (Cmd-Opt-I on Mac) to launch the WITH.")
            self.InitInspection()
        self.frame.Show()
        return True

    def SwitchFrame(self, type):
        # 切换Frame对象
        self.frame.Show(False)
        self.frame = self.manager.get_frame(type)
        self.frame.Show(True)
