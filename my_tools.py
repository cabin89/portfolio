# -*- coding: utf-8 -*-
# from __future__ import division
# from urllib.request import urlopen
# from urllib.parse import quote_plus
# from urllib import parse
from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common import actions
# from selenium.webdriver.common.action_chains import ActionChains
from decimal import Decimal, DecimalException, BasicContext
from multiprocessing import Manager, Pool, freeze_support, Lock
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from functools import reduce

import datetime
import itertools
import functools
import socket
import browser_cookie3
import datetime
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
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:!eNULL:!MD5'
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

start_time = time.time()

def random_time_sleep_short(time_second):
    random_float = random.random()
    time.sleep(time_second + random_float)


#크롬웹드라이버 설정 / 헤드리스 옵션
# options = webdriver.ChromeOptions()
# # options.headless = True
# options.add_argument('window-size=1920x1080')
# options.add_argument("--start-maximized")
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--ignore-ssl-errors')
# options.add_experimental_option('excludeSwitches', ['enable-automation'])   #차단우회 
# options.add_experimental_option('useAutomationExtension', False)            #차단우회 
# options.add_argument('--disable-blink-features=AutomationControlled')       #차단우회 
# options.add_argument('Referer : https://world.taobao.com/')
# options.add_argument('User-Agent : Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
# driver = webdriver.Chrome(executable_path='C:/Users/find-us/Desktop/Shaw/Find_python/chromedriver.exe', options=options)


'''네이버 검색 > 종목코드, 시가총액, 업종 가져오기 (변수는 회사명 리스트로 전달)'''
def market_capital__price__category__ticker(company_name):
    with requests.Session() as s:
        referer = {'Referer' : 'https://www.naver.com/'}
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
        s.headers.update(referer)
        s.headers.update(headers)
        url = '{}{}'.format('https://search.naver.com/search.naver?query=', company_name)
        res = s.get(url)
        time.sleep(0.5)
        html = res.text
        soup = BeautifulSoup(html, features='lxml')
        try:
            market_capital = int(soup.select_one('.mc dd').get_text().replace('조', '').replace('억', '').replace(',', '').replace(' ', ''))
        except:
            market_capital = ''
        try:
            current_price = int(soup.select('.spt_con')[0].select_one('strong').get_text().replace(',', ''))
        except:
            current_price = ''
        try:
            ticker = soup.select_one('.t_nm').get_text()
        except:
            ticker = ''
        try:
            company_category = [l.select_one('.txt_info').get_text() for l in soup.select('.company_info li') if not re.search('업종', str(l)) == None][0]
        except:
            company_category = ''
        company_info_merge = [company_name, ticker, company_category, market_capital, current_price]
        return company_info_merge


