from shutil import copyfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os

URL = 'https://dict.hjenglish.com/jp/jc/'
TEMPLATE_PATH = 'template.md'
PERSIST_PATH = 'words.md'

# Prepare Driver
service = Service('chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)
driver.set_page_load_timeout(40)


def persist(info: list):
    if not os.path.exists(PERSIST_PATH):
        createMarkDownFile()
    f = open(PERSIST_PATH, 'a', encoding='utf-8')
    f.write(buildRow(info))


def buildRow(info: list):
    return '|' + "|".join(info) + '|\n'


def createMarkDownFile():
    # 拷贝模板会比较简单
    copyfile(TEMPLATE_PATH, PERSIST_PATH)


def reptile(word) -> list:
    url = URL + word
    # hj 的网页逻辑是第一次Get时候做验证，但验证不是到Cookie之类的，没找到验证的点，第二次就能获取到了，所以第一次可能查不到+可能超时
    for i in range(5):
        driver.get(url)
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')

        bs = BeautifulSoup(driver.page_source, features="lxml")

        word_details = bs.find("header", {"class": "word-details-pane-header"})
        if word_details is None:
            continue
        word_info = word_details.find("div", {"class": "word-info"})
        word_simple = word_details.find("div", {"class": "simple"})
        if word_info is None or word_simple is None:
            continue

        # 拼装一个答案
        # | Tag  | 漢字 | 词性 | 注音　| 声调 | 助记 | 中文 |
        res = []
        base = [' '] * 7
        # 0.Tag 留空
        base[1] = word_info.find("div", {"class": "word-text"}).find("h2").get_text()
        base[2] = word_simple.find("h2").get_text()
        base[3] = word_info.find("div", {"class": "pronounces"}).find("span").get_text()
        base[4] = word_info.find("span", {"class": "pronounce-value-jp"}).get_text()
        # 5. 助记 留空

        explains = list(map(lambda a: a.get_text(), word_simple.find_all("li")))
        # base[6] = r'<br\>'.join(explains)

        for index in range(len(explains)):
            if index == 0:
                base[6] = explains[index]
                res.append(base)
            else:
                addition = [' '] * 7
                addition[6] = explains[index]
                res.append(addition)

        return res
    print('超时或词语不存在')
    return None


def debug():
    info = ['N', '测试', '动', '注音', '助记', '汉字', '声？']
    persist(info)


if __name__ == '__main__':
    print('输入要查找的日文词汇，退出输入q')
    while True:
        word = input()
        if word == 'q':
            break
        if word.strip() == '':
            print('不要输入空字符啊kora')
            continue

        wordInfo = reptile(word)
        if wordInfo is not None:
            for exp in wordInfo:
                print(exp)
                persist(exp)
