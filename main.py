import requests
import robot_config as rc
import time
import _thread as thread
from threading import Timer
import tokens

birth_data = dict()


def init():
    syslog('系统初始化')
    load_birth()
    syslog('初始化完成')


def print_motd():
    otmsg = '[今日公告]\n'
    have_motd = False
    motd = open("motd.data", "r")
    for lines in motd.readlines():
        have_motd = True
        otmsg += lines
    otmsg += '\n'
    motd.close()
    otmsg += dbgmsg("每日公告处理完毕")
    otmsg += '\n'
    if have_motd:
        motd = open("motd.data", "w")
        motd.truncate()
        motd.close()
        return otmsg
    else:
        return ''


def get_earthquake():
    quakelist = []
    f = open("quake_reported.txt", "r")
    reported_quakes = f.readlines()
    f.close()
    f = open("quake_reported.txt", "w")
    res = requests.request('GET', 'http://news.ceic.ac.cn/ajax/google')
    if res.status_code != 200:
        return 'error'
    resj = res.json()
    for quake in resj:
        if float(quake['M']) >= 7.0:
            if time.time() - time.mktime(time.strptime(quake['O_TIME'], '%Y-%m-%d %H:%M:%S')) <= 60 * 60 * 1:
                if quake['CATA_ID'] + '\n' not in reported_quakes:
                    quakelist.append("地点:" + quake["LOCATION_C"] + " 震级:" + str(quake['M']))
                    f.write(quake['CATA_ID'] + '\n')
    f.close()
    return quakelist


def send_shuoshuo(msg):

    # gtk = rc.gtk
    cookies, gtk = tokens.get_token()
    cookies_str = ''
    for cookie in cookies:
        cookies_str += (cookie['name'] + '=' + cookie['value'] + '; ')
    # print(cookies_str)
    url = rc.url

    querystring = {"qzonetoken": rc.qztoken,
                   "g_tk": gtk}

    payload = {
        'code_version': '1',
        'con': msg,
        'feedversion': '1',
        'format': 'fs',
        'hostuin': rc.qq,
        'paramstr': '1',
        'pic_template': '',
        'qzreferrer': 'https://user.qzone.qq.com/' + rc.qq,
        'richtype': '',
        'richval': '',
        'special_url': '',
        'subrichtype': '',
        'syn_tweet_verson': '1',
        'to_sign': '0',
        'ugc_right': '1',
        'ver': '1',
        'who': '1'
    }

    headers = {
        'origin': "https://user.qzone.qq.com",
        'user-agent': rc.user_agent,
        'content-type': "application/x-www-form-urlencoded",
        'accept': "*/*",
        'dnt': "1",
        'referer': "https://user.qzone.qq.com/" + rc.qq,
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6,zh;q=0.4",
        # 'cookie': 'p_skey=' + pskey
        'cookie': cookies_str
    }
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    # print(response.text)
    syslog('说说发送请求，返回状态' + str(response.status_code))


def syslog(w):
    print("[系统日志] " + w)


def dbgmsg(debugwords):
    if rc.debug_mode:
        return '[调试信息] ' + debugwords + '\n'
    else:
        return ''


def get_weather():
    weathers = requests.request("GET", rc.weather_apiurl + 'id=' + rc.weather_apicityid + '&APPID=' + rc.weather_apikey)
    if weathers.status_code != 200:
        return ''
    weather_json = weathers.json()
    tmpmin = weather_json['list'][weather_json['cnt'] - 1]['main']['temp'] - 273
    tmpmax = weather_json['list'][weather_json['cnt'] - 1]['main']['temp'] - 273
    desc = ''
    desc += '[天气]\n'
    if str(round(tmpmin, 1)) != str(round(tmpmax, 1)):
        desc += ('温度:' + str(round(tmpmin, 1)) + "～" + str(round(tmpmax, 1)) + '度\n')
    else:
        desc += ('温度:' + str(round(tmpmax, 1)) + '度\n')
    desc_condition = 0
    desc += '天气:'
    for node in weather_json['list'][weather_json['cnt'] - 1]['weather']:
        if desc_condition >= 1:
            desc += ' then '
        desc += node['main']
        desc_condition += 1
    desc += '\n'
    return desc


