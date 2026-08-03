"""3D几何计算器 - 后端日志模块

与 2D 原版完全相同：日志同时输出到控制台和 log/ 目录下的时间戳文件。
为什么用两个 logger：
- frontend_logger：前端 JS 调用后端时报的错（方便排查前端传参问题）
- backend_logger：后端自己（求解过程）的日志
"""

import os
import datetime
import logging
import sys
import traceback

# 确保 log 目录存在（相对路径，所以要在 backend/ 下运行）
os.makedirs('log', exist_ok=True)

filename = f'log/log_{datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")}.txt'

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s %(levelname)s %(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(), logging.FileHandler(filename, encoding='utf-8')]
)

frontend_logger = logging.getLogger('前端')
backend_logger = logging.getLogger('后端')


def excepthook(exc_type: type[BaseException], exc_value: BaseException, exc_traceback) -> None:
    """全局未捕获异常钩子：把堆栈写进日志而不是静默崩溃"""
    s = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    backend_logger.error(s)


sys.excepthook = excepthook
