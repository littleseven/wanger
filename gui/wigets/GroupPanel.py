import wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure


class GroupPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=-1)

        # 分割子图实现代码
        self.figure = Figure(figsize=(8, 8))

        self.relate = self.figure.add_subplot(1, 1, 1)

        self.FigureCanvas = FigureCanvas(self, -1, self.figure)  # figure加到FigureCanvas
        self.TopBoxSizer = wx.BoxSizer(wx.VERTICAL)
        self.TopBoxSizer.Add(self.FigureCanvas, proportion=10, border=2, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(self.TopBoxSizer)
