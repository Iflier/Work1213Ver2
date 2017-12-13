# -*- coding:utf-8 -*-
"""
Dec:
Created on : 2017.12.12
Modified on : 2017.12.13
好奇怪，json无法序列化任何对象了？？？？？
还是无法解决json无法序列化对象的问题
Author: Iflier
"""

import os
import csv
import json
import hashlib
import os.path

import cv2


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
        print(os.path.dirname(__file__))
        img = cv2.imread(imgFilePath)
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
        cv2.imwrite(processedFilePath, img)
        # 返回文件名和人脸矩形框的坐标
        # print(loc)
        return imgFilePath.split('\\')[-1], loc

    def computerHash(self, filePath):
        pass
    

if __name__ == "__main__":
    processTools = imgProcess()
    processFileName = processTools.getRectangel("G:\\Feifei.jpg")
    print(processFileName)
