import wx
from matplotlib import gridspec as gridspec
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure

from common.FileUtil import FileUtil


class BasePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=-1)

        sys_para = FileUtil.load_sys_para("sys_para.json")

        # 分割子图实现代码
        self.figure = Figure(figsize=(sys_para["multi-panels"]["mpl_fig_x"],
                                      sys_para["multi-panels"]["mpl_fig_y"]))  # 调整尺寸-figsize(x,y)

        gs = gridspec.GridSpec(2, 1, left=sys_para["multi-panels"]["mpl_fig_left"],
                               bottom=sys_para["multi-panels"]["mpl_fig_bottom"],
                               right=sys_para["multi-panels"]["mpl_fig_right"],
                               top=sys_para["multi-panels"]["mpl_fig_top"],
                               wspace=None, hspace=0.1, height_ratios=[3.5, 1])

        self.ochl = self.figure.add_subplot(gs[0, :])
        self.vol = self.figure.add_subplot(gs[1, :])

        self.FigureCanvas = FigureCanvas(self, -1, self.figure)  # figure加到FigureCanvas
        self.TopBoxSizer = wx.BoxSizer(wx.VERTICAL)
        self.TopBoxSizer.Add(self.FigureCanvas, proportion=10, border=2, flag=wx.ALL | wx.EXPAND)

        self.SetSizer(self.TopBoxSizer)
