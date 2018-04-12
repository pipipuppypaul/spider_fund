# -*-coding:utf-8-*-
#
"""
@version: 0.2
@author: Bobby Yu
@file: fullPSQL.py
@time: 2018/4/11 下午1:15
"""
############################ 全数据模式
import requests
from  settings  import * #自己的
import time
import json
from lxml import html
import multiprocessing
import getSymbol  # 自己的
import os
import sys
import psycopg2


num = range(1,101)  # 1--(n-1) 页
symbols = getSymbol.get_symbols()[0:3]

def get_full_comment():
    session = requests.session()
    try:
        conn = psycopg2.connect(
            database=PSQL_DATABASE,
            user=PSQL_USERNAME,
            password=PSQL_PASSWORD,
            host=PSQL_HOST,
            port=PSQL_PORT
        )
    except:
        print('database connection error')
        exit(0)
    for symbol in symbols:  # 对每支股票创建自己的table
        tablename = +str(symbol)
        time.sleep(5)

        for i in num:
            print('sleep for 3s')
            time.sleep(3) #如果抓取太频繁会被封锁IP，为了体谅一下别人网站，设置了睡眠时间
            url = comment_url.format(symbol=symbol, page=str(i))
            print(url)
            First_request = session.get(url='https://xueqiu.com/', headers=headers, timeout=15)
            # 写firstrequest是为了获取cookie，不然无法获取后续信息
            comments_list = session.get(url, headers=headers, timeout=15)
            if str(comments_list.status_code) == str(200):  # 是否正常返回数据
                #######################################################
                stocks_comment = json.loads(comments_list.text)['list']
                page = json.loads(comments_list.text)['maxPage']  # 获取最大页数
            else:
                print('load',symbol,'error',comments_list.status_code)
                continue
            print('正在获取第', i, '页，该股票一共', page)
            for stork in stocks_comment:
                text = stork.get('text').strip()
                selector = html.fromstring(text)
                comment = selector.xpath('string(.)')
                user_info = stork.get('user')  # 评论者名字
                stock_code = symbol  # 股票代码
                comment_id = stork.get('id')  # 每条评论都要唯一的ID
                com_time = stork.get('timeBefore')  # 评论时间
                if '今天' in com_time:
                    com_time = com_time.replace('今天',str(time.strftime("%m-%d", time.localtime())))
                elif '分钟前' in com_time:
                    minute = com_time[:-3]
                    com_time = com_time.replace(com_time,str(time.strftime("%m-%d %H:%M", time.localtime())))
                    com_time = com_time.replace(com_time[-2:],str(time.localtime().tm_min - int(minute)))
                print(user_info['screen_name'], comment_id, com_time,comment_id)
                storeIn_psql(tableName=tablename, code=stock_code, usr_info=user_info, timeT=com_time,
                             comment=comment, comment_id=comment_id,connection = conn)
            if str(page) == str(i):  # 抓取到了最后一页
                print(symbol, '该股票抓取结束')
                break
        print('当前股票爬取完毕')
    conn.close()


def storeIn_psql(tableName,code, usr_info, timeT, comment, comment_id,connection):

    cur = connection.cursor()
    cur.execute('''
        create table if not exists ''' + tableName + '''
        (user_name varchar(32),
         id SERIAL primary key,
         com_time varchar(16),
         comment TEXT,
         comment_id int UNIQUE)    
        ''')
    connection.commit()
    try:
        insert_cmd = "insert into "+ tableName+ " (user_name,com_time,comment,comment_id) "+\
                     " values ('"+usr_info['screen_name']+"','"+timeT+"','"+comment+"'," +str(comment_id)+ ")"
        print(insert_cmd)
        cur.execute(insert_cmd)
        connection.commit()
    except :
        cur.execute("rollback;")
        connection.commit()
        print('A duplicated message, insertion rejected. Prog continues...')



def process_crawler():
    process = []
    # num_cups=multiprocessing.cpu_count()
    num_cups = 1
    for i in range(int(num_cups)):
        p = multiprocessing.Process(target=get_full_comment)  # 需要的话可以创建多进程
        p.start()
        process.append(p)
        for p in process:
            p.join()


if __name__ == '__main__':
    process_crawler()
