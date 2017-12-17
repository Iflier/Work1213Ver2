# Work1213Ver2
相较于第一个版本，做了如下改进:<br>
1.proj.py文件的书写更加的规范<br>
2.headerPage.html做了进一步的美化<br>
目前json无法序列化对象的问题还是没有解决 :-( <br>
# 2017.12.17<br>
json无法序列化numpy.ndarray类型的对象。使用list方法强制转换多数情况下由于没有合适的兼容类型，多数是失败的转换，解决方法是<br>
使用ndarray的tolist()方法转换为list类型<br>
改进：<br>
1.增加了对非人脸图像的处理<br>
2.增加了对不包含人脸的任务图像的处理，增强了容错性<br>
