# 快速入门

1. 获取代码
2. 修改配置
- mqtt 中的 broker 信息，自定义指令中的设备标识 Sxxx
3. 准备环境
- Python 3.x （大部分 Linux 都会默认安装）
- opencv-python
- tkinter
- mqtt broker - mosquitto(没有程序也能运行，但无法控制 esp32)


生产环境（树莓派 4B 2021-05-07-raspios-buster-armhf.zip）  
在树莓派上测试表明 venv 创建的环境中会将系统安装的 python3-opencv 隔离开导致无法使用 cv2,而用 pip(pip3) 则是永无止境的错误最后告诉你它没辙了。

```bash
#安装 opencv-python，不要使用 pip、pip3
sudo apt install python3-opencv 
#测试：
python3 -c "import cv2; print(cv2.__version__)"
#安装 tkinter
sudo apt install python3-tk
#测试：
python -m tkinter
# 安装：
sudo apt install mosquitto mosquitto-clients

# 依赖包
sudo apt install python3-pil python3-pil.imagetk
pip3 install Pillow paho-mqtt
```

开发环境（AMD x86 Manjaro Linux）
```bash
sudo pacman -S tk mosquitto
# 建立虚拟环境（非必须）
python -m venv env
# 激活虚拟环境，同上
source env/bin/activate
# 安装依赖，必须，为了安装 opencv-python、Pillow、paho-mqtt，其他就是开发辅助包了
pip install -r requirement.txt 
```

5. 运行程序

```bash
python3 gui.py
```

# mqtt 指令格式

参见 /UC2-Software-GIT/HARDWARE_CONTROL/ESP32/README.md

mosquitto  测试


```bash
# 测试启动，使用默认配置 1883 端口
mosquitto

客户端，模拟订阅
mosquitto_sub -v -t topic01
// motor
mosquitto_sub -v -t /S001/MOT01/STAT
mosquitto_sub -v -t /S001/MOT01/RECM
// led
mosquitto_sub -v -t /S001/LAR01/STAT
mosquitto_sub -v -t /S001/LAR01/RECM
mosquitto_sub -v -t /S001/LAR01/ANNO

一个客户端，模拟发布
mosquitto_pub -t topic01 -m hello
mosquitto_pub -t /S001/MOT01/RECM -m "DRVZ+1000"
mosquitto_pub -t /S001/MOT01/RECM -m "DRVZ+-1000"
mosquitto_pub -t /S001/LAR01/RECM -m "PXL+2+127+255+50"
mosquitto_pub -t /S001/LAR01/RECM -m "CLEAR"
mosquitto_pub -t /S001/LAR01/RECM -m "RECT+0+0+8+8+0+255+0"
```

## LED

|COMMAND|RANGE|EXAMPLE|
|---|---|---|
|NA|UINT8 [0...4]|"NA+4"| 
|PXL|UINT8 [0...64,0...255,0...255,0...255] = [pixelNBR,R,G,B]|"PXL+20+127+255+50"|
|HLINE|UINT8 [0...8,0...8,0...8,0...8,0...255,0...255,0...255] = [x,y,w,h,R,G,B]|"HLINE+0+2+8+1+120+120+120" -> not active|
|VLINE|UINT8 [0...8,0...8,0...8,0...8,0...255,0...255,0...255] = [x,y,w,h,R,G,B]|"VLINE+0+2+8+1+10+10+90" -> not active|
|RECT|UINT8 [0...8,0...8,0...8,0...8,0...255,0...255,0...255] = [x,y,w,h,R,G,B]|"RECT+1+1+3+3+250+130+250"|
|CIRC|UINT8 [0...255,0...255,0...255] = [R,G,B]|"CIRC+85+86+87" -> not active|
|LEFT|UINT8 [0...255,0...255,0...255] = [R,G,B]|"LEFT+85+86+87"|
|RIGHT|UINT8 [0...255,0...255,0...255] = [R,G,B]|"RIGHT+85+86+87"|
|TOP|UINT8 [0...255,0...255,0...255] = [R,G,B]|"TOP+85+86+87"|
|BOTTOM|UINT8 [0...255,0...255,0...255] = [R,G,B]|"BOTTOM+85+86+87"|
|CLEAR|None|"CLEAR"|
|PRESET|None|"PRESET"|
|SETPRE|None|"SETPRE"|
|FLYBY|None|"FLYBY"|
|ALIVE|None|"ALIVE"|

