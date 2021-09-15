
#

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

# 参考

- [Python GUI之tkinter教程](http://www.coolpython.net/tk/tk_primary/index.html)
- [UPython+opencv+tkinter整合demo完成！荣轩浩 2018-04-17](https://blog.csdn.net/a1_a1_a/article/details/79981788)
- [python Tkinter Display images on canvas, it always blink](https://stackoverflow.com/questions/20307718/python-tkinter-display-images-on-canvas-it-always-blink):用 canvas 闪烁的解决办法就是不用它，用 label 就没有这个问题
- [opencv-python-learn](https://gitee.com/anidea/opencv-python-learn):video/camera.py
- [用Python和摄像头制作简单的延时摄影. 達聞西.2015-03-25](https://www.cnblogs.com/frombeijingwithlove/p/4366605.html)
- []()
