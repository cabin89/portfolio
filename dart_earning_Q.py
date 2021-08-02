# -*- coding: utf-8 -*-
# from urllib.request import urlopen
# from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from functools import partial
import itertools
import functools
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common import actions
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from decimal import Decimal
# from multiprocessing import Manager, Pool, freeze_support, Lock
# import multiprocessing
from datetime import date
from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
import numpy as np
import urllib.request
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import requests
import re
import os
import random
import csv
import json
import math
import urllib
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
from my_tools import market_capital__price__category__ticker
start_time = time.time()

# # 크롬웹드라이버 설정 / 헤드리스 옵션
# options = webdriver.ChromeOptions()
# # options.headless = True
# options.add_argument('window-size=1920x1080')
# options.add_argument("--start-maximized")
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--ignore-ssl-errors')
# options.add_experimental_option('excludeSwitches', ['enable-automation'])    #차단우회 ?
# options.add_experimental_option('useAutomationExtension', False)
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument('Referer : https://ko.aliexpress.com/')
# options.add_argument('User-Agent : Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
# driver = webdriver.Chrome(executable_path='C:/Users/find-us/Desktop/Shaw/Find_python/chromedriver.exe', options=options)


# dart 최근공시에서 영업(잠정)실적(공정공시) url 가져오기 / parameters(공시명regex, 검색을 원하는 일수)
def dart_latest_report(re_report_name, days):
    report_list = []
    with requests.Session() as s:
        referer = {'Referer' : 'http://dart.fss.or.kr/dsac001/main.do'}
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
        s.headers.update(referer)
        s.headers.update(headers)
        print_date = dt.now() - timedelta(days=days)
        print(print_date.strftime('%Y-%m-%d'))
        print('          page.1')
    
        # 첫페이지
        data = {
            'currentPage': '1',
            'maxResults': '',
            'maxLinks': '',
            'sort': '',
            'series': '',
            'pageGrouping': 'Y',
            'mdayCnt': days,
            'selectDate': '',
            'textCrpCik': '',
        }
        res = s.post('http://dart.fss.or.kr/dsac001/search.ax', data=data)
        time.sleep(1)
        html = res.text
        soup = BeautifulSoup(html, features='lxml')
        if re.search('검색된 자료가 없습니다', html) == None:
            total_page = re.search('(\d+건)', str(soup.select_one('.table_tit'))).group(1).replace('건', '')
            report = soup.select('tr > td:nth-of-type(3)')
            report = [report_list.append('{}{}'.format('http://dart.fss.or.kr', r.a.get('href'))) for r in report if not re.search('영업\(잠정\)', str(r)) == None]
            if int(total_page) <= 100:  #한페이지에 100개, 100개 넘으면 다음 페이지 추출
                pass
            elif int(total_page) > 100:
                page_amount = math.ceil(int(total_page)/100)
                page_amount = [p+1 for p in range(page_amount)]
                del page_amount[0]  #첫페이지 제거
                def rest_of_page(days, page):
                    print('{}{}'.format('          page.',page))
                    data = {
                        'currentPage': page,
                        'maxResults': '',
                        'maxLinks': '',
                        'sort': '',
                        'series': '',
                        'pageGrouping': 'Y',
                        'mdayCnt': days,
                        'selectDate': '',
                        'textCrpCik': '',
                    }
                    res = s.post('http://dart.fss.or.kr/dsac001/search.ax', data=data)
                    time.sleep(1)
                    html = res.text
                    soup = BeautifulSoup(html, features='lxml')
                    if re.search('검색된 자료가 없습니다', html) == None:
                        total_page = re.search('(\d+건)', str(soup.select_one('.table_tit'))).group(1).replace('건', '')
                        report = soup.select('tr > td:nth-of-type(3)')
                        report = [report_list.append('{}{}'.format('http://dart.fss.or.kr', r.a.get('href'))) for r in report if not re.search('영업\(잠정\)', str(r)) == None]
                    elif not re.search('검색된 자료가 없습니다', html) == None:
                        return 
                list(map(partial(rest_of_page, days), page_amount))
        elif not re.search('검색된 자료가 없습니다', html) == None:
            pass
    return report_list


