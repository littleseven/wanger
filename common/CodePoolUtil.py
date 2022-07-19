#! /usr/bin/env python
# -*-  encoding: utf-8 -*-
# author 王二

from common.FileUtil import FileUtil


class CodePoolUtil:

    def __init__(self, syslog_obj):
        self.syslog = syslog_obj

    def load_my_pool(self):
        # 加载自选股票池
        self_pool = FileUtil.load_sys_para("stock_self_pool.json")
        self.syslog.re_print("从Json文件获取自选股票池成功...\n")
        return self_pool

    def save_self_pool(self, total_code):
        FileUtil.save_sys_para("stock_self_pool.json", total_code)
        self.syslog.re_print("保存自选股票池至Json文件成功...\n")

    def load_pool_stock(self):
        # 加载自选股票池-个股
        return self.load_my_pool()["股票"]

    def load_pool_index(self):
        # 加载自选股票池-指数
        return self.load_my_pool()["指数"]

    def update_increase_st(self, new_code):
        # 增量更新
        st_code = self.load_my_pool()
        st_code['股票'].update(new_code)
        self.save_self_pool(st_code)
        self.syslog.re_print("增量更新自选股票池成功...\n")

    def update_replace_st(self, new_code):
        # 完全替换
        st_code = self.load_my_pool()
        st_code['股票'].clear()
        st_code['股票'].update(new_code)
        self.save_self_pool(st_code)
        self.syslog.re_print("完全替换自选股票池成功...\n")

    def delete_one_st(self, one_code):
        # 删除股票
        st_code = self.load_my_pool()
        st_code['股票'].pop(one_code)
        self.save_self_pool(st_code)
        self.syslog.re_print("删除自选股票池中{0}...\n".format(one_code))
