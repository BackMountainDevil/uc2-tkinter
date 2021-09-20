#!/usr/bin/env python3
# -*- encoding: UTF-8 -*-
import sys  # for python version check

if not sys.version_info >= (3,):  # if python2
    print(
        "Your python version is:",
        sys.version_info,
        ".Please run this with python 3. Exit now",
    )
    exit(0)

import configparser
import os
import time
import tkinter as tk
from gettext import gettext as _
from tkinter import colorchooser, messagebox
from tkinter.ttk import Notebook, PanedWindow
from mqtt import UCMqtt
from util import Logger

log = Logger("uc2.log", level="debug")  # 全局记录


try:
    import cv2
except ImportError as i:
    log.logger.error(
        _("%s\nMaybe you should try this: sudo apt install python3-opencv"), i
    )
    exit(0)


try:
    from PIL import Image, ImageTk
except ImportError as i:
    log.logger.error(
        _("%s\nTry this: sudo apt install python3-pil python3-pil.imagetk"), i
    )
    exit(0)


configFile = "config.ini"
cfg = configparser.RawConfigParser()  # 创建配置文件对象
cfg.optionxform = lambda option: option  # 重载键值存储时不重置为小写
cfg.read(configFile, encoding="utf-8")  # 读取配置文件，没有就创建
if not cfg.has_section("TKINTER"):
    cfg.add_section("TKINTER")  # 没有就创建


def checkQuit():
    """再次确认是否关闭程序"""
    global isRecord
    if isRecord:
        messagebox.showwarning(
            _("Warning"), _("Record task is running. Turn it off before exit")
        )
    else:
        res = messagebox.askokcancel(_("Tip"), _("Are u sure to quit?"))
        if res:
            root.destroy()  # 这里不推荐 quit 方法，在 root.mainloop()加 sleep就知道了


# 整体布局
try:
    global root
    root = tk.Tk()
except Exception as e:
    log.logger.error(
        _("%s\nPlease run this app in Desktop environment. App shutdown now"), e
    )
    exit(0)

root.protocol("WM_DELETE_WINDOW", checkQuit)  # 关闭窗口再次会再次确认
root.title(_("UC2"))  # 设置窗口的标题
root.geometry("640x480")  # 设置窗口的大小

pw = PanedWindow(orient=tk.HORIZONTAL)
pw.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# 左右两块区域
lfCam = tk.LabelFrame(pw, text=_("Camera"), width=320)
pw.add(lfCam, weight=2)
lfControl = tk.LabelFrame(pw, text=_("Control"), width=320)
pw.add(lfControl, weight=2)

# 右面版分为两个标签页
nb = Notebook(lfControl)
fLed = tk.Frame()
fMotor = tk.Frame()
nb.add(fLed, text=_("LED"))
nb.add(fMotor, text=_("Motor"))
nb.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

# 左面版


def ensurePath(filepath):
    """文件路径检测,不存在就创建"""
    if not os.path.exists(filepath):
        os.makedirs(filepath)


def ShowImg():
    """获取摄像头画面，并显示在 label 上"""
    global labCam, Cap
    ret, frame = Cap.read()  # 一帧一帧获取画面
    if not ret:
        print(_("Can't receive frame (stream end?)"))
    else:
        frame = cv2.flip(frame, 1)
        cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        pilImage = Image.fromarray(cvimage)
        pilImage = pilImage.resize((imgWidth, imgHeight), Image.ANTIALIAS)
        tkImage = ImageTk.PhotoImage(image=pilImage)
        labCam.imgtk = tkImage
        labCam.config(image=tkImage)
        labCam.after(100, ShowImg)  # 定时器，间隔 100 ms 后调用自身


def ImageSave():
    """将摄像头画面保存为 拍摄时间.jpg 文件"""
    global Cap, CapDir
    timestr = time.strftime("%Y%m%d_%H%M%S")
    filename = "{}.jpg".format(timestr)
    ref, frame = Cap.read()
    frame = cv2.flip(frame, 1)
    filepath = os.path.join(os.getcwd(), CapDir)
    filefullpath = os.path.join(filepath, filename)
    cv2.imwrite(filefullpath, frame)
    log.logger.debug(_("Snap to file: %s"), filefullpath)


