import sys
from PUWebSpider import *

try:  # Network monitoring module
    requests.get('http://njtech.pocketuni.net/')
except requests.exceptions.ProxyError:
    sys.exit()

# example = PU(None, '10086', 'password')
# example = PU('480', '10086', 'password')
# example.set_college('斯莱特林学院', '魔法类9.75')
print('输入 1 使用手机号登录')
print('输入 2 使用学号登录（南京工业大学独占）')
while True:
    while True:
        mode = input()
        if mode == '1':
            account = str(input('手机号：'))
            password = str(input('密码：'))
            example = PU(None, account, password)
            break
        elif mode == '2':
            sid = '480'
            account = str(input('学号：'))
            password = str(input('密码：'))
            example = PU(sid, account, password)
            break
        else:
            print('输入有误，请重试')
    if example.verification():
        print('登陆成功')
        break
    else:
        print('登录失败，请重试')

college_list = example.get_college_list()
for i in range(len(college_list)):
    print(i + 1, college_list[i])
college = college_list[int(input('学院序号：')) - 1]
class_ = input('班级：')
example.set_college(college, class_)

list_ = example.filtered_activities
page = 0
totalCount = len(list_)  # 内容总数量
loadCount = 10  # 每页加载数量
totalPage = (totalCount + loadCount - 1) // loadCount  # 所求总页数


def end(p):
    if totalCount - loadCount * (p + 1) < 0:
        return totalCount - loadCount * p
    else:
        return loadCount


if not list_:
    print('无可用活动')
else:
    for i in range(0, end(page)):
        print(i + 1, list_[i]['title'])
    while True:
        print('查看上一页输入"<" 查看活动详情输入序号 查看下一页输入">"')
        print('退出程序输入0')
        cmd = input('请输入命令：')
        if cmd == '<':
            if page > 0:
                page -= 1
            for i in range(loadCount * page, end(page)):
                print(i % 10 + 1, list_[i]['title'])
        elif cmd == '>':
            if page < totalPage - 1:
                page += 1
            for i in range(loadCount * page, end(page)):
                print(i % 10 + 1, list_[i]['title'])
        elif ('0' <= cmd <= '9') or cmd == '10':
            if cmd == '0':
                break
            # for k, v in list_[loadCount * page + int(cmd) - 1].items():
            #     print(k, v)
            tmp = loadCount * page + int(cmd) - 1
            print('活动名称：' + list_[tmp]['title'])
            print('归属组织：' + list_[tmp]['author'])
            print('活动分类：' + list_[tmp]['class'])
            print('活动地点：' + list_[tmp]['location'])
            print('活动院系：', end='')
            if list_[tmp]['college'] is None:
                print("限制")
            else:
                print(list_[tmp]['college'])
            print('活动年级：', end='')
            if list_[tmp]['grade'] is None:
                print("限制")
            else:
                print(list_[tmp]['grade'])
            print('可参与部落：', end='')
            if list_[tmp]['tribe'] is None:
                print("无限制")
            else:
                print(list_[tmp]['tribe'])
            print('活动时间：' + list_[tmp]['time'])
            print('报名起止：' + list_[tmp]['reg'])
            print('外勤打卡：' + list_[tmp]['clock_in'])
            print('参加费用：' + list_[tmp]['cost'])
            print('参加人数：' + list_[tmp]['exist'])
            print('剩余名额：' + list_[tmp]['surplus'])
            print('联系方式：', end='')
            if list_[tmp]['contact'] is None:
                print("无限制")
            else:
                print(list_[tmp]['contact'])
            print('活动简介：' + list_[tmp]['intro'])
            for i in range(loadCount * page, end(page)):
                print(i % 10 + 1, list_[i]['title'])
        else:
            print('输入有误，请重试')
