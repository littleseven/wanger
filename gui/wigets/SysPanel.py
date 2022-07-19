import wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from graph.SystemApply import Sys_MultiGraph


class Sys_Panel(Sys_MultiGraph, wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent=parent, id=-1)
        Sys_MultiGraph.__init__(self, **kwargs)

        self.FigureCanvas = FigureCanvas(self, -1, self.fig)  # figure加到FigureCanvas
        self.TopBoxSizer = wx.BoxSizer(wx.VERTICAL)
        self.TopBoxSizer.Add(self.FigureCanvas, proportion=-1, border=2, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(self.TopBoxSizer)

    def update_subgraph(self):
        self.FigureCanvas.draw()
