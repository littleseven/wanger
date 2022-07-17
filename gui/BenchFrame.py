#! /usr/bin/env python 
# -*- encoding: utf-8 -*-
# author 王二

import wx
import wx.adv
import wx.grid
import wx.html2
import wx.lib.agw.aui as aui
import os


class BenchFrame(wx.Frame):
    rel_path = os.path.dirname(os.path.dirname(__file__)) + '/config/'

    def __init__(self, parent=None, id=-1, displaySize=(1550, 900), switchFrame=None):
        displaySize = 0.05 * displaySize[0], 0.5 * displaySize[1]
        wx.Frame.__init__(self, parent=None, title=u'', size=displaySize, style=wx.DEFAULT_FRAME_STYLE)
        self.uimanager = aui.AuiManager()
        self.uimanager.SetManagedWindow(self)
        toolbar = self._create_toolbar()
        self.uimanager.AddPane(toolbar, aui.AuiPaneInfo().Name('').Caption('工具条').ToolbarPane().Right().Floatable(True))
        self.uimanager.Update()
        self.switchFrame = switchFrame



    def _create_toolbar(self):
        toolbar = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                                 agwStyle=aui.AUI_TB_TEXT|aui.AUI_TB_VERTICAL)
        toolbar.SetToolBitmapSize((55, 55))
        img_quant = wx.Image(self.rel_path + "png/test.png", "image/png").Scale(55, 55)
        img_price = wx.Image(self.rel_path + "png/price.png", "image/png").Scale(55, 55)
        img_trade = wx.Image(self.rel_path + "png/trade.png", "image/png").Scale(55, 55)
        img_config = wx.Image(self.rel_path + "png/config.png", "image/png").Scale(55, 55)

        toolbar.AddSimpleTool(1100, '量化', wx.Bitmap(img_quant, wx.BITMAP_SCREEN_DEPTH), '量化')
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(1101, '行情', wx.Bitmap(img_price, wx.BITMAP_SCREEN_DEPTH), '行情')
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(1102, '交易', wx.Bitmap(img_trade, wx.BITMAP_SCREEN_DEPTH), '交易')
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(1103, '配置', wx.Bitmap(img_config, wx.BITMAP_SCREEN_DEPTH), '配置')

        toolbar.Realize()
        toolbar.Bind(wx.EVT_TOOL, self.OnEventTrig)
        return toolbar

    def OnEventTrig(self, event):
        if event.GetId() == 1100:  # 量化按钮
            self.switchFrame(1)
        elif event.GetId() == 1101:  # 数据按钮
            self.switchFrame(2)
        elif event.GetId() == 1102:  # 选股按钮
            # self.switchFrame(3)
            print("功能预留-后期实现！")
        elif event.GetId() == 1103:  # 配置按钮
            self.switchFrame(4)
        else:
            pass
