from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import pandas as pd
import numpy as np
import urllib.request
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import requests
import re
import decimal
# 공시 url 수집
def url_crawling():
    report_name = soup.select('.table_list td > a')
    for i in report_name:
        text = i.get_text()
        # 원하는 보고서 명 정규표현식으로 기재
        if_report = re.search('영업\(잠정\)실적\(공정공시\)', text)
        if not if_report == None:
            report_url = i.get('href')
            report_url_list.append('http://dart.fss.or.kr/' + report_url)
# 공시일 수집
def updated_date_crawling():
    updated = soup.select('.table_list tbody > tr')
    for i in updated:
        text = i.get_text()
        if_updated = re.search('영업\(잠정\)실적\(공정공시\)', str(text))
        if not if_updated == None:
            updated = i.select_one('td:nth-of-type(5)').string
            updated_date.append(updated)
# 네이버 시가총액과 업종 수집
def market_capital_and_category():
    for i in company_name:
        url = 'https://www.naver.com/'
        driver.get(url)
        time.sleep(1.5)
        html = driver.page_source
        soup = BeautifulSoup(html, features='lxml')
        driver.find_element_by_xpath('//*[@id="query"]').click()
        time.sleep(0.5)
        driver.find_element_by_xpath('//*[@id="query"]').send_keys(i)
        time.sleep(0.5)
        driver.find_element_by_xpath('//*[@id="query"]').send_keys(Keys.RETURN)
        time.sleep(0.5)
        html = driver.page_source
        soup = BeautifulSoup(html, features='lxml')
        # 시가총액
        capital = soup.select_one('.mc > dl > dd').get_text()
        market_cap.append(capital)
        # 업종
        try:
            search = soup.find('span',text=re.compile(r'업종'))
            category.append(search.next_sibling.string)
        except:
            category.append('-')




#타겟페이지 (dart 최근공시)
url ='http://dart.fss.or.kr/dsac001/mainY.do#'
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument('window-size=1920x1080')
options.add_argument('User-Agent : Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36')
driver = webdriver.Chrome(executable_path='/Users/macintoshhd/Desktop/Coding/Python/chromedriver', options=options)
driver.get(url)
time.sleep(2)
html = driver.page_source
soup = BeautifulSoup(html, features='lxml')

# 수집 리스트 목록
report_url_list = []
sorted_report_url_list = []

company_name = []
category = []
market_cap = []
Sales_Q = []
Operating_income_Q = []
Net_income_Q = []
Sales_YOY = []
Operating_income_YOY = []
Net_income_YOY = []
Sales_QOQ = []
Operating_income_QOQ = []
Net_income_QOQ = []
updated_date = []

# 최근공시 크롤링
date = soup.select('#date > .date_choice > a')
for i in date:
    # 수집날짜 출력
    print(i.string.strip())
    print('수집중...')
n = +1
for i in range(len(date)-1):
    i = i + n
    driver.find_element_by_xpath('//*[@id="date"]/p/a['+str(i)+']').click()
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, features='lxml')
    # 1페이지에서 수집
    url_crawling()
    # 공시일 크롤링
    updated_date_crawling()
    time.sleep(1)
    try:
        page_num = soup.select('.page_list > input[value]')
        for i in page_num:
            page_num_value = i.get('value')
            for i in page_num_value:
                driver.find_element_by_xpath('//*[@id="listContents"]/div[2]/input['+str(i)+']').click()
                time.sleep(1)
                html = driver.page_source
                soup = BeautifulSoup(html, features='lxml')
                time.sleep(1)
                # 나머지 페이지에서 수집
                url_crawling()
                # 공시일 크롤링
                updated_date_crawling()

    except:
        None

# 데이터 가공(공시에서 테이블 url 뽑아내기)
for i in report_url_list:
    html = driver.get(i)
    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, features='lxml')
    # 기업명수집
    c_name = soup.select_one('.view_tit p a[title]').string
    c_name = company_name.append(c_name)
    time.sleep(1)
    find_table = soup.find('iframe', {'id' : 'ifrm'})
    table_url = find_table.get('src')
    time.sleep(1)
    table_url = 'http://dart.fss.or.kr' + table_url
    sorted_report_url_list.append(table_url)
