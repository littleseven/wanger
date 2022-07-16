#! /usr/bin/env python
# -*-  encoding: utf-8 -*-
# author 王二

# 通读<8.1 定制可视化接口> -- 代码具体出现于<8.1.2 可视化接口框架实现>
class MethodTable:

    def __init__(self):
        self.routes = {}

    def method(self, func_key):
        def decorator(f):
            self.routes[func_key] = f
            return f
        return decorator

    def get_method(self, func_key):
        function_val = self.routes.get(func_key)
        if function_val:
            return function_val
        else:
            raise ValueError('Route "{}"" has not been registered'.format(func_key))
