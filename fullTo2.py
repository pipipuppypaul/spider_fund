#-*-coding:utf-8-*-
"""
@version: 0.2
@author: Bobby Yu
@file: xueqiu_fullTo2.py
@time: 2018/4/11 下午14:27
"""

import requests
import Agents  # 自己的
from  settings  import * #自己的
import getSymbol  # 自己的
import random
import time
import json
from lxml import html
import multiprocessing
import os
import sys

num = range(1,3)  # 1--(n-1)页
symbols = getSymbol.get_symbols()

n = 4  # 每n页评论放入一个文件

def get_full_comment():
    session = requests.session()
    # proxy = requests.get('http://localhost:5010/get').text()  # 必要的话获取本地代理池代理
    for symbol in symbols:# 对每支股票创建自己的目录
        time.sleep(5)
        NEWEST_COMMENT_TIME = ''
        #dir_path = '~/work/bobby/empty/' + str(symbol)
        dir_path = './'+ str(symbol)
        page_path = '1'
        mkdir_cmd = '''
        if [ ! -d '''+ dir_path +''' ]; then
         mkdir '''+dir_path+'''
        fi
        '''
        #print(mkdir_cmd)
        ssh.exec_command(mkdir_cmd)
        for i in num:
            print('sleep for 5s')
            time.sleep(5)
            if (i - 1) % n == 0:  # 每n页放在同一个文件
                page_path = str(int((i - 1) / n + 1))
            filename = dir_path + '/' + page_path + '.txt'
            url = comment_url.format(symbol=symbol, page=str(i))
            print(url)
            First_request = session.get(url='https://xueqiu.com/', headers=headers, timeout=15)
            comments_list = session.get(url, headers=headers, timeout=15)
            if str(comments_list.status_code) == str(200):  # 是否正常返回数据
                #######################################################
                stocks_comment = json.loads(comments_list.text)['list']
                page = json.loads(comments_list.text)['maxPage']  # 获取最大页数
                print('load',symbol,'200 OK')
            else :
                print('load', symbol, 'error', comments_list.status_code)
                continue
            print('正在爬取第', i, '页，该股票一共', page)
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
                if (i == 1) and (NEWEST_COMMENT_TIME == ''):
                    NEWEST_COMMENT_TIME = com_time  # 用于更新文件中记录的评论时间
                #print(user_info['screen_name'], comment_id, com_time, comment_id)
                storeIn_psql(file=filename, code=stock_code, usr_info=user_info, timeT=com_time,
                             comment=comment, comment_id=comment_id)
                if str(page) == str(i):  # 抓取到了最后一页
                    print(symbol, '该股票抓取结束')
                    break
            page_cmd = ' echo "\n \t\t\t\t\t\t\t\t\t\t\t\t\tpage" '+str(i)+' "overed" >> '+filename+' '
            ssh.exec_command(page_cmd)
        meta_data_update(dir_path, NEWEST_COMMENT_TIME)  # 更新元数据文件
        print('当前股票爬取完毕')


def storeIn_psql(file, code, usr_info, timeT, comment, comment_id):
#    with open(file, 'a+') as f:
#        f.write('发帖人：{} \t 发帖时间：{} \t 内容：{} \t 帖子编号：{} \n\n\n'.format(
#            usr_info['screen_name'], time, comment, comment_id))
    print(file, usr_info['screen_name'], timeT, comment_id)
    name_cmd = ' echo "发帖人: '+usr_info["screen_name"]
    time_cmd = '\t 发帖时间: '+timeT
    com_cmd = '\t 内容: '+ comment
    com_id_cmd = '\t 帖子编号: '+str(comment_id)
    full_cmd = name_cmd+time_cmd+com_cmd+com_id_cmd+' " >> '+ file
    print(full_cmd)
    ssh.exec_command(full_cmd)


def meta_data_update(path, newTime):
    file_path = path + '/0_recent.txt'
#    with open(file_path, 'w') as f:
#        f.write('{}'.format(str(newTime)))
    meta_cmd = ' echo "'+str(newTime)+'" > '+file_path
    ssh.exec_command(meta_cmd)


if __name__ == '__main__':
    get_full_comment()
    ssh.close()