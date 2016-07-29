# coding=utf-8


import time
import requests
import os
import re
from pcha import ecp, fff, top, rmbg, split_image
from PIL import Image, ImageEnhance, ImageFilter
import cv2
from pytesseract import image_to_string
from fabric.colors import green

path = '/qdky'
home = '/home/august/vcapcha/png/' + path
if not os.path.exists(home):
    os.mkdir(home)
os.chdir(home)

# url = 'http://www.e2go.com.cn/Home/LoginCheckCode/'
# url = 'http://www.bus365.com/imagevalidate/createValidateImage'
# url = 'http://www.jslw.gov.cn/verifyCode'
# url = 'http://www.hn96520.com/membercode.aspx'
# url = 'http://ptlogin.4399.com/ptlogin/captcha.do?captchaId=captchaReq011404b815f6235726'

url = 'http://ticket.qdjyjt.com/yzm.aspx'


def cnoise(fn):
    if fn.endswith('.png'):
        im = Image.open(fn)
        # im = rmbg(im, 20)
        im = im.convert('L')
        im = im.point(lambda x: 255 if x > 225 else 0)
        # im = im.crop((140, 70, 225, 90)).convert(
        # 'L').point(lambda x: 255 if x > 160 else 0)

        # im = cv2.imread(fn)
        # im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        # im = cv2.adaptiveThreshold(
        #     im, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 40)
        im = ecp(im, 8)
        # im = fff(im, 4, 20)
        # im = im.filter(ImageFilter.MedianFilter())
        # im.show()
        # return im
        nfn = fn[:-4] + '_g.png'
        print nfn
        # print(nfn)
        # # cv2.imwrite(nfn, im)
        im.save(nfn)


def getImage(url, i=None):
    print('Downloading {0} <== {1}'.format(i, url))
    r = requests.get(url)
    fn = '00' + str(i) + '.png'
    with open(fn, 'wb') as f:
        f.writelines(r.content)
    return fn


def printColor(fn):
    im = Image.open(fn)
    top(im)


def vcode(fn):
    im = cnoise(fn)
    try:
        # lang = 'e2go1'
        # cmd = 'tesseract {0} 1 -l {1} -psm 8'.format(fn, lang)
        # os.system(cmd)
        # code = image_to_string(im, lang='jslw', config='-psm 8')
        code = image_to_string(im, lang='gdcd', config='-psm 7')
        print(fn)
        print(code)
        info = re.findall(r'[0-9]', str(code))
        code = ''.join(info)
        if len(code.strip()) != 4:
            print(code)
            return 'Failed!!!, {0}'.format(fn)
        new = code + '.png'
        im.save(new)
        # os.rename(fn, new)
        return code
    except Exception as e:
        print(e)


def start(n, init=0):
    for x in xrange(init, n):
        fn = getImage(url, x)
        print fn
        # try:
        #     cnoise(fn)
        # except Exception as e:
        #     print(e)
        # print(vcode(fn))
        time.sleep(0.5)

# start(100)


def lstart(home):
    for x in os.listdir(home):
        if '_g' not in x:
            cnoise(x)
            # vcode(x)
            print(green(2333))

lstart(home)


def rmNonSource(home):
    for x in os.listdir(home):
        if '_g' in x:
            os.remove(x)
# rmNonSource(home)


# 生成box
# cmd = 'sh genBox.sh '.format(home, )
# 'tesseract -psm 8  -l gdcd code.font.exp0.tif code.font.exp0 batch.nochop makebox'

for x in os.listdir(home):
    if x.endswith('_g.png'):
        cmd = 'convert {0} -flatten -monochrome {1}.tif'.format(x, x[:-4])
        os.system(cmd)
cmd = 'tiffcp -c none *.tif target.tif'
os.system(cmd)
os.system('mv target.tif code.font.exp0.tif')
cmd = 'tesseract -psm 8 code.font.exp0.tif code.font.exp0 batch.nochop makebox'
os.system(cmd)

# 生成data
# 解压 combine_tessdata -u eng.traineddata eng/eng.
cmd = './genData.sh {0} {1}'.format('png' + path, home.split('/')[-1])
print(cmd)
# os.system(cmd)
