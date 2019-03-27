import requests
import re
import json
import time
import os


def get_content(url, flag):
    """
    通过url获取HTML
    :param url: 链接
    :param flag:选择获取image还是获取html
    :return: 获取到的内容，获取失败返回None
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/73.0.3683.86 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            if flag == 'image':
                return response.content
            elif flag == 'html':
                return response.text
        return None
    except requests.exceptions.RequestException:
        print("ERROR!")
        return None


def parse_html(html):
    """
    使用正则表达式提取HTML中所需要的数据
    :param html: HTML文档
    :return: 可迭代的字典的集合，每个字典包含了一个电影的信息
    """
    pattern = re.compile('<dd>.*?board-index.*?>(.*?)</i>.*?data-src="(.*?)".*?name.*?a.*?>(.*?)</a>'
                         '.*?star.*?>(.*?)</p>.*?releasetime.*?>'
                         '(.*?)</p>.*?integer.*?>(.*?)</i>.*?fraction.*?>(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2].strip(),
            'actor': item[3].strip()[3:] if len(item[3]) > 3 else '',
            'time': item[4].strip()[5:] if len(item[4]) > 5 else '',
            'score': item[5].strip()+item[6].strip()
        }


def write_to_file(content):
    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False)+'\n')


def save_image(film_name, content):
    """
    保存电影的海报
    :param film_name: 电影名
    :param content: 图片的内容
    """
    if not os.path.isdir(r'.\电影海报\\'):
        os.makedirs(r'.\电影海报\\')
    with open(r'.\电影海报\\'+film_name+'.jpg', 'wb') as f:
        f.write(content)


def main(offset):
    """
    主函数
    :param offset: 偏移量，用来定位访问的排名返回（offset to offset+10）
    """
    url = 'http://maoyan.com/board/4?offset=' + str(offset*10)
    html = get_content(url, 'html')
    for item in parse_html(html):
        print(item)
        write_to_file(item)
        image = get_content(item['image'], 'image')
        save_image(item['title'], image)


if __name__ == '__main__':
    for offset in range(10):
        main(offset)
        # 此处若不休眠一秒，在爬取一部分数据后便爬不到数据了
        time.sleep(1)
