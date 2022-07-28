# -*- coding:utf-8 -*-

import os
import sys
from datetime import datetime
import yfinance as yf

import numpy as np

from datautil import converter
from tools.database.db_interface import db
from tools.util import date

path = os.path.dirname(__file__) + os.sep + '..' + os.sep
sys.path.append(path)
from futu import *

from tools.util import *
from tools.database import *


def get_daily():
    list_sql = '''
                select * from hsc_stocks_info;
               '''

    start = datetime.now()
    stk_info = db.read_data_from_sql(list_sql)
    stk_codes = stk_info.code.copy()
    stk_info = stk_info.set_index(['code'])

    table = 'hsc_stocks_d'
    db.truncate_table(table)


    # 获取日K线数据
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    for code in stk_codes:
        time.sleep(2)
        futu_code = converter.yfinance_code_to_futu_code(code)
        print(futu_code)
        ret, data, page_req_key = quote_ctx.request_history_kline(futu_code,
                                                                  start=date.get_9month_ago(),
                                                                  end=date.get_end_day(),
                                                                  max_count=200)  # 每页5个，请求第一页
        if ret == RET_OK:
            # print(data)
            # print(data['code'][0])  # 取第一条的股票代码
            # print(data['close'].values.tolist())  # 第一页收盘价转为 list
            handle_data(table, code, stk_info, data)
        else:
            print('error:', code, data)
        while page_req_key is not None:  # 请求后面的所有结果
            print('*************************************')
            ret, data, page_req_key = quote_ctx.request_history_kline(futu_code,
                                                                      start=date.get_9month_ago(),
                                                                      end=date.get_end_day(),
                                                                      max_count=200,
                                                                      page_req_key=page_req_key)  # 请求翻页后的数据
            if ret == RET_OK:
                # print(data)
                handle_data(table, code, stk_info, data)
            else:
                print('error:', code, data)
        print('All pages are finished!')
    quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽
    end = datetime.now()
    print('Download Data use {}'.format(end - start))


def handle_data(table, code, stk_info, data):
    columns = ['code', 'date', 'name', 'sector', 'sp_sector', 'industry', 'total_cap',
               'is_ss', 'is_sz', 'is_hs', 'is_spx', 'open', 'high', 'low', 'close', 'volume',
               'turnover', 'pe_ratio', 'turnover_rate', 'change_rate'
               ]
    stock = stk_info.loc[code]
    data['code'] = code
    data['name'] = stock.get('name')
    data['sector'] = stock.get('sector')
    data['sp_sector'] = stock.get('sp_sector')
    data['industry'] = stock.get('industry')
    data['total_cap'] = stock.get('total_cap')
    data['is_ss'] = stock.get('is_ss')
    data['is_sz'] = stock.get('is_sz')
    data['is_hs'] = stock.get('is_hs')
    data['is_spx'] = stock.get('is_spx')

    data.rename(columns={'time_key': 'date'}, inplace=True)
    data = data[columns]
    db.upsert_table(table, columns, data)

if __name__ == '__main__':
    get_daily()