def VideoRecord():
    """将画面录制成视频"""
    global timeGap, Cap, isRecord, isSave, CapFile, CapDir, CapDirName
    ret, frame = Cap.read()  # 一帧一帧获取画面
    if isRecord:
        if ret:
            frame = cv2.flip(frame, 1)
            timestr = time.strftime("%Y%m%d_%H%M%S")
            filename = "{}.jpg".format(timestr)
            filepath = os.path.join(os.getcwd(), CapDir, CapDirName)
            cv2.imwrite(os.path.join(filepath, filename), frame)  # 保存图片，以防断电
            CapFile.write(frame)  # 将画面写入视频文件
        else:
            print("Can't receive frame (stream end?)")

    try:  # 输入校验
        delayTime = timeGap.get()  # 单位：秒
    except Exception as e:
        print("Function VideoRecord: ", e)
        checkTimeGap()
        delayTime = timeGap.get()

    if delayTime < 3:  # 0 会运行异常
        delayTime = 3
        print(_("Warning: Time is less than 3! It will be set to 3"))
    labCam.after(1000 * delayTime, VideoRecord)  # 定时器，间隔 xx ms 后调用自身，注意单位


def isVideoRecord():
    """开始录制或结束录制"""
    global Cap, CapFile, CapDir, isRecord, timeGap, sbTime, btnRecord, CapDirName
    if not checkTimeGap():  # 强制检查输入
        return False
    FPS = 25  # 生成视频的帧率
    FRAME_WIDTH = int(Cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 获取相机帧的宽高
    FRAME_HEIGHT = int(Cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    FORMAT = cv2.VideoWriter_fourcc(*"XVID")  # 固定的文件格式
    if not isRecord:
        isRecord = not isRecord
        sbTime["state"] = "disable"  # 录制期间禁止修改间隔时间
        btnRecord["text"] = _("Stop Record")
        btnRecord["bg"] = "red"
        timestr = time.strftime("%Y%m%d_%H%M%S")
        delayTime = timeGap.get()
        filename = "{}_{}.avi".format(timestr, delayTime)  # 文件名:时间_间隔时间.avi
        CapDirName = "{}_{}".format(timestr, delayTime)
        filepath = os.path.join(os.getcwd(), CapDir, CapDirName)
        ensurePath(filepath)
        filefullpath = os.path.join(filepath, filename)
        log.logger.debug(_("Start record to file: %s"), filefullpath)
        CapFile = cv2.VideoWriter(
            filefullpath, FORMAT, FPS, (FRAME_WIDTH, FRAME_HEIGHT)
        )
    else:
        isRecord = False  # 结束录制
        sbTime["state"] = "normal"  # 恢复允许修改间隔时间
        btnRecord["text"] = _("Start Record")
        btnRecord["bg"] = "#eff0f1"
        CapFile = None
        log.logger.debug(_("Stop record"))


def checkTimeGap():
    """对用户的拍摄间隔时间进行合法性验证"""
    global timeGap
    try:
        delayTime = timeGap.get()  # 字符数据会触发异常，小数会自动转化为整数
        if isinstance(delayTime, int):  # 整数验证，这一步似乎多余
            return True
        else:
            return False
    except Exception as e:
        print(e)
        timeGap.set(30)
        messagebox.showerror(
            _("Error"),
            _("The time format you input is invalid\nSet it to Integer like 30"),
        )
        return False


Cap = cv2.VideoCapture(0)  # 创建摄像头对象
CapFile = None  # 视频文件
CapDir = ""  # 视频（图像）文件的一级目录，可在配置文件中自定义
if cfg.has_option("TKINTER", "CapDir"):
    CapDir = cfg.get("TKINTER", "CapDir")
else:
    CapDir = "output"  # 默认值
CapDirName = ""  # 视频（图像）文件的二级目录,程序自动创建：时间_间隔时间
ensurePath(os.path.join(os.getcwd(), CapDir))  # 确保 snap 拍摄的时候存在路径
isRecord = False  # 暂停录制


imgWidth = 300
imgHeight = 200
labCam = tk.Label(lfCam, bg="white", width=imgWidth, height=imgHeight)
labCam.grid(row=0, column=0, rowspan=1, columnspan=3)  # 占据三个格子

labTime = tk.Label(lfCam, text=_("Time(s)"))  # 时间标签
labTime.grid(row=1, column=0, padx=5, pady=5)

timeGap = tk.IntVar()  # 时间间隔
timeGap.set(30)  # 拍摄间隔默认值（秒）
sbTime = tk.Spinbox(
    lfCam,
    from_=0,  # 最小值
    to=1000,  # 最大值
    increment=1,  # 点击一次变化幅度为 1
    textvariable=timeGap,
    width=10,
    validate="key",  # 当输入框被编辑的时候调用校验
    validatecommand=checkTimeGap,  # 校验函数
)
sbTime.grid(row=1, column=2, padx=5, pady=5)

btn_snap = tk.Button(lfCam, text=_("SNAP"), width=5, height=2, command=ImageSave)
btn_snap.grid(row=2, column=0)

btnRecord = tk.Button(
    lfCam, text=_("Start Record"), width=10, height=2, command=isVideoRecord
)
btnRecord.grid(row=2, column=1, columnspan=2)

# 右面板的 LED 标签页
labColor = tk.Label(fLed, text=_("Color Preview"), height=5, width=25)  # 颜色预览标签
labColor.grid(row=0, column=0, columnspan=2)
if cfg.has_option("TKINTER", "ledColor"):
    labColor["bg"] = cfg.get("TKINTER", "ledColor")
else:
    labColor["bg"] = "#ffffff"


def ChooseColor():
    """设置颜色，但先不使设置生效，需要 LedOn 使其生效，避免失误"""
    global labColor
    r = colorchooser.askcolor(title=_("Choose new color"), color=labColor["bg"])
    # ((239, 240, 241), '#eff0f1')
    if r[1]:  # 避免选择 cancel 将 NULL 赋值给 颜色预览标签
        labColor["bg"] = r[1]
        cfg.set("TKINTER", "ledColor", r[1])
        with open(configFile, "w", encoding="utf-8") as configfile:  # 保存颜色配置
            cfg.write(configfile)


btnColor = tk.Button(fLed, text=_("Choose Color"), command=ChooseColor)
btnColor.grid(row=1, column=0, columnspan=2)


def LedOn():
    """将颜色设置发送 mqtt 开灯指令"""
    global labColor, mqclient
    mqclient.pubLedOn(labColor.cget("bg"))


def LedOff():
    """发送 mqtt 关灯指令"""
    global mqclient
    mqclient.pubLedOff()


btnLedOn = tk.Button(fLed, text=_("LedOn"), bg="lightgreen", command=LedOn)
btnLedOff = tk.Button(fLed, text=_("LedOFF"), bg="tomato", command=LedOff)
btnLedOn.grid(row=2, column=0)
btnLedOff.grid(row=2, column=1)

# 右面板的 Motor 标签页


def MotroMove():
    """
    获取 slidebar 的值，向舵机发送 mqtt 指令
    """
    global motorValue, mqclient
    value = motorValue.get()
    cmd = "DRVZ+" + str(value)
    mqclient.pubMotorZ(cmd)


motorValue = tk.IntVar()
sbMotor = tk.Spinbox(
    fMotor,
    from_=-1000,  # 最小值
    to=1000,  # 最大值
    increment=10,  # 点击一次变化幅度为 10
    textvariable=motorValue,  # 绑定变量
)
sbMotor.grid(row=0, column=0, columnspan=2)
btnMotor = tk.Button(fMotor, text=_("MOVE"), width=25, height=2, command=MotroMove)
btnMotor.grid(row=1, column=0, columnspan=2)


mqclient = UCMqtt(log)  # 创建 mqtt 对象实例
mqclient.connect()  # 连接 broker


ShowImg()
VideoRecord()  # 录制事件
root.mainloop()
Cap.release()
cv2.destroyAllWindows()
log.logger.debug(_("app close"))
