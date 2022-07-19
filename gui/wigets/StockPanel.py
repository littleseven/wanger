import mplfinance as mpf
import numpy as np
import pandas as pd

from gui.wigets.BasePanel import BasePanel


class StockPanel:
    def __init__(self, parent):
        self.disp_panel = BasePanel(parent)  # 自定义
        self.figure = self.disp_panel.figure
        self.ochl = self.disp_panel.ochl
        self.vol = self.disp_panel.vol

        self.FigureCanvas = self.disp_panel.FigureCanvas

    def clear_subgraph(self):
        # 再次画图前,必须调用该命令清空原来的图形
        self.ochl.clear()
        self.vol.clear()

    def update_subgraph(self):
        self.FigureCanvas.draw()

    def draw_subgraph(self, stockdat, st_name, st_kylabel):
        # 绘制多子图页面
        num_bars = np.arange(0, len(stockdat.index))

        # 绘制K线
        # 原mpl_finance方法
        """
        ohlc = list(zip(num_bars, stockdat.Open, stockdat.Close, stockdat.High, stockdat.Low))
        mpf.candlestick_ochl(self.ochl, ohlc, width=0.5, colorup='r', colordown='g')  # 绘制K线走势
        """
        # 现mplfinance方法
        """
        make_marketcolors() 设置k线颜色
        :up 设置阳线柱填充颜色
        :down 设置阴线柱填充颜色
        ：edge 设置蜡烛线边缘颜色 'i' 代表继承k线的颜色
        ：wick 设置蜡烛上下影线的颜色
        ：volume 设置成交量颜色
        ：inherit 是否继承, 如果设置了继承inherit=True，那么edge即便设了颜色也会无效
        """
        def_color = mpf.make_marketcolors(up='red', down='green', edge='black', wick='black')
        """
        make_mpf_style() 设置mpf样式
        ：gridaxis:设置网格线位置,both双向
        ：gridstyle:设置网格线线型
        ：y_on_right:设置y轴位置是否在右
        """
        def_style = mpf.make_mpf_style(marketcolors=def_color, gridaxis='both', gridstyle='-.', y_on_right=False)
        mpf.plot(pd.DataFrame(stockdat), type='candle', style=def_style,  ax=self.ochl)

        # 绘制成交量
        self.vol.bar(num_bars, stockdat.Volume, color=['g' if stockdat.Open[x] > stockdat.Close[x] else 'r' for x in
                                                    range(0, len(stockdat.index))])

        self.ochl.set_ylabel(st_kylabel)
        self.vol.set_ylabel(u"成交量")
        self.ochl.set_title(st_name + " 行情走势图")

        major_tick = len(num_bars)
        self.ochl.set_xlim(0, major_tick)  # 设置一下x轴的范围
        self.vol.set_xlim(0, major_tick)  # 设置一下x轴的范围

        self.ochl.set_xticks(range(0, major_tick, 15))  # 每五天标一个日期
        self.vol.set_xticks(range(0, major_tick, 15))  # 每五天标一个日期
        self.vol.set_xticklabels(
            [stockdat.index.strftime('%Y-%m-%d %H:%M')[index] for index in self.vol.get_xticks()])  # 标签设置为日期

        for label in self.ochl.xaxis.get_ticklabels():  # X-轴每个ticker标签隐藏
            label.set_visible(False)
        for label in self.vol.xaxis.get_ticklabels():  # X-轴每个ticker标签隐藏
            label.set_rotation(45)  # X-轴每个ticker标签都向右倾斜45度
            label.set_fontsize(10)  # 设置标签字体

        self.ochl.grid(True, color='k')
        self.vol.grid(True, color='k')
