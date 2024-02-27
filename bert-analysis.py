import torch.nn.functional
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import mysql.connector
from db_config import db_config
import requests
import pandas as pd
from bs4 import BeautifulSoup
import nltk
import spacy
nlp = spacy.load('en_core_web_sm')

# Create a tokenizer object
bert_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")

# fetch the pretrained model
pre_trained_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")


def import_article_list():
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


def scraper(url):
    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        html = r.text

        # Creating a BeautifulSoup object from the HTML
        soup = BeautifulSoup(html, features="lxml")
        text = soup.get_text(separator=' ', strip=True)

        # Clean Text
        clean_text = text.replace('\n', ' ')
        clean_text = clean_text.replace("/", " ")
        clean_text = ''.join([c for c in clean_text if c != "'"])

        # Split into Separate Sentences
        sentences = []
        tokens = nlp(clean_text)
        for sent in tokens.sents:
            sentences.append((sent.text.strip()))

        stopwords = nltk.corpus.stopwords.words('english')
        relevant_sentences = []
        for sen in sentences:
            relevance = 0
            for sw in stopwords:
                if ' ' + sw + ' ' in sen:
                    relevance += 1
            if relevance > 1:
                relevant_sentences.append(sen)

        df = pd.DataFrame(relevant_sentences, columns=['Sentence'])
        return df

    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e} ")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in Scraper: {e} ")
        return None


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
            ['date', 'stock', 'Open', 'Close', 'Volume', 'Sentence', 'Positive', 'Negative', 'Neutral', 'Price_change']]
    except:
        pass
    return df


if __name__ == "__main__":
    try:
        article_list = import_article_list()
        if not article_list:
            print("Article List is empty")
        else:
            pass

        sentence_df = scraper(article_list[6][0])
        if sentence_df.empty:
            print("Scraper has no data")
        else:
            pass

        result = senti_analyzer(sentence_df, bert_tokenizer, pre_trained_model)
        print(result.to_string())

    except Exception as e:
        print(f"An unexpected error occurred in execution : {e}")
