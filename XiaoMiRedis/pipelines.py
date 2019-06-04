# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from XiaoMiRedis.utils import get_db
mongo_db = get_db()



class XiaomiredisPipeline(object):
    # 创建文件方法
    def open_spider(self, spider):
        """
        在当前路径下创建文件记录爬取的目标字段
        路径的可以根据实际需求做修改
        :param spider:
        :return:
        """
        # 在当前目录下创建为文件
        self.file = open('./小米应用商城数据_1.txt', 'a+', encoding='utf-8')
    # 管道方法，对目标字段的入库或者写入文件等操作在此书写
    def process_item(self, item, spider):
        """
        处理目标字段，统一格式后写入文件
         :param item:
         :param spider:
         :return:
         """
        # 关键字
        keyword = item['keyword']
        print("查看关键字==========================：", keyword)
        # APP名称
        app_name = item['app_name']
        print("查看APP名称==========================：", app_name)
        # APP 描述
        app_desc = item['app_desc']
        print("查看APP描述==========================：", app_desc)
        # APP发布时间
        app_publishTime = item['app_publishTime']
        print("查看APP发布时间======================：", app_publishTime)
        # APP开发者
        app_author = item['app_author']
        print("查看APP开发者========================：", app_author)
        # APP下载量
        app_downloads = item['app_downloads']
        print("查看APP下载量========================：", app_downloads)
        # APP图片链接
        app_img = item['app_img']
        print("查看APP图片==========================：", app_img)
        # APP详情页
        detail_page = item['detail_page']
        print("查看APP详情页========================：", detail_page)
        # APP所属分类
        app_category = item['app_category']
        print("查看APP分类==========================：", app_category)
        # APP大小
        app_fileSize = item['app_fileSize']
        print("查看App大小==========================：", app_fileSize)
        # APP版本号
        app_version = item['app_version']
        print("查看APP版本号========================：", app_version)
        # APP评分
        app_comment = item['app_comment']
        print("查看APP评分==========================：", app_comment)
        # APP评论次数
        app_commentNum = item['app_commentNum']
        print("查看APP评论数========================：", app_commentNum)
        # 将获取的目标字段整理成统一格式，定义一个变量用于拼接最后结果
        result_content = ""
        result_content = result_content.join(
            keyword + "ÿ" + app_name + "ÿ" + app_desc + "ÿ" + app_publishTime + "ÿ" + app_author + "ÿ" +
            app_downloads + "ÿ" + app_img + "ÿ" + detail_page + "ÿ" + app_category + "ÿ" +
            app_fileSize + "ÿ" + app_version + "ÿ" + app_comment + "ÿ" + app_commentNum + "\n"
        )
        # 将文件写入本地文件
        self.file.write(result_content)
        self.file.flush()
        return item
    # 关闭文件的方法
    def close_spider(self, spider):
        # 文件写入完成，关闭文件
        self.file.close()


# 以下代码是存储到 mongodb时需要的代码
class ResultMongoPipeline(object):
    """抓取结果导入 mongo"""

    def __init__(self, settings):
        self.collections_name = settings.get('RESULT_COLLECTIONS_NAME')

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings)

    def process_item(self, item, spider):
        mongo_db[self.collections_name].insert(item)
        return item

