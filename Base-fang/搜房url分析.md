# 搜房网的url分析

1.获取所有城市的url链接。
    https://www.fang.com/SoufunFamily.htm
2.获取所有城市的新房的url链接。
    例：安庆：https://anqing.fang.com
    安庆新房：https://anqing.newhouse.fang.com/house/s/
2.获取所有城市的二手房的url链接。
    例：安庆：https://anqing.fang.com
    安庆二手：https://anqing.esf.fang.com/

北京是个例外：
    北京：https://bj.fang.com/
    新房：https://newhouse.fang.com/house/s/
    二手房：https://esf.fang.com/


二：分析网站结构
三：创建项目
scrapy startproject fang
scrapy gentspider fang.com

