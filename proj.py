# -*- coding:utf-8 -*-
"""
Dec: 尽管HTML页面上显示的图像被缩放了，但是保存的检测结果对应于原始图像大小
Created on : 2017.12.12
Modified on : 2017.12.13
json无法序列化对象了
优化访问静态文件方法
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
        # 目前有3种不同目的的post请求，分别为：上传图像、检测人脸和保存结果
        # print("In detect post: {0}".format(self.get_argument('pic', default=None)))
        if self.get_argument('detect', default=None):
            # 如果是触发检测图片的请求
            print("In detect: {0}".format(self.get_argument('detect', default=None)))
            global location
            # json 此时 不能 序列化对象了，所以才使用了global，尽管这样并不美好
            kwargs = dict()
            # 读取图片的路径。调用后返回文件名和框选区域的坐标
            fileName, loc = processTools.getRectangel(os.path.join('static',
                                                                   'img',
                                                                   'imgFiles',
                                                                   self.get_secure_cookie("filename").decode()
                                                                   )
                                                      )
            kwargs['filePath'] = os.path.join('img',
                                              'imgFilesProcessed',
                                              fileName
                                              )
            location = loc
            # print("Serialize: {0}".format(json.dumps(79)))
            self.render('headerPage.html', **kwargs)
        elif self.get_argument("save", default=None):
            # 如果是提交了保存的请求
            print("In save: {0}".format(self.get_argument("save", default=None)))
            kwargs = dict()
            if not os.path.exists(os.path.join(os.path.dirname(__file__),
                                               'savedResult')):
                os.mkdir(os.path.join(os.path.dirname(__file__), 'savedResult'))
            with open(os.path.join(os.path.dirname(__file__), "savedResult",
                                   'result.csv'),
                      'a+', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow([self.get_secure_cookie("filename").decode()] + [location])
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
                    kwargs["filePath"] = os.path.join('img', 'imgFiles',
                                                      filename)
                    self.set_secure_cookie("filename", filename)
                    # 可以在各个请求之间传递
                    print("Path: {0}".format(kwargs["filePath"]))
            self.render('headerPage.html', **kwargs)
        else:
            kwargs = dict()
            kwargs["filePath"] = None
            self.render("headerPage.html", **kwargs)
    
    def on_finish(self):
        print("Request finished.")


if __name__ == "__main__":
    PORT = 20001
    print("Bind to {0} port".format(PORT))
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.bind(PORT)
    http_server.start()
    tornado.ioloop.IOLoop().current().start()