# 리포트 데이터 추출
def get_report_data(report_list):
    global num, sales_Q, sales_QoQ, sales_QoQ_percent, sales_YoY, sales_YoY_percent, operation_profit_Q, operation_profit_QoQ, operation_profit_QoQ_percent, operation_profit_YoY, operation_profit_YoY_percent, net_income_Q, net_income_QoQ, net_income_QoQ_percent, net_income_YoY, net_income_YoY_percent
    report_data_list = []
    with requests.Session() as s:
        referer = {'Referer' : 'http://dart.fss.or.kr/dsac001/main.do'}
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
        s.headers.update(referer)
        s.headers.update(headers)
        num += 1
        
        res = s.get(report_list)
        time.sleep(1)
        html = res.text
        soup = BeautifulSoup(html, features='lxml')
        company_name = soup.select_one('title').get_text().split('/')[0].strip()
        report_name = soup.select_one('title').get_text().split('/')[1].strip()
        upload_date = soup.select_one('title').get_text().split('/')[2].strip()
        print('{}{}{}{}{}'.format(num, '. ', company_name, '  ', report_list))
        query = re.search('href:\s"javascript:\sviewDoc\(\'(\d+?)\',\s\'(\d+?)\'', html).group(1,2)
        rcpNo = query[0]
        dcmNo = query[1]

        table_url = s.get(f'http://dart.fss.or.kr/report/viewer.do?rcpNo={rcpNo}&dcmNo={dcmNo}&eleId=0&offset=0&length=0&dtd=HTML').text
        try:
            table = pd.read_html(table_url, match='동 정보는 잠정치로서 향후 확정치와는 다를 수 있음', header=(1,2), index_col=[0,1], na_values='-')[0]
        except:
            report_data_list = []
            return report_data_list
        time.sleep(1)
        
        if not re.search('정정일자', table_url) == None:
            check_edited_report = '정정'
        else:
            check_edited_report = ''

        # 0 : 당기실적,	 1 : 전기실적, 	2 : 전기대비증감율(%),  3 : 전년동기실적,  4 : 전년동기대비증감율(%)
        sales = [str(data).replace('NA', '0').replace('nan', '0') for data in table.loc['매출액', '당해실적'].values[0]]
        operation_profit = [str(data).replace('NA', '0').replace('nan', '0') for data in table.loc['영업이익', '당해실적'].values[0]]
        net_income = [str(data).replace('NA', '0').replace('nan', '0') for data in table.loc['당기순이익', '당해실적'].values[0]]

        # 백만원, 억원, 조원 (억원으로 통일)
        money_unit = table.columns.tolist()
        if not re.search('백만원', str(money_unit)) == None:
            sales_Q = round(Decimal(sales[0]) / Decimal('100'))
            sales_QoQ = round(Decimal(sales[1]) / Decimal('100'))
            sales_QoQ_percent = sales[2].replace('%', '')
            sales_YoY = round(Decimal(sales[3]) / Decimal('100'))
            sales_YoY_percent = sales[4].replace('%', '')

            operation_profit_Q = round(Decimal(operation_profit[0]) / Decimal('100'))
            operation_profit_QoQ = round(Decimal(operation_profit[1]) / Decimal('100'))
            operation_profit_QoQ_percent = operation_profit[2].replace('%', '')
            operation_profit_YoY = round(Decimal(operation_profit[3]) / Decimal('100'))
            operation_profit_YoY_percent = operation_profit[4].replace('%', '')
            net_income_Q = round(Decimal(net_income[0]) / Decimal('100'))
            net_income_QoQ = round(Decimal(net_income[1]) / Decimal('100'))
            net_income_QoQ_percent = net_income[2].replace('%', '')
            net_income_YoY = round(Decimal(net_income[3]) / Decimal('100'))
            net_income_YoY_percent = net_income[4].replace('%', '')
        elif not re.search('조원', str(money_unit)) == None:
            sales_Q = round(Decimal(sales[0]) * Decimal('10000'))
            sales_QoQ = round(Decimal(sales[1]) * Decimal('10000'))
            sales_QoQ_percent = sales[2].replace('%', '')
            sales_YoY = round(Decimal(sales[3]) * Decimal('10000'))
            sales_YoY_percent = sales[4].replace('%', '')

            operation_profit_Q = round(Decimal(operation_profit[0]) * Decimal('10000'))
            operation_profit_QoQ = round(Decimal(operation_profit[1]) * Decimal('10000'))
            operation_profit_QoQ_percent = operation_profit[2].replace('%', '')
            operation_profit_YoY = round(Decimal(operation_profit[3]) * Decimal('10000'))
            operation_profit_YoY_percent = operation_profit[4].replace('%', '')
            
            net_income_Q = round(Decimal(net_income[0]) * Decimal('10000'))
            net_income_QoQ = round(Decimal(net_income[1]) * Decimal('10000'))
            net_income_QoQ_percent = net_income[2].replace('%', '')
            net_income_YoY = round(Decimal(net_income[3]) * Decimal('10000'))
            net_income_YoY_percent = net_income[4].replace('%', '')
        elif not re.search('억원', str(money_unit)) == None:
            sales_Q = int(sales[0])
            sales_QoQ = int(sales[1])
            sales_QoQ_percent = sales[2].replace('%', '')
            sales_YoY = int(sales[3])
            sales_YoY_percent = sales[4].replace('%', '')

            operation_profit_Q = int(operation_profit[0])
            operation_profit_QoQ = int(operation_profit[1])
            operation_profit_QoQ_percent = operation_profit[2].replace('%', '')
            operation_profit_YoY = int(operation_profit[3])
            operation_profit_YoY_percent = operation_profit[4].replace('%', '')
            
            net_income_Q = int(net_income[0])
            net_income_QoQ = int(net_income[1])
            net_income_QoQ_percent = net_income[2].replace('%', '')
            net_income_YoY = int(net_income[3])
            net_income_YoY_percent = net_income[4].replace('%', '')
        
        #네이버에서 회사명으로 증권정보가 검색이 안될경우 검색가능한 사명으로 수정
        company_name = company_name.replace('쌍용씨앤이', '쌍용C&E').replace('유나이티드', '유나이티드제약')    
        company_name_quote = urllib.parse.quote(company_name)
        # my_tools 스크립트에서 함수참조 > [종목명, 종목코드, 업종, 시가총액, 현재가]
        company_info= market_capital__price__category__ticker(company_name_quote)

        data_list = [
            company_name, #종목명
            company_info[1],#종목코드
            company_info[2], #업종
            company_info[3], #시가총액
            sales_Q, #매출액(Q)
            sales_QoQ, #매출액(QoQ)
            sales_QoQ_percent, #매출액증감률(QoQ, %)
            sales_YoY, #매출액(YoY)
            sales_YoY_percent, #매출액증감률(YoY, %)
            operation_profit_Q, #영업이익(Q)
            operation_profit_QoQ, #영업이익(QoQ)
            operation_profit_QoQ_percent, #영업이익증감률(QoQ, %)
            operation_profit_YoY, #영업이익(YoY)
            operation_profit_YoY_percent, #영업이익증감률(YoY, %)
            net_income_Q, #순이익(Q)
            net_income_QoQ, #순이익(QoQ)
            net_income_QoQ_percent, #순이익증감률(QoQ, %)
            net_income_YoY, #순이익(YoY)
            net_income_YoY_percent, #순이익증감률(YoY, %)
            upload_date, #공시일
            check_edited_report, #정정공시여부
            report_name, #공시명
            report_list, #공시url
        ]
        report_data_list.append(data_list)
    return report_data_list


