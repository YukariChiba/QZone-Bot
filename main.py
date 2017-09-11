import requests
import robot_config as rc
import time


def send_shuoshuo(msg):
    url = rc.url

    querystring = {"qzonetoken": rc.qztoken,
                   "g_tk": rc.gtk}

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
        'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'accept': "*/*",
        'dnt': "1",
        'referer': "https://user.qzone.qq.com/" + rc.qq,
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6,zh;q=0.4",
        'cookie': rc.cookie
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
    weather_json = weathers.json()
    tmpmin = weather_json['list'][weather_json['cnt'] - 1]['main']['temp'] - 273
    tmpmax = weather_json['list'][weather_json['cnt'] - 1]['main']['temp'] - 273
    desc = ''
    desc += '[天气]\n'
    desc += ('温度:' + str(tmpmin) + "～" + str(tmpmax) + '\n')
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
    return res.text


def one_word_en():
    res = requests.request("GET", rc.yiju_en)
    return res.json()['content']


def print_oneword():
    otmsg = '[每日一句]\n'
    if rc.yiju_mode_cn:
        otmsg += one_word_cn()
    else:
        otmsg += one_word_en()
    otmsg += '\n'
    otmsg += dbgmsg('每日一句模块加载正常')
    otmsg += '\n'
    return otmsg


def print_debug():
    otmsg = dbgmsg('[模块测试模式]')
    otmsg += ('版本号: ' + rc.version + '\n')
    otmsg += ('作者:' + rc.author + '\n')
    otmsg += ('QQ:' + rc.qq + '\n')
    otmsg += ('当前时间' + str(time.time()) + ' ticks\n')
    otmsg += dbgmsg('调试信息模块加载正常')
    otmsg += '\n'
    return otmsg


def print_weather():
    otmsg = get_weather()
    otmsg += dbgmsg("天气信息模块加载正常")
    otmsg += '\n'
    return otmsg


outmsg = ''
outmsg += print_debug()
outmsg += print_weather()
outmsg += print_oneword()
# send_shuoshuo(outmsg)
print(outmsg)
