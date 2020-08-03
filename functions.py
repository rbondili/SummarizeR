import streamlit as st
import pandas as pd
from newsapi import NewsApiClient
import json
import requests
import streamlit_theme as stt
import pickle
# from summarizer import Summarizer

# DB
from managed_db import *

# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

def call_api_source():
	# sources = newsapi.get_sources()
	headers = {'Authorization': '68353e14ce514929ac111b8b0f24556e'}
	sources_url = 'https://newsapi.org/v2/sources'
	sources_payload = {'language': 'en', 'country': 'us'}
	response = requests.get(url=sources_url, headers=headers, params=sources_payload)

	# rows list initialization
	rows = []
	# appending rows
	for data in [response.json()]:
		data_row = data['sources']

		for row in data_row:
			rows.append(row)

	# using data frame
	df = pd.DataFrame(rows)

	return df


def make_clickable(url, text):
    return f'<a target="_blank" href="{url}">{text}</a>'

def call_api_news():
	# user_pref = user_preference(username,check_hashes(password,hashed_pswd))
	# df_pref = validate_user_prefrences(user_pref)
	url = ('http://newsapi.org/v2/top-headlines?'
       'country=us&'
       'apiKey=68353e14ce514929ac111b8b0f24556e')
	response = requests.get(url)
	# rows list initialization
	rows = []
	# appending rows
	for data in [response.json()]:
		data_row = data['articles']

		for row in data_row:
			rows.append(row)

	# using data frame
	df = pd.DataFrame(rows)

	return df

def search_news(search_type, newsapi, username, password, hashed_pswd, from_date, to_date, search_query):
	articles_retrieved = False
	if search_type == 'Search':
		all_articles = newsapi.get_everything(q=str(search_query),
                                      from_param=from_date,
                                      to=to_date,
                                      language='en',
                                      sort_by='relevancy',
                                      page=1)
		articles_retrieved = True
	elif search_type == 'user_pref':
		user_pref = user_preference(username,check_hashes(password,hashed_pswd))
		df_pref = validate_user_prefrences(user_pref)
		sources = (','.join(df_pref.Unique_Id.to_list()))
		print(sources)
		all_articles = newsapi.get_everything(sources=sources,
                                      from_param=from_date,
                                      to=to_date,
                                      language='en',
                                      sort_by='relevancy',
                                      page=1)
		articles_retrieved = True

	if articles_retrieved == True:
		# rows list initialization
		rows = []
		# appending rows
		for data in [all_articles]:
			data_row = data['articles']

			for row in data_row:
				rows.append(row)

		# using data frame
		df = pd.DataFrame(rows)

		return df

def validate_user_prefrences(user_pref):
    jdata = json.loads(user_pref[0][0])
    df_pref = pd.DataFrame(jdata)
    return(df_pref)

def read_article(file, article=''):
    clean_article = ''
    raw_article = ''
    if file != '':
        with open(file,'r',encoding="utf8",buffering=100000) as f:
            for line in f:
                raw_article = raw_article + line
                line = line.replace('\n', '')
                clean_article = clean_article + line
    else:
        for line in article:
            raw_article = raw_article + line
            line = line.replace('\n', '')
            clean_article = clean_article + line
    return raw_article, clean_article


def display_preferences(username, password, hashed_pswd):
    user_pref = user_preference(username,check_hashes(password,hashed_pswd))
    if len(user_pref[0][0]) == 4:
        return st.write("Please update the user preferences")
    else:
        df_pref = validate_user_prefrences(user_pref)
        return st.table(df_pref.style)

def format_display_news(df_news):
	df_news['preview'] = df_news.apply(lambda x: make_clickable(x['url'], x['title']), axis=1)
	df_disp_news = pd.DataFrame(df_news.preview)
	df_disp_news.rename(columns={'preview':'Tops News'}, inplace=True)

	return df_disp_news

# def model_summary(model, body):
# 	load_model = pickle.load(open('model.pkl', 'rb'))
# 	result = load_model(body, max_length=250)
# 	summary = ''.join(result)
#
# 	return summary
