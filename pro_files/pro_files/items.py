# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProFilesItem(scrapy.Item):
    # define the fields for your item here like:
    status = scrapy.Field()  # 项目状态
    pj_no = scrapy.Field()   # 项目编号
    title = scrapy.Field()   # 项目名称
    end_time = scrapy.Field()       # 截标日期
    created_time = scrapy.Field()   # 开标日期
    pj_type = scrapy.Field()        # 项目类型
    proxy = scrapy.Field()          # 代理机构
    contact = scrapy.Field()        # 联系人
    contact_phone = scrapy.Field()  # 联系人电话
    tenderer = scrapy.Field()       # 招标人
    file_path = scrapy.Field()      # 招标文件
    tender = scrapy.Field()         # 标书
    contact_email = scrapy.Field()

