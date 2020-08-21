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


#타겟페이지 (쿠팡카테고리 클릭페이지) 120개보기 먼저 클릭
Target_channel ='https://www.coupang.com/np/categories/115673?listSize=120&brand=&offerCondition=&filterType=&isPriceRange=false&minPrice=&maxPrice=&page=1&channel=user&fromComponent=N&selectedPlpKeepFilter=&sorter=bestAsc&filter=&rating=0'


url = Target_channel
driver = webdriver.Chrome(executable_path='/Users/macintoshhd/Desktop/Coding/Python/chromedriver')
driver.get(Target_channel)
time.sleep(2)
# assert "YouTube" in driver.title

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
html = requests.get(url, headers = headers).text

body = driver.find_element_by_tag_name("body")

html = driver.page_source
soup = BeautifulSoup(html, features='lxml')

Name = []
Price_value = []
Out_of_stock = []
Price_info = []
Rating = []
Rating_total_count = []
Badge_rocket = []
Badge_falcon = []
Subscribable_info = []
Link = []
# 상품페이지 횟수 (+str(i)+)
page_count = [1,2,3,4,5,6,7,8,9]
for i in page_count:
    target_adress = 'https://www.coupang.com/np/categories/115673?listSize=120&brand=&offerCondition=&filterType=&isPriceRange=false&minPrice=&maxPrice=&page='+str(i)+'&channel=user&fromComponent=N&selectedPlpKeepFilter=&sorter=bestAsc&filter=&rating=0'
    html = requests.get(target_adress, headers = headers).text
    soup = BeautifulSoup(html, features='lxml')

    all_product_id_list = soup.select('#productList li')
    product_id_list = [soup.select('#productList li')[n]['id'] for n in range(0, len(all_product_id_list))]


    for i in product_id_list:
        selected_product = soup.find('li', {'id' : i})

        name = selected_product.find('div', {'class' : 'name'}).string.replace('\n','')
        Name.append(name)

        price_value = selected_product.find('strong', {'class' : 'price-value'}).string
        Price_value.append(price_value)

        try:
            out_of_stock = selected_product.find('div', {'class' : 'out-of-stock'}).string
            Out_of_stock.append(out_of_stock)
        except:
            Out_of_stock.append('None')

        try:
            rating = selected_product.find('em', {'class' : 'rating'}).string
            Rating.append(rating)
        except:
            Rating.append('None')

        try:
            rating_total_count = selected_product.find('span', {'class' : 'rating-total-count'}).string.replace('(','').replace(')','')
            Rating_total_count.append(rating_total_count)
        except:
            Rating_total_count.append('None')

        try:
            badge_rocket = selected_product.select_one('.badge.rocket > img').get('alt').replace('로켓배송', '1')
            Badge_rocket.append(badge_rocket)
        except:
            Badge_rocket.append('0')

        try:
            badge_falcon = selected_product.select_one('.badge.falcon > img').get('alt').replace('로켓직구', '1')
            Badge_falcon.append(badge_falcon)
        except:
            Badge_falcon.append('0')

        try:
            subscribable_info = selected_product.select_one('.subscribable-info > img').get('alt').replace('정기배송 가능', '1')
            Subscribable_info.append(subscribable_info)
        except:
            Subscribable_info.append('0')

        try:
            price_info = selected_product.select_one('.price-info').get_text().replace('\n','  ').replace('|','')
            Price_info.append(price_info)
        except:
            Price_info.append('None')

        link = selected_product.find('a', {'data-product-id' : i}).get('href')
        Link.append('https://www.coupang.com' + link)



insert_category = {'상품명' : Name,
                '가격' : Price_value,
                '품절' : Out_of_stock,
                '할인' : Price_info,
                '평점' : Rating,
                '상품평 수' : Rating_total_count,
                '로켓배송' : Badge_rocket,
                '로켓와우/직구' : Badge_falcon,
                '정기배송' : Subscribable_info,
                '링크' : Link
                }

coupang_category_best = pd.DataFrame.from_dict(insert_category, orient='index')
coupang_category_best.index.name = 'Num'
coupang_category_best.columns.name = 'Info'


coupang_category_best.transpose().to_excel('coupang_category_best1.xlsx', encoding='utf-8-sig')

# 차트분석용 상품명 데이타프레임
product_name_for_analysis = pd.DataFrame(Name, columns=['comment'])
product_name_for_analysis.to_csv('product_name_for_analysis.txt', index=True, sep=' ', header=None, encoding='utf-8-sig')

print(coupang_category_best.transpose())
print('Finish')
driver.close()
