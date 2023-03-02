import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re


st.set_option('deprecation.showPyplotGlobalUse', False)

st.title("Анализ данных по публикациям данной [группы VK](https://vk.com/rgooinadezhda)")

VKdf = pd.read_excel('posts.xlsx', sheet_name='РГООИ_Надежда_')
VKdf['only_date'] = VKdf['date'].dt.strftime('%Y-%m')
VKdf['only_time'] = VKdf['date'].dt.strftime('%H')
VKdf['weekday'] = VKdf['date'].dt.dayofweek
months = pd.date_range('2022-01-03', '2022-09-01', freq='1M', normalize=True)
months_to_analyse = [d.strftime('%Y-%m') for d in months]
vk2022 = VKdf.loc[VKdf['only_date'].isin(months_to_analyse)]

def find_topic(text): 
    regular = r'#\S+'
    compiled = re.compile(regular)
    try: 
        lst_topics = compiled.findall(text)
    except BaseException: 
        lst_topics = ['No topic']
    return lst_topics
vk2022['topics'] = vk2022.apply(lambda row : find_topic(row['text']), axis=1)

def word_count(textik): 
    lst = str(textik).split()
    return len(lst)
vk2022['text_length'] = vk2022.apply(lambda row : word_count(row['text']), axis=1)
vk2022['count'] = 1

vk2022_exploded = vk2022.explode('topics')

vkdf = vk2022
vkexp_df = vk2022_exploded

def text_group_by_count(textt):
    if textt < 50:
        return 50
    elif textt >= 50 and textt < 100:
        return 100 
    elif textt >= 100 and textt < 150:
        return 150 
    elif textt >= 150 and textt < 200:
        return 200 
    elif textt >= 200 and textt < 250:
        return 250 
    else:
        return 300 
    
vkdf['text_length'] = vkdf.apply(lambda row : text_group_by_count(row['text_length']), axis=1)
time_grouped = vkdf.groupby('only_time').agg('sum').reset_index()

st.dataframe(time_grouped)

st.write('Рассмотрев активность по часам можно заметить,что наилучшие показатели активности в виде отметки нравится приходятся на 10 и 16 часов, a репостов в 18 часов. Из чего можно сделать вывод о том, что для улучшения статистистики большую часть постов следует публиковать в данные часы, но если желательно высокое распространение среди аудитории, то в 18 часов.')

workday_df_not_rush = vkdf.loc[(vkdf['weekday'].isin(list(range(0, 5)))) & (vkdf['only_time'].isin(['09','10','16','17','18','19','20',]))]
workday_df_not_rush['only_time'].unique()


median_activity = workday_df_not_rush.groupby('only_time').agg('median').reset_index()
length_count_time = workday_df_not_rush.groupby('only_time')['count'].sum().reset_index()
fig, ax = plt.subplots(figsize = (8, 4))
for activity in ['comments', 'likes', 'reposts']: 
    plt.plot(median_activity['only_time'], median_activity[activity], label = activity)
plt.plot(length_count_time['only_time'], length_count_time['count'], label = 'count')
plt.xticks(list(median_activity['only_time'].unique()))
plt.title('Средние значения активности среди читающих данную группу по времени публикации в будни в не самые популярные часы')
plt.xlabel('Время публикации, час')
plt.ylabel('Количество единиц активности')
plt.xticks(rotation=0)
plt.legend()
st.pyplot()

st.write('Была замечена закономерность активности и количества слов в постах, чем длиннее текст, тем большую заинтересованность он представляет для аудитории. Хуже всего показали себя записи с 50-100 слов.')

length_count = workday_df_not_rush.groupby('text_length')['count'].sum().reset_index()
length_grouped = workday_df_not_rush.groupby('text_length').agg('median').reset_index()
fig, ax = plt.subplots(figsize = (8, 4))
for activity in ['comments', 'likes', 'reposts']: 
    plt.plot(length_grouped['text_length'], length_grouped[activity], label = activity)
plt.plot(length_count['text_length'], length_count['count'], label = 'count')
plt.title('Корреляция значения активностей посетителей группы с длиной текста в публикации')
plt.xlabel('Длина текста')
plt.ylabel('Количество активностей')
plt.xticks(rotation=0)
plt.legend()
st.pyplot()

st.write('Посты совмещающие в себе текст и вложенное изображение или видео показывают хорошие показатели активности, что достаточно очевидно.')

attachments = workday_df_not_rush.groupby('media 1').agg({'likes' : 'median', 'reposts' : 'median', 'media count' : 'median', 'count' : 'sum'}).reset_index()
attachments.sort_values('likes')

workday_rush = vkdf.loc[(vkdf['weekday'].isin(list(range(0, 5)))) & (vkdf['only_time'].isin(['11','12','13','14','15']))]
median_activity = workday_rush.groupby('only_time').agg('median').reset_index()
length_count_time = workday_rush.groupby('only_time')['count'].sum().reset_index()
fig, ax = plt.subplots(figsize = (8, 4))
for activity in ['comments', 'likes', 'reposts']: 
    plt.plot(median_activity['only_time'], median_activity[activity], label = activity)
plt.plot(length_count_time['only_time'], length_count_time['count'], label = 'count')
plt.xticks(list(median_activity['only_time'].unique()))
plt.title('Средние значения активности среди читающих данную группу по времени публикации в будни в самые популярные часы')
plt.xlabel('Время публикации, час')
plt.ylabel('Количество единиц активности')
plt.xticks(rotation=45)
plt.legend()
st.pyplot()

