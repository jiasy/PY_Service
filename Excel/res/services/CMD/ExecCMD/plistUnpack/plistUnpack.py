#!/usr/bin/python
import os, sys
from xml.etree import ElementTree
from PIL import Image


def tree_to_dict(tree):
    d = {}
    for index, item in enumerate(tree):
        if item.tag == 'key':
            if tree[index + 1].tag == 'string':
                d[item.text] = tree[index + 1].text
            elif tree[index + 1].tag == 'true':
                d[item.text] = True
            elif tree[index + 1].tag == 'false':
                d[item.text] = False
            elif tree[index + 1].tag == 'dict':
                d[item.text] = tree_to_dict(tree[index + 1])
    return d


def gen_png_from_plist(plist_filename, png_filename):
    file_path = plist_filename.replace('.plist', '')
    big_image = Image.open(png_filename)
    root = ElementTree.fromstring(open(plist_filename, 'r').read())
    plist_dict = tree_to_dict(root[0])

    def to_list(x_):
        return x_.replace('{', '').replace('}', '').split(',')

    for _key, _value in plist_dict['frames'].items():
        rectlist = to_list(_value['frame'])
        width = int(rectlist[3] if _value['rotated'] else rectlist[2])
        height = int(rectlist[2] if _value['rotated'] else rectlist[3])
        box = (
            int(rectlist[0]),
            int(rectlist[1]),
            int(rectlist[0]) + width,
            int(rectlist[1]) + height,
        )
        sizelist = [int(x) for x in to_list(_value['sourceSize'])]
        rect_on_big = big_image.crop(box)

        if _value['rotated']:
            rect_on_big = rect_on_big.transpose(Image.ROTATE_90)
        if _key.endswith(".png"):
            result_image = Image.new('RGBA', sizelist, (0, 0, 0))
        elif _key.endswith(".jpg"):
            result_image = Image.new('RGB', sizelist, (0, 0, 0))
        else:
            print("不支持的格式 " + _key)
        if _value['rotated']:
            result_box = (
                int((sizelist[0] - height) / 2),
                int((sizelist[1] - width) / 2),
                int((sizelist[0] + height) / 2),
                int((sizelist[1] + width) / 2)
            )
        else:
            result_box = (
                int((sizelist[0] - width) / 2),
                int((sizelist[1] - height) / 2),
                int((sizelist[0] + width) / 2),
                int((sizelist[1] + height) / 2)
            )
        result_image.paste(rect_on_big, result_box, mask=0)
        if not os.path.isdir(file_path):
            os.mkdir(file_path)
        outfile = (file_path + '/' + _key)
        result_image.save(outfile)
        print(outfile, "generated")


# python /Volumes/Files/develop/GitHub/PY_Service/ExcelCommand.py --excelPath /Volumes/Files/develop/GitHub/PY_Service/Excel/res/services/CMD/ExecCMD/plistUnpack/plistUnpack.xlsx --executeType 命令行驱动
if __name__ == '__main__':
    baseFilePath = sys.argv[1]
    plist_filePath = baseFilePath + '.plist'
    if os.path.realpath(plist_filePath) == baseFilePath + '.plist':
        png_filePath = baseFilePath + '.png'
        if os.path.exists(plist_filePath) and \
                os.path.exists(png_filePath) and \
                os.path.dirname(plist_filePath) == os.path.dirname(png_filePath):
            gen_png_from_plist(plist_filePath, png_filePath)
        else:
            print("ERROR 请确保plist和png在同一个文件夹")
    else:
        print("ERROR 请使用绝对路径指定plist和png公共路径名称")
