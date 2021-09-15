
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


- [Python GUI之tkinter教程](http://www.coolpython.net/tk/tk_primary/index.html)
- [Python调用摄像头，实时显示视频在Tkinter界面.lyx4949. 2021-05-20](https://blog.csdn.net/lyx4949/article/details/117086277)
- []()
- []()
