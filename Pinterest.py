# -*- coding: cp936 -*-
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import time
import re
import requests
import sys
stdout = sys.stdout
stdin = sys.stdin
stderr = sys.stderr
reload(sys)
sys.stdout = stdout
sys.stdin = stdin
sys.stderr = stderr
sys.setdefaultencoding('utf8')

browser = webdriver.Chrome()
#login
def login(login, pw):
      url = 'https://www.pinterest.com/login/'
      #set timeout
      browser.set_page_load_timeout(120)
      #load page
      try:
            browser.get(url)
      except TimeoutException:
            print u'time out after 120s when loading page'
            #stop loading page
            browser.execute_script('window.stop()')
      time.sleep(10)
      #input email
      try:
            browser.find_element_by_name('id').send_keys(login)
            print u'input email success!'
      except:
            print u'input email error!'
      time.sleep(3)
      #input password
      try:
            browser.find_element_by_name('password').send_keys(pw)
            print u'input password success!'
      except:
            print u'input password error!'
      time.sleep(10)
      #click and login
      try:
            browser.find_element_by_css_selector('button[type="submit"]').click()
            print u'click continue success!'
      except:
            print u'click continue error!'


#crawl
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
                  print u'downloading current image failed'
                  continue
            except  requests.exceptions.ConnectTimeout:
                  print u'downloading current image failed'
                  continue
            except  requests.exceptions.Timeout:
                  print u'downloading current image failed'
                  continue
            print str(num)+'.jpg is downloaded.'
            string = "D:\\pinterest\\jpg name\\" + str(num) + ".jpg"
            fp = open(string,'wb')
            fp.write(pic.content)
            fp.close()
            num+=1
      
      reg = r'alt="(.*?)"'
      namelist = re.findall(reg,content)
      for name in namelist:
            print name
            file = open(r"D:\pinterest\jpg name\name.txt",'a')
            file.write(name + '\n')
            file.close()
      return True


num = 1
if __name__ == '__main__':
      email = raw_input('please input your email:')
      pw = raw_input('please input your password:')
 
      file = open(r"D:\pinterest\jpg name\num.txt")
      num = file.read()
      num = int(num)
      file.close()
      login(login=email,pw=pw)
      print 'sleep 60s'
      time.sleep(60)
      print u'start crawl!'
      while True:
            if not getImage():
                  break
            try:
                  browser.refresh()               
            except Exception as e: 
                  print u'Exception found',e
                  continue
            print u'refresh successfully'
            time.sleep(30)
            
            print u'next'
            
      file = open(r"D:\pinterest\jpg\num.txt",'w')
      file.write(str(num))
      file.close()
      print u'Program terminated normally'

                                                
