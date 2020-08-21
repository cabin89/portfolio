from collections import Counter
from wordcloud import WordCloud
from wordcloud import STOPWORDS
from matplotlib import font_manager, rc
#import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def get_noun():

    f = open('product_name_for_analysis.txt', 'r')
    Name_for_chart = f.read()

    from konlpy.tag import Hannanum

    hannanum = Hannanum()
    noun = hannanum.nouns(Name_for_chart)
    # 불용어구 제거
    stopwords = ['1세트','2개','쿠팡','브랜드','화이트','3개','품','10팩','500ml','30롤','1L','4개','100매','1개입','코멧','1개','+','마스크','세트','50개입','대형','브랜드']
    for i in noun:
        if i in stopwords:
            noun.remove(i)

    return noun

#counting and bar chart
counts = Counter(get_noun())
tags = counts.most_common(70)


chart = pd.DataFrame({'word':[],
                    'count':[]})

for i in range(len(tags)):
    word = tags[i][0]
    count = tags[i][1]

    insert_data = pd.DataFrame({'word':[word],
                                'count':[count]})
    chart = chart.append(insert_data)

chart.index = range(len(chart))
# np.arrange에 대한 설명 https://codepractice.tistory.com/88
index = np.arange(len(chart))
# matplotlib 폰트설정

rc('font', family='AppleGothic')
#한글 사용시 마이너스 폰트 깨짐 문제 해결
plt.rcParams['axes.unicode_minus'] = False
plt.bar(index,chart['count'].tolist())
plt.xticks(index, chart['word'].tolist(), fontsize=10, rotation=40)
plt.xlabel('word', fontsize=15)
plt.ylabel('count', fontsize=15)
plt.title('단어 빈도수 시각화')
plt.show()



# ,'혼합','화이트','그레이','핑크','세트','개','색상','베스트'
#wordcloud
wc = WordCloud(font_path='font/NanumGothic.ttf', background_color='white', width=800, height=600)

print(dict(tags))
cloud = wc.generate_from_frequencies(dict(tags))
plt.figure(figsize=(10, 8))
plt.axis('off')
plt.imshow(cloud, interpolation='lanczos')
plt.show()
