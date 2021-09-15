from gettext import gettext as _
import tkinter as tk
from tkinter import colorchooser
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk  # 图像控件
import time

root = tk.Tk()

root.title(_("第一个窗口"))  # 设置窗口的标题
root.geometry("640x480")  # 设置窗口的大小

m1 = tk.PanedWindow(root, showhandle=True, sashrelief="raised")  # 默认是左右分布的
m1.pack(fill=tk.BOTH, expand=1)

left = tk.Label(m1, text="CAMERA", bg="blue")
m1.add(left)


m2 = tk.PanedWindow(orient=tk.VERTICAL, showhandle=True, sashrelief="raised")
m1.add(m2)

root = tk.Label(m2, text="标签2", bg="green")
m2.add(root)

bottom = tk.Label(m2, text="标签3", bg="red")
m2.add(bottom)

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


image_width = 600
image_height = 500
canvas = tk.Canvas(m1, bg="white", width=image_width, height=image_height)  # 绘制画布
canvas.place(x=0, y=0)


def ImageSave():
    timestr = time.strftime("%Y%m%d_%H%M%S")
    filename = "image/{}.png".format(timestr)
    ref, frame = cap.read()
    frame = cv2.flip(frame, 1)  # 摄像头翻转
    cv2.imwrite(filename, frame)


btn_snap = tk.Button(m1, text=_("SNAP"), width=5, height=2, command=ImageSave)
btn_snap.pack()


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


def click_button():
    """
    当按钮被点击时执行该函数
    """
    messagebox.showinfo(title=_("友情提示"), message=_("你点击了按钮"))


btn_motor = tk.Button(m2, text=_("MOVE"), width=5, height=2, command=click_button)
btn_motor.pack()


def ChooseColor():
    r = tk.colorchooser.askcolor(title=_("颜色选择器"))
    print(r)


button1 = tk.Button(m2, text=_("Choose Color"), command=ChooseColor)
button1.pack()


while True:
    pic = tkImage()
    canvas.create_image(0, 0, anchor="nw", image=pic)
    m1.update()
    m1.after(100)
cap.release()
print("loop")

root.mainloop()  # 启动窗口
