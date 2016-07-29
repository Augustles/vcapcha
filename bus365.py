# coding=utf-8

# 66.7%
import os
import re
import requests
from pcha import ecp
from PIL import Image
from pytesseract import image_to_string

url = 'http://www.bus365.com/imagevalidate/createValidateImage'


def vcode(fn):
    r = requests.get(url)
    with open(fn, 'wb') as f:
        f.writelines(r.content)
    im = Image.open(fn)
    im = im.convert('L')
    im = im.point(lambda x: 255 if x > 140 else 0)
    im = ecp(im)
    try:
        code = image_to_string(im, lang='bus365', config='-psm 8')
        # print(code)
        info = re.findall(r'[0-9a-zA-Z]', str(code))
        code = ''.join(info)
        if len(code.strip()) != 4:
            return 'Failed!!!'
        return code
    except Exception as e:
        print(e)

print(vcode('bus365.png'))