st.write("""Если брать идеальную формулу для самого популярного поста то она будет из себя представлять такие пункты:""")
st.write("""1.текст длиной в 200-300 слов""")
st.write("""2.время публикации - 12 часов дня""")
st.write("""3.изображение соответствующее контексту""")
attachments = workday_rush.groupby('media 1').agg({'likes' : 'median', 'reposts' : 'median', 'media count' : 'median', 'count' : 'sum'}).reset_index()
attachments.sort_values('likes')

weekend_df = vkdf.loc[(vkdf['weekday'].isin(list(range(5, 7))))]

median_activity = weekend_df.groupby('only_time').agg('median').reset_index()
length_count_time = weekend_df.groupby('only_time')['count'].sum().reset_index()
fig, ax = plt.subplots(figsize = (8, 4))
for activity in ['comments', 'likes', 'reposts']: 
    plt.plot(median_activity['only_time'], median_activity[activity], label = activity)
plt.plot(length_count_time['only_time'], length_count_time['count'], label = 'count')
plt.xticks(list(median_activity['only_time'].unique()))
plt.title('Средние значения активности читающих данную группу по времени публикации в выходные')
plt.xlabel('Время публикации, час')
plt.ylabel('Количество единиц активности')
plt.xticks(rotation=0)
plt.legend()
st.pyplot()

length_count = weekend_df.groupby('text_length')['count'].sum().reset_index()
length_grouped = weekend_df.groupby('text_length').agg('median').reset_index()
fig, ax = plt.subplots(figsize = (8, 4))
for activity in ['comments', 'likes', 'reposts']: 
    plt.plot(length_grouped['text_length'], length_grouped[activity], label = activity)
plt.plot(length_count['text_length'], length_count['count'], label = 'count')
plt.title('Корреляция значения активности читающих в группе с длиной текста в публикациях в выходные')
plt.xlabel('Длина текста')
plt.ylabel('Количество активностей')
plt.xticks(rotation=0)
plt.legend()
st.pyplot()

st.write("""Рассмотрим ситуацию происходящую в выходные дни:""")

colb1, colb2 =st.columns(2)

with colb1:
    st.write("""1.К сожалению, активность достаточно нестабильная вещь. В 10 и 13 часов были пики активности, после которых происходил резкий спад. И увеличение количества публикаций никак не влияло на саму активность потребителей/""")
with colb2:
    st.write("""2. Но зато популярность небольшого количества слов в постах возрасла до уровня других , с огромным разрывом по комментариям вышли публикации в 250 слов.Но тут была замечена ситуация обратной ранее описанной: длинные посты стали менее популярны среди посетителей.""")

attachments1 = weekend_df.groupby('media 1').agg({'likes' : 'median', 'reposts' : 'median', 'media count' : 'median', 'count' : 'sum'}).reset_index()
attachments1.sort_values('likes')

topics_sorted = vkexp_df['topics'].value_counts()[vkexp_df['topics'].value_counts(normalize=True) > 0.01]

vkexp_df['topics'] = vkexp_df['topics'].str.lower()
topics_sorted1 = vkexp_df['topics'].value_counts()[vkexp_df['topics'].value_counts(normalize=True) > 0.01]  


top_topics = list(topics_sorted1.index)
vk_pop_topics = vkexp_df.loc[vkexp_df['topics'].isin(top_topics)]

vk_pop_topics.groupby('topics').agg({'likes' : 'median', 'reposts' : 'median', 'media count' : 'median', 'count' : 'sum'}).reset_index().sort_values(by='likes', ascending=False)

vk_pop_topics_weekday = vk_pop_topics.loc[(vk_pop_topics['weekday'].isin(list(range(0, 5))))]
st.dataframe(vk_pop_topics_weekday.groupby('topics').agg({'likes' : 'median', 'reposts' : 'median', 'media count' : 'median', 'count' : 'sum'}).reset_index().sort_values(by='likes', ascending=False))


st.write("""Можно заметить, что такие темы как : #интегративныйлагерь, #кабардинканадеждикус, #летнийлагерь, #море, #островокнадежды и #отдых собирают большое количестов лайков и репостов . На них и нужно обратить внимание, но насколько я понимаю, все они завязаны на летнем отдыхе, что актуально лишь в лентее время. Поэтому стоит обратить внимание на возможно не сезонные топики по типу #подопечныенадежды, #добраясреда, #благотворительность, #ростовнадону. Посты без топика же поддерживаются достаточно скудную активность, но в целом, их не так уж и много.""")


vk_pop_topics_weekend = vk_pop_topics.loc[(vk_pop_topics['weekday'].isin(list(range(5, 7))))]
st.dataframe(vk_pop_topics_weekend.groupby('topics').agg({'likes' : 'median', 'reposts' : 'median', 'media count' : 'median', 'count' : 'sum'}).reset_index().sort_values(by='likes', ascending=False))


st.write("""Темы связанные с отдыхом также остаются популярными в будни, а вот в выходные дни всё меняется, популярными темами становятся #подопечныенадежды, #добраясреда, #ростовнадону, #детитакнеделятся, соответсвенно в выходные дни следует использовать данные темы в большем количестве , так как только в одном частном случае они при своём малом количестве не имели высокое количество лайков и репостов""")

st.write("""Автор - [Мельников Владислав](https://vk.com/mindoken89)""")