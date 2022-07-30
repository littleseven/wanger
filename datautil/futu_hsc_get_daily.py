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

    date_start = date.get_3year_ago()
    date_end = date.get_end_day()

    # 获取日K线数据
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    for code in stk_codes:
        download_data(quote_ctx, table, code, stk_info, date_start, date_end)
        time.sleep(2.5)
    quote_ctx.close()  # 结束后记得关闭当条连接，防止连接条数用尽
    end = datetime.now()
    print('Download Data use {}'.format(end - start))


result = None


def download_data(quote_ctx, table, code, stk_info, start, end):
    global result
    result = None
    futu_code = converter.yf_to_ft(code)
    print(futu_code)
    ret, data, page_req_key = quote_ctx.request_history_kline(futu_code,
                                                              start=start,
                                                              end=end,
                                                              max_count=128)  # 每页5个，请求第一页
    if ret == RET_OK:
        result = handle_data(table, code, stk_info, data)
    else:
        print('error:', code, data)
    while page_req_key is not None:  # 请求后面的所有结果
        ret, data, page_req_key = quote_ctx.request_history_kline(futu_code,
                                                                  start=start,
                                                                  end=end,
                                                                  max_count=128,
                                                                  page_req_key=page_req_key)  # 请求翻页后的数据
        if ret == RET_OK:
            # print(data)
            result = pd.concat([result, handle_data(table, code, stk_info, data)], ignore_index=True)
        else:
            print('error:', code, data)
    columns = ['code', 'date', 'name', 'sector', 'sp_sector', 'industry', 'total_cap',
               'is_ss', 'is_sz', 'is_hs', 'is_spx', 'open', 'high', 'low', 'close', 'volume',
               'turnover', 'pe_ratio', 'turnover_rate', 'change_rate'
               ]
    if result is not None:
        db.upsert_table(table, columns, result)
    print('download ' + code + ' data finish')
    return result


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
    # db.upsert_table(table, columns, data)
    return data


if __name__ == '__main__':
    get_daily()
