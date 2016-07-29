# coding=utf-8

from operator import itemgetter
from PIL import Image


def rmbg(im, cp=20, r=0):
    w, h = im.size
    for x in xrange(w):
        for y in xrange(h):
            pix = im.getpixel((x, y))
            if pix < (cp, cp, cp):
                im.putpixel((x, y), (255, 255, 255))
    return im


def top(im, flag='P', n=10):
    im = im.convert(flag)
    his = im.histogram()
    values = {}
    for i in range(256):
        values[i] = his[i]
    # 排名前十的色彩, pix依据这里值进行判断
    for j, k in sorted(values.items(), key=itemgetter(1), reverse=True)[:n]:
        print j, k


def ecp(im, dcount=6):
    frame = im.load()
    (w, h) = im.size
    for i in xrange(w):
        for j in xrange(h):
            if frame[i, j] != 255:
                count = 0
                try:
                    if frame[i, j - 1] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i, j + 1] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i - 1, j - 1] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i - 1, j] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i - 1, j + 1] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i + 1, j - 1] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i + 1, j] == 255:
                        count += 1
                except IndexError:
                    pass
                try:
                    if frame[i + 1, j + 1] == 255:
                        count += 1
                except IndexError:
                    pass
                if count >= dcount:
                    frame[i, j] = 255
    return im


def fff(im, way=4, mincount=8):
    frame = im.load()
    (w, h) = im.size
    points = []
    processedpoints = []
    global goodpoints
    goodpoints = []
    for x in xrange(w):
        for y in xrange(h):
            color = frame[x, y]
            if color == 255 or ((x, y) in processedpoints):
                continue
            processedpoints.append((x, y))

            points.append((x, y))

            # points.remove((x,y))
            for (x, y) in points:

                try:
                    if frame[x, y - 1] == color and (x, y - 1) not in points:
                        points.append((x, y - 1))
                except:
                    pass
                try:
                    if frame[x, y + 1] == color and (x, y + 1) not in points:
                        points.append((x, y + 1))
                except:
                    pass
                try:
                    if frame[x - 1, y] == color and (x - 1, y) not in points:
                        points.append((x - 1, y))
                except:
                    pass
                try:
                    if frame[x + 1, y] == color and (x + 1, y) not in points:
                        points.append((x + 1, y))
                except:
                    pass
                if way == 8:
                    try:
                        if frame[x - 1, y - 1] == color and (x - 1, y - 1) not in points:
                            points.append((x - 1, y - 1))
                    except:
                        pass
                    try:
                        if frame[x + 1, y - 1] == color and (x + 1, y - 1) not in points:
                            points.append((x + 1, y - 1))
                    except:
                        pass
                    try:
                        if frame[x - 1, y + 1] == color and (x - 1, y + 1) not in points:
                            points.append((x - 1, y + 1))
                    except:
                        pass
                    try:
                        if frame[x + 1, y + 1] == color and (x + 1, y + 1) not in points:
                            points.append((x + 1, y + 1))
                    except:
                        pass
            processedpoints.extend(points)
            # print color,len(points)
            # print points
            if 1 < len(points) < mincount:
                for (x, y) in points:
                    # print x,y
                    frame[x, y] = 255
            if len(points) > 16:
                goodpoints.extend(points)

            points = []

    return im


# 图片x轴的投影，如果有数据（黑色像素点）值为1否则为0
def get_projection_x(image):
    p_x = [0 for x in xrange(image.size[0])]
    for w in xrange(image.size[1]):
        for h in xrange(image.size[0]):
            if image.getpixel((h, w)) == 0:
                p_x[h] = 1
    return p_x

# 获取分割后的x轴坐标点
# 返回值为[起始位置, 长度] 的列表


def get_split_seq(projection_x):
    res = []
    for idx in xrange(len(projection_x) - 1):
        p1 = projection_x[idx]
        p2 = projection_x[idx + 1]
        if p1 == 1 and idx == 0:
            res.append([idx, 1])
        elif p1 == 0 and p2 == 0:
            continue
        elif p1 == 1 and p2 == 1:
            res[-1][1] += 1
        elif p1 == 0 and p2 == 1:
            res.append([idx + 1, 1])
        elif p1 == 1 and p2 == 0:
            continue
    return res

# 分割后的图片，x轴分割后，同时去掉y轴上线多余的空白


def split_image(image, split_seq=None):
    if split_seq is None:
        split_seq = get_split_seq(get_projection_x(image))
    length = len(split_seq)
    imgs = [[] for i in xrange(length)]
    res = []
    for w in xrange(image.size[1]):
        line = [image.getpixel((h, w)) for h in xrange(image.size[0])]
        for idx in xrange(length):
            pos = split_seq[idx][0]
            llen = split_seq[idx][1]
            l = line[pos:pos + llen]
            imgs[idx].append(l)
    for idx in xrange(length):
        datas = []
        height = 0
        for data in imgs[idx]:
            flag = False
            for d in data:
                if d == 0:
                    flag = True
            if flag == True:
                height += 1
                datas += data
        child_img = Image.new('L', (split_seq[idx][1], height))
        child_img.putdata(datas)
        # child_img.save(str(idx) + '.png')
        res.append(child_img)
    return res
