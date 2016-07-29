# coding=utf-8

# 80~90%
import requests
from pcha import ecp, fff
from PIL import Image
from pytesseract import image_to_string
import os
import re

url = 'http://ticket.qdjyjt.com/yzm.aspx'

def vcode(fn):
    r = requests.get(url)
    with open(fn, 'wb') as f:
        f.writelines(r.content)
    im = Image.open(fn)
    sim = im
    im = im.convert('L')
    im = im.point(lambda x: 255 if x > 225 else 0)
    im = ecp(im, 8)
    code = image_to_string(im, lang='qdky', config='-psm 8')
    code = re.findall(r'[0-9a-zA-Z]', str(code))
    code = ''.join(code)
    if len(code) == 4:
        sim.save(code + '.png')
        return code
    else:
        return 0

while 1:
    code = vcode('qdky.png')
    if code:
        print code
        break
