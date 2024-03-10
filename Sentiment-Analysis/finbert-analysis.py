import time
import torch.nn.functional
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import mysql.connector
from db_config import db_config
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import spacy
nlp = spacy.load('en_core_web_sm')

# Create a tokenizer object
bert_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")

# fetch the pretrained model
pre_trained_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

positive_paragraph = ["The radiant morning sun gently kissed the dew-covered grass, casting a warm glow across the "
                      "tranquil meadow. Birds chirped happily in the clear azure sky, creating a symphony of nature's "
                      "joyful melodies. Fragrant flowers bloomed, painting the landscape with a vibrant palette of "
                      "colors, a testament to life's beauty. Laughter echoed through the air as families gathered for "
                      "a picnic, sharing moments of joy and connection. The gentle breeze carried the sweet scent of "
                      "freshly baked cookies, inviting everyone to savor the simple pleasures. Children played games "
                      "with boundless enthusiasm, their innocent laughter echoing like music in the open space. Each "
                      "moment felt like a precious gift, wrapped in the warmth of love and gratitude, "
                      "creating memories to cherish. Smiles adorned the faces of friends as they shared stories, "
                      "creating an atmosphere of camaraderie and friendship. As the sun began to set, "
                      "casting a golden hue on the horizon, the day unfolded as a perfect symphony of happiness. This "
                      "idyllic scene captured the essence of a blissful day, a testament to the beauty that exists in "
                      "the simplest moments."]
negative_paragraph = ["The gloomy overcast sky hung low, casting a shadow over the desolate landscape, devoid of any "
                      "signs of life. Crows cawed ominously, their harsh calls echoing through the barren trees, "
                      "creating a sense of eerie solitude. Barren branches swayed in the chilling wind, "
                      "a stark reminder of the harshness of the unforgiving environment. The air felt heavy with an "
                      "unspoken tension, as if the world itself carried the weight of countless sorrows. Abandoned "
                      "buildings stood as silent witnesses to the decay and neglect that had befallen this "
                      "once-thriving community. A somber mood enveloped the surroundings, with the only sound being "
                      "the distant howling of a forlorn wind. Faces etched with weariness and despair wandered "
                      "aimlessly, carrying the burdens of unspoken hardships. The echoes of shattered dreams "
                      "resonated in the vacant streets, haunted by the memories of what once was. Every step felt "
                      "like a journey through a melancholic labyrinth, where hope had long since lost its way. In "
                      "this desolate realm, the bitter taste of solitude lingered, and the very air seemed to mourn "
                      "the loss of brighter days."]
neutral_paragraph = ["The sky exhibited a calm and clear demeanor, with a gentle breeze playing through the branches "
                     "of the trees. Everyday activities continued in the bustling town, with people going about their "
                     "routines with a sense of normalcy. A well-tended garden showcased an array of plants, "
                     "neither flourishing nor withering, but simply existing in equilibrium. The rhythmic ticking of "
                     "a clock in a quiet room provided a steady background noise, a constant in the passage of time. "
                     "Ordinary conversations unfolded in a local cafe, where the exchanges were neither exceptionally "
                     "joyful nor overly somber. A cat lazily stretched in the sunlight filtering through the window, "
                     "embodying a serene and uncomplicated existence. The scent of freshly brewed coffee permeated "
                     "the air, creating a neutral and familiar olfactory backdrop. The daily commute saw people "
                     "moving with purpose, navigating the urban landscape with a practiced and indifferent demeanor. "
                     "Office spaces hummed with the usual sounds of typing and occasional chatter, a routine scene "
                     "repeated day after day. Life moved forward, neither particularly remarkable nor distressingly "
                     "challenging, as the world turned in its predictable cadence."]


def import_article_links():
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
        print(f"Error in Database: {e}")
        return []


def web_scraper(web_url):
    try:
        response = requests.get(web_url)
        response.encoding = 'utf-8'
        html = response.content
        # Creating a BeautifulSoup object from the HTML
        soup = BeautifulSoup(html, features="lxml")

        divs = soup.find_all('div')

        paragraphs = []
        for div in divs:
            p_tags = div.find_all('p')
            for p in p_tags:
                p_tag = p.text if p else None
                if p_tag not in paragraphs and p_tag is not None:
                    paragraphs.append(p_tag)

        return paragraphs

    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e} ")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in Scraper: {e} ")


def cleaner(p_list):
    try:
        sentence_list = []
        for st in p_list:
            sentence = st.split('. ')
            sentence_list.extend(sentence)

        pd.set_option('display.max_columns', 4)
        return pd.DataFrame(sentence_list, columns=['Sentence'])

    except Exception as e:
        print(f"An unexpected error occurred in Cleaner: {e} ")
        return pd.DataFrame(columns=['Sentence'])


def senti_analyzer(df, tokenizer, model):

    for i in tqdm(df.index):
        try:
            sentence = df.loc[i, 'Sentence']
        except:
            return print(' \'Sentence\' column might be missing from dataframe')

        # Pre-process input phrase
        input = tokenizer(sentence, padding=True, truncation=True, return_tensors='pt')

        # Estimate output
        output = model(**input)

        # Pass model output logits through a softmax layer.
        predictions = torch.nn.functional.softmax(output.logits, dim=-1)
        df.loc[i, 'Positive'] = predictions[0][0].tolist()
        df.loc[i, 'Negative'] = predictions[0][1].tolist()
        df.loc[i, 'Neutral'] = predictions[0][2].tolist()
    # rearrange column order
    try:
        df = df[
            ['Sentence', 'Positive', 'Negative', 'Neutral']]
    except:
        pass
    return df


def article_sentiment(df):

    positive = []
    negative = []
    neutral = []

    try:
        for i in tqdm(df.index):
            if df.loc[i, 'Positive'] > 0.1:
                positive.append(df.loc[i, 'Positive'])
            if df.loc[i, 'Negative'] > 0.1:
                negative.append(df.loc[i, 'Negative'])
            if df.loc[i, 'Neutral'] > 0.1:
                neutral.append(df.loc[i, 'Neutral'])

        if df.empty:
            print("No data in Dataframe")
        else:
            c_positive = np.nanmean(positive)
            c_negative = np.nanmean(negative)
            c_neutral = np.nanmean(neutral)

            print(positive, negative, neutral)
            return c_positive, len(positive), c_negative, len(negative), c_neutral, len(neutral)

    except Exception as e:
        print(f"Dataframe is Empty: {e}")


if __name__ == "__main__":
    try:
        article_links = import_article_links()
        if not article_links:
            print("Article List is empty")
        else:
            # for link in article_links:
            url = article_links[1][0]
            sentence_df = cleaner(web_scraper(url))
            if sentence_df.empty:
                print(f"Could not find/retrieve data from {url}")
            else:
                result = senti_analyzer(sentence_df, bert_tokenizer, pre_trained_model)
                print(result.to_string())
                acc_result = article_sentiment(result)
                print(acc_result)
                print(url)
                time.sleep(2)

    except Exception as e:
        print(f"An unexpected error occurred in execution : {e}")
