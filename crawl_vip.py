# coding:utf-8
"""
	爬取vip reading
"""
import requests
import json
from bs4 import BeautifulSoup
import codecs
import os
from urlparse import urljoin

base_url = "http://www.vipreading.com/"
books_path = 'books/'
chapters_path = 'chapters/'


novel_list = {
    "type": [1, 2, 3, 4, 5, 6, 7],
    "close": [1, 2]
}
type_mapping = {
    1: "中国古典文学",
    2: "中国现代文学",
    3: "外国文学",
    4: "校园文学",
    5: "语录",
    6: "散文",
    7: "其他文学"
}

close_mapping = {
    1: "完结",
    2: "未完结"

}


def parse_book_list(content):
    soup = BeautifulSoup(content, 'html5lib')
    bd = soup.find_all('div', {"class": "bd"})[1]
    book_elements = bd.find_all('tr')
    book_list = []
    for ele in book_elements[1:]:
        book = {
            "index": ele.find('td', {"class": "index"}).text,
            "name": ele.find('a', {"class": "title"}).text,
            "url": ele.find('a', {"class": "title"}).get('href'),
            "author": ele.find('a', {"class": "author"}).text,
            "words": ele.find('td', {"class": "words"}).text,
            "time": ele.find('td', {"class": "time"}).text,
        }
        book_list.append(book)
    return book_list


def parse_book_info(content):
    soup = BeautifulSoup(content, 'html5lib')
    summary = soup.find('div', {"class": "summary"}).text
    download_url = soup.find(
        'a', {"rel": "nofollow", "data-collect-index": "2", "class": "index"}).get('href')
    chapter_elements = soup.find_all("li", {"class": "", "createdate": ""})
    chapter_list = []
    for ele in chapter_elements:
        try:
            if 't' in ele.get('class'):
                continue
            chapter_url = ele.find('a', {"class": "name"}).get('href')
            chapter_name = ele.find('a', {"class": "name"}).text
            chapter_list.append({"url": chapter_url, "name": chapter_name})
        except Exception as e:
            pass
    print summary
    print download_url
    return {
        "summary": summary,
        "download_url": download_url,
        "chapter_list": chapter_list
    }


def _crawl_book_list(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception('error:%s', url)
    resp.encoding = "gbk"
    book_list = parse_book_list(resp.text)
    return book_list


def _crawl_book_info(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception('error:%s', url)
    resp.encoding = "gbk"
    book_info = parse_book_info(resp.text)
    return book_info


def _crawl_book_content(book_path, url):
    if os.path.exists(books_path):
        return books_path
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception('error:%s', url)
    resp.encoding = 'gbk'
    with codecs.open(book_path, 'wb', encoding="utf-8") as f:
        f.write(resp.text)
    return book_path


def _crawl_book_chapter(chapter_path, url):
    if os.path.exists(chapter_path):
        return chapter_path
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception('error:%s', url)
    resp.encoding = 'gbk'
    with codecs.open(chapter_path, 'wb', encoding="utf-8") as f:
        f.write(resp.text)
    return chapter_path


def crawl_book_list():
    if os.path.exists('book_list.json'):
        with open('book_list.json', 'r') as f:
            return json.load(f)
    url = "http://www.vipreading.com/novel-list-0-0-0-0-0-0-0-%d.html"
    book_list = []
    for i in xrange(1, 71):
        book_list.extend(_crawl_book_list(url % (i)))
    with codecs.open('book_list.json', 'w', encoding='utf-8') as f:
        json.dump(book_list, f, encoding="utf-8", indent=2)
    return book_list


def crawl_book_info():
    book_list = crawl_book_list()
    for book in book_list:
        if "info" in book.keys():
            return book_list
        url = base_url + book['url']
        book_info = _crawl_book_info(url)
        book['info'] = book_info
    with codecs.open('book_list.json', 'w', encoding='utf-8') as f:
        json.dump(book_list, f, encoding="utf-8", indent=2)
    return book_list


def crawl_book_content():
    book_list = crawl_book_info()
    count = 0
    for book in book_list:
        if "local_path" in book['info'].keys():
            continue
        url = urljoin(base_url,book['info']['download_url'])
        book_path = books_path + book['name']+'.txt'
        book['info']['local_path'] = _crawl_book_content(book_path, url)
        count += 1
        if count % 40 == 0:
            with codecs.open('book_list.json', 'w', encoding='utf-8') as f:
                json.dump(book_list, f, encoding="utf-8", indent=2)
    with codecs.open('book_list.json', 'w', encoding='utf-8') as f:
        json.dump(book_list, f, encoding="utf-8", indent=2)
    return book_list


def crawl_book_chapter():
    book_list = crawl_book_info()
    count = 0
    for book in book_list:
        for chapter in book['info']['chapter_list']:
            if 'path' in chapter.keys():
            	print chapter['path']
                continue
            url = urljoin(base_url,chapter['url'])
            chapter_path = chapters_path + chapter['name']+'.txt'
            chapter['path'] = _crawl_book_chapter(chapter_path, url)
        if count % 40 == 0:
            with codecs.open('book_list.json', 'w', encoding='utf-8') as f:
                json.dump(book_list, f, encoding="utf-8", indent=2)
        count += 1
        print count
    with codecs.open('book_list.json', 'w', encoding='utf-8') as f:
        json.dump(book_list, f, encoding="utf-8", indent=2)


if __name__ == '__main__':
    crawl_book_chapter()
