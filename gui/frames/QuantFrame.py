#! /usr/bin/env python 
# -*- encoding: utf-8 -*-
# author 王二

import wx
import wx.adv
import wx.grid
import wx.html2
import os
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import webbrowser

from wx.lib.agw import aui

from gui import constants
from gui.panels.MainPanel import MainPanel
from gui.wigets.SysPanel import Sys_Panel
from gui.wigets.MpfGraphs import MpfGraphs
from gui.wigets.WebGraphs import WebGraphs
from gui.wigets.DefTreelist import CollegeTreeListCtrl
from gui.wigets.DefGrid import GridTable
from gui.wigets.DefEchart import Pyechart_Drive

from gui.wigets.DefDialog import UserDialog, MessageDialog, ImportFileDiag, GroupPctDiag, GroupTrendDiag, \
    ProgressDialog, ChoiceDialog, BrowserF10, WebDialog, DouBottomDialog
from gui.wigets.DefAnimation import AnimationDialog

from datautil.Tushare import Tspro_Backend
from datautil.FundData import readFundDatFromSql
from datautil.CrawerDaily import CrawerDailyBackend
from datautil.CrawerNorth import CrawerNorthBackend
from datautil.EastmUpLimit import UpLimitBackend
from datautil.CsvData import CsvBackend

# 分离控件事件中调用的子事件
from event.DefEvent import EventHandle
from strategy.StrategyGath import Base_Strategy_Group
from strategy.PattenGath import Base_Patten_Group

from common.FileUtil import FileUtil
from common.CodeTableUtil import CodeTableUtil
from common.CodePoolUtil import CodePoolUtil
from common.LogUtil import SysLog, BizLog
from common.MailUtil import auto_send_email

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.rcParams['figure.dpi'] = 50


