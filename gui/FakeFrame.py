import os

import wx
import wx.lib.agw.aui as aui

from gui.MainPanel import MainPanel
from gui.panels.DataPanel import DataPanel


class MainFrame(wx.Frame):
    """从wx.Frame派生主窗口类"""

    rel_path = os.path.dirname(os.path.dirname(__file__)) + '/config/'

    id_open = wx.NewIdRef()
    id_save = wx.NewIdRef()
    id_quit = wx.NewIdRef()

    id_help = wx.NewIdRef()
    id_about = wx.NewIdRef()

    def __init__(self, parent):
        """构造函数"""

        wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE)

        self.SetTitle('菜单、工具栏、状态栏')
        # self.SetIcon(wx.Icon('res/wx.ico'))
        self.SetBackgroundColour((224, 224, 224))  # 设置窗口背景色
        self.SetSize((640, 480))

        self._init_ui()
        self.Center()

    def _init_ui(self):
        """初始化界面"""

        self.tb1 = self._create_toolbar()
        self.tb2 = self._create_toolbar()
        self.tbv = self._create_toolbar('V')

        p_left = wx.Panel(self, -1)
        p_center0 = DataPanel(self, -1, displaySize=(1600, 900))
        p_center0.SetSize((1600, 900))
        p_center1 = MainPanel(self, -1)
        p_bottom = wx.Panel(self, -1)

        btn = wx.Button(p_left, -1, '切换', pos=(30, 200), size=(100, -1))
        btn.Bind(wx.EVT_BUTTON, self.on_switch)

        # text0 = wx.StaticText(p_center0, -1, '我是第1页', pos=(40, 100), size=(200, -1), style=wx.ALIGN_LEFT)
        text1 = wx.StaticText(p_center1, -1, '我是第2页', pos=(40, 100), size=(200, -1), style=wx.ALIGN_LEFT)

        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)

        self._mgr.AddPane(self.tb1,
                          aui.AuiPaneInfo().Name('ToolBar1').Caption('工具条').ToolbarPane().Top().Row(0).Position(
                              0).Floatable(False)
                          )
        self._mgr.AddPane(self.tb2,
                          aui.AuiPaneInfo().Name('ToolBar2').Caption('工具条').ToolbarPane().Top().Row(0).Position(
                              1).Floatable(True)
                          )
        self._mgr.AddPane(self.tbv,
                          aui.AuiPaneInfo().Name('ToolBarV').Caption('工具条').ToolbarPane().Right().Floatable(True)
                          )

        self._mgr.AddPane(p_left,
                          aui.AuiPaneInfo().Name('LeftPanel').Left().Layer(1).MinSize((200, -1)).Caption(
                              '操作区').MinimizeButton(True).MaximizeButton(True).CloseButton(True)
                          )

        self._mgr.AddPane(p_center0, aui.AuiPaneInfo().CenterPane().Name("RightPanel").Resizable(True).Show())

        self._mgr.AddPane(p_center1,
                          aui.AuiPaneInfo().Name('CenterPanel1').CenterPane().Hide()
                          )

        self._mgr.AddPane(p_bottom,
                          aui.AuiPaneInfo().Name('BottomPanel').Bottom().MinSize((-1, 100)).Caption(
                              '消息区').CaptionVisible(False).Resizable(True)
                          )

        self._mgr.Update()

    def _create_toolbar(self, d='H'):
        """创建工具栏"""

        # bmp_open = wx.Bitmap('res/open_mso.png', wx.BITMAP_TYPE_ANY)
        # bmp_save = wx.Bitmap('res/save_mso.png', wx.BITMAP_TYPE_ANY)
        # bmp_help = wx.Bitmap('res/help_mso.png', wx.BITMAP_TYPE_ANY)
        # bmp_about = wx.Bitmap('res/info_mso.png', wx.BITMAP_TYPE_ANY)
        
        img_quant = wx.Image(self.rel_path + "png/test.png", "image/png").Scale(35, 35)
        img_price = wx.Image(self.rel_path + "png/price.png", "image/png").Scale(35, 35)
        img_trade = wx.Image(self.rel_path + "png/trade.png", "image/png").Scale(35, 35)
        img_config = wx.Image(self.rel_path + "png/config.png", "image/png").Scale(35, 35)



        if d.upper() in ['V', 'VERTICAL']:
            tb = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                                agwStyle=aui.AUI_TB_TEXT | aui.AUI_TB_VERTICAL)
        else:
            tb = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, agwStyle=aui.AUI_TB_TEXT)
        tb.SetToolBitmapSize(wx.Size(16, 16))

        tb.AddSimpleTool(self.id_open, '打开', wx.Bitmap(img_quant, wx.BITMAP_SCREEN_DEPTH), '打开文件')
        tb.AddSimpleTool(self.id_save, '保存', wx.Bitmap(img_price, wx.BITMAP_SCREEN_DEPTH), '保存文件')
        tb.AddSeparator()
        tb.AddSimpleTool(self.id_help, '帮助', wx.Bitmap(img_trade, wx.BITMAP_SCREEN_DEPTH), '帮助')
        tb.AddSimpleTool(self.id_about, '关于', wx.Bitmap(img_config, wx.BITMAP_SCREEN_DEPTH), '关于')

        tb.Realize()
        return tb

    def on_switch(self, evt):
        """切换信息显示窗口"""

        p0 = self._mgr.GetPane('CenterPanel0')
        p1 = self._mgr.GetPane('CenterPanel1')

        p0.Show(not p0.IsShown())
        p1.Show(not p1.IsShown())

        self._mgr.Update()


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()