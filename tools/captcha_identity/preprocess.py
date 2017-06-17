# -*- coding: utf-8 -*-
'''
Created on 2017年5月10日

@author: chenyitao
'''

from PIL import Image
from libsvm.svmutil import *
import os


class CaptchaIdentity(object):
    
    def __init__(self):
        pass
    
    @staticmethod
    def get_bin_table():
        threshold = 80
        table = [0 if i < threshold else 1 for i in range(256)]
        return table

    @staticmethod
    def to_grey(img):
        img_grey = img.convert('L')
        table = CaptchaIdentity.get_bin_table()
        out = img_grey.point(table, '1')
        return out
 
    @staticmethod
    def spiltimg(img, chr_num, left, top, bottom, width, space):
        child_img_list = []
        for index in range(chr_num):
            x = left + index * (width + space)  # 见原理图
            y = top
            child_img = img.crop((x, y, x + width, img.height - bottom))
            child_img_list.append(child_img)
        return child_img_list
 
    @staticmethod
    def split_img(captcha_filename, chr_num, left, top, bottom, width, space):
        filenames = []
        new_img = CaptchaIdentity.to_grey(Image.open(captcha_filename))
        childs = CaptchaIdentity.spiltimg(new_img, chr_num, left, top, bottom, width, space)
        if '/' in captcha_filename:
            name = captcha_filename.split('/')[-1].split('.')[0]
        else:
            name = captcha_filename.split('.')[0]
        for i, c in enumerate(childs):
            _filename = './tmp/%s_' % name + str(i) + '.jpeg'
            filenames.append(_filename)
            c.save(_filename)
        return filenames

    @staticmethod
    def get_feature(img):
        width, height = img.size
        pixel_cnt_list = []
        for y in range(height):
            pix_cnt_x = 0
            for x in range(width):
                if img.getpixel((x, y)) <= 100:  # 黑色点
                    pix_cnt_x += 1
            pixel_cnt_list.append(pix_cnt_x)
        for x in range(width):
            pix_cnt_y = 0
            for y in range(height):
                if img.getpixel((x, y)) <= 100:  # 黑色点
                    pix_cnt_y += 1
            pixel_cnt_list.append(pix_cnt_y)
        return pixel_cnt_list

    @staticmethod
    def captcha_identity(captcha_filename, chr_num, left, top, bottom, width, space, model_file='svm_model_file'):
        childs = CaptchaIdentity.split_img(captcha_filename, chr_num, left, top, bottom, width, space)
        line = ''
        for fn in childs:
            line += '-1 '
            img = Image.open(fn)
            feature = CaptchaIdentity.get_feature(img)
            for j in range(1, len(feature) + 1):
                line += "%d:%d " % (j, feature[j - 1])
            line += "\n"
        else:
            with open('feature_tmp.txt', 'w') as f:
                f.write(line)
        yt, xt = svm_read_problem('feature_tmp.txt')
        model = svm_load_model(model_file)
        p_label, _, _ = svm_predict(yt, xt, model)  # p_label即为识别的结果
        cnt = 0
        results = []
        result = ''
        for item in p_label:  # item:float
            if int(item) >= 97:
                result += chr(int(item))
            else:
                result += str(int(item))
            cnt += 1
            if cnt % 4 == 0:
                results.append(result)
                result = ''
        return results



# 判断像素点是黑点还是白点
def getflag(img, x, y):
    tmp_pixel = img.getpixel((x, y))
    return 0 if tmp_pixel > 288 else 1


