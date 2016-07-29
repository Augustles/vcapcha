# coding=utf-8

# 60~70%
import requests
from pcha import ecp, fff
from PIL import Image
from pytesseract import image_to_string
import os
import re

url = 'http://www.zhwsbs.gov.cn:9013/jsps/shfw/checkCode.jsp'

os.chdir('zhw3')


def vcode(fn):
    r = requests.get(url)
    with open(fn, 'wb') as f:
        f.writelines(r.content)
    im = Image.open(fn)
    sim = im
    im = im.convert('L')
    im = im.point(lambda x: 255 if x > 130 else 0)
    im = ecp(im, 7)
    im = fff(im, 4, 15)
    code = image_to_string(im, lang='zhw2', config='-psm 8')
    code = re.findall(r'[0-9a-zA-Z]', str(code))
    code = ''.join(code)
    if len(code) == 4:
        sim.save(code + '.png')
        return code
    else:
        return 0


while 1:
    code = vcode('zhw.png')
    if code:
        print code
        # break
