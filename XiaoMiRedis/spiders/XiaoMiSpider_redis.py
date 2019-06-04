import scrapy
import redis
from urllib import parse

from scrapy_redis.spiders import RedisSpider

from XiaoMiRedis.items import XiaomiredisItem
# 定义全局变量设定默认值
default_value = "null"
"""
此爬虫根据提供的关键字采集小米应用商城相关字段的信息

"""
# 定义爬虫类
class XiaoMiSpider_redis(RedisSpider):
    name = "XiaoMiSpider_redis"     # 爬虫命名
    redis_key = "XiaoMiSpider_redis:start_urls"     # 启动爬虫的命令
    # 初始化方法
    def __init__(self):
        self.base_url = "http://app.mi.com/search?keywords={0}"     # 与获取的关键字构造出初始请求
        self.show_all = "http://app.mi.com{}"   # 显示所有
        self.next_page = "http://app.mi.com/searchAll{}"    # 构造下一页的请求
    # 构造初始请求
    def start_requests(self):
        """
        从redis数据库获取关键字构造初始请求
        :return:
        """
        connect = redis.Redis(host='127.0.0.1',port=6379,db=4, password='pengfeiQDS')  # 获取redis的链接
        keyword_total = connect.dbsize()    # 获取关键字的总数
        # 遍历获取每一个关键字
        #for index in range(keyword_total):  # 测试时代码
        for index in range(340001,400001):
            # 使用get方法获取关键字
            keyword = connect.get(str(index)).decode('utf-8')
            # 关键字与base_url拼接获取搜索页面
            target_url = self.base_url.format(parse.quote(keyword))
            # 将url加入到采集队列中
            yield scrapy.Request(url=target_url,callback=self.get_page,meta={'keyword':keyword})
    # 解析搜索页面
    def get_page(self,response):
        if response.status == 200:
            # 获取手机的页面，作为是否有显示全部的判断依据
            phone_page = response.xpath('//div[@class="applist-wrap"][1]/ul/li').extract_first()
            # 获取pad的页面，作为是否有显示全部的判断依据
            pad_page = response.xpath('//div[@class="applist-wrap"][2]/ul/li').extract_first()
            # 获取显示所有的链接
            show_all_phone_url = response.xpath('//div[@class="applist-wrap"][1]/div/a/@href').extract_first()
            show_all_pad_url = response.xpath('//div[@class="applist-wrap"][2]/div/a/@href').extract_first()
            # 判断手机端是否有匹配结果
            if phone_page:
                # 构造显示所有的完整请求
                yield scrapy.Request(url=self.show_all.format(show_all_phone_url),callback=self.get_all,meta=response.meta)
            # 判断pad端是否有匹配结果
            if pad_page:
                # 构造显示所有的完整请求
                yield scrapy.Request(url=self.show_all.format(show_all_pad_url),callback=self.get_all,meta=response.meta)
            # 两个都无匹配结果，将关键写入文件
            if not phone_page and not pad_page:
                with open('./无匹配结果关键字.txt', 'a+', encoding='utf-8') as f:
                    f.write(response.meta['keyword'] + "\n")
    # 解析完整的页面
    def get_all(self,response):
        if response.status == 200:
            """
            特别说明：存在这样一种情况，比如搜索fname时候一共三个搜索结果，
            却有下一页的链接，但其实是无效的链接，应该终止，故在此处加了一层逻辑判断，
            以后页面改变，此出逻辑判断可能需要省略！！！
            """
            # 判断响应的页面是否有数据
            has_data = response.xpath('//div[@class="applist-wrap"]/ul[@class="applist"]/li').extract()
            if has_data:    # 有数据才执行解析页面的操作
                # 获取详情页的url
                detail_urls = response.xpath('//div[@class="applist-wrap"]/ul/li/a/@href').extract()
                # 获取是否有下一页的判断依据
                has_next = response.xpath('//div[@class="pages"]/a[@class="next"]').extract()
                # 遍历获取每一个APP详情页链接
                for detail_url in detail_urls:
                    # 加入解析的队列
                    yield scrapy.Request(url=self.show_all.format(detail_url),callback=self.detail_page,meta=response.meta)
                # 需要根据下一页的判断递归调用此方法
                if has_next:
                    # 如果存在下一页，获取下一页的链接
                    next_page_url = response.xpath('//div[@class="pages"]/a[@class="next"]/@href').extract_first()
                    # 构造下一页完整的请求，并加入到采集队列之中
                    yield scrapy.Request(url=self.next_page.format(next_page_url),callback=self.get_all,meta=response.meta)
                # # 没有下一页，代表该关键字采集完成
                # else:
                #     with open('./完成搜索关键字.txt', 'a+', encoding='utf-8') as f:
                #         f.write(response.meta['keyword'] + "\n")
    # 解析详情页
    def detail_page(self,response):
        if response.status == 200:
            # print("查看当前的url：",response.url)
            # print("查看响应的内容：",response.text)
            # 解析获取目标字段
            # APP名称
            app_name = response.xpath('//div[@class="app-info"]/div[@class="intro-titles"]/h3/text()').extract_first()
            # APP 描述
            app_desc = response.xpath('//div[@class="app-text"]/p[@class="pslide"]/text()').extract_first()
            # APP发布时间
            app_publishTime = response.xpath(
                '//div[@class="look-detail"]/div[@class="details preventDefault"]/ul[1]/li[6]/text()').extract_first()
            # APP开发者
            app_author = response.xpath(
                '//div[@class="app-info"]/div[@class="intro-titles"]/p[1]/text()').extract_first()
            # APP下载量无
            # APP图片链接
            app_img = response.xpath('//div[@class="app-info"]/img/@src').extract_first()
            # APP详情页链接
            detail_page = response.url
            # APP所属分类
            app_category = response.xpath(
                '//div[@class="app-info"]/div[@class="intro-titles"]/p[2]/text()[1]').extract_first()
            # APP大小
            app_fileSize = response.xpath(
                '//div[@class="look-detail"]/div[@class="details preventDefault"]/ul[1]/li[2]/text()').extract_first()
            # APP版本号,需要拼接一个 V
            app_version = response.xpath(
                '//div[@class="look-detail"]/div[@class="details preventDefault"]/ul[1]/li[4]/text()').extract_first()
            # APP评分,需要按 - 切分然后取最后一个
            app_comment = response.xpath('//div[@class="app-info"]/div[@class="intro-titles"]/div[@class="star1-empty"]/div/@class').extract_first()
            # APP评论数
            app_commentNum = response.xpath(
                '//div[@class="app-info"]/div[@class="intro-titles"]/span[@class="app-intro-comment"]/text()').extract_first()
            """
            在此处增加判断，如果APP名称或者APP的开发者中包含关键字则当前的item才执行写加入管道文件
            """
            # if response.meta['keyword'] in [app_name, app_author]:
            # 创建item
            item = XiaomiredisItem()
            # 判断是否为空，不为空添加，为空赋默认值，否则丢失数据
            item['keyword'] = (response.meta['keyword']).strip()    # 关键字
            item['app_name'] = app_name if app_name else default_value  # APP名称
            item['app_desc'] = app_desc.strip() if app_desc else default_value  # APP描述
            item['app_publishTime'] = app_publishTime if app_publishTime else default_value  # APP上线时间
            item['app_author'] = app_author if app_author else default_value    # APP开发者
            item['app_downloads'] = default_value   # APP下载量，无
            item['app_img'] = app_img if app_img else default_value     # APP图片
            item['detail_page'] = detail_page   # APP详情页
            item['app_category'] = app_category if app_category else default_value  # APP种类
            item['app_fileSize'] = app_fileSize if app_fileSize else default_value  # APP大小
            item['app_version'] = "V" + " " + app_version if app_version else default_value  # APP版本
            item['app_comment'] = app_comment.split('-')[-1] if app_comment else default_value  # APP评分
            print("查看切分后的列表：", app_comment.split('-'))
            item['app_commentNum'] = app_commentNum[2:-1] if app_commentNum else default_value    # APP评论数
            yield item
        else:
            print("无匹配结果，写入文件：", response.meta['keyword'])
            with open(r'./无匹配结果.text', 'a+', encoding='utf-8') as f:
                f.write(response.meta['keyword'])
