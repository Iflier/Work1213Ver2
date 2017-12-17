# -*- coding:utf-8 -*-
"""
Dec: 尽管HTML页面上显示的图像被缩放了，但是保存的检测结果对应于原始图像大小
Created on : 2017.12.12
Modified on : 2017.12.13
json无法序列化numpy.ndarray对象。
优化访问静态文件方法
Modified on : 2017.12.17
直接使用list强制转换(ndarray)是不可以的，
因为转换前与转换后的类型多数情况下是不能对应到Python的类型，
因此使用ndarray的tolist()方法，进行类型转换
增强容错性：对于非人脸或者不包含人脸的图像也能正确返回
如果没有检测到人脸矩形，它不会被进一步地保存到imgFilesProcessed文件夹中
Author: Iflier
"""
import os
import csv
import json
import os.path
import argparse

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.web import url

from processApi import imgProcess


processTools = imgProcess()


class Application(tornado.web.Application):    
    def __init__(self):
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), 'static'),
            "template_path": os.path.join(os.path.dirname(__file__), 'templates'),
            "xsrf_cookies": True,
            "debug": True,  # 生产环境下，记得改回来
            "cookie_secret": "eb70ecb5-4b67-47fb-b4f0-201f63094786",
            "startic_url_prefix": "/static/"
        }
        handlers = [
            url(r'/', EnterHandler, name='enterPoint'),
            url(r"/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path']))
            # 暂时还不清楚为什么要写这个，如果不，图片无法显示 :-(。研究了半天还是不明白
        ]
        tornado.web.Application.__init__(self, handlers=handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    """Handlers的基类"""
    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('404.html')
        elif status_code == 500:
            self.render('500.html')
        else:
            self.write("""<html>
                            <body>
                                <h1 style="color: blue;">Error: {0}</h1>
                            </body>
                          </html>""".format(status_code)
                       )


class EnterHandler(BaseHandler):
    """入口点"""
    def get(self):
        kwargs = dict()
        kwargs["filePath"] = None
        self.render("headerPage.html", **kwargs)
    
    def post(self):
        """目前有3种不同目的的post请求，分别为：上传图像、检测人脸和保存结果。
        不同的POST请求，返回的页面是一样的，关键在于更改了filePath参数指向的路径
        """
        print("In detect post: {0}".format(self.get_argument('pic', default=None)))
        if self.get_argument('detect', default=None):
            # 如果是触发检测图片的请求
            kwargs = dict()
            print("In detect: {0}".format(self.get_argument('detect', default=None)))
            # 读取图片的路径。调用后返回文件名和框选区域的坐标
            fileName, loc = processTools.getRectangel(os.path.join('static',
                                                                   'img',
                                                                   'imgFiles',
                                                                   self.get_secure_cookie("filename").decode()
                                                                   )
                                                      )
            if isinstance(loc, type(None)):
                # 如果没有检测到人脸，返回原文件的路径.filePath是相对于static目录的一个相对路径
                self.set_secure_cookie('loc', json.dumps(None))  # 不同类型的loc区别对待
                kwargs['filePath'] = os.path.join('img',
                                                  'imgFiles',
                                                  fileName
                                                  )
            else:
                # 把坐标保存到cookie中
                self.set_secure_cookie('loc', json.dumps(loc.tolist()))
                kwargs['filePath'] = os.path.join('img',
                                                  'imgFilesProcessed',
                                                  fileName
                                                  )
            print("Cookie filename: {0}".format(self.get_secure_cookie("filename").decode()))
            self.render('headerPage.html', **kwargs)
        elif self.get_argument("save", default=None):
            # 如果是提交了保存检测结果的请求
            print("In save: {0}".format(self.get_argument("save", default=None)))
            kwargs = dict()
            location = json.loads(self.get_secure_cookie('loc').decode())
            # type = list或者None。没有进一步还原loc类型是因为，保存到文件的时候还是需要被序列化:-)
            if not os.path.exists(os.path.join(os.path.dirname(__file__),
                                               'savedResult')):
                os.mkdir(os.path.join(os.path.dirname(__file__), 'savedResult'))
            with open(os.path.join(os.path.dirname(__file__), "savedResult",
                                   'result.csv'),
                      'a+', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow([self.get_secure_cookie("filename").decode()] + [location])
            if isinstance(location, type(None)):
                # 如果图像中不包含人脸，返回上传的图像保存的路径
                kwargs['filePath'] = os.path.join('img',
                                                'imgFiles',
                                                self.get_secure_cookie("filename").decode()
                                                )
            else:
                # 否则返回处理后的图像的路径
                kwargs['filePath'] = os.path.join('img',
                                                'imgFilesProcessed',
                                                self.get_secure_cookie("filename").decode()
                                                )
                # 更改了图片的路径，指向检测后保存的结果图像的路径
            self.render('headerPage.html', **kwargs)
        elif self.get_argument("upload", default=None):
            # 通过input元素的属性值区分不同的请求目的
            print("In upload: {0}".format(self.get_argument("upload")))
            kwargs = dict()
            # 检查用于保存上传文件的目录是否存在
            if not os.path.exists(os.path.join(os.path.dirname(__file__),
                                  'templates', 'imgFiles')):
                os.mkdir(os.path.join(os.path.dirname(__file__), 'templates',
                                      'imgFiles'))
            # fileMetas = self.request.files.get('pic', None)
            # print("Type of : {0}".format(self.request.files))
            """
            这个对象包含了上传文件的16进制格式的内容，通过body键获取
            内容类型，通过content_type键获取
            上传的文件的名称，通过filename获取
            """
            for _, files in self.request.files.items():
                for info in files:
                    filename, contentType = info['filename'], info['content_type']
                    # 保存提交的图片到本地
                    with open(os.path.join('static', 'img', 'imgFiles',
                                           filename), 'wb') as file:
                        file.write(info['body'])
                    kwargs["filePath"] = os.path.join('img', 'imgFiles', filename)
                    # filePath保存的路径是相对于static目录的
                    self.set_secure_cookie("filename", filename)
            self.render('headerPage.html', **kwargs)
        else:
            kwargs = dict()
            kwargs["filePath"] = None
            self.render("headerPage.html", **kwargs)
    
    def on_finish(self):
        # 添加一些清理工作，如关闭游标，数据库等
        print("Request finished.")


if __name__ == "__main__":
    PORT = 20001
    print("Bind to {0} port".format(PORT))
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.bind(PORT)
    http_server.start()
    tornado.ioloop.IOLoop().current().start()
