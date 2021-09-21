import configparser
import logging
import os
from logging import handlers


def Rgb2Hex(rgb=(255, 255, 255)):
    """
    将 RGB 颜色三元组转换成十六进制颜色的字符串
    如： (255, 255, 0) -> #ffff00
    https://blog.csdn.net/hepu8/article/details/88630979
    """
    return "#%02x%02x%02x" % rgb


def Hex2Rgb(hex="#ffffff"):
    """
    将十六进制的颜色字符串转换为 RGB 格式
    https://blog.csdn.net/sinat_37967865/article/details/93203689
    """
    r = int(hex[1:3], 16)
    g = int(hex[3:5], 16)
    b = int(hex[5:7], 16)
    rgb = str(r) + "+" + str(g) + "+" + str(b)  # 自定义 rgb 连接符号
    return rgb


def ensurePath(filepath):
    """文件路径检测,不存在就创建"""
    if not os.path.exists(filepath):
        os.makedirs(filepath)


def getDefalultFileDir(filename, configFile="config.ini"):
    """从配置文件中，获取日志文件路径,没有就默认 /log/logging.log"""
    if not filename:
        cfg = configparser.RawConfigParser()  # 创建配置文件对象
        cfg.optionxform = lambda option: option  # 重载键值存储时不重置为小写
        cfg.read(configFile, encoding="utf-8")  # 读取配置文件，没有就创建
        if not cfg.has_section("LOG"):
            cfg.add_section("LOG")  # 没有就创建
        if cfg.has_option("LOG", "fileDir") and cfg.has_option("LOG", "fileName"):
            fileDir = cfg.get("LOG", "fileDir")
            fileName = cfg.get("LOG", "fileName")
            filename = os.path.join(os.getcwd(), fileDir, fileName)
        else:
            fileDir = os.path.join(os.getcwd(), "log")
            filename = os.path.join(fileDir, "logging.log")
        ensurePath(fileDir)
    return filename


class Logger(object):
    """日志记录类：屏幕输出提示与文件长期记录"""

    level_relations = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARNING,
        "error": logging.ERROR,
        "crit": logging.CRITICAL,
    }  # 日志级别关系映射

    def __init__(
        self,
        filename=None,
        level="info",
        when="W0",
        backCount=0,
        fmC='%(levelname)s: %(message)s. File "%(pathname)s", line:%(lineno)d',
        fmF='%(levelname)s: %(message)s. In %(module)s %(funcName)s %(asctime)s \n\tFile "%(pathname)s", line:%(lineno)d',  # noqa
    ):
        """
        filename: 日志文件名称
        level:  日志级别
        when:   分割文件周期： W0 每周一、D 每日、 H 每小时
        backCount: 保留的备份文件的个数，多了旧的会被删除
        fmC:    日志输出到控制台的格式
        fmF:    日志文件的记录格式
        """
        filename = getDefalultFileDir(filename)  # 获取默认文件名称
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别

        fmConsole = logging.Formatter(fmC)  # 设置日志输出格式
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(fmConsole)  # 设置屏幕上显示的格式

        th = handlers.TimedRotatingFileHandler(
            filename=filename, when=when, backupCount=backCount, encoding="utf-8"
        )
        fmFile = logging.Formatter(fmF)  # 文件记录格式
        th.setFormatter(fmFile)  # 设置文件里写入的格式
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)


if __name__ == "__main__":
    # 测试颜色转换
    print(Rgb2Hex((255, 255, 0)))
    print(Hex2Rgb("#FF7F02"))
    # 测试日志功能
    log = Logger("uc2.log")
    log.logger.debug("正在调试")
    log.logger.info("一般信息")
    log.logger.warning("发生了警告")
    log.logger.error("发生了错误")
    log.logger.critical("严重错误，没救了")

    Logger("error.log", level="error").logger.error("真的没救了吗")
