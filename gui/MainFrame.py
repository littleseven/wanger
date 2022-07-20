#! /usr/bin/env python 
# -*- encoding: utf-8 -*-
# author 王二

import wx
import wx.adv
import wx.grid
import wx.html2
import os


class MainFrame(wx.Frame):
    rel_path = os.path.dirname(os.path.dirname(__file__)) + '/config/'

    def __init__(self, parent=None, id=-1, displaySize=(1280, 800), Fun_SwFrame=None):

        displaySize = 0.05 * displaySize[0], 0.5 * displaySize[1]

        wx.Frame.__init__(self, parent=None, title=u'', size=displaySize, style=wx.DEFAULT_FRAME_STYLE)

        self.fun_swframe = Fun_SwFrame
        toolbar = wx.ToolBar(self, style=wx.TB_TEXT | wx.TB_VERTICAL)
        img_quant = wx.Image(MainFrame.rel_path + "png/test.png", "image/png").Scale(55, 55)
        img_price = wx.Image(MainFrame.rel_path + "png/price.png", "image/png").Scale(55, 55)
        img_trade = wx.Image(MainFrame.rel_path + "png/trade.png", "image/png").Scale(55, 55)
        img_config = wx.Image(MainFrame.rel_path + "png/config.png", "image/png").Scale(55, 55)

        toolbar.AddTool(1100, '量化', wx.Bitmap(img_quant, wx.BITMAP_SCREEN_DEPTH))
        toolbar.AddSeparator()
        toolbar.AddTool(1101, '行情', wx.Bitmap(img_price, wx.BITMAP_SCREEN_DEPTH))
        toolbar.AddSeparator()
        toolbar.AddTool(1102, '交易', wx.Bitmap(img_trade, wx.BITMAP_SCREEN_DEPTH))
        toolbar.AddSeparator()
        toolbar.AddTool(1103, '配置', wx.Bitmap(img_config, wx.BITMAP_SCREEN_DEPTH))

        toolbar.Realize()
        toolbar.Bind(wx.EVT_TOOL, self.OnEventTrig)

    def OnEventTrig(self, event):
        if event.GetId() == 1100:  # 量化按钮
            self.fun_swframe(1)
        elif event.GetId() == 1101:  # 数据按钮
            self.fun_swframe(2)
        elif event.GetId() == 1102:  # 选股按钮
            # self.fun_swframe(3)
            print("功能预留-后期实现！")
        elif event.GetId() == 1103:  # 配置按钮
            self.fun_swframe(4)
        else:
            pass
