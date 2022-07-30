# -*- coding:utf-8 -*-
import math
from datetime import datetime

import pandas as pd
import os
import sys
import yfinance as yf

# import xldr
from gui import constants
from tools.util import *
from tools.database.db_interface import db

path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/datafiles/'

sys.path.append(path)


def fix_code(x):
    if math.isnan(x):
        return None
    elif isinstance(x, int) or isinstance(x, float):
        x = int(x)
        if x > 1000:
            y = str(x)
        elif x < 10:
            y = '000' + str(x)
        elif x < 100:
            y = '00' + str(x)
        elif x < 1000:
            y = '0' + str(x)
        return y + '.HK'
    else:
        return None


def fix_acode(x):
    if math.isnan(x):
        return None
    elif isinstance(x, int) or isinstance(x, float):
        x = int(x)
        if 600000 <= x < 700000:
            y = str(x) + '.SS'
        elif 10000 <= x < 600000:
            y = str(x) + '.SZ'
        elif 1000 <= x < 10000:
            y = '00' + str(x) + '.SZ'
        elif 100 <= x < 1000:
            y = '000' + str(x) + '.SZ'
        elif 10 <= x < 100:
            y = '0000' + str(x) + '.SZ'
        elif 0 < x < 10:
            y = '00000' + str(x) + '.SZ'
        return y
    else:
        return None


def fix_number(x):
    if math.isnan(x):
        return 0
    else:
        return x

def get_code(c, a, h):
    if c is not None:
        return c
    elif h is not None:
        return h
    elif a is not None:
        return a


def get_sector(sector):
    sectors = {
        'Utilities': 'Utilities',
        'Consumer Cyclical': 'Consumer Discretionary',
        'Healthcare': 'Health Care',
        'Technology': 'Information Technology',
        'Consumer Defensive': 'Consumer Staples',
        'Financial Services': 'Financials',
        'Basic Materials': 'Materials',
        'Industrials': 'Industrials',
        'Real Estate': 'Real Estate',
        'Energy': 'Energy',
        'Communication Services': 'Communication Services'
    }
    return sectors.get(sector, None)


def get_industry(code):
    print(code)
    ticker = yf.Ticker(code)
    info = ticker.info
    return info['industry']


def is_ss(x):
    if isinstance(x, str) and x.endswith('SS'):
        return 'Y'
    else:
        return 'N'


def is_sz(x):
    if isinstance(x, str) and x.endswith('SZ'):
        return 'Y'
    else:
        return 'N'


def is_hs(x):
    if isinstance(x, str) and x.endswith('HK'):
        return 'Y'
    else:
        return 'N'


def is_spx(x):
    if isinstance(x, str) and not (x.endswith('HK') or x.endswith('SS') or x.endswith('SZ')):
        return 'Y'
    else:
        return 'N'


start = datetime.now()

info_table = 'hsc_stocks_info'
columns = ['code', 'name', 'sector', 'industry', 'is_hs', 'is_ss', 'is_sz', 'is_spx', 'sp_sector', 'total_cap',
           'country']

sql = ''' SELECT `{}` FROM `{}` WHERE sector != '' AND sector is not null;''' \
    .format('`,`'.join(columns), info_table)
data = db.read_data_from_sql(sql)

# 更新 标普500 权重股
hk_columns = ['code', 'name']
symbols = pd.read_excel(constants.DATA_PATH + 'hsc500c.xls', sheet_name='hsci500')
# 'acode', 'hcode'
if symbols is not None:
    symbols.rename(columns={'code': 'code', 'name': 'name', 'sector': 'sector', 'industry': 'industry'},
                   inplace=True)
    # symbols['is_hs'] = 'Y'
    # symbols['sector'] = ''
    # symbols['industry'] = ''
    # symbols['sp_sector'] = ''
    symbols.hcode = symbols.hcode.map(fix_code)
    symbols.code = symbols.code.map(fix_code)
    symbols.acode = symbols.acode.map(fix_acode)
    symbols.code = symbols.apply(lambda row: get_code(row['code'], row['acode'], row['hcode']), axis=1)
    symbols['is_hs'] = symbols.code.map(is_hs)
    symbols['is_ss'] = symbols.code.map(is_ss)
    symbols['is_sz'] = symbols.code.map(is_sz)
    symbols['is_spx'] = symbols.code.map(is_spx)
    # codes = symbols.code #[0:10]
    # db.upsert_table(info_table, columns, symbols)
    if data is not None:
        symbols = pd.merge(symbols, data, on=['code', 'name', 'is_hs', 'is_ss', 'is_sz', 'is_spx'], how='left')

    symbols.total_cap = symbols.total_cap.map(fix_number)
    db.upsert_table(info_table, columns, symbols)
    codes = symbols[symbols['sector'].isnull() | symbols['country'].isnull()].code
    # codes = symbols[symbols['sector'] == ''].code
    for code in codes:
        now = datetime.now()
        ticker = yf.Ticker(code)
        info = ticker.info
        print('download {} cost {}'.format(code, datetime.now() - now))
        if info is not None:
            symbols.loc[symbols.code == code, 'sector'] = info['sector']
            symbols.loc[symbols.code == code, 'sp_sector'] = get_sector(info['sector'])
            symbols.loc[symbols.code == code, 'industry'] = info['industry']
            symbols.loc[symbols.code == code, 'country'] = info['country']
            symbols.loc[symbols.code == code, 'total_cap'] = info['marketCap']
            db.upsert_table(info_table, columns, symbols.loc[symbols.code == code])

    symbols.sp_sector = symbols.sector.map(get_sector)
    # db.truncate_table(info_table)
    db.upsert_table(info_table, columns, symbols)


end = datetime.now()
print('Download Data use {}'.format(end - start))