'''네이버금융 > 종목분석 > Financial Summary 테이블 (변수는 종목코드 리스트로 전달)'''
def naver_finance_company_info(ticker):
    # for i in ticker_list:
    url = '{}{}'.format('https://finance.naver.com/item/coinfo.nhn?code=', ticker)
    res = s.get(url)
    time.sleep(0.5)
    html = res.text
    soup = BeautifulSoup(html, features='lxml')
    iframe = soup.select_one('#coinfo_cp').get('src')
    res = s.get(iframe)
    time.sleep(0.5)
    html = res.text
    soup = BeautifulSoup(html, features='lxml')
    # 네이버 주요재무정보
    fin_typ = 0
    freq_typ = 'Y'    # A: 전체, Y: 연간, Q: 분기
    encparam_query = re.search('encparam:\s\'(.+?)\'', html).group(1)
    id_query = re.search('\$\(\'#(.+?)\'\)\.html\(data\)', html).group(1)
    financial_summary_table_url = f'https://navercomp.wisereport.co.kr/v2/company/ajax/cF1001.aspx?cmp_cd={ticker}&fin_typ={fin_typ}&freq_typ={freq_typ}&encparam={encparam_query}&id={id_query}'
    headers = {
        'Referer' : '{}{}'.format('https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd=', ticker),
        'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    }
    table = pd.read_html(s.get(financial_summary_table_url, headers=headers).text, header=1, index_col=0, encoding='utf-8')[1]
    return table


'''5년 평균값(결측값이 있을경우 제외하고 계산 ex.2년평균, 3년평균)'''
def _5_years_average(index_name, table):    
    table = table.fillna(0)
    table = table.astype('str')
    per_row = table.loc[index_name]
    # per_tm4 = per_row[0]
    # per_tm3 = per_row[1]
    # per_tm2 = per_row[2]
    # per_tm1 = per_row[3]
    # per_t0 = per_row[4]
    # per_tp1 = per_row[5]
    # per_tp2 = per_row[6]
    # per_tp3 = per_row[7]
    denominator = [i for i in per_row[:5] if float(i) != 0]     # 어떤 년도에 결측치가 있을경우 몇 년도 분의 값이 있는지 구해서 분모로 사용
    if len(denominator) != 0:
        mean = round(sum(per_row[:5].apply(Decimal)) / Decimal(f'{len(denominator)}'), 2)
    elif len(denominator) == 0:
        mean = 'None'
    return mean


'''5년 연환산 평균값(결측값이 있을경우 제외하고 계산 ex.2년평균, 3년평균) ---수익률, ROE, ROA 등등 퍼센트 비교시 연환산으로---'''
def _5_years_anunalized(index_name, table):    
    table = table.fillna(0)
    table = table.astype('str')
    per_row = table.loc[index_name] 
    # per_tm4 = per_row[0]
    # per_tm3 = per_row[1]
    # per_tm2 = per_row[2]
    # per_tm1 = per_row[3]
    # per_t0 = per_row[4]
    # per_tp1 = per_row[5]
    # per_tp2 = per_row[6]
    # per_tp3 = per_row[7]
    denominator = [i for i in per_row[:5] if float(i) != 0]     # 어떤 년도에 결측치가 있을경우 몇 년도 분의 값이 있는지 구해서 분모로 사용
    if len(denominator) != 0:
        mean = list(map(lambda x: (Decimal(x)/Decimal('100')) + Decimal('1'), per_row[:5]))
        mean = reduce(lambda x, y: x * y, mean)
        mean = round((mean**(Decimal('1')/Decimal(str(len(denominator)))) - Decimal('1')) * Decimal('100'), 2)
    elif len(denominator) == 0:
        mean = 'None'
    return mean


'''EPS증가율(연환산)  변수 years는 리스트로 전달 ex.[4,1]    t-4 = 0 / t-3 = 1 / t-2 = 2 / t-1 = 3 / t0 = 4 / t+1 = 5 / t+2 = 6 / t+3 = 7'''
def eps_growth_rate(years, table):
    global growth_rate
    # table = table.fillna(0)   # 해당 연도에 데이터가 없을경우 NaN을 출력하기 위해 주석처리
    table = table.astype('str')
    eps_row = table.loc['EPS(원)'] 
    # print(eps_row)
    # eps_tm4 = eps_row[0]
    # eps_tm3 = eps_row[1]
    # eps_tm2 = eps_row[2]
    # eps_tm1 = eps_row[3]
    # eps_t0 = eps_row[4]
    # eps_tp1 = eps_row[5]
    # eps_tp2 = eps_row[6]
    # eps_tp3 = eps_row[7]
    if eps_row[years[0]] != 'nan' and eps_row[years[1]] != 'nan':  #값이 있는 경우에만 계산 
        year_count = years[1] - years[0]
        if Decimal(str(eps_row[years[0]])) > Decimal('0') and Decimal(str(eps_row[years[1]])) > Decimal('0'):
            growth_rate = round((((Decimal(eps_row[years[1]])/Decimal(eps_row[years[0]]))**(Decimal('1')/Decimal(str(year_count)))) - Decimal('1')), 4)
        elif Decimal(str(eps_row[years[0]])) < Decimal('0') and Decimal(str(eps_row[years[1]])) > Decimal('0'):
            growth_rate = '흑자전환'
        elif Decimal(str(eps_row[years[0]])) > Decimal('0') and Decimal(str(eps_row[years[1]])) < Decimal('0'):
            growth_rate = '적자전환'
        elif Decimal(str(eps_row[years[0]])) < Decimal('0') and Decimal(str(eps_row[years[1]])) < Decimal('0'):
            growth_rate = '적자지속'
    elif eps_row[years[0]] == 'nan' or eps_row[years[1]] == 'nan':  #값이 있는 경우에만 계산
        growth_rate = 'None'
    return growth_rate
    

'''현재 PER (현재가/EPS)'''
def current_per(current_price, table):
    table = table.astype('str')
    eps_row = table.loc['EPS(원)'] 
    eps_t0 = eps_row[4]
    c_price = current_price[4]
    if eps_t0 != 'nan':   #값이 있는 경우만 계산
        if Decimal(str(eps_t0)) > Decimal('0'):
            c_per = round(Decimal(str(c_price)) / Decimal(str(eps_t0)), 2)
        elif Decimal(str(eps_t0)) < Decimal('0'):
            c_per = 'None'
    elif eps_t0 == 'nan':   #값이 있는 경우만 계산
        c_per = 'None'
    return c_per


'''현재 PBR (현재가/BPS)'''
def current_pbr(current_price, table):
    table = table.astype('str')
    bps_row = table.loc['BPS(원)'] 
    bps_t0 = bps_row[4]
    c_price = current_price[4]
    if bps_t0 != 'nan':   #값이 있는 경우만 계산
        if Decimal(str(bps_t0)) > Decimal('0'):
            c_bps = round(Decimal(str(c_price)) / Decimal(str(bps_t0)), 2)
        elif Decimal(str(bps_t0)) < Decimal('0'):
            c_bps = 'None'
    elif bps_t0 == 'nan':   #값이 있는 경우만 계산
        c_bps = 'None'
    return c_bps


'''dart 재무제표 6년치 데이터프레임(변수조정으로 원하는 리포트 적용가능)'''
def dart(ticker):
    with requests.Session() as s:
        referer = {'Referer' : 'http://dart.fss.or.kr/dsab001/main.do'}
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
        s.headers.update(referer)
        s.headers.update(headers)
        textCrpCik = s.post('http://dart.fss.or.kr/corp/searchExistAll.ax', data={'textCrpNm': ticker})
        textCrpCik = textCrpCik.text
        data = {
            'currentPage': '1',
            'maxResults': '15',
            'maxLinks': '10',
            'sort': 'date',
            'series': 'desc',
            'textCrpCik': textCrpCik,
            'textCrpNm': ticker,
            'finalReport': 'recent',
            'startDate': '19990101',
            'endDate': datetime.date.today().strftime('%Y%m%d'),
            'publicType': 'A001',           #정기공시> A001 : 사업보고서, A002 : 반기보고서, A003 : 분기보고서
        }
        res = s.post('http://dart.fss.or.kr/dsab001/search.ax', data=data)
        html = res.text
        soup = BeautifulSoup(html, features='lxml')
        # 보고서
        reports = [['{}{}'.format('http://dart.fss.or.kr', i.a.get('href')), i.get_text().replace('\r','').replace('\n','').replace('\t','').strip()] for i in soup.select('tr > td:nth-of-type(3)')]
        
        # 연결재무제표
        report_list = [reports[0][0], reports[3][0]]    #최근 3년 : reports[0][0], 이어서 3년 : reports[0][3] ---> 합치면 총 6년치 자료
        def concatenate_report(report_list):
            get_report = s.get(report_list)   
            html = get_report.text
            find_query = re.search('연결재무제표.+?.viewDoc\((.+?)\).+?cnt', html, re.DOTALL).group(1)  #필요한 문서목차의 이름을 적용하여 원하는 리포트 가져오기
            find_query = re.findall('\'(.+?)\'', find_query)
            referer = {'Referer' : report_list}
            s.headers.update(referer)
            target_report = s.get(f'http://dart.fss.or.kr/report/viewer.do?rcpNo={find_query[0]}&dcmNo={find_query[1]}&eleId={find_query[2]}&offset={find_query[3]}&length={find_query[4]}&dtd={find_query[5]}')
            html = target_report.text
            table = pd.read_html(html)[1]   # [1] : 연결 재무상태표, [3] : 포괄손익계산서, [5] : 연결 자본변동표, [7] : 연결 현금흐름표
            return table
        get_report = list(map(concatenate_report, report_list))
        df_concatenate = pd.merge(get_report[0],get_report[1], how='outer', on='Unnamed: 0', sort=False).set_index('Unnamed: 0')
        
        #두 개의 재무상태표를 합칠 때 같은 인덱스 값은 중복제거 후 하나로 독립 인덱스와 같이 순서대로 정렬하기위해 사용한 함수
        from difflib import SequenceMatcher
        def merge_sequences(seq1,seq2):     # 공부해보기
            sm=SequenceMatcher(a=seq1,b=seq2)
            res = []
            for (op, start1, end1, start2, end2) in sm.get_opcodes():
                if op == 'equal' or op=='delete':
                    #This range appears in both sequences, or only in the first one.
                    res += seq1[start1:end1]
                elif op == 'insert':
                    #This range appears in only the second sequence.
                    res += seq2[start2:end2]
                elif op == 'replace':
                    #There are different ranges in each sequence - add both.
                    res += seq1[start1:end1]
                    res += seq2[start2:end2]
            return res
        sorted_index = merge_sequences(get_report[0]['Unnamed: 0'].tolist(),get_report[1]['Unnamed: 0'].tolist())
        df_concatenate = df_concatenate.reindex(sorted_index)
        print(df_concatenate)
# dart('086670')

if __name__ == '__main__':
    # 세션열기, 로그인 쿠키 적용
    with requests.Session() as s:
        # referer = {'Referer' : 'https://world.taobao.com/'}
        headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
        # s.headers.update(referer)
        s.headers.update(headers)

        # company_name_list = ['삼성전자', '에스엘', '현대모비스', '레이', '클래시스', 'HSD엔진']
        # company_name_list = ['삼양식품', '농심', '오리온', '오뚜기', '샘표식품', '대상', '풀무원', '우양', 'CJ제일제당']
        # company_name_list = ['nice평가정보', '나이스디앤비', '이크레더블', '한국기업평가']
        # company_name_list = ['DL이엔씨', 'HDC현대산업개발', '동원개발', '한신공영', '계룡건설', '한라', 'KCC건설', '대우건설' , 'SGC이테크건설']
        # company_name_list = ['비엠티', '하이록코리아', '디케이락', '성광벤드', '태광']
        # company_name_list = ['현대해상', '메리츠화재', '한화손해보험', '흥국화재', '삼성화재', 'DB손해보험']
        company_name_list = ['콜마비앤에이치', '노바렉스', '뉴트리', '서흥']
        # company_name_list = ['종근당', '종근당홀딩스']
        # company_name_list = ['다나와']
        test = list(map(market_capital__price__category__ticker, company_name_list))
        for i in test:
            print(i)

        # ticker_list = ['005930', '005850', '012330', '228670']
        ticker_list = [ticker[1] for ticker in test]
        test1 = list(map(naver_finance_company_info, ticker_list))
        
        per_5y_mean = list(map(functools.partial(_5_years_average, 'PER(배)'), test1))
        print(per_5y_mean)
        pbr_5y_mean = list(map(functools.partial(_5_years_average, 'PBR(배)'), test1))
        print(pbr_5y_mean)
        
        roe_5y_annualized = list(map(functools.partial(_5_years_anunalized, 'ROE(%)'), test1))
        print(roe_5y_annualized)
        roa_5y_annualized = list(map(functools.partial(_5_years_anunalized, 'ROA(%)'), test1))
        print(roa_5y_annualized)
        
        eps_growth_rate_1y = list(map(functools.partial(eps_growth_rate, [3,4]), test1))   #3년 평균 EPS증가율 기준)t0
        print(eps_growth_rate_1y)
        eps_growth_rate_3y = list(map(functools.partial(eps_growth_rate, [1,4]), test1))   #3년 평균 EPS증가율 기준)t0
        print(eps_growth_rate_3y)

        current_per = list(map(current_per, test, test1))
        print(current_per)
        current_pbr = list(map(current_pbr, test, test1))
        print(current_pbr)
       
        # 조정per = per은 수익가치, 자산가치, 배당가치 중에 수익가치만 반영 그래서 들고있는 현금을 시가총액에서 뺀뒤 per을 계산한것