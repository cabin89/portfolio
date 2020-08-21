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


#타겟채널 (이곳에 채널명을 입력하시오)
Target_channel ='https://www.coupang.com/'


url = Target_channel
driver = webdriver.Chrome(executable_path='/Users/macintoshhd/Desktop/Coding/Python/chromedriver')
driver.get(Target_channel)
time.sleep(2)
# assert "YouTube" in driver.title

# driver.find_element_by_xpath('').click()

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
html = requests.get(url, headers = headers).text

body = driver.find_element_by_tag_name("body")

html = driver.page_source
soup = BeautifulSoup(html, features='lxml')


# 지정 횟수 스크롤
for i in range(2): #( )안에 스크롤 반복횟수 입력
    body.send_keys(Keys.END)
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, features='lxml')
    all_categoryBest_car = soup.select('#categoryBest_car .hot-keyword a')
    categoryBest_car = [soup.select('#categoryBest_car .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_car))]
    all_categoryBest_womanclothe = soup.select('#categoryBest_womanclothe .hot-keyword a')
    categoryBest_womanclothe = [soup.select('#categoryBest_womanclothe .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_womanclothe))]
    all_categoryBest_manclothe = soup.select('#categoryBest_manclothe .hot-keyword a')
    categoryBest_manclothe = [soup.select('#categoryBest_manclothe .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_manclothe))]
    all_categoryBest_food = soup.select('#categoryBest_food .hot-keyword a')
    categoryBest_food = [soup.select('#categoryBest_food .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_food))]
    all_categoryBest_home_decoration = soup.select('#categoryBest_home_decoration .hot-keyword a')
    categoryBest_home_decoration = [soup.select('#categoryBest_home_decoration .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_home_decoration))]
    all_categoryBest_digital = soup.select('#categoryBest_digital .hot-keyword a')
    categoryBest_digital = [soup.select('#categoryBest_digital .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_digital))]
    all_categoryBest_office = soup.select('#categoryBest_office .hot-keyword a')
    categoryBest_office = [soup.select('#categoryBest_office .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_office))]
    all_categoryBest_living = soup.select('#categoryBest_living .hot-keyword a')
    categoryBest_living = [soup.select('#categoryBest_living .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_living))]
    all_categoryBest_beauty = soup.select('#categoryBest_beauty .hot-keyword a')
    categoryBest_beauty = [soup.select('#categoryBest_beauty .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_beauty))]
    all_categoryBest_sports = soup.select('#categoryBest_sports .hot-keyword a')
    categoryBest_sports = [soup.select('#categoryBest_sports .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_sports))]
    all_categoryBest_health = soup.select('#categoryBest_health .hot-keyword a')
    categoryBest_health = [soup.select('#categoryBest_health .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_health))]
    all_categoryBest_baby = soup.select('#categoryBest_baby .hot-keyword a')
    categoryBest_baby = [soup.select('#categoryBest_baby .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_baby))]
    all_categoryBest_babyfashion = soup.select('#categoryBest_babyfashion .hot-keyword a')
    categoryBest_babyfashion = [soup.select('#categoryBest_babyfashion .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_babyfashion))]
    all_categoryBest_kitchen = soup.select('#categoryBest_kitchen .hot-keyword a')
    categoryBest_kitchen = [soup.select('#categoryBest_kitchen .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_kitchen))]
    all_categoryBest_pets = soup.select('#categoryBest_pets .hot-keyword a')
    categoryBest_pets = [soup.select('#categoryBest_pets .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_pets))]
    all_categoryBest_hobby = soup.select('#categoryBest_hobby .hot-keyword a')
    categoryBest_hobby = [soup.select('#categoryBest_hobby .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_hobby))]
    all_categoryBest_book = soup.select('#categoryBest_book .hot-keyword a')
    categoryBest_book = [soup.select('#categoryBest_book .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_book))]
    all_categoryBest_travel = soup.select('#categoryBest_travel .hot-keyword a')
    categoryBest_travel = [soup.select('#categoryBest_travel .hot-keyword a')[n].string.replace('#','') for n in range(0, len(all_categoryBest_travel))]


insert_category = {'자동차_오토바이' : categoryBest_car,
                '여성패션' : categoryBest_womanclothe,
                '남성패션' : categoryBest_manclothe,
                '식품' : categoryBest_food,
                '가구_홈인테리어' : categoryBest_home_decoration,
                '가전_디지털' : categoryBest_digital,
                '문구_오피스' : categoryBest_office,
                '생활용품' : categoryBest_living,
                '뷰티' : categoryBest_beauty,
                '스포츠_레저용품' : categoryBest_sports,
                '헬스_건강식품' : categoryBest_health,
                '출산_유아동' : categoryBest_baby,
                '유아동패션' : categoryBest_babyfashion,
                '주방용품' : categoryBest_kitchen,
                '반려동물용품' : categoryBest_pets,
                '완구_취미' : categoryBest_hobby,
                '도서_CD_DVD' : categoryBest_book,
                '여행' : categoryBest_travel,
                }

coupang_hotkeyword = pd.DataFrame.from_dict(insert_category, orient='index')
coupang_hotkeyword.index.name = 'Num'
coupang_hotkeyword.columns.name = 'Info'

coupang_hotkeyword.to_csv('coupang_hotkeyword.csv', mode='w', encoding='utf-8-sig')

print(coupang_hotkeyword)
driver.close()
