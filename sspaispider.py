# coding: utf-8

import time
import re
import os
import requests
import re
from bs4 import BeautifulSoup
from multiprocessing import Pool

# 初始化一些值
headers = {
    'Authorization': '',
    'Host': 'sspai.com',
    'Referer': 'https://sspai.com/',
    'User-Agent': 'Mozilla/5.0',
   'Cookie': '' # 按需填写
}
total = 0
offset = 0
limit = 50

def get_time(timestamp):
    time_local = time.localtime(timestamp)
    dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)    
    return dt

def get_list():
    global total,offset,limit
    article_dict = {}
    while True:
        url = "https://sspai.com/api/v1/articles?offset={0}&limit={1}".format(str(offset),str(limit))
        print('fetching',url)
        try:
            resp = requests.get(url,headers=headers)
            j = resp.json()
            data = j['list']
            total = j['total']
        except:
            print('get list failed')
        for article in data:
            aid = article['id']
            akeys = article_dict.keys()
            print(aid)
            if aid not in akeys:
                article_dict[aid] = [article['title'],get_time(article['released_at'])]
    
        if (offset+limit) >= total:
            break
            
        offset += 50
            
        time.sleep(3)
    
    with open('sspai_ids.txt', 'w',encoding='utf-8') as f:
        items = sorted(article_dict.items())
        for item in items:
            f.write('{0} {1} {2}\n'.format(item[0],item[1][0],item[1][1]))

def get_html(url):
    title = re.sub('[\/\\\:\*\?\"\<\>\|]', '-', url[1])  # 正则过滤非法文件字符
    file_name = '%03d. %s.html' % (url[2], title)
    if os.path.exists(file_name):
        print(title, 'already exists.')
        return
    else:
        print('saving', title)
    html = requests.get("https://sspai.com/post/"+url[0], headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    try:
        content = soup.find("div", {"class": "article-detail"})
        content = content.article.prettify()
    except:
        # print("saving", title, "error")
        logmes = "saving {0} {1} error\n".format(url[0],title)
        with open("error.log", 'a+', encoding='utf-8') as f:
            f.write(logmes)
        return
    content = content.replace('h1>', 'h2>')
    content = '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body><h1>%s</h1>%s</body></html>' % (
        title, content)
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(content)
    time.sleep(3)

def get_details():
    detailList = []
    with open('sspai_ids.txt', 'r', encoding='utf-8') as f:
        i = 1
        for line in f:
            lst = line.strip().split(' ')
            url = lst[0]
            title = '_'.join(lst[1:])
            detailList.append((url,title,i))
            i += 1
    return detailList


if __name__ == '__main__':
#     get_list()
    pool = Pool(processes=10) # 进程池
    s1 = time.time()
    pool.map(get_html,get_details())
    pool.close()
    pool.join()
    print("time used ",int(time.time()-s1))

