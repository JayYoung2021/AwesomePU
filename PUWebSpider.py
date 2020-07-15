import re
import requests
from lxml import etree


def unescape(text):
    text = text.replace('&quot;', '"')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&nbsp;', ' ')
    return text


def parse_one_page(html):
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


def parse_one_activity(html):
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
    sid = ''
    number = ''
    password = ''
    college = ''
    tribe = ''
    grade = ''

    def __init__(self, sid, number, password, college='', tribe=''):
        # TODO mobile login
        self.sid = sid
        self.number = str(number)
        self.password = str(password)

        self.college = college
        self.tribe = tribe
        self.grade = '20' + re.search('\\d+', self.tribe)[0][:2]

    def get_one_activity(self, get_url):
        post_url = 'http://pocketuni.net/index.php?app=home&mod=Public&act=doLogin'
        post_data = {
            'sid': self.sid,
            'number': self.number,
            'password': self.password,
            'remember': 'on'
        }
        session = requests.Session()
        session.post(post_url, data=post_data)
        return session.get(get_url).text

    def filtered_activities(self):
        p = 0
        list_ = []
        while True:
            p += 1
            url = 'http://njtech.pocketuni.net/index.php?app=event&mod=School&act=board&cat=all&&p=' + str(p)
            html_page = requests.get(url).text
            items = parse_one_page(html_page)

            count = 0
            for item in items:
                if item['status'] == ['活动已结束']:
                    count += 1
            if count >= 10:
                break

            for item in items:
                if item['status'] != ['活动已结束']:
                    bool_ = False
                    info_activity = parse_one_activity(self.get_one_activity(item['link']))
                    if info_activity['tribe'] is None:
                        if (self.college in info_activity['college']) or (info_activity['college'] == '全部'):
                            if (self.grade in info_activity['grade']) or (info_activity['grade'] == '全部'):
                                bool_ = True
                    else:
                        if self.tribe in info_activity['tribe']:
                            bool_ = True
                    if bool_ is True:
                        list_.append(info_activity)
        return list_
