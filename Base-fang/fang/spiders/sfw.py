# -*- coding: utf-8 -*-
import scrapy
import re
from fang.items import NewHouseItem,ESFHouseItem
class SfwSpider(scrapy.Spider):
    name = 'sfw'
    allowed_domains = ['fang.com']
    start_urls = ['https://www.fang.com/SoufunFamily.htm']

    def parse(self, response):
        # 获取所有的tr
        trs = response.xpath("//div[@class='outCont']//tr")
        provinces = None
        # 取出td
        for tr in trs:
            #取出不带有class属性的td
            tds = tr.xpath(".//td[not(@class)]")
            # 取到省份td：
            provinces_td = tds[0]
            provinces_text = provinces_td.xpath(".//text()").get()
            provinces_text = re.sub(r'\s',"",provinces_text)
            if provinces_text:
                provinces = provinces_text
            # 外国的房子就不要了
            if provinces=='其它':
                continue
            city_td = tds[1]
            # 获取所有a标签
            city_links = city_td.xpath(".//a")
            #取出url 和城市名
            for city_link in city_links:
                city = city_link.xpath(".//text()").get()
                city_url = city_link.xpath(".//@href").get()
                url_module = city_url.split('.')
                scheme = url_module[0]
                domain = url_module[1]
                com = url_module[2]
                print(scheme,domain,com)
                # 单独给北京构造链接
                newhouse_url = None
                esf_url = None
                if city == '北京':
                    newhouse_url = 'https://newhouse.fang.com/house/s/'
                    esf_url = 'https://esf.fang.com/?ctm=1.bj.xf_search.head.104'
                else:
                    # 构建每个城市的新房链接
                    newhouse_url = scheme + '.newhouse.'+domain+'.'+com+'house/s/'
                    #构建每个城市的二手房链接
                    esf_url = scheme+'.esf.'+domain+'.'+com+''
                # 发送请求 解析新房的url 里下想要的数据
                yield scrapy.Request(url=newhouse_url,callback=self.parse_newhouse,meta={"info":(provinces,city)})
                # 发送请求 解析二手房房的url 里下想要的数据
                yield scrapy.Request(url=esf_url, callback=self.parse_esf, meta={"info": (provinces, city)})
    #解析新房 得到数据
    def parse_newhouse(self,response):
        provinces,city = response.meta.get("info")
        #实例化一个items
        item = NewHouseItem()
        #得到所有的房源列表
        lis = response.xpath('//div[contains(@class,"nl_con")]/ul/li')
        for li in lis:
            #去广告的li标签，
            if not li.xpath('.//div[@class="nlcd_name"]'):
                continue
            # 房名
            item["name"] = li.xpath('.//div[@class="nlcd_name"]/a/text()').get().strip()
            house_type_text = li.xpath(".//div[contains(@class,'house_type')]/a//text()").getall()
            # 几居
            item["rooms"] = list(filter(lambda x: x.endswith('居'or '以上'),house_type_text))
            area = "".join(li.xpath('.//div[contains(@class,"house_type")]/text()').getall())
            # 面积
            item["area"] = re.sub(r"\s|/|－","",area)
            # 地区
            item["address"] = li.xpath('.//div[@class="address"]/a/@title').get()
            # 行政区
            district = "".join(li.xpath('.//div[@class="address"]/a//text()').getall())
            # 没有行政
            if "[" not in  district:
                item["district"] = None
            else:
                item["district"] = re.search(r".*\[(.+)\].*", district).group(1)
            # 销售状态
            item["sale"] = li.xpath('.//div[contains(@class,"fangyuan")]/span/text()').get()
            # price
            price = "".join(li.xpath(".//div[@class='nhouse_price']//text()").getall())
            item["price"] = re.sub(r'\s|"广告"',"",price)
            # origin_url
            item["origin_url"] = response.urljoin(li.xpath('.//div[@class="nlcd_name"]/a/@href').get())
            item["provinces"] = provinces
            item["city"] = city
            yield item
            next_url = response.xpath("//div[@class='page']//a[@class='next']/@href").get()
            if next_url:
                yield scrapy.Request(url=response.urljoin(next_url),callback=self.parse_newhouse,meta={"info":(provinces,city)})


    def parse_esf(self,response):
        print(response.url)
        provinces, city = response.meta.get("info")
        item = ESFHouseItem(provinces=provinces,city=city)
        #获取所有的dls
        dls = response.xpath('//div[contains(@class,"shop_list")]/dl')
        for dl in dls:
            item["name"] = dl.xpath('.//p[@class="add_shop"]/a/@title').get()
            infos = dl.xpath('.//p[@class="tel_shop"]/text()').getall()
            infos = list(map(lambda x:re.sub(r"\s","",x),infos))
            for info in infos:
                print(info)
                if  '室' in info:
                    item["rooms"] = info
                elif  '层' in info:
                    item["floor"] = info
                elif '向' in info:
                    item["toward"] = info
                elif  '㎡' in info:
                    item['area'] = info
                else:
                    item["year"] = info.replace("建筑年代","")
            #地址
            item['address'] = dl.xpath('.//p[@class="add_shop"]/span/text()').get()
            #总价格
            price_s = dl.xpath('.//dd[@class="price_right"]/span/b/text()').get()
            price_w = dl.xpath('.//dd[@class="price_right"]/span[1]/text()').get()
            if price_s and price_w:
                item['price'] = ''.join(price_s)+ ''.join(price_w)
            else:
                item['price'] = ' '
            #
            #多少一平米
            item['unit'] = dl.xpath('.//dd[@class="price_right"]/span[2]/text()').get()
            # origin_url
            item['origin_url'] = response.urljoin(dl.xpath('.//h4/a/@href').get())
            print(item,response.url,city)
            yield  item
        next_url = response.xpath('//div[@class="page_al"]/p[1]/a/@href').get()
        if  next_url:
            yield  scrapy.Request(url=response.urljoin(next_url),callback=self.parse_esf,meta={"info":(provinces,city)})
