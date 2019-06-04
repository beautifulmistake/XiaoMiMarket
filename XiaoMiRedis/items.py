# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class XiaomiredisItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    # 关键字
    keyword = scrapy.Field()
    # APP名称
    app_name = scrapy.Field()
    # APP 描述
    app_desc = scrapy.Field()
    # APP发布时间
    app_publishTime = scrapy.Field()
    # APP开发者
    app_author = scrapy.Field()
    # APP下载量
    app_downloads = scrapy.Field()
    # APP图片链接
    app_img = scrapy.Field()
    # APP详情页
    detail_page = scrapy.Field()
    # APP所属分类
    app_category = scrapy.Field()
    # APP大小
    app_fileSize = scrapy.Field()
    # APP版本号
    app_version = scrapy.Field()
    # APP评分
    app_comment = scrapy.Field()
    # APP评论次数
    app_commentNum = scrapy.Field()






