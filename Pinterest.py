# -*- coding: cp936 -*-
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from Queue import Queue
import time
import re
import requests
import sys
import threading

stdout = sys.stdout
stdin = sys.stdin
stderr = sys.stderr
reload(sys)
sys.stdout = stdout
sys.stdin = stdin
sys.stderr = stderr
sys.setdefaultencoding('utf8')

browser = webdriver.Chrome()
cond = threading.Condition()
queue = Queue()  # image url
num = 1


# login
def login(login, pw):
    url = 'https://www.pinterest.com/login/'
    # set timeout
    browser.set_page_load_timeout(60)
    # load page
    try:
        browser.get(url)
    except TimeoutException:
        print u'time out after 60s when loading page'
        # stop loading page
        browser.execute_script('window.stop()')
    # input email
    try:
        browser.find_element_by_name('id').send_keys(login)
        print u'input email success!'
    except:
        print u'input email error!'
    time.sleep(3)
    # input password
    try:
        browser.find_element_by_name('password').send_keys(pw)
        print u'input password success!'
    except:
        print u'input password error!'
    time.sleep(10)
    # click and login
    try:
        browser.find_element_by_css_selector('button[type="submit"]').click()
        print u'click continue success!'
    except:
        print u'click continue error!'


class Producer(threading.Thread):
    def run(self):
        global queue
        # 每轮都刷新一次，更新页面，然后开始爬取所有图片url，最后刷新
        while True:
            content = browser.page_source
            reg = r'https://s-media-cache-ak0.pinimg.com/originals/.+?\.jpg 4x'
            imglist = re.findall(reg, content)
            # 输向queue输入新的数据时需要上锁
            if cond.acquire():
                for img in imglist:
                    img = img.replace(" 4x", '')
                    queue.put(img)
                print 'push new ' + str(len(imglist)) + ' to queue.'
                cond.notify()  # 唤醒Comsumer
                cond.release()
            print 'refresh'
            try:
                browser.refresh()
            except Exception as e:
                print u'Exception found', e
                continue
            time.sleep(15)


class Comsumer(threading.Thread):
    def run(self):
        global num
        global queue
        while True:

            # 如果上锁了，说明生产者正在使用queue，此时不能进入
            if cond.acquire():
                if queue.empty():
                    cond.wait()  # 让Comsumer等待
                img = queue.get()
                try:
                    pic = requests.get(img, timeout=10)
                except  requests.exceptions.ConnectionError:
                    print u'downloading current image failed'
                    continue
                except  requests.exceptions.ConnectTimeout:
                    print u'downloading current image failed'
                    continue
                except  requests.exceptions.Timeout:
                    print u'downloading current image failed'
                    continue
                print str(num) + '.jpg is downloaded.'
                string = "D:\\pinterest\\jpg name\\" + str(num) + ".jpg"
                fp = open(string, 'wb')
                fp.write(pic.content)
                fp.close()
                num += 1
                print 'queue.qsize=' + str(queue.qsize())
                cond.release()


if __name__ == '__main__':
    email = raw_input('please input your email:')
    pw = raw_input('please input your password:')
    file = open(r"D:\pinterest\jpg name\num.txt")
    num = file.read()
    num = int(num)
    file.close()
    login(login=email, pw=pw)
    print 'sleep 15s'
    time.sleep(15)
    print 'start to crawl'
    producer = Producer()
    comsumer = Comsumer()
    producer.start()
    comsumer.start()
    
    if num == 3000:
        producer.join()
        comsumer.join()
        file = open(r"D:\pinterest\jpg\num.txt", 'w')
        file.write(str(num))
        file.close()
        print u'Program terminated normally'