class QuantFrame(wx.Frame):
    rel_path = constants.CONFIG_PATH
    contentWidth = 0
    contentHeight = 0

    def __init__(self, parent=None, id=-1, displaySize=(1600, 900), Fun_SwFrame=None):
        wx.Frame.__init__(self, parent=None, title=u'王二量化实验室', size=displaySize,
                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.checkEnv()
        self.setFrameSize(displaySize)
        self.SetIcon(wx.Icon(self.rel_path + "png/we.ico"))
        self.SetMinSize((640, 480))

        # 用于量化工具集成到整体系统中
        self.fun_swframe = Fun_SwFrame

        # 用 aui 做整体布局
        self._mgr = aui.AuiManager()
        self.mainPanel = mainPanel = MainPanel(self)
        self._mgr.SetManagedWindow(self.mainPanel)

        self.leftPanel = leftPanel = wx.Panel(mainPanel, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN)
        self.rightPanel = rightPanel = wx.Panel(mainPanel, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN)

        # 多子图布局对象
        self.FlexGridSizer = None

        # 存储单个行情数据
        self.stock_dat = pd.DataFrame()

        # 存储策略函数
        self.function = ''

        # 初始化事件调用接口
        self.EventHandle = EventHandle()
        self.call_method = self.EventHandle.call_method
        self.event_task = self.EventHandle.event_task

        # 添加参数布局
        self.vbox_sizer_left = wx.BoxSizer(wx.VERTICAL)  # 纵向box
        # self.vbox_sizer_left.Add(self._init_treelist_ctrl(), proportion=3, flag=wx.EXPAND | wx.BOTTOM, border=5)
        self.vbox_sizer_left.Add(self._init_text_log(leftPanel), proportion=1, flag=wx.EXPAND | wx.BOTTOM, border=5)
        self.vbox_sizer_left.Add(self._init_listbox_mult(leftPanel), proportion=1, flag=wx.EXPAND | wx.BOTTOM, border=5)
        self.vbox_sizer_left.Add(self._init_nav_notebook(leftPanel), proportion=2, flag=wx.EXPAND | wx.BOTTOM, border=5)
        # self.vbox_sizer_left.Add(self._init_grid_pl(), proportion=5, flag=wx.EXPAND | wx.BOTTOM, border=5)
        self.vbox_sizer_left.Fit(self)
        leftPanel.SetSizer(self.vbox_sizer_left)
        # 加载配置文件
        firm_para = FileUtil.load_sys_para("firm_para.json")
        back_para = FileUtil.load_sys_para("back_para.json")

        # 创建显示区面板
        self.QuantPanel = Sys_Panel(rightPanel, **firm_para['layout_dict'])  # 自定义
        self.BackMplPanel = Sys_Panel(rightPanel, **back_para['layout_dict'])  # 自定义
        self.BackMplPanel.Hide()
        self.tempStockPanel = self.QuantPanel

        # 第二层布局
        self.vbox_sizer_right = wx.BoxSizer(wx.VERTICAL)  # 纵向box
        self.vbox_sizer_right.SetMinSize((800, 800))
        self.vbox_sizer_right.Add(self._init_param_notebook(rightPanel), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 添加行情参数布局
        self.vbox_sizer_right.Add(self.tempStockPanel, proportion=9, flag=wx.EXPAND | wx.ALL, border=5)  # 添加行情参数布局

        # 创建text日志对象
        self._init_patten_log(rightPanel)
        self._init_grid_pk(rightPanel)
        self.vbox_sizer_right.Fit(self)
        rightPanel.SetSizer(self.vbox_sizer_right)

        # 第一层布局
        self._init_status_bar()
        self._init_menu_bar()
        toolbar = self._create_toolbar(mainPanel)
        toolbar.Bind(wx.EVT_TOOL, self.OnEventTrig)
        self._mgr.AddPane(toolbar, aui.AuiPaneInfo().Name('').Caption('工具条').ToolbarPane().Right().Floatable(True))
        self._mgr.AddPane(self.leftPanel,
                          aui.AuiPaneInfo().
                          Left().Layer(2).BestSize((self.leftWidth, self.leftHeight)).
                          MinSize((self.leftWidth, self.leftHeight)).
                          Floatable(True).FloatingSize((self.leftWidth, self.leftHeight)).
                          CloseButton(False).
                          Name("LeftPanel"))
        self._mgr.AddPane(self.rightPanel, aui.AuiPaneInfo().CenterPane().Name("RightPanel").Resizable(True))
        self.mainPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainPanel.Layout()
        # 初始化全部页面
        # self.switch_content_panel(self.patten_log_sizer, self.grid_pick_box, False)
        # self.switch_content_panel(self.grid_pick_box, self.BackMplPanel, False)
        # self.switch_content_panel(self.BackMplPanel, self.QuantPanel, True)  # 等类型替换

        self.mainPanel.SetSizerAndFit(self.mainPanelSizer)  # 使布局有效
        self.mainPanelSizer.Layout()
        ################################### 辅助配置 ###################################
        self.syslog = SysLog(self.sys_log_tx)
        self.patlog = BizLog(self.patten_log_text)

        # self.timer = wx.Timer(self)  # 创建定时器
        # self.Bind(wx.EVT_TIMER, self.ev_int_timer, self.timer)  # 绑定一个定时器事件

        ################################### 加载股票代码表 ###################################
        self.code_table = CodeTableUtil(self.syslog)
        self.code_table.update_stock_code()

        ################################### 加载自选股票池 ###################################
        self.code_pool = CodePoolUtil(self.syslog)
        self.grid_stock_pool.SetTable(self.code_pool.load_my_pool(), ["自选股", "代码"])

        self._mgr.Update()
        self._mgr.SetAGWFlags(self._mgr.GetAGWFlags() ^ aui.AUI_MGR_TRANSPARENT_DRAG)
        self.CenterOnScreen(wx.BOTH)

    def _init_treelist_ctrl(self, subpanel):

        # 创建一个 treeListCtrl object
        self.treeListCtrl = CollegeTreeListCtrl(parent=subpanel, pos=(-1, 39), size=(250, 200))
        self.treeListCtrl.Bind(wx.EVT_TREE_SEL_CHANGED, self._ev_click_on_treelist)

        return self.treeListCtrl

    def _init_nav_notebook(self, parent):
        # 左侧参数区面板
        self.navNoteBook = wx.Notebook(parent)

        self.navNoteBook.AddPage(self._init_treelist_ctrl(self.navNoteBook), "策略导航")
        self.navNoteBook.AddPage(self._init_grid_stock_pool(self.navNoteBook), "股票池索引")

        return self.navNoteBook

    def _init_param_notebook(self, parent):
        # 创建参数区面板
        self.paramNotebook = wx.Notebook(parent)
        self.stockPanel = wx.Panel(self.paramNotebook, -1)  # 行情
        self.backTestPanel = wx.Panel(self.paramNotebook, -1)  # 回测 back test
        self.pickPanel = wx.Panel(self.paramNotebook, -1)  # 条件选股 pick stock
        self.patternPanel = wx.Panel(self.paramNotebook, -1)  # 形态选股 pattern

        # 第二层布局
        self.stockPanel.SetSizer(self.add_stock_para_lay(self.stockPanel))
        self.backTestPanel.SetSizer(self.add_backt_para_lay(self.backTestPanel))
        self.pickPanel.SetSizer(self.add_pick_para_lay(self.pickPanel))
        self.patternPanel.SetSizer(self.add_patten_para_lay(self.patternPanel))

        self.paramNotebook.AddPage(self.stockPanel, "行情参数")
        self.paramNotebook.AddPage(self.backTestPanel, "回测参数")
        self.paramNotebook.AddPage(self.pickPanel, "条件选股")
        self.paramNotebook.AddPage(self.patternPanel, "形态选股")

        # 此处涉及windows和macos的区别
        sys_para = FileUtil.load_sys_para("sys_para.json")
        if sys_para["operate_sys"] == "macos":
            self.paramNotebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._ev_change_notebook)
        else:
            self.paramNotebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._ev_change_notebook)

        return self.paramNotebook

    def _create_toolbar(self, parent):
        toolbar = aui.AuiToolBar(parent, -1, wx.DefaultPosition, wx.DefaultSize,
                                 agwStyle=aui.AUI_TB_TEXT | aui.AUI_TB_VERTICAL)
        toolbar.SetToolBitmapSize((35, 35))
        img_quant = wx.Image(self.rel_path + "png/test.png", "image/png").Scale(35, 35)
        img_price = wx.Image(self.rel_path + "png/price.png", "image/png").Scale(35, 35)
        img_trade = wx.Image(self.rel_path + "png/trade.png", "image/png").Scale(35, 35)
        img_config = wx.Image(self.rel_path + "png/config.png", "image/png").Scale(35, 35)

        toolbar.AddSimpleTool(1100, '量化', wx.Bitmap(img_quant, wx.BITMAP_SCREEN_DEPTH), '量化')
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(1101, '行情', wx.Bitmap(img_price, wx.BITMAP_SCREEN_DEPTH), '行情')
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(1102, '交易', wx.Bitmap(img_trade, wx.BITMAP_SCREEN_DEPTH), '交易')
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(1103, '配置', wx.Bitmap(img_config, wx.BITMAP_SCREEN_DEPTH), '配置')

        toolbar.Realize()
        # toolbar.Bind(wx.EVT_TOOL, self.OnEventTrig)
        return toolbar

    def _init_status_bar(self):

        self.statusBar = self.CreateStatusBar()  # 创建状态条
        # 将状态栏分割为3个区域,比例为2:1
        self.statusBar.SetFieldsCount(3)
        self.statusBar.SetStatusWidths([-2, -1, -1])
        t = time.localtime(time.time())
        self.SetStatusText("公众号：程序员道哥带你用Python量化交易", 0)
        self.SetStatusText("当前版本：%s" % FileUtil.load_sys_para("sys_para.json")["__version__"], 1)
        self.SetStatusText(time.strftime("%Y-%B-%d %I:%M:%S", t), 2)
        self.SetStatusText(time.strftime("%Y-%B-%d %I:%M:%S", t), 2)

    def _init_menu_bar(self):

        regMenuInfter = {"&星球量化工具": {"&基金持仓-预留": None, '&实时数据-预留': None, '&板块数据-预留': None, '&事件型回测-预留': None},
                         "&使用帮助": {"&报错排查": self._ev_err_guide_menu, '&功能说明': self._ev_funt_guide_menu},
                         "&股票池管理": {"&增量更新股票池": self._ev_code_inc_menu, "&完全替换股票池": self._ev_code_rep_menu},
                         "&主菜单": {"&返回": self._ev_switch_menu}}

        # 创建窗口面板
        menuBar = wx.MenuBar(style=wx.MB_DOCKABLE)

        if isinstance(regMenuInfter, dict):  # 使用isinstance检测数据类型
            for mainmenu, submenus in regMenuInfter.items():
                menuobj = wx.Menu()
                for submenu, funct in submenus.items():
                    subitem = wx.MenuItem(menuobj, wx.ID_ANY, submenu)
                    if funct != None:
                        self.Bind(wx.EVT_MENU, funct, subitem)  # 绑定事件
                    menuobj.AppendSeparator()
                    menuobj.Append(subitem)
                menuBar.Append(menuobj, mainmenu)
            self.SetMenuBar(menuBar)

        # 以上代码遍历方式完成以下的内容
        """
        # 返回主菜单按钮
        mainmenu = wx.Menu() 
        backitem = wx.MenuItem(mainmenu, wx.ID_ANY, '&返回')
        self.Bind(wx.EVT_MENU, self._ev_switch_menu, backitem)  # 绑定事件
        mainmenu.Append(backitem)
        menuBar.Append(mainmenu, '&主菜单')
        self.SetMenuBar(menuBar)
        """

    def switch_content_panel(self, org_panel=None, new_panel=None, inplace=True):

        if id(org_panel) != id(new_panel):
            # if not org_panel.IsShown():
            self.vbox_sizer_right.Hide(org_panel)
            if inplace:
                self.vbox_sizer_right.Replace(org_panel, new_panel)  # 等类型可替换
            else:
                # 先删除后添加
                self.vbox_sizer_right.Detach(org_panel)
                self.vbox_sizer_right.Add(new_panel, proportion=10, flag=wx.EXPAND | wx.BOTTOM, border=5)
            self.vbox_sizer_right.Show(new_panel)
            self.vbox_sizer_right.Layout()

    def _ev_change_notebook(self, event):
        # print(self.paramNotebook.GetSelection())
        old = event.GetOldSelection()
        new = event.GetSelection()

        sw_obj = [[self.QuantPanel, self.FlexGridSizer], self.BackMplPanel, self.grid_pick, self.patten_log_text]

        if (old >= len(sw_obj)) or (new >= len(sw_obj)):
            raise ValueError(u"切换面板号出错！")

        org_panel = sw_obj[old]
        new_panel = sw_obj[new]

        if (old == 0):
            if self.pick_graph_last != 0:
                org_panel = self.FlexGridSizer
            else:
                org_panel = self.QuantPanel

        if new == 0:
            if self.pick_graph_last != 0:
                new_panel = self.FlexGridSizer
            else:
                new_panel = self.QuantPanel

        ex_flag = False

        if type(sw_obj[old]) == type(sw_obj[new]):
            ex_flag = True  # 等类型可替换

        self.switch_content_panel(org_panel, new_panel, ex_flag)

    def add_stock_para_lay(self, sub_panel):

        # 行情参数
        stock_para_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 行情参数——日历控件时间周期
        self.dpc_end_time = wx.adv.DatePickerCtrl(sub_panel, -1,
                                                  style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)  # 结束时间
        self.dpc_start_time = wx.adv.DatePickerCtrl(sub_panel, -1,
                                                    style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)  # 起始时间

        self.start_date_box = wx.StaticBox(sub_panel, -1, u'开始日期(Start)')
        self.end_date_box = wx.StaticBox(sub_panel, -1, u'结束日期(End)')
        self.start_date_sizer = wx.StaticBoxSizer(self.start_date_box, wx.VERTICAL)
        self.end_date_sizer = wx.StaticBoxSizer(self.end_date_box, wx.VERTICAL)
        self.start_date_sizer.Add(self.dpc_start_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.end_date_sizer.Add(self.dpc_end_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.dpc_end_time.SetValue(date_time_now)
        self.dpc_start_time.SetValue(date_time_now.SetYear(date_time_now.year - 1))

        # 行情参数——输入股票代码
        self.stock_code_box = wx.StaticBox(sub_panel, -1, u'股票代码')
        self.stock_code_sizer = wx.StaticBoxSizer(self.stock_code_box, wx.VERTICAL)
        self.stock_code_input = wx.TextCtrl(sub_panel, -1, "sz.000876", style=wx.TE_PROCESS_ENTER)
        self.stock_code_sizer.Add(self.stock_code_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.stock_code_input.Bind(wx.EVT_TEXT_ENTER, self._ev_enter_stcode)

        # 行情参数——股票周期选择
        self.stock_period_box = wx.StaticBox(sub_panel, -1, u'股票周期')
        self.stock_period_sizer = wx.StaticBoxSizer(self.stock_period_box, wx.VERTICAL)
        self.stock_period_cbox = wx.ComboBox(sub_panel, -1, u"", choices=[u"30分钟", u"60分钟", u"日线", u"周线"])
        self.stock_period_cbox.SetSelection(2)
        self.stock_period_sizer.Add(self.stock_period_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 行情参数——股票复权选择
        self.stock_authority_box = wx.StaticBox(sub_panel, -1, u'股票复权')
        self.stock_authority_sizer = wx.StaticBoxSizer(self.stock_authority_box, wx.VERTICAL)
        self.stock_authority_cbox = wx.ComboBox(sub_panel, -1, u"", choices=[u"前复权", u"后复权", u"不复权"])
        self.stock_authority_cbox.SetSelection(2)
        self.stock_authority_sizer.Add(self.stock_authority_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                       border=2)

        # 行情参数——多子图显示
        self.pick_graph_box = wx.StaticBox(sub_panel, -1, u'多子图显示')
        self.pick_graph_sizer = wx.StaticBoxSizer(self.pick_graph_box, wx.VERTICAL)
        self.pick_graph_cbox = wx.ComboBox(sub_panel, -1, u"未开启",
                                           choices=[u"未开启", u"A股票走势-MPL", u"B股票走势-MPL", u"C股票走势-MPL", u"D股票走势-MPL",
                                                    u"A股票走势-WEB", u"B股票走势-WEB", u"C股票走势-WEB", u"D股票走势-WEB"],
                                           style=wx.CB_READONLY | wx.CB_DROPDOWN)
        self.pick_graph_cbox.SetSelection(0)
        self.pick_graph_last = self.pick_graph_cbox.GetSelection()
        self.pick_graph_sizer.Add(self.pick_graph_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.pick_graph_cbox.Bind(wx.EVT_COMBOBOX, self._ev_select_graph)

        # 行情参数——股票组合分析
        self.group_analy_box = wx.StaticBox(sub_panel, -1, u'投资组合分析')
        self.group_analy_sizer = wx.StaticBoxSizer(self.group_analy_box, wx.VERTICAL)
        self.group_analy_cmbo = wx.ComboBox(sub_panel, -1, u"预留A",
                                            choices=[u"预留A", u"收益率/波动率", u"走势叠加分析", u"财务指标评分-预留"],
                                            style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 策略名称
        self.group_analy_sizer.Add(self.group_analy_cmbo, proportion=0,
                                   flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.group_analy_cmbo.Bind(wx.EVT_COMBOBOX, self._ev_group_analy)  # 绑定ComboBox事件

        stock_para_sizer.Add(self.start_date_sizer, proportion=0, flag=wx.EXPAND | wx.CENTER | wx.ALL, border=10)
        stock_para_sizer.Add(self.end_date_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.stock_code_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.stock_period_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.stock_authority_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.pick_graph_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        stock_para_sizer.Add(self.group_analy_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)

        return stock_para_sizer

    def add_backt_para_lay(self, sub_panel):

        # 回测参数
        back_para_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.init_cash_box = wx.StaticBox(sub_panel, -1, u'初始资金')
        self.init_cash_sizer = wx.StaticBoxSizer(self.init_cash_box, wx.VERTICAL)
        self.init_cash_input = wx.TextCtrl(sub_panel, -1, "100000", style=wx.TE_LEFT)
        self.init_cash_sizer.Add(self.init_cash_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.init_stake_box = wx.StaticBox(sub_panel, -1, u'交易规模')
        self.init_stake_sizer = wx.StaticBoxSizer(self.init_stake_box, wx.VERTICAL)
        self.init_stake_input = wx.TextCtrl(sub_panel, -1, "all", style=wx.TE_LEFT)
        self.init_stake_sizer.Add(self.init_stake_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        self.init_slippage_box = wx.StaticBox(sub_panel, -1, u'滑点')
        self.init_slippage_sizer = wx.StaticBoxSizer(self.init_slippage_box, wx.VERTICAL)
        self.init_slippage_input = wx.TextCtrl(sub_panel, -1, "0.01", style=wx.TE_LEFT)
        self.init_slippage_sizer.Add(self.init_slippage_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                     border=2)

        self.init_commission_box = wx.StaticBox(sub_panel, -1, u'手续费')
        self.init_commission_sizer = wx.StaticBoxSizer(self.init_commission_box, wx.VERTICAL)
        self.init_commission_input = wx.TextCtrl(sub_panel, -1, "0.0005", style=wx.TE_LEFT)
        self.init_commission_sizer.Add(self.init_commission_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                       border=2)

        self.init_tax_box = wx.StaticBox(sub_panel, -1, u'印花税')
        self.init_tax_sizer = wx.StaticBoxSizer(self.init_tax_box, wx.VERTICAL)
        self.init_tax_input = wx.TextCtrl(sub_panel, -1, "0.001", style=wx.TE_LEFT)
        self.init_tax_sizer.Add(self.init_tax_input, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 回测按钮
        self.start_back_but = wx.Button(sub_panel, -1, "开始回测")
        self.start_back_but.Bind(wx.EVT_BUTTON, self._ev_start_run)  # 绑定按钮事件

        # 交易日志
        self.trade_log_but = wx.Button(sub_panel, -1, "交易日志")
        self.trade_log_but.Bind(wx.EVT_BUTTON, self._ev_trade_log)  # 绑定按钮事件

        back_para_sizer.Add(self.init_cash_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        back_para_sizer.Add(self.init_stake_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        back_para_sizer.Add(self.init_slippage_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        back_para_sizer.Add(self.init_commission_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        back_para_sizer.Add(self.init_tax_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        back_para_sizer.Add(self.start_back_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        back_para_sizer.Add(self.trade_log_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        return back_para_sizer

    def add_pick_para_lay(self, sub_panel):

        # 选股参数
        pick_para_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 选股参数——日历控件时间周期
        self.dpc_cur_time = wx.adv.DatePickerCtrl(sub_panel, -1,
                                                  style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)  # 当前时间

        self.cur_date_box = wx.StaticBox(sub_panel, -1, u'当前日期(Start)')
        self.cur_date_sizer = wx.StaticBoxSizer(self.cur_date_box, wx.VERTICAL)
        self.cur_date_sizer.Add(self.dpc_cur_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.dpc_cur_time.SetValue(date_time_now)
        # self.dpc_cur_time.SetValue(date_time_now.SetDay(9)) # 以9日为例 先不考虑周末的干扰

        # 选股参数——条件表达式分析
        self.pick_stock_box = wx.StaticBox(sub_panel, -1, u'条件表达式选股')
        self.pick_stock_sizer = wx.StaticBoxSizer(self.pick_stock_box, wx.HORIZONTAL)

        self.pick_item_cmbo = wx.ComboBox(sub_panel, -1, choices=[],
                                          style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 选股项

        self.pick_cond_cmbo = wx.ComboBox(sub_panel, -1, u"大于",
                                          choices=[u"大于", u"等于", u"小于"],
                                          style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 选股条件
        self.pick_value_text = wx.TextCtrl(sub_panel, -1, "0", style=wx.TE_LEFT)

        self.sort_values_cmbo = wx.ComboBox(sub_panel, -1, u"不排列",
                                            choices=[u"不排列", u"升序", u"降序"],
                                            style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 排列条件

        self.pick_stock_sizer.Add(self.pick_item_cmbo, proportion=0,
                                  flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.pick_stock_sizer.Add(self.pick_cond_cmbo, proportion=0,
                                  flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.pick_stock_sizer.Add(self.pick_value_text, proportion=0,
                                  flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.pick_stock_sizer.Add(self.sort_values_cmbo, proportion=0,
                                  flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 子参数——剔除ST/*ST 及 标记自选股
        self.adv_select_box = wx.StaticBox(sub_panel, -1, u'勾选确认')
        self.adv_select_sizer = wx.StaticBoxSizer(self.adv_select_box, wx.HORIZONTAL)
        self.mark_self_chk = wx.CheckBox(sub_panel, label='标记自选股')
        self.mark_self_chk.Bind(wx.EVT_CHECKBOX, self._ev_mark_self)  # 绑定复选框事件

        self.remove_st_chk = wx.CheckBox(sub_panel, label='剔除ST/*ST')
        self.adv_select_sizer.Add(self.mark_self_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        self.adv_select_sizer.Add(self.remove_st_chk, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 子参数——选股数据源选取
        self.src_dat_box = wx.StaticBox(sub_panel, -1, u'选股数据源选取')
        self.src_dat_sizer = wx.StaticBoxSizer(self.src_dat_box, wx.HORIZONTAL)

        self.src_dat_cmbo = wx.ComboBox(sub_panel, -1, choices=["tushare每日指标",
                                                                "爬虫接口获取",
                                                                "基金季度持仓",
                                                                "离线每日指标",
                                                                "离线业绩预告",
                                                                "离线财务报告"],
                                        style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 选股项

        # 爬虫接口获取目前支持以下几类
        self.crawer_backend = {u"爬虫每日指标": CrawerDailyBackend,
                               u"爬虫北向资金": CrawerNorthBackend,
                               u"爬虫每日涨停": UpLimitBackend}

        self.src_dat_sizer.Add(self.src_dat_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        """
        self.src_dat_radio = wx.RadioBox(sub_panel, -1, label=u'数据源选取', choices=["tushare每日指标","离线每日指标"],
                                         majorDimension = 2, style = wx.RA_SPECIFY_ROWS)
        """
        self.src_dat_cmbo.Bind(wx.EVT_RADIOBUTTON, self._ev_src_choose)

        # 选股序列按钮——刷新数据 + 开始选股 + 保存结果
        self.start_pick_but = wx.Button(sub_panel, -1, "选股过程")
        self.start_pick_but.Bind(wx.EVT_BUTTON, self._ev_select_seq)  # 绑定按钮事件

        pick_para_sizer.Add(self.cur_date_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        pick_para_sizer.Add(self.pick_stock_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        pick_para_sizer.Add(self.adv_select_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        pick_para_sizer.Add(self.src_dat_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        pick_para_sizer.Add(self.start_pick_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)

        return pick_para_sizer

    def add_patten_para_lay(self, sub_panel):

        # 形态选股参数
        patten_para_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 形态选股参数——日历控件时间周期
        self.patten_end_time = wx.adv.DatePickerCtrl(sub_panel, -1,
                                                     style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)  # 结束时间
        self.patten_start_time = wx.adv.DatePickerCtrl(sub_panel, -1,
                                                       style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)  # 起始时间

        self.patten_start_date_box = wx.StaticBox(sub_panel, -1, u'开始日期(Start)')
        self.patten_end_date_box = wx.StaticBox(sub_panel, -1, u'结束日期(End)')
        self.patten_start_date_sizer = wx.StaticBoxSizer(self.patten_start_date_box, wx.VERTICAL)
        self.patten_end_date_sizer = wx.StaticBoxSizer(self.patten_end_date_box, wx.VERTICAL)
        self.patten_start_date_sizer.Add(self.patten_start_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                         border=2)
        self.patten_end_date_sizer.Add(self.patten_end_time, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                       border=2)

        date_time_now = wx.DateTime.Now()  # wx.DateTime格式"03/03/18 00:00:00"
        self.patten_end_time.SetValue(date_time_now)
        self.patten_start_time.SetValue(date_time_now.SetYear(date_time_now.year - 1))

        # 形态选股参数——股票周期选择
        self.patten_period_box = wx.StaticBox(sub_panel, -1, u'股票周期')
        self.patten_period_sizer = wx.StaticBoxSizer(self.patten_period_box, wx.VERTICAL)
        self.patten_period_cbox = wx.ComboBox(sub_panel, -1, u"", choices=[u"30分钟", u"60分钟", u"日线", u"周线"])
        self.patten_period_cbox.SetSelection(2)
        self.patten_period_sizer.Add(self.patten_period_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                     border=2)

        # 形态选股参数——股票复权选择
        self.patten_authority_box = wx.StaticBox(sub_panel, -1, u'股票复权')
        self.patten_authority_sizer = wx.StaticBoxSizer(self.patten_authority_box, wx.VERTICAL)
        self.patten_authority_cbox = wx.ComboBox(sub_panel, -1, u"", choices=[u"前复权", u"后复权", u"不复权"])
        self.patten_authority_cbox.SetSelection(2)
        self.patten_authority_sizer.Add(self.patten_authority_cbox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER,
                                        border=2)

        # 形态选股参数———形态类型选取
        self.patten_type_box = wx.StaticBox(sub_panel, -1, u'形态类型选取')
        self.patten_type_sizer = wx.StaticBoxSizer(self.patten_type_box, wx.HORIZONTAL)

        self.patten_type_cmbo = wx.ComboBox(sub_panel, -1, choices=["双底形态", "跳空缺口-预留", "金叉死叉-预留", "线性回归-预留"],
                                            style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 选股项
        self.patten_type_sizer.Add(self.patten_type_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 形态选股参数———股票池选取
        self.patten_pool_box = wx.StaticBox(sub_panel, -1, u'股票池选取')
        self.patten_pool_sizer = wx.StaticBoxSizer(self.patten_pool_box, wx.HORIZONTAL)

        self.patten_pool_cmbo = wx.ComboBox(sub_panel, -1, choices=["自选股票池", "全市场股票"],
                                            style=wx.CB_READONLY | wx.CB_DROPDOWN)  # 选股项
        self.patten_pool_sizer.Add(self.patten_pool_cmbo, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        # 选股按钮
        self.pick_patten_but = wx.Button(sub_panel, -1, "开始选股")
        self.pick_patten_but.Bind(wx.EVT_BUTTON, self._ev_patten_select)  # 绑定按钮事件

        # 保存按钮
        # self.save_patten_but = wx.Button(sub_panel, -1, "保存结果")
        # self.save_patten_but.Bind(wx.EVT_BUTTON, self._ev_patten_save)  # 绑定按钮事件

        patten_para_sizer.Add(self.patten_start_date_sizer, proportion=0, flag=wx.EXPAND | wx.CENTER | wx.ALL,
                              border=10)
        patten_para_sizer.Add(self.patten_end_date_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        patten_para_sizer.Add(self.patten_period_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        patten_para_sizer.Add(self.patten_authority_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        patten_para_sizer.Add(self.patten_type_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        patten_para_sizer.Add(self.patten_pool_sizer, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        patten_para_sizer.Add(self.pick_patten_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)
        # patten_para_sizer.Add(self.save_patten_but, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=10)

        return patten_para_sizer

    def _init_grid_pk(self, parent):
        # 初始化选股表格
        self.grid_pick = GridTable(parent=parent)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._ev_cell_lclick_pkcode, self.grid_pick)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self._ev_label_lclick_pkcode, self.grid_pick)

        self.df_use = pd.DataFrame()
        self.filter_result = pd.DataFrame()
        self.grid_pick.Hide()

    def _init_patten_log(self, parent):
        # 创建形态选股日志
        self.patten_log_text = wx.TextCtrl(parent=parent, style=wx.TE_MULTILINE, size=(self.rightWidth, 20))
        self.patten_log_text.AppendText("hello world")
        self.patten_log_text.Hide()

    def _init_grid_stock_pool(self, parent):
        # 初始化股票池表格
        self.grid_stock_pool = GridTable(parent=parent, nrow=0, ncol=2)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self._ev_click_plcode, self.grid_stock_pool)
        return self.grid_stock_pool

    def _init_listbox_mult(self, parent):

        self.mult_analyse_box = wx.StaticBox(parent, -1, u'组合分析股票池')
        self.mult_analyse_sizer = wx.StaticBoxSizer(self.mult_analyse_box, wx.VERTICAL)
        self.listBox = wx.ListBox(parent, -1, size=(self.leftWidth, self.M1S2_length), choices=[], style=wx.LB_EXTENDED)
        self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self._ev_list_select)
        self.mult_analyse_sizer.Add(self.listBox, proportion=0, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)

        return self.mult_analyse_sizer

    def _init_text_log(self, parent):

        # 创建并初始化系统日志框
        self.sys_log_box = wx.StaticBox(parent, -1, u'系统日志')
        self.sys_log_sizer = wx.StaticBoxSizer(self.sys_log_box, wx.VERTICAL)
        self.sys_log_tx = wx.TextCtrl(parent, style=wx.TE_MULTILINE, size=(self.leftWidth, self.M1S1_length))
        self.sys_log_sizer.Add(self.sys_log_tx, proportion=1, flag=wx.EXPAND | wx.ALL | wx.CENTER, border=2)
        return self.sys_log_sizer

    def refresh_grid(self, df, back_col=""):
        self.grid_pick.SetTable(df, self.tran_col)
        self.grid_pick.SetSelectCol(back_col)

    def _ev_select_graph(self, event):

        item = event.GetSelection()

        # 显示区一级切换
        if item != 0 and self.pick_graph_last == 0:  # 单图切到多子图

            if item <= 4:  # 1-4 属于MPL显示区
                self.graphs_obj = MpfGraphs(self.rightPanel)
            elif item <= 8:  # 5-8 属于WEB显示区
                self.graphs_obj = WebGraphs(self.rightPanel)
            else:  # 故障保护
                MessageDialog("一级切换-0错误！")
                self.graphs_obj = MpfGraphs(self.rightPanel)
            self.switch_content_panel(self.QuantPanel, self.graphs_obj.FlexGridSizer, False)
            self.FlexGridSizer = self.graphs_obj.FlexGridSizer

        elif item == 0 and self.pick_graph_last != 0:  # 多子图切到单图
            # print(self.vbox_sizer_right.GetItem(self.QuantPanel))
            self.switch_content_panel(self.FlexGridSizer, self.QuantPanel, False)

        elif item <= 4 and self.pick_graph_last > 4:
            self.graphs_obj = MpfGraphs(self.rightPanel)
            self.switch_content_panel(self.FlexGridSizer, self.graphs_obj.FlexGridSizer, True)
            self.FlexGridSizer = self.graphs_obj.FlexGridSizer

        elif item > 4 and self.pick_graph_last <= 4:
            self.graphs_obj = WebGraphs(self.rightPanel)
            self.switch_content_panel(self.FlexGridSizer, self.graphs_obj.FlexGridSizer, True)
            self.FlexGridSizer = self.graphs_obj.FlexGridSizer
        else:
            pass

        # 显示区二级切换
        if item == 1 or item == 5:
            self.tempStockPanel = self.graphs_obj.DispPanel0
            # self.ochl = self.DispPanel0.ochl
            # self.vol = self.DispPanel0.vol
        elif item == 2 or item == 6:
            self.tempStockPanel = self.graphs_obj.DispPanel1
            # self.ochl = self.DispPanel1.ochl
            # self.vol = self.DispPanel1.vol
        elif item == 3 or item == 7:
            self.tempStockPanel = self.graphs_obj.DispPanel2
            # self.ochl = self.DispPanel2.ochl
            # self.vol = self.DispPanel2.vol
        elif item == 4 or item == 8:
            self.tempStockPanel = self.graphs_obj.DispPanel3
            # self.ochl = self.DispPanel3.ochl
            # self.vol = self.DispPanel3.vol
        else:
            self.tempStockPanel = self.QuantPanel

        self.pick_graph_last = item

    def _ev_select_seq(self, event):

        select_msg = ChoiceDialog(u"选股流程点击处理事件", [u"第一步:刷新选股数据",
                                                  u"第二步:开始条件选股",
                                                  u"第三步:保存选股结果"])

        if select_msg == u"第一步:刷新选股数据":
            self._download_st_data()

        elif select_msg == u"第二步:开始条件选股":
            self._start_st_slect()

        elif select_msg == u"第三步:保存选股结果":
            self._save_st_result()

        else:
            pass

    def _start_st_slect(self):

        if self.df_use.empty == True:
            MessageDialog("请先获取选股数据！")
            return

        if self.mark_self_chk.GetValue() == True:  # 复选框被选中
            MessageDialog("先取消复选框！！！")
            return

        if self.remove_st_chk.GetValue() == True:  # 剔除ST/*ST

            self.df_use.dropna(subset=['股票名称'], inplace=True)
            self.df_use = self.df_use[self.df_use['股票名称'].apply(lambda x: x.find('ST') < 0)]

        val = self.pick_item_cmbo.GetStringSelection()  # 获取当前选股combox的选项

        if val in self.df_use.columns.tolist():  # DataFrame中是否存在指标

            para_value = self.pick_value_text.GetValue()

            if val in [u"股票代码", u"所属行业", u"股票名称"]:
                # 字符串type
                para_values = str(self.pick_value_text.GetValue())

                if self.pick_cond_cmbo.GetStringSelection() == u"等于":
                    self.filter_result = pd.DataFrame()
                    for value in para_values.split("|"):  # 支持用"｜"符号查询多个
                        self.filter_result = pd.concat([self.filter_result, self.df_use[self.df_use[val] == value]])
                else:
                    MessageDialog("【%s】选项只支持【等于】条件判断！！！" % (val))
                    return

            if self.pick_cond_cmbo.GetStringSelection() == u"大于":
                self.filter_result = self.df_use[self.df_use[val] > float(para_value)]
            elif self.pick_cond_cmbo.GetStringSelection() == u"小于":
                self.filter_result = self.df_use[self.df_use[val] < float(para_value)]
            elif self.pick_cond_cmbo.GetStringSelection() == u"等于":
                self.filter_result = self.df_use[self.df_use[val] == para_value]
            else:
                pass

            if self.sort_values_cmbo.GetStringSelection() == u"降序":
                self.filter_result.sort_values(by=val, axis='index', ascending=False, inplace=True,
                                               na_position='last')
            elif self.sort_values_cmbo.GetStringSelection() == u"升序":
                self.filter_result.sort_values(by=val, axis='index', ascending=True, inplace=True,
                                               na_position='last')
            else:
                pass

            if self.filter_result.empty != True:

                ser_col = self.filter_result[val]  # 先单独保存
                self.filter_result.drop(val, axis=1, inplace=True)  # 而后从原数据中删除
                self.filter_result.insert(0, val, ser_col)  # 插入至首个位置

                self.df_use = self.filter_result
                self.refresh_grid(self.filter_result, val)
            else:
                MessageDialog("未找到符合条件的数据！！！")

    def _download_st_data(self):  # 复位选股按钮事件

        if self.mark_self_chk.GetValue() == True:  # 复选框被选中
            MessageDialog("先取消复选框！！！")
            return

        sdate_obj = self.dpc_cur_time.GetValue()
        sdate_val = datetime.datetime(sdate_obj.year, sdate_obj.month + 1, sdate_obj.day)

        if self.src_dat_cmbo.GetStringSelection() == "tushare每日指标":

            # 组合加入tushare数据
            self.ts_data = Tspro_Backend()
            self.df_join = self.ts_data.datafame_join(sdate_val.strftime('%Y%m%d'))  # 刷新self.df_join

        elif self.src_dat_cmbo.GetStringSelection() == "爬虫接口获取":

            select_msg = ChoiceDialog(u"爬虫数据类型选择", list(self.crawer_backend.keys()))

            self.ts_data = self.crawer_backend[select_msg](self.syslog)
            self.df_join = self.ts_data.datafame_join(sdate_val.strftime('%Y%m%d'))  # 刷新self.df_join

        elif self.src_dat_cmbo.GetStringSelection() == "基金季度持仓":

            self.df_join = readFundDatFromSql(self.syslog)
            print(self.df_join)

        else:  # 离线csv文件
            # 第一步:收集导入文件路径
            get_path = ImportFileDiag()

            if get_path != '':
                # 组合加入tushare数据
                self.ts_data = CsvBackend(self.src_dat_cmbo.GetStringSelection())
                self.df_join = self.ts_data.load_pick_data(get_path)

        if self.df_join.empty == True:
            MessageDialog("选股数据为空！请检查数据源是否有效！\n")
        else:
            # 数据获取正常后执行

            self.filter = self.df_join.columns.tolist()
            self.tran_col = dict(zip(self.df_join.columns.tolist(), self.filter))

            self.pick_item_cmbo.Clear()
            self.pick_item_cmbo.Append(self.filter)
            self.pick_item_cmbo.SetValue(self.filter[0])

            if self.src_dat_cmbo.GetStringSelection() == "爬虫每日指标":

                dlg_mesg = wx.SingleChoiceDialog(None, "刷新股票池 或者 刷新数据源？",
                                                 u"刷新类别选择", ['A股数据源', '自选股票池'])
                dlg_mesg.SetSelection(0)  # default selection

                if dlg_mesg.ShowModal() == wx.ID_OK:
                    message = dlg_mesg.GetStringSelection()
                    dlg_mesg.Destroy()

                    if message == '自选股票池':
                        df_pool = pd.DataFrame()
                        for sub_dict in self.code_pool.load_pool_stock().values():
                            num, sym = sub_dict.upper().split(".")
                            code = sym + "." + num
                            df_pool = df_pool.append(self.df_join[self.df_join["股票代码"] == code],
                                                     ignore_index=True)
                        self.df_join = df_pool

            self.df_use = self.df_join
            self.refresh_grid(self.df_use, self.df_use.columns.tolist()[0])

            if self.src_dat_cmbo.GetStringSelection() == "爬虫每日指标":

                if MessageDialog('是否查看Web版【板块-个股-涨跌幅】集合') == "点击Yes":
                    # try:
                    bk_to_pct = self.df_join.groupby(u'所属行业')[u'涨跌幅'].mean()
                    st_to_pct = self.df_join.groupby([u'所属行业', u'股票名称'])[u'涨跌幅'].mean()

                    bk_treemap = []

                    for bk_name, bk_pct in bk_to_pct.items():
                        child_treemap = []

                        for st_name, st_pct in st_to_pct[bk_name].items():
                            child_treemap.append({"value": round(st_pct, 2), "name": st_name})

                        bk_treemap.append({"value": round(bk_pct, 2), "name": bk_name, "children": child_treemap})

                    Pyechart_Drive.TreeMap_Handle(bk_treemap, "所属行业-个股-涨幅%", "行业板块")

                    web_disp = WebDialog(self, "", "treemap_base.html")
                    if web_disp.ShowModal() == wx.ID_OK:
                        pass
                    # except:
                    #    MessageDialog("html文件加载出错，可前往文件夹点击查看！")

    def _save_st_result(self):

        # 保存选股按钮事件
        if self.src_dat_cmbo.GetStringSelection() == "tushare每日指标" or \
                self.src_dat_cmbo.GetStringSelection() == "离线每日指标" or \
                self.src_dat_cmbo.GetStringSelection() == "爬虫每日指标":
            # 原股票格式 tushare
            st_name_code_dict = dict(zip(self.df_use["股票名称"].values, self.df_use["股票代码"].values))

            for k, v in st_name_code_dict.items():
                code_split = v.lower().split(".")
                st_name_code_dict[k] = code_split[1] + "." + code_split[0]  # tushare转baostock

        elif self.src_dat_cmbo.GetStringSelection() == "离线业绩预告" or \
                self.src_dat_cmbo.GetStringSelection() == "离线基金持仓" or \
                self.src_dat_cmbo.GetStringSelection() == "离线财务报告":
            # 原股票格式 baostock
            st_name_code_dict = dict(zip(self.df_use["股票名称"].values, self.df_use["股票代码"].values))
        else:
            # 原股票格式 行情软件
            st_name_code_dict = dict(zip(self.df_use["股票名称"].values, self.df_use["股票代码"].values))

            for k, v in st_name_code_dict.items():
                st_name_code_dict[k] = "sh." + v if v[0] == '6' else "sz." + v  # 行情转baostock

        choice_msg = ChoiceDialog("保存条件筛选后的股票", [u"完全替换", u"增量更新"])

        if choice_msg == u"完全替换":
            self.code_pool.update_replace_st(st_name_code_dict)
        elif choice_msg == u"增量更新":
            self.code_pool.update_increase_st(st_name_code_dict)
        else:
            pass
        self.grid_stock_pool.SetTable(self.code_pool.load_my_pool(), ["自选股", "代码"])
        # self.df_use.to_csv('table-stock.csv', columns=self.df_use.columns, index=True, encoding='GB18030')

    def _ev_mark_self(self, event):
        # 标记自选股事件

        if self.df_use.empty == True:
            MessageDialog("无选股数据！")
        else:
            self.df_use.reset_index(drop=True, inplace=True)  # 重排索引

            if self.mark_self_box_chk.GetValue() == True:  # 复选框被选中

                for code in list(self.code_pool.load_pool_stock().values()):  # 加载自选股票池
                    symbol, number = code.upper().split('.')
                    new_code = number + "." + symbol
                    n_list = self.df_use[self.df_use["股票代码"] == new_code].index.tolist()
                    if n_list != []:
                        self.grid_pick.SetCellBackgroundColour(n_list[0], 0, wx.YELLOW)
                        self.grid_pick.SetCellBackgroundColour(n_list[0], 1, wx.YELLOW)
            else:
                for code in list(self.code_pool.load_pool_stock().values()):  # 加载自选股票池
                    symbol, number = code.upper().split('.')
                    new_code = number + "." + symbol
                    n_list = self.df_use[self.df_use["股票代码"] == new_code].index.tolist()
                    if n_list != []:
                        self.grid_pick.SetCellBackgroundColour(n_list[0], 0, wx.WHITE)
                        self.grid_pick.SetCellBackgroundColour(n_list[0], 1, wx.WHITE)
            self.grid_pick.Refresh()

    def _ev_trade_log(self, event):

        user_trade_log = UserDialog(self, title=u"回测提示信息", label=u"交易详细日志")

        """ 自定义提示框 """
        if user_trade_log.ShowModal() == wx.ID_OK:
            pass
        else:
            pass

    def _ev_click_on_treelist(self, event):

        self.curTreeItem = self.treeListCtrl.GetItemText(event.GetItem())

        if self.curTreeItem != None:
            # 当前选中的TreeItemId对象操作

            MessageDialog('当前点击:{0}!'.format(self.curTreeItem))
            for m_key, m_val in self.treeListCtrl.colleges.items():
                for s_key in m_val:
                    if s_key.get('名称', '') == self.curTreeItem:
                        if s_key.get('函数', '') != "未定义":
                            if (m_key == u"衍生指标") or (m_key == u"K线形态"):
                                # 第一步:收集控件中设置的选项
                                st_label = s_key['标识']
                                st_code = self.stock_code_input.GetValue()
                                st_name = self.code_table.get_name(st_code)
                                st_period = self.stock_period_cbox.GetStringSelection()
                                st_auth = self.stock_authority_cbox.GetStringSelection()
                                sdate_obj = self.dpc_start_time.GetValue()
                                edate_obj = self.dpc_end_time.GetValue()

                                # 第二步:获取股票数据-使用self.stock_dat存储数据
                                if self.stock_dat.empty == True:
                                    MessageDialog("获取股票数据出错！\n")
                                else:
                                    # 第三步:绘制可视化图形
                                    if self.pick_graph_cbox.GetSelection() != 0:
                                        self.tempStockPanel.clear_subgraph()  # 必须清理图形才能显示下一幅图
                                        self.tempStockPanel.draw_subgraph(self.stock_dat, st_code, st_period + st_auth)
                                    else:
                                        # 配置图表属性
                                        firm_para = self.call_method(self.event_task['cfg_firm_para'],
                                                                     st_code=st_code,
                                                                     st_name=st_name,
                                                                     st_period=st_period,
                                                                     st_auth=st_auth,
                                                                     st_label=st_label)

                                        self.tempStockPanel.firm_graph_run(self.stock_dat, **firm_para)

                                    self.tempStockPanel.update_subgraph()  # 必须刷新才能显示下一幅图
                            else:
                                self.function = getattr(Base_Strategy_Group, s_key.get('define', ''))
                        else:
                            MessageDialog("该接口未定义！")
                        break

    def _ev_start_run(self, event):  # 点击运行回测

        # 第一步:收集控件中设置的选项
        st_code = self.stock_code_input.GetValue()
        cash_value = self.init_cash_input.GetValue()
        stake_value = self.init_stake_input.GetValue()
        slippage_value = self.init_slippage_input.GetValue()
        commission_value = self.init_commission_input.GetValue()
        tax_value = self.init_tax_input.GetValue()

        # 第二步:获取股票数据-依赖行情界面获取的数据
        if self.stock_dat.empty == True:
            MessageDialog("先在行情界面获取回测数据！\n")

        # 第三步:绘制可视化图形
        # 配置图表属性
        back_para = self.call_method(self.event_task['cfg_back_para'],
                                     st_code=st_code,
                                     cash_value=cash_value,
                                     stake_value=stake_value,
                                     slippage_value=slippage_value,
                                     commission_value=commission_value,
                                     tax_value=tax_value)

        if self.function == '':
            MessageDialog("未选择回测策略！")
        else:
            self.BackMplPanel.back_graph_run(self.function(self.stock_dat), **back_para)
            # 修改图形的任何属性后都必须更新GUI界面
            self.BackMplPanel.update_subgraph()

    def requset_stock_dat(self, st_code, st_name, st_period, st_auth, sdate_obj, edate_obj):

        # 第二步:获取股票数据-调用sub event handle
        stock_dat = self.call_method(self.event_task['get_stock_dat'],
                                     st_code=st_code,
                                     st_period=st_period,
                                     st_auth=st_auth,
                                     sdate_obj=sdate_obj,
                                     edate_obj=edate_obj)
        return stock_dat

    def handle_active_code(self, st_code, st_name):  # 点击股票代码后处理模块

        select_msg = ChoiceDialog(u"自选股点击处理事件", [u"从股票池中剔除",
                                                 u"加入组合分析池",
                                                 u"查看行情走势",
                                                 u"查看F10资料",
                                                 u"K线自动播放",
                                                 u"导入离线数据"
                                                 ])

        if select_msg == u"查看行情走势":

            # 第一步:收集控件中设置的选项
            st_period = self.stock_period_cbox.GetStringSelection()
            st_auth = self.stock_authority_cbox.GetStringSelection()
            sdate_obj = self.dpc_start_time.GetValue()
            edate_obj = self.dpc_end_time.GetValue()

            self.stock_dat = self.requset_stock_dat(st_code, st_name, st_period, st_auth,
                                                    sdate_obj, edate_obj)

            if self.stock_dat.empty == True:
                MessageDialog("获取股票数据出错！\n")
            else:

                if len(self.stock_dat) >= 356:
                    MessageDialog("获取股票数据量较大！默认显示最近的365个BAR数据！\n")
                    self.stock_dat = self.stock_dat[-356:]

                # 第三步:绘制可视化图形
                if self.pick_graph_cbox.GetSelection() != 0:
                    self.tempStockPanel.clear_subgraph()  # 必须清理图形才能显示下一幅图
                    self.tempStockPanel.draw_subgraph(self.stock_dat, st_code, st_period + st_auth)

                else:
                    # 配置图表属性
                    firm_para = self.call_method(self.event_task['cfg_firm_para'],
                                                 st_code=st_code,
                                                 st_name=st_name,
                                                 st_period=st_period,
                                                 st_auth=st_auth)

                    self.tempStockPanel.firm_graph_run(self.stock_dat, **firm_para)

                self.tempStockPanel.update_subgraph()  # 必须刷新才能显示下一幅图

        elif select_msg == u"加入组合分析池":
            self._add_analyse_list(st_code + "|" + st_name)

        elif select_msg == u"从股票池中剔除":
            self.code_pool.delete_one_st(st_name)
            self.grid_stock_pool.SetTable(self.code_pool.load_my_pool(), ["自选股", "代码"])

        elif select_msg == u"查看F10资料":
            dialog = BrowserF10(self, u"个股F10资料", st_code)
            dialog.Show()

        elif select_msg == u"K线自动播放":

            # 第一步:收集控件中设置的选项
            st_period = self.stock_period_cbox.GetStringSelection()
            st_auth = self.stock_authority_cbox.GetStringSelection()
            sdate_obj = self.dpc_start_time.GetValue()
            edate_obj = self.dpc_end_time.GetValue()

            self.stock_dat = self.requset_stock_dat(st_code, st_name, st_period, st_auth,
                                                    sdate_obj, edate_obj)

            dialog = AnimationDialog(self, u"K线自动播放", self.stock_dat)
            dialog.Show()

        elif select_msg == u"导入离线数据":

            if MessageDialog("请手动填写[股票名称][股票周期][股票复权]！\n该内容与图表标签相关！\n点击Yes继续；点击No去配置") == "点击No":
                return

            # 第一步:收集导入文件路径/名称/周期/起始时间
            get_path = ImportFileDiag()
            st_code = self.stock_code_input.GetValue()
            st_name = self.code_table.get_name(st_code)
            st_period = self.stock_period_cbox.GetValue()
            st_auth = self.stock_authority_cbox.GetValue()
            sdate_obj = self.dpc_start_time.GetValue()
            edate_obj = self.dpc_end_time.GetValue()

            # 第二步:加载csv文件中的数据
            if get_path != '':
                self.stock_dat = self.call_method(self.event_task['get_csvst_dat'],
                                                  get_path=get_path,
                                                  sdate_obj=sdate_obj, edate_obj=edate_obj,
                                                  st_auth=st_auth, st_period=st_period)

                if self.stock_dat.empty == True:
                    MessageDialog("文件内容为空！\n")
                else:

                    # 第三步:绘制可视化图形
                    if self.pick_graph_cbox.GetSelection() != 0:
                        self.tempStockPanel.clear_subgraph()  # 必须清理图形才能显示下一幅图
                        self.tempStockPanel.draw_subgraph(self.stock_dat, "csv导入" + st_code, st_name)
                    else:
                        # 配置图表属性
                        firm_para = self.call_method(self.event_task['cfg_firm_para'],
                                                     st_code="csv导入" + st_code,
                                                     st_name=st_name,
                                                     st_period=st_period,
                                                     st_auth="不复权")
                        self.tempStockPanel.firm_graph_run(self.stock_dat, **firm_para)
                    self.tempStockPanel.update_subgraph()  # 必须刷新才能显示下一幅图
        else:
            pass

    def _ev_enter_stcode(self, event):  # 输入股票代码

        # 第一步:收集控件中设置的选项
        st_code = self.stock_code_input.GetValue()
        st_name = self.code_table.get_name(st_code)

        self.handle_active_code(st_code, st_name)

    def _ev_click_plcode(self, event):  # 点击股票池股票代码

        # 收集股票池中名称和代码
        st_code = self.grid_stock_pool.GetCellValue(event.GetRow(), 1)
        st_name = self.grid_stock_pool.GetCellValue(event.GetRow(), 0)

        self.handle_active_code(st_code, st_name)

    def _ev_label_lclick_pkcode(self, event):

        # 收集表格中的列名
        col_label = self.grid_pick.GetColLabelValue(event.GetCol())

        if col_label == "所属行业" and self.src_dat_cmbo.GetStringSelection() == "离线财务报告":

            if MessageDialog("是否对比个股业绩报告？建议同行业板块对比！") == "点击Yes":

                if self.df_use.empty != True:

                    self.df_use.dropna(how='all', axis=1, inplace=True)
                    self.df_use.fillna(0, inplace=True)
                    self.df_use = self.df_use.assign(总分=0)

                    for col, series in self.df_use.iteritems():

                        if series.dtype == float and col != "总分":
                            self.df_use[col] = (series - series.mean()) / series.var()
                            self.df_use.loc[:, "总分"] += self.df_use[col]

                    self.df_use.sort_values(by=["总分"], axis='index', ascending=False, inplace=True,
                                            na_position='last')  # 降序

                    text = "对比后排名前五名单如下:\n"
                    updat_dict = {}
                    for name, code in zip(self.df_use["股票名称"][0:5], self.df_use["股票代码"][0:5]):
                        code = code[1:-1]
                        text += name + "|" + code + "\n"
                        updat_dict.update({name: self.code_table.conv_code(code)})

                    if MessageDialog(text + "\n添加股票到自选股票池？") == "点击Yes":
                        # 自选股票池 更新股票
                        self.code_pool.update_increase_st(updat_dict)
                        self.grid_stock_pool.SetTable(self.code_pool.load_my_pool(), ["自选股", "代码"])

    def _ev_cell_lclick_pkcode(self, event):  # 点击选股表中股票代码

        # 收集表格中的列名
        col_label = self.grid_pick.GetColLabelValue(event.GetCol())

        if col_label == "股票代码":
            # 收集表格中的单元格

            try:
                st_code = self.grid_pick.GetCellValue(event.GetRow(), event.GetCol())
                st_name = self.code_table.get_name(st_code)

                text = self.call_method(self.event_task['get_cash_flow'], st_code=self.code_table.conv_code(st_code))

                if MessageDialog(
                        text + "\n添加股票[%s]到自选股票池？" % (self.code_table.conv_code(st_code) + "|" + st_name)) == "点击Yes":
                    # self._add_analyse_list(self.code_table.conv_code(st_code) + "|" + st_name)
                    # 自选股票池 更新股票
                    self.code_pool.update_increase_st({st_name: self.code_table.conv_code(st_code)})
                    self.grid_stock_pool.SetTable(self.code_pool.load_my_pool(), ["自选股", "代码"])
            except:
                MessageDialog("股票代码不在存储表中！检查是否为新股/退市等情况！")

        elif col_label == "股票名称":
            # 收集表格中的单元格
            try:
                st_name = self.grid_pick.GetCellValue(event.GetRow(), event.GetCol())
                st_code = self.code_table.get_code(st_name)

                text = self.call_method(self.event_task['get_cash_flow'], st_code=self.code_table.conv_code(st_code))

                if MessageDialog(
                        text + "\n添加股票[%s]到自选股票池？" % (self.code_table.conv_code(st_code) + "|" + st_name)) == "点击Yes":
                    # self._add_analyse_list(self.code_table.conv_code(st_code) + "|" + st_name)
                    # 自选股票池 更新股票
                    self.code_pool.update_increase_st({st_name: self.code_table.conv_code(st_code)})
                    self.grid_stock_pool.SetTable(self.code_pool.load_my_pool(), ["自选股", "代码"])
            except:
                MessageDialog("股票名称不在存储表中！检查是否为新股/退市等情况！")

        else:
            MessageDialog("请点击股票代码或股票名称！")

    def _ev_src_choose(self, event):
        # 预留
        pass

    def _ev_list_select(self, event):  # 双击从列表中剔除股票

        # 等价与GetSelection() and indexSelected
        if MessageDialog("是否从组合分析股票池中删除该股票？") == "点击Yes":
            indexSelected = event.GetEventObject().GetSelections()
            event.GetEventObject().Delete(indexSelected[0])

    def _ev_group_analy(self, event):

        item = event.GetSelection()
        stock_set = self.listBox.GetStrings()

        # 第一步:收集控件中设置的选项
        st_period = self.stock_period_cbox.GetStringSelection()
        st_auth = self.stock_authority_cbox.GetStringSelection()
        sdate_obj = self.dpc_start_time.GetValue()
        edate_obj = self.dpc_end_time.GetValue()

        if item == 1:  # 显示收益率/波动率分布
            pct_chg = pd.DataFrame()

            for stock in stock_set:
                # 第二步:获取股票数据-调用sub event handle
                try:
                    pct_chg[stock] = self.call_method(self.event_task['get_stock_dat'],
                                                      st_code=stock.split("|")[0],
                                                      st_period=st_period,
                                                      st_auth=st_auth,
                                                      sdate_obj=sdate_obj,
                                                      edate_obj=edate_obj)['Pctchg']
                except:
                    MessageDialog("[%s]涨幅数据获取失败！" % stock)

            # 计算股票收益率的均值和标准差
            rets = pct_chg.dropna()
            ret_mean = rets.mean()
            ret_std = rets.std()

            # 第三步:绘制可视化图形
            analy_group_pct = GroupPctDiag(self, u"多股收益率/波动率对比分析", stock_set, ret_mean, ret_std)
            """ 自定义提示框 """
            if analy_group_pct.ShowModal() == wx.ID_OK:
                pass
            else:
                pass

        elif item == 2:  # 显示走势叠加分析
            pct_chg = pd.DataFrame()
            for stock in stock_set:
                # 第二步:获取股票数据-调用sub event handle
                try:
                    pct_chg[stock] = (self.call_method(self.event_task['get_stock_dat'],
                                                       st_code=stock.split("|")[0],
                                                       st_period=st_period,
                                                       st_auth=st_auth,
                                                       sdate_obj=sdate_obj,
                                                       edate_obj=edate_obj)['Pctchg'] / 100 + 1).cumprod()
                except:
                    MessageDialog("[%s]涨幅数据获取失败！" % stock)
            # 第三步:绘制可视化图形
            analy_group_pct = GroupTrendDiag(self, u"多股行情走势叠加对比分析", stock_set, pct_chg)
            """ 自定义提示框 """
            if analy_group_pct.ShowModal() == wx.ID_OK:
                pass
            else:
                pass

        elif item == 3:  # 显示财务指标评分
            pass

    def _ev_patten_select(self, event):

        # 第一步: 收集控件中设置的选项
        st_period = self.patten_period_cbox.GetStringSelection()
        st_auth = self.patten_authority_cbox.GetStringSelection()
        sdate_obj = self.patten_start_time.GetValue()
        edate_obj = self.patten_end_time.GetValue()
        patten_pool = self.patten_pool_cmbo.GetStringSelection()

        if patten_pool == "自选股票池":
            MessageDialog("温馨提示：自选股票池符合形态股票会自动存入组合分析股票池")
            dict_basic = self.code_pool.load_pool_stock()
        else:
            MessageDialog("温馨提示：全市场股票符合形态股票自动存入本地csv文件")
            dict_basic = self.code_table.stock_codes

        self.patlog.clr_print()
        self.patlog.re_print(f"启动{patten_pool} 形态分析......\n")

        proc_dialog = ProgressDialog("开始分析", len(dict_basic.keys()))

        if self.patten_type_cmbo.GetStringSelection() == "双底形态":

            patten_recognize = DouBottomDialog(self, "双底形态识别参数配置")

            if patten_recognize.ShowModal() == wx.ID_OK:

                count = 0
                df_search = pd.DataFrame()
                for name, code in dict_basic.items():

                    count += 1
                    # 第二步: 获取股票数据-调用sub event handle
                    stock_dat = self.call_method(self.event_task['get_stock_dat'],
                                                 st_code=code,
                                                 st_period=st_period,
                                                 st_auth=st_auth,
                                                 sdate_obj=sdate_obj,
                                                 edate_obj=edate_obj)

                    df_return = Base_Patten_Group.double_bottom_search(name, code, stock_dat, self.patlog,
                                                                       **patten_recognize.feedback_paras())
                    if (df_return.empty != True):
                        df_search = pd.concat([df_search, df_return], ignore_index=True)

                        if patten_pool == "自选股票池":
                            # 有效则添加至 组合分析股票池
                            self._add_analyse_list(code + "|" + name)

                    proc_dialog.update_bar(count)

        self.patlog.re_print("\n形态分析完成！符合条件股票自动存储至组合股票池！")
        self.patlog.re_print("\n形态分析明细查看ConfigFiles路径的双底形态分析结果.csv")
        proc_dialog.close_bar()

        FileUtil.save_patten_analysis(df_search, f"{datetime.datetime.now().strftime('%y-%m-%d')}-双底形态分析结果")

        sys_para = FileUtil.load_sys_para("sys_para.json")
        auto_send_email('主人！你的双底形态分析报告来啦', "\n形态分析明细查看ConfigFiles路径的双底形态分析结果.csv",
                        f"{datetime.datetime.now().strftime('%y-%m-%d')}-双底形态分析结果.csv",
                        self.patlog, **sys_para["mailbox"])

        # print(self.patlog.get_values()) # 返回控件中所有的内容

    def _ev_int_timer(self, event):
        pass

    def _ev_patten_save(self, event):
        pass

    def _ev_switch_menu(self, event):
        self.fun_swframe(0)  # 切换 Frame 主界面

    def _add_analyse_list(self, item):

        if item in self.listBox.GetStrings():
            MessageDialog("股票%s已经存在！\n" % item)
        else:
            self.listBox.InsertItems([item], 0)  # 插入item

    def _ev_err_guide_menu(self, event):
        webbrowser.open('https://blog.csdn.net/hangzhouyx/article/details/113774922?spm=1001.2014.3001.3501')

    def _ev_funt_guide_menu(self, event):
        webbrowser.open('https://blog.csdn.net/hangzhouyx/article/details/116496181?spm=1001.2014.3001.3501')

    def _ev_code_inc_menu(self, event):
        # 增量更新
        # 收集导入文件路径
        get_path = ImportFileDiag()

        # 加载csv文件中的数据
        if get_path != '':
            add_code = self.call_method(self.event_task['get_csvst_pool'], get_path=get_path)
            print(add_code)
            if add_code:
                self.code_pool.update_increase_st(add_code)
                self.grid_stock_pool.SetTable(self.code_pool.load_my_pool(), ["自选股", "代码"])
            else:
                MessageDialog("文件内容为空！\n")

    def _ev_code_rep_menu(self, event):
        # 完全替换
        # 收集导入文件路径
        get_path = ImportFileDiag()

        # 加载csv文件中的数据
        if get_path != '':
            add_code = self.call_method(self.event_task['get_csvst_pool'], get_path=get_path)
            if add_code:
                self.code_pool.update_replace_st(add_code)
                self.grid_stock_pool.SetTable(self.code_pool.load_my_pool(), ["自选股", "代码"])
            else:
                MessageDialog("文件内容为空！\n")

    def OnEventTrig(self, event):
        if event.GetId() == 1100:  # 量化按钮
            # MainApp.switchFrame(1)
            print("功能预留-后期实现！")
        elif event.GetId() == 1101:  # 数据按钮
            # MainApp.manager.switchFrame(2)
            print("功能预留-后期实现！")
        elif event.GetId() == 1102:  # 选股按钮
            # self.switchFrame(3)
            print("功能预留-后期实现！")
        elif event.GetId() == 1103:  # 配置按钮
            # MainApp.switchFrame(4)
            print("功能预留-后期实现！")
        else:
            pass

    def checkEnv(self):
        # 此处涉及windows和macos的区别
        sys_para = FileUtil.load_sys_para("sys_para.json")
        if sys_para["operate_sys"] == "windows":
            try:
                # WIN环境下兼容WEB配置
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     r"SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_BROWSER_EMULATION",
                                     0, winreg.KEY_ALL_ACCESS)  # 打开所有权限
                # 设置注册表python.exe 值为 11000(IE11)
                winreg.SetValueEx(key, 'python.exe', 0, winreg.REG_DWORD, 0x00002af8)
            except:
                # 设置出现错误
                MessageDialog("WIN环境配置注册表中浏览器兼容显示出错,检查是否安装第三方库【winreg】")

    def setFrameSize(self, displaySize):
        self.contentWidth = displaySize[0]
        self.contentHeight = displaySize[1]

        # M1 与 M2 横向布局时宽度分割
        self.leftWidth = int(self.contentWidth * 0.2)
        self.rightWidth = int(self.contentWidth * 0.8)
        # M1 纵向100%
        self.leftHeight = self.contentHeight

        # M1中S1 S2 S3 纵向布局高度分割
        self.M1S1_length = int(self.leftHeight * 0.2)
        self.M1S2_length = int(self.leftHeight * 0.2)
        self.M1S3_length = int(self.leftHeight * 0.6)
