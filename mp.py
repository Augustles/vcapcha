# coding=utf-8

# 96.8%
import requests
from pcha import ecp
from PIL import Image
from pytesseract import image_to_string
import re

url = 'http://www.mp0769.com/checkcode.asp'


def vcode(fn):
    r = requests.get(url)
    with open(fn, 'wb') as f:
        f.writelines(r.content)
    im = Image.open(fn)
    im = im.convert('L')
    im = im.point(lambda x: 255 if x > 190 else 0)
    im = ecp(im, 7)
    code = image_to_string(im, lang='mp', config='-psm 7')
    info = re.findall(r'[0-9]', str(code))
    code = ''.join(info)
    if len(code.strip()) == 4:
        return code
    else:
        return 'Fail'

print(vcode('mp.png'))
