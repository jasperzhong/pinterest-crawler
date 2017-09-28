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

metex = threading.Lock()
num = 1


# login
def login(login, pw, browser, timeout):
    url = 'https://www.pinterest.com/login/'
    # set timeout
    browser.set_page_load_timeout(timeout)
    # load page
    try:
        browser.get(url)
    except TimeoutException:
        print u'time out after 30s when loading page'
        # stop load
        while True:
            try:
                browser.execute_script('window.stop()')
                break
            except:
                pass

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
    def __init__(self, queue, browser, cond, id):
        super(Producer, self).__init__()
        self.queue = queue
        self.browser = browser
        self.cond = cond
        self.id = id

    def run(self):
        # 每轮都刷新一次，更新页面，然后开始爬取所有图片url，最后刷新
        while True:
            content = self.browser.page_source
            reg = r'https://s-media-cache-ak0.pinimg.com/originals/.+?\.jpg 4x'
            imglist = re.findall(reg, content)
            # 输向queue输入新的数据时需要上锁
            if self.cond.acquire():
                for img in imglist:
                    img = img.replace(" 4x", '')
                    self.queue.put(img)
                print 'push ' + str(len(imglist)) + ' new urls to the queue' + str(self.id)
                self.cond.notify()  # 唤醒Comsumer
                self.cond.release()
            print 'refresh'
            try:
                self.browser.refresh()
            except Exception as e:
                print u'Exception found', e
                continue
            time.sleep(15)


class Comsumer(threading.Thread):
    def __init__(self, queue, cond, id):
        super(Comsumer, self).__init__()
        self.queue = queue
        self.cond = cond
        self.id = id

    def run(self):
        global num
        while True:
            # 如果上锁了，说明生产者正在使用queue，此时不能进入
            if self.cond.acquire():
                if self.queue.empty():
                    self.cond.wait()  # 让Comsumer等待
                else:
                    while self.queue.empty() == False:
                        img = self.queue.get()
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
                        metex.acquire()
                        num += 1
                        metex.release()
                        print 'queue' + str(self.id) + '.qsize=' + str(self.queue.qsize())
                    self.cond.release()


if __name__ == '__main__':
    # email = raw_input('please input your email:')
    # pw = raw_input('please input your password:')
    email = 'izhongyuchen@163.com'
    pw = 'zyc759631647'
    file = open(r"D:\pinterest\jpg name\num.txt")
    num = file.read()
    num = int(num)
    file.close()
    # True Thread numbers is THREAD_NUM*2
    THREAD_NUM = 2
    browser = range(0, THREAD_NUM)
    queue = range(0, THREAD_NUM)
    cond = range(0, THREAD_NUM)
    for i in range(0, THREAD_NUM):
        browser[i] = webdriver.Chrome()
        queue[i] = Queue()
        cond[i] = threading.Condition()

    producer = range(0, THREAD_NUM)
    comsumer = range(0, THREAD_NUM)
    for i in range(0, THREAD_NUM):
        login(login=email, pw=pw, browser=browser[i], timeout=60 + i * 15)
        time.sleep(15)
        try:
            browser[i].refresh()
        except:
            pass
        print 'sleep 15s'
        time.sleep(15)
        producer[i] = Producer(queue=queue[i], browser=browser[i], cond=cond[i], id=i)
        comsumer[i] = Comsumer(queue=queue[i], cond=cond[i], id=i)
        print str(i) + ' start to crawl'
        producer[i].start()
        comsumer[i].start()

    if num == 3000:
        for i in range(0, THREAD_NUM):
            producer[i].join()
            comsumer[i].join()

        file = open(r"D:\pinterest\jpg\num.txt", 'w')
        file.write(str(num))
        file.close()
        print u'Program terminated normally'


