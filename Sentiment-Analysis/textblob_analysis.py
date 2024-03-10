# Importing the essential libraries
# Beautiful Soup is a Python library for pulling data out of HTML and XML files
# The Natural Language Toolkit
import time
import re
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# %matplotlib inline
import random
from wordcloud import WordCloud
import os
from textblob import TextBlob
from pattern.text import sentiment
import mysql.connector
from db_config import db_config
from IPython.display import display
import nltk
# nltk.download('punkt')
import spacy
nlp = spacy.load('en_core_web_sm')


def data_retriever():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT article_link FROM articles
        ''')
        query = cursor.fetchall()
        conn.commit()
        conn.close()
        return query

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return []


# article_list = data_retriever()
# url = article_list[5][0]
# print(url)


def semantic_analyzer(url):
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        html = r.text

        # Creating a BeautifulSoup object from the HTML
        soup = BeautifulSoup(html, features="lxml")
        text = soup.get_text(separator=' ', strip=True)
        # print(text)
        # Clean Text
        clean_text = text.replace('\n', ' ')
        clean_text = clean_text.replace("/", " ")
        clean_text = ''.join([c for c in clean_text if c != "'"])

        # Step 4: Remove non-alphanumeric characters
        # clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

        # Step 5: Remove extra whitespaces
        # clean_text = re.sub(r'\s+', ' ', clean_text)
        # print(clean_text)

        # Split into Separate Sentences
        sentence = []
        tokens = nlp(clean_text)
        for sent in tokens.sents:
            sentence.append((sent.text.strip()))
            # print("*"+sent.text.strip())

        stopwords = nltk.corpus.stopwords.words('english')

        relevant_sentences = []
        for sen in sentence:
            relevance = 0
            for sw in stopwords:
                if ' '+sw+' ' in sen:
                    relevance += 1
            if relevance > 1:
                relevant_sentences.append(sen)

        # for i in sentence:
        #     print('- ' + i)
        print(len(sentence))
        print(sentence)
        # for i in relevant_sentences:
        #     print('* ' + i)
        print(len(relevant_sentences))
        #
        # # Sentiment Analysis with TextBlob
        textblob_sentiment = []
        polarity_list = []
        subjectivity_list = []
        for s in relevant_sentences:
            txt = TextBlob(s)
            polarity = txt.polarity
            subjectivity = txt.subjectivity
            textblob_sentiment.append((s, polarity, subjectivity))
            polarity_list.append(polarity)
            subjectivity_list.append(subjectivity)

        # Dataframe for TextBlob
        # df_textBlob = pd.DataFrame(textblob_sentiment, columns=['Sentence', 'Polarity', 'Subjectivity',])
        # display(df_textBlob.to_string())
        # df_textBlob.info()

        # Calculate overall Polarity Score
        if polarity_list is not []:
            polarity_score = np.nanmean(polarity_list)
            return polarity_score

    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e} ")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e} ")
        return None


if __name__ == "__main__":
    # article_list = data_retriever()
    # for i in range(10):
    #     semantic_analyzer(article_list[i][0])
    try:
        article_list = data_retriever()
        if not article_list:
            print("No data received from the Database")
        else:
            rating_list = []
            for article in article_list:
                rating = semantic_analyzer(article[0])
                if rating is not None:
                    if rating >= 0.5:
                        rating_list.append(('Very Positive', rating, article))
                    elif 0 < rating < 0.5:
                        rating_list.append(('Slightly Positive', rating, article))
                    elif 0 < rating < -0.05:
                        rating_list.append(('Slightly Negative', rating, article))
                    elif rating <= -0.5:
                        rating_list.append(('Very Negative', rating, article))
                    elif rating == 0:
                        rating_list.append(('Neutral', rating, article))
                else:
                    rating_list.append(('Error', rating, article))
            for i in rating_list:
                print(i)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