def one_word_cn():
    res = requests.request("GET", rc.yiju_cn)
    if res.status_code == 200:
        return res.text
    else:
        return ''


def one_word_en():
    res = requests.request("GET", rc.yiju_en)
    if res.status_code == 200:
        return res.json()['content'] + "\n" + res.json()['note']
    else:
        return ''


def print_oneword():
    otmsg = '[每日一句]\n'
    receive_msg = ''
    if rc.yiju_mode_cn:
        receive_msg += one_word_cn()
    else:
        receive_msg += one_word_en()
    if receive_msg == '':
        otmsg += dbgmsg('每日一句模块错误')
        return otmsg
    otmsg += receive_msg
    otmsg += '\n'
    otmsg += dbgmsg('每日一句模块加载正常')
    otmsg += '\n'
    return otmsg


def load_birth():
    f = open("birth.data", "r")
    raw_birthdata = f.readlines()
    for person in raw_birthdata:
        person_name = person.split(",")[0]
        person_birth = person.split(",")[1].replace('\n', '')
        if person_birth not in birth_data.keys():
            birth_data[person_birth] = []
            birth_data[person_birth].append(person_name)
        else:
            birth_data[person_birth].append(person_name)
    syslog('生日信息初始化完成')


def get_birth():
    if time.strftime("%m-%d", time.localtime()) in birth_data.keys():
        return birth_data[time.strftime("%m-%d", time.localtime())]


def print_title():
    otmsg = '--[通信一班小喇叭 每日播报]--\n'
    otmsg += time.strftime("%m月%d日\n", time.localtime())
    birth_got = get_birth()
    if birth_got:
        otmsg += '祝 '
        for person in birth_got:
            otmsg += (person + ' ')
        otmsg += '生日快乐!\n'
    otmsg += dbgmsg('每日播报模块运行正常')
    otmsg += '\n'
    return otmsg


def print_debug():
    otmsg = ''
    if rc.debug_mode:
        otmsg += dbgmsg('模块测试模式')
        otmsg += ('版本号: ' + rc.version + '\n')
        otmsg += ('作者:' + rc.author + '\n')
        otmsg += ('QQ:' + rc.qq + '\n')
        otmsg += ('当前时间' + str(time.time()) + ' ticks\n')
        otmsg += ('定时发送:' + str(rc.time_send_mode))
        otmsg += '\n'
        otmsg += dbgmsg('调试信息模块加载正常')
        otmsg += '\n'
    return otmsg


def print_weather():
    otmsg = get_weather()
    if otmsg != '':
        otmsg += dbgmsg("天气信息模块加载正常")
    else:
        otmsg += dbgmsg("天气信息模块错误")
        return otmsg
    otmsg += '\n'
    return otmsg


def print_quake():
    rec_quake = get_earthquake()
    if rec_quake:
        otmsg = ''
        otmsg += '[紧急播报:地震]\n'
        for quakei in rec_quake:
            otmsg += (quakei + '\n')
        send_shuoshuo(otmsg)


def exec_daily():
    outmsg = ''
    outmsg += print_title()
    outmsg += print_motd()
    outmsg += print_debug()
    outmsg += print_weather()
    outmsg += print_oneword()
    send_shuoshuo(outmsg)
    # print(outmsg)


def exec_emer_quake():
    time.sleep(3)
    while True:
        print_quake()
        time.sleep(180)


init()
time.sleep(3600 * 3)
exec_daily_timer = Timer(3600 * 24, exec_daily(), tuple())
exec_daily_timer.start()
thread.start_new_thread(exec_emer_quake, tuple())
while 1:
    pass

