# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.linkextractors import LinkExtractor
import ipdb
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy import log, Selector
from pro_files.items import ProFilesItem


class PrjInfoSpider(CrawlSpider):
    name = 'prj_info'
    # 该属性定义可以爬去的域名列表。如果没有定义该属性，则表示可以爬取任意域名
    allowed_domains = ['ecp.sgcc.com.cn']
    start_url = 'http://ecp.sgcc.com.cn/topic_project_list.jsp?columnName=topic10'

    # 该属性为一个正则表达式集合，用于告知爬虫需要跟踪哪些链接
    # rules = (
    #     Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    # )
    def __init__(self, *args, **kwargs):
        super(PrjInfoSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        return [Request(
            self.start_url,
            callback=self.parse_homepage,
            errback=self.parse_err
                        )]

    def replace_page_no(self, first_url, page_no):
        prefix, _ = first_url.rsplit('=', 1)
        return "{}{}".format(prefix, page_no)

    def parse_homepage(self, response):
        selector = Selector(response)
        max_page = max([int(item) for item in selector.xpath('//div[@class="page"]/a/text()').extract()])
        first_url = selector.xpath('//div[@class="page"]/a/@href').extract_first()
        prefix, _ = first_url.rsplit('=', 1)
        # max_page = 2
        for index in range(1, max_page, 1):
            complete_url = "http://ecp.sgcc.com.cn/{}={}".format(prefix, index)
            print complete_url
            yield Request(complete_url,
                          callback=self.parse_pj_list,
                          errback=self.parse_err)

    def parse_pj_list(self, response):
        selector = Selector(response)
        prefix_url = "http://ecp.sgcc.com.cn/html/project/{}/{}.html"

        for item in selector.xpath("//td/a/@onclick").extract():
            pj_id, hash_code = self._get_pj_args(item)
            complete_url = prefix_url.format(pj_id, hash_code)
            print complete_url
            yield Request(complete_url,
                          callback=self.parse_pj,
                          errback=self.parse_err)
            pass

    @staticmethod
    def _get_pj_args(raw_str):
        pattern = r"showProjectDetail\('([0-9]+)','([0-9]+)'\)"

        match_group = re.match(pattern, raw_str)
        return str(match_group.group(1)), str(match_group.group(2))

    def _set_pf_item(self, k, v, pf_item):
        config_data = {
            u'项目状态': 'status',
            u'项目编号': 'pj_no',
            u'项目名称': 'title',
            u'截标时间': 'end_time',
            u'开标时间': 'created_time',
            u'项目类型': 'pj_type',
            u'招标人': 'tenderer',
            u'代理机构': 'proxy',
            u'联系人': 'contact',
            u'联系电话': 'contact_phone',
            u'E-MAIL': 'contact_email'
        }
        for c_k in config_data.keys():
            if c_k.startswith(k):
                pf_item[config_data[c_k]] = v
                break
                # setattr(pf_item, config_data[c_k], v)

    def _download_zip_file(self, k, item):
        if not k.startswith(u'项目公告文件'):
            return
        link = item.xpath('td/a/@href').extract_first()
        complete_link = "http://{}{}".format(self.allowed_domains[0], link)

        return complete_link

    def parse_pj(self, response):
        selector = Selector(response)

        pf_item = ProFilesItem()
        for item in selector.xpath("//tr"):

            res = item.xpath("td/text()").extract()
            if len(res) < 2:
                print(res)
                continue
            key = res[0].replace(u'：', '')
            value = res[1].replace('\r', '').replace('\t', '').replace('\n', '')
            self._set_pf_item(key, value, pf_item)

            url_path = self._download_zip_file(key, item)
            if url_path:
                pf_item['file_path'] = url_path
        yield pf_item

    def parse_err(self, response):
        log.ERROR('crawl {} failed'.format(response.url))