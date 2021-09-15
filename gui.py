from gettext import gettext as _
import tkinter as tk
from tkinter import colorchooser
import cv2
from PIL import Image, ImageTk  # 图像控件
import time

root = tk.Tk()

root.title(_("第一个窗口"))  # 设置窗口的标题
root.geometry("640x480")  # 设置窗口的大小

m1 = tk.PanedWindow(root, showhandle=True, sashrelief="raised")  # 默认是左右分布的
m1.pack(fill=tk.BOTH, expand=1)


cap = cv2.VideoCapture(0)  # 创建摄像头对象


# 界面画布更新图像
def tkImage():
    ref, frame = cap.read()
    frame = cv2.flip(frame, 1)  # 摄像头翻转
    cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    pilImage = Image.fromarray(cvimage)
    pilImage = pilImage.resize((image_width, image_height), Image.ANTIALIAS)
    tkImage = ImageTk.PhotoImage(image=pilImage)
    # tkImage = ImageTk.PhotoImage(image=Image.fromarray(pilImage))
    return tkImage


image_width = 300
image_height = 200
canvas = tk.Canvas(m1, bg="white", width=image_width, height=image_height)
# canvas.pack(side="top")
m1.add(canvas)


def ImageSave():
    timestr = time.strftime("%Y%m%d_%H%M%S")
    filename = "{}.png".format(timestr)
    ref, frame = cap.read()
    frame = cv2.flip(frame, 1)  # 摄像头翻转
    cv2.imwrite(filename, frame)


btn_snap = tk.Button(m1, text=_("SNAP"), width=5, height=2, command=ImageSave)
btn_snap.pack(side="bottom")

m2 = tk.PanedWindow(orient=tk.VERTICAL, showhandle=True, sashrelief="raised")
m1.add(m2)


def motorchange():
    print(motorvalue.get())


motorvalue = tk.IntVar()
sb1 = tk.Spinbox(
    m2,
    from_=0,  # 最小值0
    to=100,  # 最大值100
    increment=10,  # 点击一次变化幅度为5
    textvariable=motorvalue,  # 绑定变量
    command=motorchange,
)
sb1.pack()


def MotroMove():
    """
    获取 slidebar 的值，向舵机发送 mqtt 指令
    """
    print("value: ", motorvalue.get())


btn_motor = tk.Button(m2, text=_("MOVE"), width=5, height=2, command=MotroMove)
btn_motor.pack()

LedColor = (255, 255, 255)


def ChooseColor():
    r = colorchooser.askcolor(title=_("颜色选择器"))
    print(r, r[0])
    # ((239, 240, 241), '#eff0f1')
    if r[0]:  # 避免选择 cancel 将 NULL 赋值给 LedColor
        global LedColor
        LedColor = r[0]


button1 = tk.Button(m2, text=_("Choose Color"), command=ChooseColor)
button1.pack()


def LedOn():
    """获取颜色，并发送 mqtt 开灯指令"""
    print("LedOn, color: ", LedColor)


def LedOff():
    """发送 mqtt 关灯指令"""
    print("LedOff")
    pass


btnLedOn = tk.Button(m2, text=_("LedOn"), command=LedOn)
btnLedOff = tk.Button(m2, text=_("LedOFF"), command=LedOff)
btnLedOn.pack()
btnLedOff.pack()

while True:
    pic = tkImage()
    canvas.create_image(0, 0, anchor="nw", image=pic)
    m1.update()
    m1.after(100)
cap.release()
print("loop")

root.mainloop()  # 启动窗口
