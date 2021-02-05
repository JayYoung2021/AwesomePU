import os
import re
from html import unescape
from sys import exit
from time import sleep

import requests
from lxml import etree


def sleep_then_exit():
    sleep(3)
    exit()


class PU:
    def __init__(self, mobile: str, password: str) -> any:
        self.college = '计算机科学与技术学院'
        self.grade = '2019'

        post_data = {
            'mobile': mobile,
            'password': password,
            'remember': 'on'
        }
        self.session = requests.Session()
        self.session.post('https://pocketuni.net/index.php?app=home&mod=Public&act=doMobileLogin', data=post_data)

    def verification(self) -> bool:
        html = etree.HTML(self.session.get('https://pocketuni.net/index.php?app=home&mod=Public&act=doLogin').text)
        result = html.xpath('/html/head/script[1]/text()')
        _UID_ = re.search('\\d+', re.search('var _UID_ {3}=(.*)', result[0]).group(1)).group(0)
        return not (_UID_ == '0')

    def set_college_and_grade(self, college: str, grade: str) -> any:
        self.college = college
        self.grade = grade

    # def get_college_list(self) -> list:  # Get the college list of user's school
    #     chrome_options = Options()
    #     chrome_options.add_argument("--headless")
    #     browser = webdriver.Chrome(options=chrome_options)
    #     browser.get(self.session.get('https://pocketuni.net/index.php?app=home&mod=Public&act=Login').url)
    #     button = browser.find_element_by_id('sub2')
    #     button.click()
    #     html = etree.HTML(browser.page_source)
    #     result = html.xpath('/html/body/div[2]/div/div[3]/div[2]/div[1]/div[1]/div[2]/a/text()')
    #     return result

    def show_activities(self) -> any:
        no_activity = True
        p = 0
        num_per_page = 5
        while num_per_page * p < 100:
            p += 1
            url = f'https://njtech.pocketuni.net/index.php?app=event&mod=School&act=board&cat=all&&p={p}'
            parent_html = etree.HTML(requests.get(url).text)
            for i in range(1, num_per_page + 1):
                status = \
                    parent_html.xpath(f'/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[{i}]/div[3]/ul/li/text()')[0]
                # if status not in ['活动已结束', '报名已结束']:
                if True:
                    rewards = parent_html.xpath(
                        f'/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[{i}]/div[2]/div[4]/text()')
                    credit_hours = re.findall('\\d+', rewards[0])[0]
                    if credit_hours != '0':
                        link = \
                            parent_html.xpath(
                                f'/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[{i}]/div[2]/div[1]/a/@href')[0]
                        sub_html = etree.HTML(self.session.get(link).text)
                        content = sub_html.xpath('string(/html/body/div[1]/div[3]/div/div/div[1]/div[2])')
                        if re.search('可参与部落：(.*)', content) is None:
                            college = sub_html.xpath('/html/body/div[1]/div[3]/div/div/div[1]/div[2]/span[5]/text()')[0]
                            grade = unescape(re.search('活动年级：(.*)', content).group(1))
                            try:
                                surplus = re.search(r'剩余名额.*\n.*?(\d+)', content).group(1)
                            except AttributeError:
                                surplus = '无限制'
                            if (my_college in college) or (college == '全部'):
                                if (my_grade in grade) or (grade == '全部'):
                                    if surplus != '0':
                                        if no_activity:
                                            no_activity = False
                                        title = parent_html.xpath(
                                            f'/html/body/div[2]/div/div[3]/div[2]/div[1]/ul/li[{i}]/div[2]/div[1]/a/text()')
                                        print(f'活动名称：{unescape(title[0])}')

                                        print(f'实践学时：{credit_hours}')

                                        location = \
                                            sub_html.xpath('/html/body/div[1]/div[3]/div/div/div[1]/div[2]/a[1]/text()')[0]
                                        print(f'活动地点：{location}')

                                        time = re.search('活动时间：(.*)', content).group(1)
                                        print(f'活动时间：{time}')

                                        intro = sub_html.xpath('/html/body/div[1]/div[3]/div/div/div[2]/div[3]/text()')[
                                            0].strip()
                                        print(f'活动简介：{intro}')

                                        print()

        if no_activity:
            print('未找到符合要求的活动')
            sleep_then_exit()
        else:
            input('请按回车键退出应用')


if __name__ == '__main__':
    try:
        requests.get('https://njtech.pocketuni.net/')
    except requests.exceptions.ProxyError:
        print('未连接到互联网')
        sleep_then_exit()

    my_college = ''
    my_grade = ''
    my_mobile = ''
    my_password = ''

    configs_file = 'configs.txt'

    if not os.path.exists(configs_file):
        try:
            with open(file=configs_file, mode='w', encoding='utf-8') as f:
                my_college = input('请输入院系，然后按回车键（例：计算机科学与技术学院 注：法政学院请输入法学院):')
                f.write(f'{my_college}\n')
                my_grade = input('请输入年级，然后按回车键（例：2019）:')
                f.write(f'{my_grade}\n')
                my_mobile = input('请输入手机号，然后按回车键:')
                f.write(f'{my_mobile}\n')
                my_password = input('请输入密码，然后按回车键:')
                f.write(f'{my_password}\n')
        except PermissionError:
            print('请以管理员身份运行应用')
            sleep_then_exit()
    else:
        with open(file=configs_file, encoding='utf-8') as f:
            lines = f.readlines()
            try:
                my_college = lines[0][:-1]
                my_grade = lines[1][:-1]
                my_mobile = lines[2][:-1]
                my_password = lines[3][:-1]
            except IndexError:
                f.close()
                os.remove(configs_file)
                print('文件已损坏，请重新打开应用')
                sleep_then_exit()

    while True:
        demo = PU(my_mobile, my_password)
        if demo.verification():
            break
        else:
            print('手机号码错误或密码错误')
            my_mobile = input('请输入手机号，然后按回车键:')
            my_password = input('请输入密码，然后按回车键:')
            f = open(file=configs_file, encoding='utf-8')
            lines = f.readlines()
            f.close()
            with open(file=configs_file, mode='w', encoding='utf-8') as f:
                my_college = lines[0][:-1]
                f.write(f'{my_college}\n')
                my_grade = lines[1][:-1]
                f.write(f'{my_grade}\n')
                f.write(f'{my_mobile}\n')
                f.write(f'{my_password}\n')

    os.system('cls')
    demo.set_college_and_grade(my_college, my_grade)
    demo.show_activities()
