#! /usr/bin/env python
# -*-  encoding: utf-8 -*-
# author 王二


from datetime import datetime, timedelta


class SysLog:
    error = '错误'
    warning = '警告'
    info = '信息'
    ind = '通知'

    def __init__(self, message):
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.message = message

    def re_print(self, cont):
        self.message.AppendText(self.time + ":\n" + cont + "\n")

    def clr_print(self):
        self.message.Clear()


class BizLog:

    def __init__(self, message):
        self.message = message

    def re_print(self, cont):
        self.message.AppendText(cont + "\n")

    def get_values(self):
        return self.message.GetValue()

    def clr_print(self):
        self.message.Clear()
