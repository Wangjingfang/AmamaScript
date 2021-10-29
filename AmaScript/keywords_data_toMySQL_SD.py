# -*- coding: utf-8 -*-

"""
@Author: MarlonYang

@Date  : 2021/6/24 18:14

@File  : test.py

@Desc  :

@2021/6/24 更新：
1. 在原有搜索词报告处理上，从生成excel改为自动导入mysql
2. 已根据当周计算好报告最小日期

"""
import numpy as np
import pandas as pd
import os
import datetime
from datetime import timedelta
import pymysql
from sqlalchemy import create_engine

def file_name():
    try:
        L = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if os.path.splitext(file)[1] == '.xlsx':
                    L.append(os.path.join(root, file))
        return L

    except Exception as e:
        print("获取各文件路径失败", e)


def read_data(L):
    try:
        L = file_name()
        df_exchange = pd.read_excel(transform_path, sheet_name='Sheet2')
        upload_file = pd.read_excel(final_path, sheet_name='SD')

        m = 0
        n = 0
        for l in L:
            df = pd.read_excel(l)
            df["Group"] = l.split("\\")[-2]
            df["Country"] = l.split("\\")[-1][4:6].upper()
            df["Station"] = l.split("\\")[-1][0:6].upper()
            df.columns = list(upload_file.columns)
            print(l.split("\\")[-1][0:6].upper(), df.shape)
            upload_file = pd.concat([upload_file, df], axis=0)
            n += 1
            m += df.shape[0]
        print("共{0}个搜索词报告文件，总数据量：{1}".format(n, m))
        print(upload_file.shape)

        upload_file = pd.merge(upload_file, df_exchange, on='Country', how='left')
        print(upload_file.shape)

        upload_file['Spend$'] = upload_file['Spend'] * upload_file['Price']
        upload_file['Sales$'] = upload_file['14 Day Total Sales'] * upload_file['Price']
        for i in ['14 Day Total Sales', '14 Day Total Orders (#)', '14 Day Total Units (#)']:
            upload_file[i] = upload_file[i].replace(0, np.nan)
        final_df = upload_file.drop(columns='Price')
        print(final_df.shape)

        # final_df.to_excel(excel_writer=upload_path, index=None)

        return final_df

    except Exception as e:
        print("读取数据失败", e)


def data_to_mysql(final_df):
    try:
        now = datetime.datetime.now()
        repo_start_date = now - timedelta(days=now.weekday()) - timedelta(days=31)
        print("报告最早时间为： {0}".format(str(min(final_df["Date"])).split(" ")[0]))
        print("数据库中将删除： {0} 此日期后的数据，导入本次新数据".format(str(repo_start_date).split(" ")[0]))

        db = pymysql.connect(host='localhost', user='root', password='123456', database='keywords')
        data_table = "keywords_sd"
        cursor = db.cursor()

        try:
            #原数据量
            cursor.execute('SELECT COUNT(Station) FROM `%s`'%(data_table))
            print("原数据量： {0}".format(cursor.fetchall()[0][0]))

            #需要删除数据量
            cursor.execute('SELECT COUNT(Station) FROM `%s` WHERE Date >= "%s"' % (data_table, str(repo_start_date).split(" ")[0]))
            print("删数据量： {0}".format(cursor.fetchall()[0][0]))

            #删除数据
            cursor.execute('delete from `%s` where Date >= "%s"'%(data_table, str(repo_start_date).split(" ")[0]))
            # cursor.execute('delete from `%s` where Date >= "%s"'%(data_table,"2021-05-21")   #人为修改删除时间：2021-01-01
            db.commit()

            #dataframe导入MySQL
            engine = create_engine('mysql+pymysql://root:123456@localhost:3306/keywords?charset=utf8mb4')
            final_df.to_sql(data_table, engine, index=False, if_exists='append')

            #现数据量
            cursor.execute('SELECT COUNT(Station) FROM `%s`'%(data_table))
            print("现数据量： {0}".format(cursor.fetchall()[0][0]))

        except Exception as e:
            print("导入数据失败", e)
            db.rollback()

    except Exception as e:
        print("进入数据库失败", e)
    else:
        print("搜索词数据导入MySQL成功")


def main():

    global path, transform_path, final_path, upload_path

    path = r"D:\Summary\SD\20210705"
    upload_path = r"D:\Summary\SD\upload\upload-{0}.xlsx".format(path.split("\\")[-1])
    transform_path = r"D:\Summary\关键词\exchange.xlsx"
    final_path = r"D:\Summary\关键词\final.xlsx"

    L = file_name()
    final_df = read_data(L)
    data_to_mysql(final_df)


if __name__ == '__main__':
    main()