## Motor Z

步进精度为 10,所以下面的范围的取值应该是 10 的整数倍

|COMMAND|FORMAT & RANGE|EXAMPLE|
|---|---|---|
|DRVZ|INT  -10000...10000|"DRVZ+1000", "DRVZ-1000"|

# FAQ
1. raspi install opencv

[How to Install OpenCV on Raspberry Pi 3.  Jul 5, 2019](https://linuxize.com/post/how-to-install-opencv-on-raspberry-pi/#:~:text=The%20OpenCV%20Python%20module%20is%20available%20from%20the,commands%3A%20sudo%20apt%20update%20sudo%20apt%20install%20python3-opencv)

2. ImportError: cannot import name 'ImageTk' from 'PIL' (/usr/lib/python3/dist-packages/PIL/__init__.py

sudo apt install python3-pil python3-pil.imagetk

[ImportError: cannot import name ‚ImageTk‘ from ‚PIL‘ (/usr/lib/python3/dist-packages/PIL/__init__.py)](http://www.programmieren-mit-python.de/importerror-cannot-import-name-imagetk-from-pil-usr-lib-python3-dist-packages-pil-__init__-py)
```bash
$ python3 gui.py 
Traceback (most recent call last):
  File "gui.py", line 10, in <module>
    from PIL import Image, ImageTk
ImportError: cannot import name 'ImageTk' from 'PIL' (/usr/lib/python3/dist-packages/PIL/__init__.py)
```

3. _tkinter.TclError: no display name and no $DISPLAY environment variable

我是从 ssh 打开遇到这个错误的。
```bash
$ python3 gui.py 
Traceback (most recent call last):
  File "gui.py", line 29, in <module>
    root = tk.Tk()
  File "/usr/lib/python3.7/tkinter/__init__.py", line 2023, in __init__
    self.tk = _tkinter.create(screenName, baseName, className, interactive, wantobjects, useTk, sync, use)
_tkinter.TclError: no display name and no $DISPLAY environment variable
```
从 vnc viewer 远程桌面打开就行

# 参考

- [Python GUI之tkinter教程](http://www.coolpython.net/tk/tk_primary/index.html)
- [UPython+opencv+tkinter整合demo完成！荣轩浩 2018-04-17](https://blog.csdn.net/a1_a1_a/article/details/79981788)
- [python Tkinter Display images on canvas, it always blink](https://stackoverflow.com/questions/20307718/python-tkinter-display-images-on-canvas-it-always-blink):用 canvas 闪烁的解决办法就是不用它，用 label 就没有这个问题
- [opencv-python-learn](https://gitee.com/anidea/opencv-python-learn):video/camera.py
- [用Python和摄像头制作简单的延时摄影. 達聞西.2015-03-25](https://www.cnblogs.com/frombeijingwithlove/p/4366605.html)
- [Python利用configparser对配置文件进行读写详解。Kearney form An idea 2020-10-20](https://blog.csdn.net/weixin_43031092/article/details/109174379)
- [python+opencv 将视频保存成 gif 动图. 一豆豆酱 2020-07-31](https://blog.csdn.net/qq_44965314/article/details/107706145)
- [opencv+tkinter录像程序.蓝色的程序猿 2020-11-20](https://blog.csdn.net/weixin_45906794/article/details/109876455)
- [Python + logging 输出到屏幕，将log日志写入文件.2018-03-13 21:26  nancy05](https://www.cnblogs.com/nancyzhu/p/8551506.html)
- []()
