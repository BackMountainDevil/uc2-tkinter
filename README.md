# 快速入门

1. 获取代码
2. 修改配置
- mqtt 中的 broker 信息，自定义指令中的设备标识 Sxxx

3. 准备环境
- Python 3.x
- tkinter（一般都需要额外安装）

4. 安装依赖包

```bash
# 建立虚拟环境（非必须）
python -m venv env
# 激活虚拟环境，同上
source env/bin/activate

# 安装依赖，必须
pip install -r requirement.txt 
```
5. 运行程序

```bash
python gui.py
```

# 安装 tkinter

Linux 系列的 python 为了轻便，不一定会把 tkinter 一并安装，根据 [python doc tkinter](https://docs.python.org/3/library/tkinter.html) 的描述可以通过 `python -m tkinter` 测试到底安装了没有，下面报错了说明没有安装

```bash
$ python -m tkinter
Traceback (most recent call last):
  File "/usr/lib/python3.9/runpy.py", line 188, in _run_module_as_main
    mod_name, mod_spec, code = _get_module_details(mod_name, _Error)
  File "/usr/lib/python3.9/runpy.py", line 147, in _get_module_details
    return _get_module_details(pkg_main_name, error)
  File "/usr/lib/python3.9/runpy.py", line 111, in _get_module_details
    __import__(pkg_name)
  File "/usr/lib/python3.9/tkinter/__init__.py", line 37, in <module>
    import _tkinter # If this fails your Python may not be configured for Tk
ImportError: libtk8.6.so: cannot open shared object file: No such file or directory
```

根据 [tkdocs install](https://tkdocs.com/tutorial/install.html#installlinux) 中对 linux 发行版的介绍，应该是可以在包管理器中找到这个包的，如 `sudo apt-get install python3-tk`，在 Arch 系列中，可以通过 `sudo pacman -S tk` 来安装 [tk](https://bbs.archlinux.org/viewtopic.php?id=260449)，此时再通过 `python -m tkinter` 测试就会出现一个窗体程序了。

# mqtt

/UC2-Software-GIT/HARDWARE_CONTROL/ESP32/README.md

本次实验中设置的不是 S007，是 S001,下面只是举一个例子

## 安装 mosquitto 
sudo pacman -S mosquitto
sudo apt-get install mosquitto mosquitto-clients

```bash
# 测试启动，使用默认配置 1883 端口
mosquitto

客户端，模拟订阅
mosquitto_sub -v -t topic01
// motor
mosquitto_sub -v -t /S007/MOT01/STAT
mosquitto_sub -v -t /S007/MOT01/RECM
// led
mosquitto_sub -v -t /S007/LAR01/STAT
mosquitto_sub -v -t /S007/LAR01/RECM
mosquitto_sub -v -t /S007/LAR01/ANNO

一个客户端，模拟发布
mosquitto_pub -t topic01 -m hello
mosquitto_pub -t /S007/MOT01/RECM -m "DRVZ+1000"

mosquitto_pub -t /S007/LAR01/RECM -m "PXL+2+127+255+50"
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



# 参考

- [Python GUI之tkinter教程](http://www.coolpython.net/tk/tk_primary/index.html)
- [UPython+opencv+tkinter整合demo完成！荣轩浩 2018-04-17](https://blog.csdn.net/a1_a1_a/article/details/79981788)
- [python Tkinter Display images on canvas, it always blink](https://stackoverflow.com/questions/20307718/python-tkinter-display-images-on-canvas-it-always-blink):用 canvas 闪烁的解决办法就是不用它，用 label 就没有这个问题
- [opencv-python-learn](https://gitee.com/anidea/opencv-python-learn):video/camera.py
- [用Python和摄像头制作简单的延时摄影. 達聞西.2015-03-25](https://www.cnblogs.com/frombeijingwithlove/p/4366605.html)
- [Python利用configparser对配置文件进行读写详解。Kearney form An idea 2020-10-20](https://blog.csdn.net/weixin_43031092/article/details/109174379)
- [python+opencv 将视频保存成 gif 动图. 一豆豆酱 2020-07-31](https://blog.csdn.net/qq_44965314/article/details/107706145)
- [opencv+tkinter录像程序.蓝色的程序猿 2020-11-20](https://blog.csdn.net/weixin_45906794/article/details/109876455)
- []()
