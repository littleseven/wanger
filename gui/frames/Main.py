import os
import time
import webbrowser

import wx
import wx.lib.agw.aui as aui
from wx.lib import inspection

from common.FileUtil import FileUtil
from gui import constants
from gui.panels.ConfigPanel import ConfigPanel
from gui.panels.DataPanel import DataPanel
from gui.panels.LabPanel import LabPanel

USE_WIT = True

AppBaseClass = wx.App
if USE_WIT:
    from wx.lib.mixins.inspection import InspectableApp
    AppBaseClass = InspectableApp



class MainFrame(wx.Frame):
    """从wx.Frame派生主窗口类"""

    rel_path = constants.CONFIG_PATH

    id_open = wx.NewIdRef()
    id_save = wx.NewIdRef()
    id_quit = wx.NewIdRef()

    id_help = wx.NewIdRef()
    id_about = wx.NewIdRef()

    def __init__(self, parent):
        """构造函数"""

        wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE)

        self.SetTitle('王二的量化交易系统')
        # self.SetIcon(wx.Icon('res/wx.ico'))
        self.SetBackgroundColour((224, 224, 224))  # 设置窗口背景色
        displaySize = wx.DisplaySize()  # (1920, 1080)
        MIN_DISPLAYSIZE = 1024, 800
        if (displaySize[0] < MIN_DISPLAYSIZE[0]) or (displaySize[1] < MIN_DISPLAYSIZE[1]):
            self.displaySize = MIN_DISPLAYSIZE[0], MIN_DISPLAYSIZE[1]
        else:
            self.displaySize = 1280, 800

        self.calcFrameSize(self.displaySize)
        self._init_ui()
        self.Center()

    def _init_ui(self):
        """初始化界面"""
        self._init_status_bar()
        self._init_menu_bar()
        self.tbv = self._create_toolbar('V')
        self.tbv.Bind(wx.EVT_TOOL, self.on_switch)

        # p_left = wx.Panel(self, -1)
        dataPanel = DataPanel(self, -1, self.displaySize)
        labPanel = LabPanel(self, -1, self.displaySize)
        configPanel = ConfigPanel(self, -1, self.displaySize)
        # p_bottom = wx.Panel(self, -1)

        # btn = wx.Button(p_left, -1, '切换', pos=(30, 200), size=(100, -1))
        # btn.Bind(wx.EVT_BUTTON, self.on_switch)

        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)

        # self._mgr.AddPane(self.tb1,
        #                   aui.AuiPaneInfo().Name('ToolBar1').Caption('工具条').ToolbarPane().Top().Row(0).Position(
        #                       0).Floatable(False)
        #                   )
        self._mgr.AddPane(self.tbv,
                          aui.AuiPaneInfo().Name('ToolBarV').Caption('工具条').ToolbarPane().Left().Floatable(True)
                          )

        # self._mgr.AddPane(p_left,
        #                   aui.AuiPaneInfo().Name('LeftPanel').Left().Layer(1).MinSize((10, -1)).Caption(
        #                       '操作区').MinimizeButton(True).MaximizeButton(True).CloseButton(True).Show(False)
        #                   )

        self._mgr.AddPane(labPanel, aui.AuiPaneInfo().CenterPane().Name("LabPanel").
                          CenterPane().BestSize((self.rightWidth, self.leftHeight)).
                          MinSize((self.rightWidth, self.leftHeight)).
                          Floatable(True).FloatingSize((self.rightWidth, self.leftHeight)).
                          CloseButton(False)
                          .Resizable(True).Show())

        self._mgr.AddPane(dataPanel, aui.AuiPaneInfo().Name('DataPanel').CenterPane().
                          CenterPane().BestSize((self.rightWidth, self.leftHeight)).
                          MinSize((self.rightWidth, self.leftHeight)).
                          Floatable(True).FloatingSize((self.rightWidth, self.leftHeight)).
                          CloseButton(False)
                          .Resizable(True)
                          .Hide())

        self._mgr.AddPane(configPanel, aui.AuiPaneInfo().Name('ConfigPanel').CenterPane().
                          CenterPane().BestSize((self.rightWidth, self.leftHeight)).
                          MinSize((self.rightWidth, self.leftHeight)).
                          Floatable(True).FloatingSize((self.rightWidth, self.leftHeight)).
                          CloseButton(False)
                          .Resizable(True)
                          .Hide())

        # self._mgr.AddPane(p_bottom,
        #                   aui.AuiPaneInfo().Name('BottomPanel').Bottom().MinSize((-1, 10)).Caption(
        #                       '消息区').CaptionVisible(False).Resizable(True)
        #                   )
        self.SetSize(self.displaySize)
        self._mgr.Update()
        self._mgr.SetAGWFlags(self._mgr.GetAGWFlags() ^ aui.AUI_MGR_TRANSPARENT_DRAG)
        self.CenterOnScreen(wx.BOTH)

    def _create_toolbar(self, d='H'):
        """创建工具栏"""
        img_quant = wx.Image(self.rel_path + "png/test.png", "image/png").Scale(35, 35)
        img_price = wx.Image(self.rel_path + "png/price.png", "image/png").Scale(35, 35)
        img_trade = wx.Image(self.rel_path + "png/trade.png", "image/png").Scale(35, 35)
        img_config = wx.Image(self.rel_path + "png/config.png", "image/png").Scale(35, 35)

        if d.upper() in ['V', 'VERTICAL']:
            toolbar = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                                     agwStyle=aui.AUI_TB_TEXT | aui.AUI_TB_VERTICAL)
        else:
            toolbar = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, agwStyle=aui.AUI_TB_TEXT)
        toolbar.SetToolBitmapSize(wx.Size(16, 16))

        toolbar.AddSimpleTool(1100, '量化', wx.Bitmap(img_quant, wx.BITMAP_SCREEN_DEPTH), '量化')
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(1101, '行情', wx.Bitmap(img_price, wx.BITMAP_SCREEN_DEPTH), '行情')
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(1102, '交易', wx.Bitmap(img_trade, wx.BITMAP_SCREEN_DEPTH), '交易')
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(1103, '配置', wx.Bitmap(img_config, wx.BITMAP_SCREEN_DEPTH), '配置')

        toolbar.Realize()
        return toolbar

    def on_switch(self, event):
        labPanel = self._mgr.GetPane('LabPanel')
        dataPanel = self._mgr.GetPane('DataPanel')
        configPanel = self._mgr.GetPane('ConfigPanel')

        """切换信息显示窗口"""
        if event.GetId() == 1100:  # 量化按钮
            if not labPanel.IsShown():
                dataPanel.Hide()
                configPanel.Hide()
                labPanel.Show()
        elif event.GetId() == 1101:  # 数据按钮
            if not dataPanel.IsShown():
                labPanel.Hide()
                configPanel.Hide()
                dataPanel.Show()
        elif event.GetId() == 1102:  # 选股按钮
            print("功能预留-后期实现！")
        elif event.GetId() == 1103:  # 配置按钮
            if not configPanel.IsShown():
                labPanel.Hide()
                dataPanel.Hide()
                configPanel.Show()
        else:
            pass
        self._mgr.Update()

    @staticmethod
    def _ev_err_guide_menu():
        webbrowser.open('https://blog.csdn.net/hangzhouyx/article/details/113774922?spm=1001.2014.3001.3501')

    @staticmethod
    def _ev_funt_guide_menu():
        webbrowser.open('https://blog.csdn.net/hangzhouyx/article/details/116496181?spm=1001.2014.3001.3501')

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
        regMenuInfter = {"&量化工具": {"&基金持仓-预留": None, '&实时数据-预留': None, '&板块数据-预留': None, '&事件型回测-预留': None},
                         "&使用帮助": {"&报错排查": self._ev_err_guide_menu}}
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

    def calcFrameSize(self, displaySize):
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


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None)
    inspection.InspectionTool().Show()
    frame.Show()
    app.MainLoop()
