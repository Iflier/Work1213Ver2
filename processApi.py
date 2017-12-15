# -*- coding:utf-8 -*-
"""
Dec:
Created on : 2017.12.12
Modified on : 2017.12.13
好奇怪，json无法序列化任何对象了？？？？？
还是无法解决json无法序列化对象的问题
Modified on: 2017.12.14
添加功能：如果文件已经存在，将不再保存
由于opencv的imread函数不能正确读取中文路径下的文件，因此，需要做些改动
Modified on : 2017.12.15
原来是这样：cv2既不能读取带有中文的路径指向文件，也不能写入中文路径下的图像文件
Author: Iflier
"""

import os
import csv
import json
import hashlib
import os.path

import cv2
import numpy as np


face_cascade = cv2.CascadeClassifier("D://opencv//sources//data//haarcascades//haarcascade_frontalface_default.xml")


class imgProcess():
    def __init__(self):
        self.face_cascade = face_cascade

    def getRectangel(self, imgFilePath):
        """
        docstring here
        :param self: 
        :param absFilePath: 将要被处理的文件的路径
        Return 被处理后的文件的保存路径字符串
        """
        loc = list()
        print("File path: {0}".format(imgFilePath))
        print(os.path.join(os.path.dirname(__file__), imgFilePath))
        img = cv2.imdecode(np.fromfile(imgFilePath, dtype=np.uint8, count=-1), cv2.IMREAD_UNCHANGED)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.03, 5, 0, (50, 50))
        # print(faces)
        # 在灰度图像上完成目标检测，矩形框绘制在原始图像上
        for x, y, w, h in faces:
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 238, 0), 2)
            loc.append([x, y, x + w, y + h])
        # 检查特定的文件路径是否存在
        if not os.path.exists(os.path.join(os.path.dirname(__file__),
                              'templates', 'imgFilesProcessed')):
            os.mkdir(os.path.join(os.path.dirname(__file__), 'templates',
                                  'imgFilesProcessed'))
        processedFilePath = os.path.join(os.path.dirname(__file__),
                                         'static', 'img',
                                         'imgFilesProcessed',
                                         imgFilePath.split('\\')[-1]
                                         )
        if not os.path.exists(processedFilePath):
            # 如果将要保存的文件不存在，才会保存
            ext = os.path.splitext(processedFilePath)[-1]  # 返回文件的扩展名
            cv2.imencode(ext, img)[-1].tofile(processedFilePath)
        # 返回文件名和人脸矩形框的坐标
        # print(loc)
        return imgFilePath.split('\\')[-1], loc

    def computeHash(self, filePath):
        md = hashlib.md5()
        with open(filePath, 'rb') as file:            
            md.update(file.read())
        mdValue = md.hexdigest()
    

if __name__ == "__main__":
    processTools = imgProcess()
    processFileName = processTools.getRectangel("G:\\Feifei.jpg")
    print(processFileName)