# 엑셀로 저장
def make_excel(df):
    today = round(time.time()*1000)          # 오늘
    file_name ='{}{}{}'.format('영업잠정실적공시(', dt.fromtimestamp(round(today,-4)/1000).strftime('%Y-%m-%d'), ').xlsx')
    save_path = '{}{}{}'.format(os.path.dirname(os.path.abspath(__file__)), '\\', file_name)
    with pd.ExcelWriter(save_path, mode='w', engine='openpyxl') as writer:
        df.to_excel(writer, index=False, encoding='utf-8-sig')
          



if __name__ == '__main__':
# 세션열기, 로그인 쿠키 적용
    days = 70    #검색하려는 일수
    days = [i for i in range(days)]
    report_list = list(map(functools.partial(dart_latest_report, '영업\(잠정\)'), days))
    report_list = sum(report_list, [])
    
    print('{}{}{}'.format('검색된 리포트 : ', len(report_list), '개'))
   
    num = 0
    report_data_list = list(map(get_report_data, report_list))     #리포트에서 데이터를 추출하여 리스트에 담는다
    report_data_list = sum(report_data_list, [])
    df = pd.DataFrame(report_data_list)
    df.columns = ['종목명', '종목코드', '업종', '시가총액', '매출액(Q)', '매출액(QoQ)', '매출액증감률(QoQ, %)', '매출액(YoY)', '매출액증감률(YoY, %)', '영업이익(Q)', '영업이익(QoQ)', '영업이익증감률(QoQ, %)', '영업이익(YoY)', '업이익증감률(YoY, %)', '순이익(Q)', '순이익(QoQ)', '순이익증감률(QoQ, %)', '순이익(YoY)', '순이익증감률(YoY, %)', '공시일', '정정공시여부', '공시명', '공시url']
    
    make_excel(df)

    print('Working time : {} sec'.format(time.time() - start_time))
    print('------Finish------')