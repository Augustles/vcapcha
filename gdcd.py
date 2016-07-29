# coding=utf-8

# 60~80%
import requests
from pcha import ecp, fff
from PIL import Image
from pytesseract import image_to_string
import os
import re

url = 'http://ticket.gdcd.gov.cn/BaseApp/ValidateCodeHandler.ashx'

os.chdir('gdcd2')


def vcode(fn):
    r = requests.get(url)
    with open(fn, 'wb') as f:
        f.writelines(r.content)
    im = Image.open(fn)
    sim = im
    im = im.convert('L')
    im = im.point(lambda x: 255 if x > 160 else 0)
    im = ecp(im, 7)
    im = fff(im, 4, 15)
    code = image_to_string(im, lang='gdcd', config='-psm 8')
    code = re.findall(r'[0-9a-fA-F]', str(code))
    code = ''.join(code)
    letter = [('l', '1'), ('o', '0'), ('O', '0'), ('L', '1'), ('s', '5'), ('S', '5'), ('B', '8'), ('A', '4')]
    if len(code) == 4:
        for x in letter:
            code = code.replace(x[0], x[1])
        sim.save(code + '.png')
        return code
    else:
        return 0


while 1:
    code = vcode('gdcd.png')
    if code:
        print code
        # break
