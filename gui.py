import time
import tkinter as tk
from gettext import gettext as _
from tkinter import colorchooser
from tkinter.ttk import Notebook, PanedWindow

import cv2
from PIL import Image, ImageTk

# 整体布局
root = tk.Tk()
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


def ShowImg():
    """获取摄像头画面，并显示在画布上"""
    ret, frame = Cap.read()  # 一帧一帧获取画面
    if not ret:
        print(_("Can't receive frame (stream end?). Exiting ..."))
    else:
        frame = cv2.flip(frame, 1)
        cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        pilImage = Image.fromarray(cvimage)
        pilImage = pilImage.resize((imgWidth, imgHeight), Image.ANTIALIAS)
        tkImage = ImageTk.PhotoImage(image=pilImage)
        CamCanvas.create_image(0, 0, anchor="nw", image=tkImage)
        CamCanvas.update()  # 强制重绘画布
        lfCam.after(10, ShowImg)  # 定时器，间隔 10 ms


def ImageSave():
    """将摄像头画面保存为 拍摄时间.jpg 文件"""
    timestr = time.strftime("%Y%m%d_%H%M%S")
    filename = "{}.jpg".format(timestr)
    ref, frame = Cap.read()
    frame = cv2.flip(frame, 1)
    cv2.imwrite(filename, frame)


Cap = cv2.VideoCapture(0)  # 创建摄像头对象

imgWidth = 300
imgHeight = 200
CamCanvas = tk.Canvas(lfCam, bg="white", width=imgWidth, height=imgHeight)
CamCanvas.pack()
btn_snap = tk.Button(lfCam, text=_("SNAP"), width=5, height=2, command=ImageSave)
btn_snap.pack(side="bottom")

# 右面板的 LED 标签页
LedColor = (255, 255, 255)


def ChooseColor():
    """设置颜色，但先不使设置生效，需要 LedOn 使其生效，避免失误"""
    r = colorchooser.askcolor(title=_("颜色选择器"))
    print(r, r[0])
    # ((239, 240, 241), '#eff0f1')
    if r[0]:  # 避免选择 cancel 将 NULL 赋值给 LedColor
        global LedColor
        LedColor = r[0]


butColor = tk.Button(fLed, text=_("Choose Color"), command=ChooseColor)
butColor.pack()


def LedOn():
    """将颜色设置发送 mqtt 开灯指令"""
    print("LedOn, color: ", LedColor)


def LedOff():
    """发送 mqtt 关灯指令"""
    print("LedOff")


btnLedOn = tk.Button(fLed, text=_("LedOn"), command=LedOn)
btnLedOff = tk.Button(fLed, text=_("LedOFF"), command=LedOff)
btnLedOn.pack()
btnLedOff.pack()

# 右面板的 Motor 标签页


def MotorChange():
    print(motorValue.get())


def MotroMove():
    """
    获取 slidebar 的值，向舵机发送 mqtt 指令
    """
    print("value: ", motorValue.get())


motorValue = tk.IntVar()
sbMotor = tk.Spinbox(
    fMotor,
    from_=0,  # 最小值0
    to=100,  # 最大值100
    increment=10,  # 点击一次变化幅度为5
    textvariable=motorValue,  # 绑定变量
    command=MotorChange,
)
sbMotor.pack()
btnMotor = tk.Button(fMotor, text=_("MOVE"), width=5, height=2, command=MotroMove)
btnMotor.pack()


ShowImg()
root.mainloop()
Cap.release()
cv2.destroyAllWindows()
print(_("app close"))
