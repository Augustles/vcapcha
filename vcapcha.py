# coding=utf-8

from PIL import Image
import numpy as np
import os
from itertools import groupby
from operator import itemgetter


# from utils import (
#     COLOR_RGB_BLACK, COLOR_RGB_WHITE, COLOR_RGBA_BLACK, COLOR_RGBA_WHITE,
#     BORDER_LEFT, BORDER_TOP, BORDER_RIGHT, BORDER_BOTTOM,
#     png, path,
#     NORM_SIZE,
# )
COLOR_RGB_BLACK = (0, 0, 0)
COLOR_RGB_WHITE = (255, 255, 255)
COLOR_RGBA_BLACK = (0, 0, 0, 255)
COLOR_RGBA_WHITE = (255, 255, 255, 255)

BORDER_LEFT = 0
BORDER_TOP = 1
BORDER_RIGHT = 2
BORDER_BOTTOM = 3

png = 'png/'
path = 'deal/'

NORM_SIZE = 20
# 存放处理后的图片数据
if not os.path.exists(path):
    os.mkdir(path)


class Vcaptcha(object):

    def __init__(self, image):
        if isinstance(image, file) or isinstance(image, str) or isinstance(image, unicode):
            self._image = Image.open(image)
        else:
            raise Exception('File Error')

    def preprocess(self):
        # 获取验证码预处理结果: 返回二维list，一行表示一个child image
        # res = []

        store_path = path + self.name.split('.')[0]
        if not os.path.exists(store_path):
            os.mkdir(store_path)

        self._binary(n=127)

        child_images = self._cut_images()
        for i in range(len(child_images)):

            normalized_image = self._resize_to_norm(child_images[i])
            # normalized_image.show()
            normalized_image.save(store_path + '/%d.jpg' % i)
            # normalized_image.show()

            # self._captcha_to_string(normalized_image, save_as = '%d'%i)
            # res.append(self._captcha_to_list(normalized_image))
        # return res

    def _binary(self, n=127):
        """
        将图片进行二值化
        """
        # 有很多种算法，这里选择rgb加权平均值算法
        width, height = self._image.size
        for y in xrange(height):
            for x in xrange(width):
                r, g, b = self._image.getpixel((x, y))
                value = 0.299 * r + 0.587 * g + 0.114 * b
                # value就是灰度值，这里使用127作为阀值
                # 小于127的就认为是黑色也就是0 大于等于127的就是白色，也就是255
                if value < n:
                    self._image.putpixel((x, y), COLOR_RGB_BLACK)
                else:
                    self._image.putpixel((x, y), COLOR_RGB_WHITE)

    def _binary1(self, n=190):
        '''
        阀值
        '''
        im = self._image
        im = im.convert('L')
        im = im.point(lambda x: 255 if x > n else 0)

    # 8邻域, 小噪点
    def _ecp(self, n=6):
        frame = self._image.load()
        (w, h) = self._image.size
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
                    if count >= n:
                        frame[i, j] = 255
        return self._image

    # 洪水填充, 大噪点
    def _floodfill(self, way=4, mincount=8):
        frame = self._image.load()
        (w, h) = self._image.size
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

        return self._image

    # 颜色top
    def _top(self, flag='P',  n=10):
        self._image.convert(flag)
        his = self._image.histogram()
        values = {}
        for i in range(256):
            values[i] = his[i]
        # 排名前十的色彩, pix依据这里值进行判断
        for j, k in sorted(values.items(), key=itemgetter(1), reverse=True)[:n]:
            print j, k

    # 图片到x轴或y轴的投影，如果有数据（黑色像素点）值为1，否则为0
    def _get_projection_x(self):  # axis = 0: x轴, axis = 1: y轴
        # 初始化投影标记list
        p_x = [0 for _ in xrange(self._image.size[0])]
        width, height = self._image.size

        for x in xrange(width):
            for y in xrange(height):
                if self._image.getpixel((x, y)) == COLOR_RGB_BLACK:
                    p_x[x] = 1
                    break
        return p_x

    # 获取切割后的x轴坐标点，返回值为[初始位置，长度]的列表
    def _get_split_seq(self, projection_x):
        split_seq = []
        start_x = 0
        length = 0
        for pos_x, val in enumerate(projection_x):
            if val == 0 and length == 0:
                continue
            elif val == 0 and length != 0:
                split_seq.append([start_x, length])
                length = 0
            elif val == 1:
                if length == 0:
                    start_x = pos_x
                length += 1
            else:
                raise Exception('generating split sequence occurs error')
        # 循环结束时如果length不为0，说明还有一部分需要append
        if length != 0:
            split_seq.append([start_x, length])
        return split_seq

    def _is_joint(self, split_len):
        """
        以字符宽度统计值判断当前split_len是否是两个字符的长度
        返回True需要进一步进行滴水算法分割
        """
        return True if split_len >= 18 else False

    def _is_black(self, rgb):
        """
        : param rgb: tuple (r, g, b)
        """
        return True if rgb == COLOR_RGB_BLACK else False

    def _drop_fall(self, image):
        """
        对粘连两个字符的图片进行drop fall算法分割
        """
        # 1. 竖直投影统计
        width, height = image.size
        print "当前待切割图片的 width: %d, height: %d" % (width, height)
        hist_width = [0] * width
        for x in xrange(width):
            for y in xrange(height):
                if self._is_black(image.getpixel((x, y))):
                    hist_width[x] += 1

        print "当前的hist_width: %s" % str(hist_width)

        # 2. 找到极小值点
        start_x = self._get_start_x(hist_width)
        print "当前的起始点是: %d" % start_x

        # 3. 以这个极小值点作为起始滴落点,实施滴水算法
        start_route = []
        for y in range(height):
            start_route.append((0, y))

        end_route = self._get_end_route(image, start_x, height)
        filter_end_route = [max(list(k))
                            for _, k in groupby(end_route, lambda x: x[1])]
        # 两个字符的图片，首先得到的是左边那个字符
        img1 = self._do_split(image, start_route, filter_end_route)
        img1 = img1.crop((self._get_black_border(img1)))

        # 再得到最右边字符
        start_route = map(lambda x: (x[0] + 1, x[1]), filter_end_route)
        end_route = []
        for y in range(height):
            end_route.append((width - 1, y))
        img2 = self._do_split(image, start_route, end_route)
        img2 = img2.crop((self._get_black_border(img2)))

        return [img1, img2]

    def _get_start_x(self, hist_width):
        """
        根据待切割的图片的竖直投影统计hist_width，找到合适的滴水起始点
        hist_width的中间值，前后再取4个值，在这个范围内找最小值
        """
        mid = len(hist_width) / 2
        # 共9个值
        return mid - 4 + np.argmin(hist_width[mid - 4:mid + 5])

    def _get_end_route(self, image, start_x, height):
        """
        获得滴水的路径
        : param start_x: 滴水的起始x位置
        """
        left_limit = 0
        right_limit = image.size[0] - 1

        end_route = []
        print "当前的start_x: %d" % start_x
        cur_p = (start_x, 0)
        last_p = cur_p
        end_route.append(cur_p)

        while cur_p[1] < (height - 1):
            sum_n = 0
            maxW = 0  # max Z_j*W_j
            nextX = cur_p[0]
            nextY = cur_p[1]
            for i in range(1, 6):
                curW = self._get_nearby_pixel_val(
                    image, cur_p[0], cur_p[1], i) * (6 - i)
                sum_n += curW
                if maxW < curW:
                    maxW = curW

            # 如果全黑，需要看惯性
            if sum_n == 0:
                maxW = 4

            # 如果全白，则默认垂直下落
            if sum_n == 15:
                maxW = 6

            if maxW == 1:
                nextX = cur_p[0] - 1
                nextY = cur_p[1]
            elif maxW == 2:
                nextX = cur_p[0] + 1
                nextY = cur_p[1]
            elif maxW == 3:
                nextX = cur_p[0] + 1
                nextY = cur_p[1] + 1
            elif maxW == 5:
                nextX = cur_p[0] - 1
                nextY = cur_p[1] + 1
            elif maxW == 6:
                nextX = cur_p[0]
                nextY = cur_p[1] + 1
            elif maxW == 4:
                if nextX > cur_p[0]:  # 具有向右的惯性
                    nextX = cur_p[0] + 1
                    nextY = cur_p[1] + 1

                if nextX < cur_p[0]:
                    nextX = cur_p[0]
                    nextY = cur_p[1] + 1

                if sum_n == 0:
                    nextX = cur_p[0]
                    nextY = cur_p[1] + 1
            else:
                raise Exception("get a wrong maxW, pls check")

            # 如果出现重复运动
            if last_p[0] == nextX and last_p[1] == nextY:
                if nextX < cur_p[0]:
                    maxW = 5
                    nextX = cur_p[0] + 1
                    nextY = cur_p[1] + 1
                else:
                    maxW = 3
                    nextX = cur_p[0] - 1
                    nextY = cur_p[1] + 1

            last_p = cur_p

            if nextX > right_limit:
                nextX = right_limit
                nextY = cur_p[1] + 1

            if nextX < left_limit:
                nextX = left_limit
                nextY = cur_p[1] + 1

            cur_p = (nextX, nextY)
            end_route.append(cur_p)

        # 返回分割路径
        return end_route

    def _get_nearby_pixel_val(self, image, cx, cy, j):
        if j == 1:
            return 0 if self._is_black(image.getpixel((cx - 1, cy + 1))) else 1
        elif j == 2:
            return 0 if self._is_black(image.getpixel((cx, cy + 1))) else 1
        elif j == 3:
            return 0 if self._is_black(image.getpixel((cx + 1, cy + 1))) else 1
        elif j == 4:
            return 0 if self._is_black(image.getpixel((cx + 1, cy))) else 1
        elif j == 5:
            return 0 if self._is_black(image.getpixel((cx - 1, cy))) else 1
        else:
            raise Exception("what you request is out of nearby range")

    def _do_split(self, source_image, starts, filter_ends):
        """
        具体实行切割
        : param starts: 每一行的起始点 tuple of list
        : param ends: 每一行的终止点
        """
        left = starts[0][0]
        top = starts[0][1]
        right = filter_ends[0][0]
        bottom = filter_ends[0][1]

        for i in range(len(starts)):
            left = min(starts[i][0], left)
            top = min(starts[i][1], top)
            right = max(filter_ends[i][0], right)
            bottom = max(filter_ends[i][1], bottom)

        width = right - left + 1
        height = bottom - top + 1

        image = Image.new('RGB', (width, height), COLOR_RGB_WHITE)

        for i in range(height):
            start = starts[i]
            end = filter_ends[i]
            for x in range(start[0], end[0] + 1):
                if self._is_black(source_image.getpixel((x, start[1]))):
                    image.putpixel((x - left, start[1] - top), COLOR_RGB_BLACK)

        return image

    def _cut_images(self):
        """
        切割图像为单个字符块
        :return: list对象, 每个元素为一个单独字符的Image Object
        """
        # _image.size返回的是(width, height)
        split_seq = self._get_split_seq(self._get_projection_x())
        print split_seq

        # 切割图片
        croped_images = []
        height = self._image.size[1]

        for start_x, width in split_seq:
            # 同时去掉y轴上下多余的空白
            begin_row = 0
            end_row = height - 1
            for row in range(height):
                flag = True
                for col in range(start_x, start_x + width):
                    if self._image.getpixel((col, row)) == COLOR_RGB_BLACK:
                        flag = False
                        break
                if not flag:  # 如果在当前行找到了黑色像素点，就是起始行
                    begin_row = row
                    break
            for row in reversed(range(height)):
                flag = True
                for col in range(start_x, start_x + width):
                    if self._image.getpixel((col, row)) == COLOR_RGB_BLACK:
                        flag = False
                        break
                if not flag:
                    end_row = row
                    break
            croped_images.append(self._image.crop(
                (start_x, begin_row, start_x + width, end_row + 1)))

        # 没考虑一个source image出现多个粘连图片的情况
        need_drop_fall = False
        for idx, split_info in enumerate(split_seq):
            # split_info: (start_x, length)
            if self._is_joint(split_info[1]):
                need_drop_fall = True
                print "找到一张粘连图片: %d" % idx
                split_images = self._drop_fall(croped_images[idx])
                break
        if need_drop_fall:
            del croped_images[idx]
            croped_images.insert(idx, split_images[0])
            croped_images.insert(idx + 1, split_images[1])

        return croped_images

    def _get_black_border(self, image):
        """
        获取指定图像的内容边界坐标
        :param image: 图像 Image Object
        :return: 图像内容边界坐标tuple (left, top, right, bottom)
        """
        width, height = image.size
        max_x = max_y = 0
        min_x = width - 1
        min_y = height - 1
        for y in range(height):
            for x in range(width):
                if image.getpixel((x, y)) == COLOR_RGB_BLACK:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
        return min_x, min_y, max_x + 1, max_y + 1

    def _rotate_image(self, image):
        """
        将单个字符图片旋转到合适角度 (投影至X轴长度最小)
        :return: 旋转后的图像 (RGB)
        """
        image = image.convert('RGBA')
        optimisim_image = image
        for angle in range(-30, 31):
            image_copy = image.rotate(angle, expand=True)
            fff = Image.new('RGBA', image_copy.size, (255, ) * 4)
            out = Image.composite(image_copy, fff, image_copy)

            border_out = self._get_black_border(out)
            border_optimisim = self._get_black_border(optimisim_image)
            if border_out[BORDER_RIGHT] - border_out[BORDER_LEFT] + 1 < border_optimisim[BORDER_RIGHT] - border_optimisim[BORDER_LEFT] + 1:
                optimisim_image = out

        border = self._get_black_border(optimisim_image)
        optimisim_image = optimisim_image.crop((
            border[BORDER_LEFT],
            border[BORDER_TOP],
            border[BORDER_RIGHT],
            border[BORDER_BOTTOM]
        ))
        optimisim_image = optimisim_image.convert('RGB')
        return optimisim_image

    def _resize_to_norm(self, image):
        """
        将单个图像缩放至32x32像素标准图像
        :param image: 图像 (RGB)
        :return: 缩放后的Image Object
        """
        if image.size[0] > NORM_SIZE or image.size[1] > NORM_SIZE:
            image = image.resize((NORM_SIZE, NORM_SIZE))
        width, height = image.size
        new_image = Image.new('RGB', (NORM_SIZE, NORM_SIZE), COLOR_RGB_WHITE)
        offset = ((NORM_SIZE - width) / 2, (NORM_SIZE - height) / 2)
        new_image.paste(image, offset)
        return new_image

    def _captcha_to_list(self, image):
        """
        将验证码转换为数字编码
        :param image: 图像
        :return: 数字编码字符串
        """
        if image.size != (NORM_SIZE, NORM_SIZE):
            raise Exception("Image needs to normalize before to string")

        # 将pixel写到列表中
        data = [0] * (NORM_SIZE * NORM_SIZE)
        for y in range(0, NORM_SIZE):
            for x in range(0, NORM_SIZE):
                data[y * NORM_SIZE +
                     x] = 1 if image.getpixel((x, y)) == COLOR_RGB_BLACK else 0

        return data

    def _captcha_to_string(self, image, save_as):
        data = self._captcha_to_list(image)
        # 写到文件: data的数据类型必须是str(map转换)
        with open(save_as, 'w') as outfile:
            for row in xrange(NORM_SIZE):
                outfile.write(
                    ''.join(map(str, data[row * NORM_SIZE:(row + 1) * NORM_SIZE])) + '\n')

    # 图片x轴的投影，如果有数据（黑色像素点）值为1否则为0
    def _get_projection_x2(self):
        p_x = [0 for x in xrange(self._image.size[0])]
        for w in xrange(self._image.size[1]):
            for h in xrange(self._image.size[0]):
                if self._image.getpixel((h, w)) == 0:
                    p_x[h] = 1
        return p_x
    # 获取分割后的x轴坐标点
    # 返回值为[起始位置, 长度] 的列表

    def _get_split_seq2(self, projection_x):
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

    def _split_image2(self, split_seq=None):
        if split_seq is None:
            split_seq = self._get_split_seq2(self._get_projection_x2())
        length = len(split_seq)
        imgs = [[] for i in xrange(length)]
        res = []
        for w in xrange(self._image.size[1]):
            line = [self._image.getpixel((h, w)) for h in xrange(self._image.size[0])]
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


def main():
    pass

if __name__ == '__main__':
    main()
