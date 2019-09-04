# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import zipfile
import shutil
from pymongo import MongoClient
from pro_files.settings import MONGO_URI, PROJECT_DIR
# from pyunpack import Archive
from pro_files.settings import STORE_DIRECTORY
import requests


class ProFilesPipeline(object):

    def __init__(self, mongo_uri, mongo_db, file_dir):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.file_dir = file_dir
        self.client = None


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=MONGO_URI,
            mongo_db='nari',
            file_dir=os.path.join(PROJECT_DIR, 'nari')
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        if not os.path.exists(self.file_dir):
            os.mkdir(self.file_dir)

    def close_spider(self, spider):
        self.client.close()

    def _process_pj(self, item):
        collection = self.db['pj']
        pj_no = item['pj_no']
        collection.update({'pj_no': pj_no}, dict(item), upsert=True)
        file_url = item['file_path']
        base_name = os.path.basename(file_url)

        path = u"{}/{}".format(STORE_DIRECTORY, item['pj_no'])
        if not os.path.exists(path):
            os.mkdir(path)

        content = requests.get(file_url, stream=True)
        with open("{}/{}".format(path, base_name), 'wb') as zip_file:
            zip_file.write(content.content)

        zip_file_path = "{}/{}".format(path, base_name)
        with zipfile.ZipFile(zip_file_path) as zip_ref:
            for fn in zip_ref.namelist():
                right_fn = fn.decode('gbk')
                with open(u"{}/{}".format(path, right_fn), 'wb') as out_file:
                    with zip_ref.open(fn) as original_file:
                        shutil.copyfileobj(original_file, out_file)
                # if right_fn.endswith('rar'):
                #     import rarfile
                #     # unrar rar file
                #     Archive(u"{}/{}".format(path, right_fn.decode('gbk'))).extractall(path)

    def process_item(self, item, spider):
        self._process_pj(item)
        return item
