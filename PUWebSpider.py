import re
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def unescape(text):
    text = text.replace('&quot;', '"')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ')
    return text


def parse_one_page(html):  # str -> list
    items = []
    html = etree.HTML(html)
    for i in range(1, 10 + 1):
        link = html.xpath('/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[' + str(i) + ']/div[1]/a/@href')
        thumb = html.xpath('/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[' + str(i) + ']/div[1]/a/img/@src')
        title = html.xpath(
            '/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[' + str(i) + ']/div[2]/div[1]/a/text()')
        class_ = html.xpath(
            '/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[' + str(i) + ']/div[2]/div[2]/a/text()')
        time = html.xpath('/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[' + str(i) + ']/div[2]/div[3]/text()')
        author = html.xpath('/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[' + str(i) + ']/div[2]/div[4]/text()')
        reward = html.xpath('/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[' + str(i) + ']/div[2]/div[5]/text()')
        count = html.xpath('/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[' + str(i) + ']/div[2]/div[6]/text()')
        status = html.xpath('/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[' + str(i) + ']/div[3]/ul/li/text()')
        item = {
            'link': link[0],
            'thumb': thumb[0],
            'title': unescape(title[0]),
            'class': class_[0][1:-1],
            'time': time[0],
            'author': author[0].strip(),
            'hour': re.findall('\\d+', reward[0])[0],
            'point': re.findall('\\d+', reward[0])[2],
            'count': re.findall('\\d+', count[0].strip())[0],
            'status': status
        }
        items.append(item)
    return items


def parse_one_activity(html):  # str -> list
    html = etree.HTML(html)
    content = html.xpath('string(/html/body/div[1]/div[3]/div/div/div[1]/div[2])')
    dict_ = {
        'title': unescape(html.xpath('/html/body/div[1]/div[3]/div/div/div[1]/div[1]/text()')[0]),
        'author': re.search('归属组织：(.*)', content).group(1),
        'class': re.search('活动分类：(.*)', content).group(1),
        'location': html.xpath('/html/body/div[1]/div[3]/div/div/div[1]/div[2]/a[1]/text()')[0],
        'college': None,
        'grade': None,
        'tribe': None,
        'time': re.search('活动时间：(.*)', content).group(1),
        'reg': re.search('报名起止：(.*)', content).group(1),
        'clock_in': re.search('外勤打卡：(.*)', content).group(1),
        'cost': html.xpath('/html/body/div[1]/div[3]/div/div/div[1]/div[2]/a[2]/text()')[0].strip(),
        'exist': re.search('参加人数：(.*)', content).group(1),
        'surplus': re.search('剩余名额：(.*)', content).group(1),
        'contact': html.xpath('/html/body/div[1]/div[3]/div/div/div[1]/div[2]/a[3]/text()'),
        'intro': html.xpath('/html/body/div[1]/div[3]/div/div/div[2]/div[3]/text()')[0].strip(),
    }
    if re.search('可参与部落：(.*)', content) is None:
        dict_['college'] = html.xpath('/html/body/div[1]/div[3]/div/div/div[1]/div[2]/span[5]/text()')[0]
        dict_['grade'] = re.search('活动年级：(.*)', content).group(1)
    else:
        dict_['tribe'] = re.search('可参与部落：(.*)', content).group(1)
    if dict_['contact']:
        dict_['contact'] = dict_['contact'][0]
    return dict_


class PU:
    def __init__(self, sid, account, password):
        self.password = str(password)
        if sid is None:  # Judge login method
            self.mobile = str(account)
            self.post_url = 'http://pocketuni.net/index.php?app=home&mod=Public&act=doMobileLogin'  # Mobile login url
            post_data = {
                'mobile': self.mobile,
                'password': self.password,
                'remember': 'on'
            }
        else:
            self.sid = str(sid)
            self.number = str(account)
            self.post_url = 'http://pocketuni.net/index.php?app=home&mod=Public&act=doLogin'  # Sid and number login url
            post_data = {
                'sid': self.sid,
                'number': self.number,
                'password': self.password,
                'remember': 'on'
            }
        self.session = requests.Session()
        self.session.post(self.post_url, data=post_data)

        self.college = None
        self.tribe = None
        self.grade = None

    def verification(self):  # Verify whether the login  process is successful
        html = etree.HTML(self.session.get('http://pocketuni.net/index.php?app=home&mod=Public&act=doLogin').text)
        result = html.xpath('/html/head/script[1]/text()')
        var = re.search('var _UID_ {3}=(.*)', result[0]).group(1)
        _UID_ = re.search('\\d+', var).group(0)
        if _UID_ == '0':
            return False
        else:
            return True

    def set_college(self, college, tribe):  # Set user's college and tribe
        self.college = college
        self.tribe = tribe.split()
        self.grade = '20' + re.search('\\d+', self.tribe[0])[0][:2]

    def get_college_list(self):  # Get the college list of user's school
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        browser = webdriver.Chrome(options=chrome_options)
        browser.get(self.session.get('http://pocketuni.net/index.php?app=home&mod=Public&act=Login').url)
        button = browser.find_element_by_id('sub2')
        button.click()
        html = etree.HTML(browser.page_source)
        result = html.xpath('/html/body/div[2]/div/div[3]/div[2]/div[1]/div[1]/div[2]/a/text()')
        return result

    def filtered_activities(self):  # Filter out expired and other unavailable activities
        p = 0
        list_ = []
        while True:
            p += 1
            url = 'http://njtech.pocketuni.net/index.php?app=event&mod=School&act=board&cat=all&&p=' + str(p)
            html_page = requests.get(url).text
            items = parse_one_page(html_page)

            count = 0
            for item in items:
                if item['status'] != ['活动已结束']:
                    bool_ = False
                    info_activity = parse_one_activity(self.session.get(item['link']).text)
                    if info_activity['tribe'] is None:
                        if (self.college in info_activity['college']) or (info_activity['college'] == '全部'):
                            if (self.grade in info_activity['grade']) or (info_activity['grade'] == '全部'):
                                bool_ = True
                    else:
                        for item_ in self.tribe:
                            if item_ in info_activity['tribe']:
                                bool_ = True
                    if bool_ is True:
                        list_.append(info_activity)
                else:
                    count += 1
                    if count >= 10:
                        break  # Break point
            else:
                continue
            break
        return list_
