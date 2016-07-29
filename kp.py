# coding=utf-8

import requests
from pcha import ecp
from PIL import Image
from pytesseract import image_to_string

url = 'http://96096kp.com/ValidateCode.aspx'


def vcode(fn):
    r = requests.get(url)
    with open(fn, 'wb') as f:
        f.writelines(r.content)
    im = Image.open(fn)
    im = im.convert('L')
    im = im.point(lambda x: 255 if x > 140 else 0)
    im = ecp(im)
    code = image_to_string(im, lang='kp', config='-psm 8')
    return code

print(vcode('96096kp.png'))