# 黑点个数
def sum_9_region(img, x, y):
    width = img.width
    height = img.height
    flag = getflag(img, x, y)
    # 如果当前点为白色区域,则不统计邻域值
    if flag == 0:
        return 0
    # 如果是黑点
    total = None
    if y == 0:  # 第一行
        if x == 0:  # 左上顶点,4邻域
            # 中心点旁边3个点
            total = getflag(img, x, y + 1) + getflag(img, x + 1, y) + getflag(img, x + 1, y + 1)
        elif x == width - 1:  # 右上顶点
            total = getflag(img, x, y + 1) + getflag(img, x - 1, y) + getflag(img, x - 1, y + 1)
        else:  # 最上非顶点,6邻域
            total = getflag(img, x - 1, y) + getflag(img, x - 1, y + 1) + getflag(img, x, y + 1) \
                    + getflag(img, x + 1, y) \
                    + getflag(img, x + 1, y + 1)
    elif y == height - 1:  # 最下面一行
        if x == 0:  # 左下顶点
            # 中心点旁边3个点
            total = getflag(img, x + 1, y) + getflag(img, x + 1, y - 1) + getflag(img, x, y - 1)
        elif x == width - 1:  # 右下顶点
            total = getflag(img, x, y - 1) + getflag(img, x - 1, y) + getflag(img, x - 1, y - 1)
        else:  # 最下非顶点,6邻域
            total = getflag(img, x - 1, y) + getflag(img, x + 1, y) + getflag(img, x, y - 1) + getflag(img, x - 1, y - 1) + getflag(img, x + 1, y - 1)
    else:  # y不在边界
        if x == 0:  # 左边非顶点
            total = getflag(img, x, y - 1) + getflag(img, x, y + 1) + getflag(img, x + 1, y - 1) + getflag(img, x + 1, y) + getflag(img, x + 1, y + 1)
        elif x == width - 1:  # 右边非顶点
            total = getflag(img, x, y - 1) + getflag(img, x, y + 1) + getflag(img, x - 1, y - 1) + getflag(img, x - 1, y) + getflag(img, x - 1, y + 1)
        else:  # 具备9领域条件的
            total = getflag(img, x - 1, y - 1) + getflag(img, x - 1, y) + getflag(img, x - 1, y + 1) + getflag(img, x, y - 1) \
                    + getflag(img, x, y + 1) + getflag(img, x + 1, y - 1) + getflag(img, x + 1, y) + getflag(img, x + 1, y + 1)
    return total
    

def to36(n):
    loop = '0123456789abcdefghijklmnopqrstuvwxyz'
    a = []
    while n != 0:
        a.append(loop[n % 36])
        n /= 36
    a.reverse()
    out = ''.join(a)
    return out


# 分割图片
def spiltimg(img, l, t, b, w, s):
    # 按照图片的特点,进行切割,这个要根据具体的验证码来进行工作. # 见原理图
    # :param img:
    # :return:
    child_img_list = []
    for index in range(4):
        x = l + index * (w + s)  # 见原理图
        y = t
        child_img = img.crop((x, y, x + w, img.height - b))
        child_img_list.append(child_img)
    return child_img_list

def greyimg(image):
    width = image.width
    height = image.height
    box = (0, 0, width, height)
    imgnew = image.crop(box)
    for i in range(0, height):
        for j in range(0, width):
            num = sum_9_region(image, j, i)
            if num < 2:
                imgnew.putpixel((j, i), 255)  # 设置为白色
            else:
                imgnew.putpixel((j, i), 0)  # 设置为黑色
    return imgnew


def get_feature(img):
    # 获取指定图片的特征值,
    # 1. 按照每排的像素点,高度为12,则有12个维度,然后为8列,总共20个维度
    # :return:一个维度为20（高度）的列表
    width, height = img.size
    pixel_cnt_list = []
    for y in range(height):
        pix_cnt_x = 0
        for x in range(width):
            if img.getpixel((x, y)) <= 100:  # 黑色点
                pix_cnt_x += 1
        pixel_cnt_list.append(pix_cnt_x)
    for x in range(width):
        pix_cnt_y = 0
        for y in range(height):
            if img.getpixel((x, y)) <= 100:  # 黑色点
                pix_cnt_y += 1
        pixel_cnt_list.append(pix_cnt_y)
    return pixel_cnt_list


