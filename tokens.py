from selenium import webdriver
import requests
import time
import robot_config as rc


def get_token():

    login_uin = rc.qq
    pwd = rc.pwd

    s = requests.Session()

    driver = webdriver.Chrome()
    driver.set_window_size(1000, 600)
    driver.get('https://mobile.qzone.qq.com')
    driver.find_element_by_id('u').clear()
    driver.find_element_by_id('u').send_keys(login_uin)
    driver.find_element_by_id('p').clear()
    driver.find_element_by_id('p').send_keys(pwd)
    driver.find_element_by_id('go').click()

    while True:
        qzonetoken = driver.execute_script("return window.shine0callback")
        if qzonetoken:
            break
        time.sleep(0.1)
    cookies = driver.get_cookies()
    driver.quit()
    skey = ''
    cookies_ = {}
    for cookie in cookies:
        if cookie['name'] == 'p_skey':
            skey = cookie['value']
        cookies_[cookie['name']] = cookie['value']

    e = 5381
    for i in range(len(skey)):
        e = e + (e << 5)+ord(skey[i])
    g_tk = str(2147483647 & e)
    return cookies, g_tk
