#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import requests
import getpass
from lxml import etree

class AuthserverLogin:

    URL_AUTHSERVER = 'http://authserver.gdut.edu.cn/authserver/login?service=http%3A%2F%2Fjxfw.gdut.edu.cn%2Fnew%2FssoLogin'

    HEADERS = {
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
        }

    def __init__(self):
        self._session = requests.session()
        self._session.headers = self.HEADERS
        self.__init_session()

    def __pre_post(self):
        dom = etree.HTML(self._session.get(self.URL_AUTHSERVER).text)
        form = dom.xpath('//*[@id="casLoginForm"]')[0]
        post_data = {i.attrib['name']:i.attrib['value'] for i in form if i.tag == 'input'}
        print('正在尝试统一认证中心密码登录......')
        post_data['username'] = input('请输入你的学号:\n')
        post_data['password'] = getpass.getpass('请输入你的登录密码:\n')
        return post_data
    
    def __init_session(self):
        dom = etree.HTML(self._session.post(self.URL_AUTHSERVER, data=self.__pre_post()).text)
        result = dom.xpath('//*[@id="msg"]/text()')
        if any(result):
            print(result[0])
            exit()
        print('登录成功')