def train(filename, merge_pic_path):
    if os.path.exists(filename):
        os.remove(filename)
    result = open(filename, 'a')
    for f in os.listdir(merge_pic_path):
        if f != '.DS_Store' and f != 'src' and os.path.isdir(merge_pic_path + f):
            for img in os.listdir(merge_pic_path + f):
                if img.endswith(".jpeg"):
                    pic = Image.open(merge_pic_path + f + "/" + img)
                    pixel_cnt_list = get_feature(pic)
                    try:
                        if ord(f) >= 97:
                            line = str(ord(f)) + " "
                        else:
                            line = f + " "
                        for i in range(1, len(pixel_cnt_list) + 1):
                            line += "%d:%d " % (i, pixel_cnt_list[i - 1])
                        result.write(line + "\n")
                    except Exception, e:
                        print(e)
    result.close()


def train_new(filename, path_new):
    if os.path.exists(filename):
        os.remove(filename)
    result_new = open(filename, 'a')
    for f in os.listdir(path_new):
        if f != '.DS_Store' and f.endswith(".jpeg"):
            pic = Image.open(path_new + f)
            pixel_cnt_list = get_feature(pic)
            # if ord(f) >= 97:
            #     line = str(ord(f)) + " "
            # else:
            line = "0 "
            for i in range(1, len(pixel_cnt_list) + 1):
                line += "%d:%d " % (i, pixel_cnt_list[i - 1])
            result_new.write(line + "\n")
    result_new.close()


# 模型训练
def train_svm_model(filename):
    y, x = svm_read_problem(filename)
    model = svm_train(y, x)
    svm_save_model("svm_model_file", model)
 
 
# 使用测{"platform": "cheok", "url": "http://www.cheok.com/car/cp_1", "row_key": "f28c6a2d65105fddb08b9500df1db7ef", "feature": "cheok.homepage",  "headers": {"Referer": "http://www.cheok.com"}}试集测试模型
def svm_model_test(filename):
    yt, xt = svm_read_problem(filename)
    model = svm_load_model("svm_model_file")
    p_label, p_acc, p_val = svm_predict(yt, xt, model)  # p_label即为识别的结果
    cnt = 0
    results = []
    result = ''
    for item in p_label:  # item:float
        if int(item) >= 97:
            result += chr(int(item))
        else:
            result += str(int(item))
        cnt += 1
        if cnt % 4 == 0:
            results.append(result)
            result = ''
    return results


def split_img():
    cnt = 1
    while cnt < 101:
        pic = Image.open('./captchas/%d.jpeg' % cnt)
        pic = CaptchaIdentity.to_grey(pic)
        pic.save('./captchas/new/%d.jpeg' % cnt)
        pic = Image.open('./captchas/new/%d.jpeg' % cnt)
        newpic = greyimg(pic)
        childs = spiltimg(newpic, l=12, t=8, b=2, w=12, s=3)
        count = 0
        for c in childs:
            c.save('./captchas/new/%d_' % cnt + str(count) + '.jpeg')
            count += 1
        cnt += 1

def main():
#     pic = Image.open('./captchas/new/2/81_1.jpeg')
#     x = get_feature(pic)
#     train('./captchas/new/features.txt', './captchas/new/')
#     train_svm_model('./captchas/new/features.txt')

#     svm_model_test('./captchas/new/features.txt')
#     print(svm_model_test('./2rz4.txt'))
    correct = 0
    path = './captchas/test3/'
    for f in os.listdir(path):
        if f != '.DS_Store' and f.endswith(".jpeg"):
            real = f.split('.')[0]
            predict = ''.join(CaptchaIdentity.captcha_identity(path + f, 4, 12, 8, 2, 12, 3)) 
            print(real, predict)
            if real == predict:
                correct += 1
            os.rename(path + f, path + predict + '.jpeg')
    print(correct / 100.0)


#     cnt = 1
#     while cnt < 101:
#         for i in range(4):
#             pic = Image.open('./captchas/new/%d_' % cnt + str(i) + '.jpeg')
#             pic.save('./captchas/new/xxx%d_' % cnt + str(i) + '.jpeg')
#         cnt += 1
                

if __name__ == '__main__':
    main()
    print('Done')
