# -*- coding: cp936 -*-
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import time
import re
import urllib
import requests

browser = webdriver.Chrome()
#登陆
def login(login, pw):
      url = 'https://www.pinterest.com/login/'
      #设置时限
      browser.set_page_load_timeout(60)
      #加载网页
      try:
            browser.get(url)
      except TimeoutException:
            print 'time out after 60s when loading page'
            #停止加载网页
            browser.execute_script('window.stop()')
      time.sleep(10)
      #输入账号邮箱
      try:
            browser.find_element_by_name('id').send_keys(login)
            print 'input email success!'
      except:
            print 'input email error!'
      time.sleep(3)
      #输入密码
      try:
            browser.find_element_by_name('password').send_keys(pw)
            print 'input password success!'
      except:
            print 'input password error!'
      time.sleep(3)
      #点击continue，登陆
      try:
            browser.find_element_by_css_selector('button[type="submit"]').click()
            print 'click continue success!'
      except:
            print 'click continue error!'


#爬图片
def getImage():
      global num
      content=browser.page_source
      reg = r'https://s-media-cache-ak0.pinimg.com/originals/.+?\.jpg 4x'
      imglist = re.findall(reg,content)
      
      for img in imglist:
            img = img.replace(" 4x",'')
            try:
                 pic = requests.get(img,timeout=10)
            except  requests.exceptions.ConnectionError:
                  print '当前图片下载失败'
                  continue
            except  requests.exceptions.ConnectTimeout:
                  print '当前图片下载失败'
                  continue
            except  requests.exceptions.Timeout:
                  print '当前图片下载失败'
                  continue
            print str(num)+'.jpg is downloaded.'
            string = "D:\\pinterest\\jpg\\" + str(num) + ".jpg"
            fp = open(string,'wb')
            fp.write(pic.content)
            fp.close()
            num+=1
      return True


num = 1
if __name__ == '__main__':
      email = raw_input('please input your email:')
      pw = raw_input('please input your password:')

      login(login=email,pw=pw)
      print 'sleep for 30s'
      time.sleep(30)
      print 'start crawl!'
      while getImage():
            try:
                  browser.refresh()
                  print 'refresh successfully'
            except Exception as e:
                  print 'Exception found',e
                  break
            time.sleep(30)
            print 'next'
            
      
      print 'Program terminated normally'

                                                
