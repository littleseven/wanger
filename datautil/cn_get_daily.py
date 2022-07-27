# -*- coding:utf-8 -*-

import os
import sys
from datetime import datetime
import yfinance as yf

import numpy as np

from tools.database.db_interface import db
from tools.util import date

path = os.path.dirname(__file__) + os.sep + '..' + os.sep
sys.path.append(path)

from tools.util import *
from tools.database import *


def get_daily():
    list_sql = '''
                select * from cn_stocks_info;
               '''

    start = datetime.now()
    stk_info = db.read_data_from_sql(list_sql)
    stk_codes = stk_info.code.copy()
    stk_info = stk_info.set_index(['code'])

    table = 'cn_stocks_d'
    db.truncate_table(table)

    columns = ['code', 'date', 'name', 'sector', 'sp_sector', 'industry', 'total_cap',
               'is_ss', 'is_sz', 'is_hs','open', 'high', 'low', 'close', 'vol'
               ]
    # 获取日K线数据
    batch = 40
    num = 0
    for n in range(0, len(stk_codes), batch):
        num += 1
        print('Processing 第 {} 批 【{}~{}/{}】...'.format(num, n, n + batch, len(stk_codes)))
        sub_codes = stk_codes[n: n + batch]
        symbol_list = ' '.join(sub_codes)
        data = yf.download(symbol_list, start=date.get_9month_ago(), end=date.get_end_day(),
                           group_by="ticker", threads=True, auto_adjust=True,
                           interval='1d')
        for i in sub_codes:
            if i in data.columns:
                stock = stk_info.loc[i]
                df = data[i]
                if df is None:
                    continue
                df = df.reset_index()
                df.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low',
                                   'Close': 'close', 'Volume': 'vol'},
                          inplace=True)
                df = df[~np.isnan(df['close'])]
                df['code'] = i
                if df is None:
                    continue
                df['name'] = stock.get('name')
                df['sector'] = stock.get('sector')
                df['sp_sector'] = stock.get('sp_sector')
                df['industry'] = stock.get('industry')
                df['total_cap'] = stock.get('total_cap')
                df['is_ss'] = stock.get('is_ss')
                df['is_sz'] = stock.get('is_sz')
                df['is_hs'] = stock.get('is_hs')
                df['is_spx'] = stock.get('is_spx')

                df = df[columns]
                db.upsert_table(table, columns, df)

    end = datetime.now()
    print('Download Data use {}'.format(end - start))


if __name__ == '__main__':
    get_daily()
