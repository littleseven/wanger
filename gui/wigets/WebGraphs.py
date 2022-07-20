import wx

from common.FileUtil import FileUtil
from gui.wigets.DefEchart import WebPanel


class WebGraphs(wx.Panel):

    def __init__(self, parent):

        # 创建FlexGridSizer布局网格 vgap定义垂直方向上行间距/hgap定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=2, cols=2, vgap=1, hgap=1)

        self.DispPanel0 = WebPanel(parent)  # 自定义
        self.DispPanel1 = WebPanel(parent)  # 自定义
        self.DispPanel2 = WebPanel(parent)  # 自定义
        self.DispPanel3 = WebPanel(parent)  # 自定义

        sys_para = FileUtil.load_sys_para("sys_para.json")

        # 调整尺寸-size(x,y)数值 体现每个panel的大小
        self.DispPanel0.bind_browser(wx.html2.WebView.New(self.DispPanel0, -1, size=(sys_para["multi-panels"]["web_size_x"],
                                                                                     sys_para["multi-panels"]["web_size_y"])))
        self.DispPanel1.bind_browser(wx.html2.WebView.New(self.DispPanel1, -1, size=(sys_para["multi-panels"]["web_size_x"],
                                                                                     sys_para["multi-panels"]["web_size_y"])))
        self.DispPanel2.bind_browser(wx.html2.WebView.New(self.DispPanel2, -1, size=(sys_para["multi-panels"]["web_size_x"],
                                                                                     sys_para["multi-panels"]["web_size_y"])))
        self.DispPanel3.bind_browser(wx.html2.WebView.New(self.DispPanel3, -1, size=(sys_para["multi-panels"]["web_size_x"],
                                                                                     sys_para["multi-panels"]["web_size_y"])))

        # 加入Sizer中
        self.FlexGridSizer.Add(self.DispPanel0, proportion=1, border=2,
                               flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.FlexGridSizer.Add(self.DispPanel1, proportion=1, border=2,
                               flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.FlexGridSizer.Add(self.DispPanel2, proportion=1, border=2,
                               flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.FlexGridSizer.Add(self.DispPanel3, proportion=1, border=2,
                               flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
