"""
将字典对象保存为excel
"""

import os
import csv

class SaveCSV(object):
    def __init__(self,keyword_list, path):
        self.keyword_list = keyword_list
        self.path = path


    def save(self,item):
        """
        保存csv方法
        :param keyword_list: 保存文件的字段或者说是表头
        :param path: 保存文件路径和名字
        :param item: 要保存的字典对象
        :return:
        """
        # 第一次打开文件时，第一行写入表头
        if not os.path.exists(self.path):
            #if not os.path.exists(path):
            #os.makedirs(self.path)
            with open(self.path, "w", newline='', encoding='utf-8') as csvfile:  # newline='' 去除空白行
                writer = csv.DictWriter(csvfile, fieldnames=self.keyword_list)  # 写字典的方法
                writer.writeheader()  # 写表头的方法

        # 接下来追加写入内容
        with open(self.path, "a", newline='', encoding='utf-8') as csvfile:  # newline='' 一定要写，否则写入数据有空白行
            writer = csv.DictWriter(csvfile, fieldnames=self.keyword_list)
            writer.writerow(item)  # 按行写入数据
            # print("^_^ write success")

        # except Exception as e:
        #     print("write error==>", e)
        #     # 记录错误数据
        #     with open("error.txt", "w") as f:
        #         f.write(json.dumps(item) + ",\n")
        #     pass