# 데이터 가공(테이블 url에서 정보추출)
for i in sorted_report_url_list:
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
    html = requests.get(i, headers = headers).text
    soup = BeautifulSoup(html, features='lxml')
    time.sleep(1)
    # 단위 백만원을 억원으로 조정
    unit = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(2) > td:nth-of-type(2) > span')
    # 지배기업 소유주지분 순이익 판별
    owners = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(13) > td > span')
    # 수집리스트에 넣을 데이터 항목
    try:
        sales_Q = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(5) > td:nth-of-type(3) > span').string.replace(',','')
    except:
        Sales_Q.append('None')
    else:
        # 계산의 용의를 위해 비어있는 항목의 '-'를 0으로 변경
        sales_Q = re.sub('\A-\Z', '0', sales_Q)
        # 백만원 단위를 찾아 억원으로 변경
        if_sales_Q = re.search('백만원', str(unit))
        if not if_sales_Q == None:
            # 반올림
            sales_Q = round(decimal.Decimal(sales_Q),-2)
            sales_Q = str(int(sales_Q))[:-2]
            Sales_Q.append(sales_Q)
        else:
            Sales_Q.append(sales_Q)

    try:
        operating_income_Q = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(7) > td:nth-of-type(3) > span').string.replace(',','')
    except:
        Operating_income_Q.append('None')
    else:
        operating_income_Q = re.sub('\A-\Z', '0', operating_income_Q)
        if_operating_income_Q = re.search('백만원', str(unit))
        if not if_operating_income_Q == None:
            operating_income_Q = round(decimal.Decimal(operating_income_Q),-2)
            operating_income_Q = str(int(operating_income_Q))[:-2]
            Operating_income_Q.append(operating_income_Q)
        else:
            Operating_income_Q.append(operating_income_Q)

    try:
        net_income_Q = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(11) > td:nth-of-type(3) > span').string.replace(',','')
    except:
        Net_income_Q.append('None')
    else:
        # 당기순이익 지배기업 소유주지분 순이익 구분
        if_net_income_attributable_to_owners = re.search('지배기업', str(owners))
        if not if_net_income_attributable_to_owners == None:
            net_income_Q = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(13) > td:nth-of-type(3) > span').string.replace(',','')
        else:
            net_income_Q = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(11) > td:nth-of-type(3) > span').string.replace(',','')
        net_income_Q = re.sub('\A-\Z', '0', net_income_Q)
        if_net_income_Q = re.search('백만원', str(unit))
        if not if_net_income_Q == None:
            net_income_Q = round(decimal.Decimal(net_income_Q),-2)
            net_income_Q = str(int(net_income_Q))[:-2]
            Net_income_Q.append(net_income_Q)
        else:
            Net_income_Q.append(net_income_Q)

    try:
        sales_YOY = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(5) > td:nth-of-type(6) > span').string.replace(',','')
    except:
        Sales_YOY.append('None')
    else:
        sales_YOY = re.sub('\A-\Z', '0', sales_YOY)
        if_sales_YOY = re.search('백만원', str(unit))
        if not if_sales_YOY == None:
            sales_YOY = round(decimal.Decimal(sales_YOY),-2)
            sales_YOY = str(int(sales_YOY))[:-2]
            Sales_YOY.append(sales_YOY)
        else:
            Sales_YOY.append(sales_YOY)

    try:
        operating_income_YOY = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(7) > td:nth-of-type(6) > span').string.replace(',','')
    except:
        Operating_income_YOY.append('None')
    else:
        operating_income_YOY = re.sub('\A-\Z', '0', operating_income_YOY)
        if_operating_income_YOY = re.search('백만원', str(unit))
        if not if_operating_income_YOY == None:
            operating_income_YOY = round(decimal.Decimal(operating_income_YOY),-2)
            operating_income_YOY = str(int(operating_income_YOY))[:-2]
            Operating_income_YOY.append(operating_income_YOY)
        else:
            Operating_income_YOY.append(operating_income_YOY)

    try:
        net_income_YOY = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(11) > td:nth-of-type(6) > span').string.replace(',','')
    except:
        Net_income_YOY.append('None')
    else:
        if_net_income_attributable_to_owners = re.search('지배기업', str(owners))
        if not if_net_income_attributable_to_owners == None:
            net_income_YOY = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(13) > td:nth-of-type(6) > span').string.replace(',','')
        else:
            net_income_YOY = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(11) > td:nth-of-type(6) > span').string.replace(',','')
        net_income_YOY = re.sub('\A-\Z', '0', net_income_YOY)
        if_net_income_YOY = re.search('백만원', str(unit))
        if not if_net_income_YOY == None:
            net_income_YOY = round(decimal.Decimal(net_income_YOY),-2)
            net_income_YOY = str(int(net_income_YOY))[:-2]
            Net_income_YOY.append(net_income_YOY)
        else:
            Net_income_YOY.append(net_income_YOY)

    try:
        sales_QOQ = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(5) > td:nth-of-type(4) > span').string.replace(',','')
    except:
        Sales_QOQ.append('None')
    else:
        sales_QOQ = re.sub('\A-\Z', '0', sales_QOQ)
        if_sales_QOQ = re.search('백만원', str(unit))
        if not if_sales_QOQ == None:
            sales_QOQ = round(decimal.Decimal(sales_QOQ),-2)
            sales_QOQ = str(int(sales_QOQ))[:-2]
            Sales_QOQ.append(sales_QOQ)
        else:
            Sales_QOQ.append(sales_QOQ)

    try:
        operating_income_QOQ = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(7) > td:nth-of-type(4) > span').string.replace(',','')
    except:
        Operating_income_QOQ.append('None')
    else:
        operating_income_QOQ = re.sub('\A-\Z', '0', operating_income_QOQ)
        if_operating_income_QOQ = re.search('백만원', str(unit))
        if not if_operating_income_QOQ == None:
            operating_income_QOQ = round(decimal.Decimal(operating_income_QOQ),-2)
            operating_income_QOQ = str(int(operating_income_QOQ))[:-2]
            Operating_income_QOQ.append(operating_income_QOQ)
        else:
            Operating_income_QOQ.append(operating_income_QOQ)

    try:
        net_income_QOQ = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(11) > td:nth-of-type(4) > span').string.replace(',','')
    except:
        Net_income_QOQ.append('None')
    else:
        if_net_income_attributable_to_owners = re.search('지배기업', str(owners))
        if not if_net_income_attributable_to_owners == None:
            net_income_QOQ = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(13) > td:nth-of-type(4) > span').string.replace(',','')
        else:
            net_income_QOQ = soup.select_one('#XFormD1_Form0_RepeatTable0 > tbody > tr:nth-of-type(11) > td:nth-of-type(4) > span').string.replace(',','')
        net_income_QOQ = re.sub('\A-\Z', '0', net_income_QOQ)
        if_net_income_QOQ = re.search('백만원', str(unit))
        if not if_net_income_QOQ == None:
            net_income_QOQ = round(decimal.Decimal(net_income_QOQ),-2)
            net_income_QOQ = str(int(net_income_QOQ))[:-2]
            Net_income_QOQ.append(net_income_QOQ)
        else:
            Net_income_QOQ.append(net_income_QOQ)

# 시가총액 크롤링
market_capital_and_category()
# 데이터프레임 생성
insert_category = {'종목명' : company_name,
                '업종' : category,
                '시가총액' : market_cap,
                '매출액(Q)' : Sales_Q,
                '영업이익(Q)' : Operating_income_Q,
                '순이익(Q)' : Net_income_Q,
                '매출액(YOY)' : Sales_YOY,
                '영업이익(YOY)' : Operating_income_YOY,
                '순이익(YOY)' : Net_income_YOY,
                '매출액(QOQ)' : Sales_QOQ,
                '영업이익(QOQ)' : Operating_income_QOQ,
                '순이익(QOQ)' : Net_income_QOQ,
                '공시일' : updated_date,
                }

dart_earning_quarter = pd.DataFrame.from_dict(insert_category, orient='index')
dart_earning_quarter.index.name = 'Num'
dart_earning_quarter.columns.name = 'Info'


dart_earning_quarter.transpose().to_excel('dart_earning_quarter.xlsx', encoding='utf-8-sig')





print(dart_earning_quarter.transpose())
driver.close()
