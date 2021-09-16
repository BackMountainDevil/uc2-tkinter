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


""" print(Rgb2Hex((255, 255, 0)))
print(Hex2Rgb("#FF7F02")) """
