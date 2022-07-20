import wx

from gui.wigets.StockPanel import StockPanel


class MpfGraphs:
    def __init__(self, parent):

        # 创建FlexGridSizer布局网格 vgap定义垂直方向上行间距/hgap定义水平方向上列间距
        self.FlexGridSizer = wx.FlexGridSizer(rows=2, cols=2, vgap=1, hgap=1)
        self.DispPanel0 = StockPanel(parent)  # 自定义
        self.DispPanel1 = StockPanel(parent)  # 自定义
        self.DispPanel2 = StockPanel(parent)  # 自定义
        self.DispPanel3 = StockPanel(parent)  # 自定义

        # 加入Sizer中
        self.FlexGridSizer.Add(self.DispPanel0.disp_panel, proportion=1, border=2,
                               flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.FlexGridSizer.Add(self.DispPanel1.disp_panel, proportion=1, border=2,
                               flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.FlexGridSizer.Add(self.DispPanel2.disp_panel, proportion=1, border=2,
                               flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.FlexGridSizer.Add(self.DispPanel3.disp_panel, proportion=1, border=2,
                               flag=wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)
