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
import csv
import re

# 키워드로드(아이템스카우트 아이템발굴 엑셀파일 가져와서 로드 https://itemscout.io/)
Keywords = []
keywords = pd.read_csv('Book1.csv')

for i in keywords:
    Keywords.append(i)

print(Keywords)

# 크롤링 리스트 목록
Keyword_name = []
Name = []
Price = []
Review_count = []
Sell_count = []
Upload_date = []
Link = []

# 크롤링시작
for Keyword in Keywords:
    url = 'https://search.shopping.naver.com/search/all?query={}&cat_id=&frm=NVSHATC'.format(urllib.parse.quote_plus(Keyword))
    driver = webdriver.Chrome(executable_path='/Users/macintoshhd/Desktop/Coding/Python/chromedriver')
    driver.get(url)
    time.sleep(1)
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
    html = requests.get(url, headers = headers).text
    # html = driver.page_source


    # 스크롤
    for i in range(1):#( )안에 스크롤 반복횟수 입력
        body = driver.find_element_by_tag_name("body")
        body.send_keys(Keys.END)
        time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, features='lxml')

    product_list_ad = soup.select('.basicList_item__2XT81.ad')
    product_list = soup.select('.basicList_item__2XT81')

    # 가격비교상품 항목 제거
    sorted_list = []
    for i in product_list:
        if i not in product_list_ad:
            compare = re.search('basicList_compare__3AjuT', str(i))
            if compare == None:
                sorted_list.append(i)

    # 정보수집, 괄호안에 판매자순위 기입(보통 1,2위)
    for i in sorted_list[0:1]:
        # 키워드
        Keyword_name.append(Keyword)
        # 상품명
        try:
            name = i.find('a', {'class' : 'basicList_link__1MaTN'}).string
            Name.append(name)
        except:
            Name.append('None')
        # 가격
        try:
            price = i.find('span', {'class' : 'price_num__2WUXn'}).string
            Price.append(price.replace('원',''))
        except:
            Price.append('None')
        # 리뷰수
        try:
            review_count = i.select('.basicList_etc_box__1Jzg6 > a')[0].get_text()
            if_review_text = re.search('리뷰', review_count)
            if not if_review_text == None:
                Review_count.append(review_count.replace('리뷰',''))
            else:
                Review_count.append('None')
        except:
            Review_count.append('None')
        # 판매수
        try:
            sell_count = i.select('.basicList_etc_box__1Jzg6 > a')[1].get_text()
            if_sell_count = re.search('구매건수', sell_count)
            if not if_sell_count == None:
                Sell_count.append(sell_count.replace('구매건수',''))
            else:
                Sell_count.append('None')
        except:
            Sell_count.append('None')
        # 등록일
        try:
            upload_date = i.select('.basicList_etc_box__1Jzg6 > span')[0].get_text()
            if_upload_date = re.search('등록일', upload_date)
            if not if_upload_date == None:
                Upload_date.append(upload_date)
            else:
                Upload_date.append('None')
        except:
            Upload_date.append('None')
        # 링크
        try:
            link = i.find('a', {'class' : 'thumbnail_thumb__3Agq6'}).get('href')
            Link.append(link)
        except:
            Link.append('None')

    driver.close()


# 데이터프레임 생성
insert_category = {'키워드' : Keyword_name,
                '상품명' : Name,
                '가격' : Price,
                '리뷰수' : Review_count,
                '구매건수' : Sell_count,
                '업로드일자' : Upload_date,
                '링크' : Link
                }

smartstore_prduct_search = pd.DataFrame.from_dict(insert_category, orient='index')
smartstore_prduct_search.index.name = 'Num'
smartstore_prduct_search.columns.name = 'Info'


smartstore_prduct_search.transpose().to_excel('smartstore_prduct_search.xlsx', encoding='utf-8-sig')

print(smartstore_prduct_search.transpose())
