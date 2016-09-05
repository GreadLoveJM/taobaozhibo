# coding=utf-8
from marionette import Marionette
import os
import sys
import pickle
import json
import urlparse
import random
import time
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import requests
import re
import logging
from retrying import retry
from multiprocessing.pool import ThreadPool
from datetime import datetime
import writes

nowtime='%d'%(time.time()*1000)
class cookieexception(Exception):
    def __init__(self,url):
        talent().refresh_cookie(url)
class myexception(Exception):
    def __init__(self):
        logging.warning('HTTPConnectionPool(): Read timed out.')
class checkexception(Exception):
    def __init__(self,jsurl):
        logging.warning('check {} or taobao.com\'s bug?'.format(jsurl) )

class talent(object):
    def __init__(self):
        self.db=writes.Content()
        self.session=requests.session()
        self.check_cookie()
        self.change_proxy()

    def change_proxy(self):
        with open('taobao_live/document/proxy') as f:
            lines=f.readlines()
            proxy_lst=[]
            for each in lines:
                proxy_lst.append(re.sub('\s+', '', each))
            proxy=random.choice(proxy_lst)
            self.proxy=proxy
            return self.proxy

    def md5(self,str):
        import hashlib
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()

    def check_cookie(self):
        with open('./taobao_live/cookie', 'r') as f:
            self.session.cookies=pickle.load(f)
        with open('./taobao_live/token', 'r') as f:
            self.token=f.readline()

    def refresh_cookie(self,url):
        logging.warning('cookie is useless,refreshing cookie ...')
        fire_fox=webdriver.Firefox(firefox_binary=FirefoxBinary('/opt/firefox-45.2.0/firefox'))
        fire_fox.get(url)
        time.sleep(10)
        cooklst= fire_fox.get_cookies()
        fire_fox.quit()

        token=''
        for each in cooklst:
            if each['name']=='_m_h5_tk':
                token= each['value']
                break
        with open('./taobao_live/token','w') as tokenf:
            tokenf.write(token.split('_')[0])
        cook1=";".join(['{}={}'.format(each['name'],each['value']) for each in cooklst])
        cookie_dict={'Cookie':'thw=cn;'+cook1}
        cookies = requests.utils.cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True)
        with open('./taobao_live/cookie', 'w') as f:
            pickle.dump(cookies, f)
        self.check_cookie()

    def get_sign(self,type):
        if type=='userid':
            pre_sign=self.token+'&'+nowtime+'&12574478&{"creatorId":"'+self.user_id+'"}'
            sign=self.md5(pre_sign)
            return sign
        if type=='id':
            pre_sign=self.token+'&'+nowtime+'&12574478&{"liveId":"'+self.id+'"}'
            sign=self.md5(pre_sign)
            return sign
        raise myexception('type is wrong')

    @retry(stop_max_attempt_number=3)
    def _extract_json(self,jsurl,headers):
        try:
            html=self.session.get(jsurl,headers=headers
                                  ,proxies={'http':self.proxy}
                                  ,timeout=5).text
            _html=json.loads(re.search('mtopjsonp2\((.*?)\)', html,re.S).group(1))
            ret=_html['ret']
        except Exception,e:
            self.change_proxy()
            raise myexception()

        if 'SUCCESS' in ret[0] and  _html['data'] is not None:
            status=_html['data']['status']
            # title=_html['data']['title']
            # location=_html['data']['location']
            if status=='0':
                status=1
                onlines=_html['data']['joinCount']
                totalnum=_html['data']['totalJoinCount']
                accountid=_html['data']['broadCaster']['accountId']
                return {'onlines':str(onlines),'totalnum':str(totalnum),'is_live':int(status),'authorid':str(accountid),'realtime':datetime.now()}
            else:
                raise checkexception(jsurl)
        if 'FAIL_SYS_USER_VALIDATE' in ret[0]:
            print html
            self.change_proxy()
            logging.warning('proxy is wrong...try to change proxy...')
            raise cookieexception(self.url)
        if 'FAIL_SYS_TOKEN_EXOIRED' in ret[0]:
            print html
            logging.warning('refresh cookie...')
            raise cookieexception(self.url)


        # try:
        #     onlines=re.search('"joinCount":"(\d+)"', html).group(1)
        #     totalnum=re.search('"totalJoinCount":"(\d+)"', html).group(1)
        #     status=re.search('"status":"(\d+)"', html).group(1)
        #     accountid=re.search('"accountId":"(\d+)"', html).group(1)
        #     if status=='0':
        #         status=1
        #     else:
        #         status=0
        #     return {'onlines':str(onlines),'totalnum':str(totalnum),'is_live':str(status),'authorid':str(accountid),'realtime':datetime.now()}
        # except:
        #     print ""
        #     print html
        #
        #     raise myexception(self.url)

    def get_taobao_live_by_userid(self):

        def get_taobao_live1():
            sign=self.get_sign('userid')
            jsurl='http://api.m.taobao.com/h5/mtop.guide.video.livedetail/2.0/?' \
                  'appKey=12574478&t={}&sign={}&api=mtop.guide.video.liveDetail&v=2.0&type=jsonp&' \
                  'dataType=jsonp&timeout=20000&callback=mtopjsonp2&' \
                  'data=%7B%22creatorId%22%3A%22{}%22%7D'.format(nowtime,sign,self.user_id)
            headers = {'GET': '',

                'Host': "api.m.taobao.com",
                'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36",
                'Referer': 'http://huodong.m.taobao.com/act/talent/live.html?userId={}'.format(self.user_id)
                }
            try:
                return self._extract_json(jsurl,headers)
            except:
                return False


        return get_taobao_live1()

    def get_taobao_live_by_id(self):

        def get_taobao_live():
            sign=self.get_sign('id')
            jsurl='http://api.m.taobao.com/h5/mtop.guide.video.livedetail/2.0/?' \
                  'appKey=12574478&t={}&sign={}&api=mtop.guide.video.liveDetail&v=2.0&type=jsonp&dataType=jsonp&' \
                  'timeout=20000&callback=mtopjsonp2&data=%7B%22liveId%22%3A%22{}%22%7D'.format(nowtime,sign,self.id)

            headers = {'GET': '',

                'Host': "api.m.taobao.com",
                'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36",
                'Referer': 'http://huodong.m.taobao.com/act/talent/live.html?id={}'.format(self.id)
                }

            try:
                return self._extract_json(jsurl,headers)
            except:
                return False

        return get_taobao_live()


    def start_crawl(self,url):
        self.url=url
        _user_id=re.search('userId=(\d+)', url)
        if _user_id:
            self.user_id=_user_id.group(1)
            return self.get_taobao_live_by_userid()

        _id=re.search('id=(\d+)', url)
        if _id:
            self.id=_id.group(1)
            return self.get_taobao_live_by_id()

    def start(self):
        while(1):
            url=set()
            with open('./taobao_live/url_watching','r') as f:
                lines=f.readlines()
                for line in lines:
                    url.add(re.sub('\s+', '' , line))
            with open('./taobao_live/url_watching','w') as f1:
                f1.write("")
            url=list(url)
            with open('./taobao_live/url_watching','a') as f2:
                time1=datetime.now()
                for each in url:
                    result= self.start_crawl(each)
                    if result:
                        if result['is_live']==1:
                            f2.write(each+'\n')
                        s=result['authorid'],result['onlines'],result['totalnum'],result['is_live'],result['realtime']
                        print s

                        self.db.insertIntoDB(s)

                time2=datetime.now()
                timediff=(time2-time1).seconds
                print timediff
                if int(timediff)<20:
                    time.sleep(20-timediff)
                else:
                    self.change_proxy()

if __name__ == '__main__':

    p=talent()
    p.start()
    # get_sign(1,1)