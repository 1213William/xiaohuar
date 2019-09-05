import pymongo
import requests
from bs4 import BeautifulSoup
from threading import Thread
from xiaohuar.config import *


client = pymongo.MongoClient('localhost', connect=False)

db = client[MONGO_D]


def get_html_content(url):
    response = requests.get(url)
    try:
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(e)


def get_tag(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    lst = soup.select('div.img')
    return lst


def get_data(user_lst):
    for i in user_lst:
        a = i.contents[1]
        link = a['href']
        img = a.img['src']
        address = a.img['alt']
        name = i.contents[3]
        name = name.text
        school = i.contents[5]

        school = school.a.text
        info = {
            'name': name.strip(),
            'school': school.strip(),
            'address': address.strip(),
            'link': link.strip(),
            'img': 'http://www.xiaohuar.com/' + img
        }
        yield info


def save(res):
    db[MONGO_T].insert(res)
    print('Successfully insert!!!')


def main(offset):
    url = 'http://www.xiaohuar.com/list-1-%s.html' % offset
    html = get_html_content(url)
    res = get_tag(html)  # 这个是一个个的div标签
    if res:
        for i in get_data(res):
            if i:
                # db[MONGO_T].insert(i)
                print(i)


if __name__ == '__main__':
    lst = []
    for i in range(GROUP_START, GROUP_END + 1):
        t = Thread(target=main, args=(i,))
        t.start()
        lst.append(t)
    for i in lst:
        i.join()


