# Importing the essential libraries
# Beautiful Soup is a Python library for pulling data out of HTML and XML files
# The Natural Language Toolkit
import time

import requests
import nltk
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# %matplotlib inline
import random
from wordcloud import WordCloud
import os
import spacy
nlp = spacy.load('en_core_web_sm')
from textblob import TextBlob
from pattern.text import sentiment
import mysql.connector
from db_config import db_config


def data_retriever():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT article_link FROM articles
    ''')

    query = cursor.fetchall()

    conn.commit()
    conn.close()

    return query


article_list = data_retriever()
url = article_list[20][0]
print(url)

r = requests.get(url)

r.encoding = 'utf-8'
time.sleep(5)
html = r.text

print(html[:5000])


# if __name__ == "__main__":
#     print(data_retriever())
