# coding=utf-8

# 76.7%
import os
import re
import requests
from pcha import ecp, rmbg
from PIL import Image
from pytesseract import image_to_string

url = 'http://www.jslw.gov.cn/verifyCode'


def vcode(fn):
    r = requests.get(url)
    with open(fn, 'wb') as f:
        f.writelines(r.content)
    im = Image.open(fn)
    im = rmbg(im, 20)
    im = im.convert('L')
    im = im.point(lambda x: 255 if x > 220 else 0)
    im = ecp(im)
    try:
        code = image_to_string(im, lang='jslw', config='-psm 8')
        # print(code)
        info = re.findall(r'[0-9a-zA-Z]', str(code))
        code = ''.join(info)
        if len(code.strip()) != 4:
            return 'Failed!!!'
        return code
    except Exception as e:
        print(e)

print(vcode('jslw.png'))
