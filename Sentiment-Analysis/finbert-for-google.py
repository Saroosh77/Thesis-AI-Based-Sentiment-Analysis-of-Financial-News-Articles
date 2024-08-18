import time
import torch.nn.functional
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import mysql.connector
from db_config import db_config
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tabulate import tabulate

# Create a tokenizer object
bert_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")

# Fetch the pretrained model
pre_trained_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")


def import_data():
    """
        Imports data containing company names and news article URLs from the database.

        Returns:
            list: A list of tuples containing company name and article URL.
        """
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''SELECT company_name, published_date, article_url FROM google_news_articles''')
        query = cursor.fetchall()
        conn.commit()
        conn.close()
        return query

    except mysql.connector.Error as e:
        print(f"Error in Database: {e}")
        return []


def web_scraper(web_url):
    """
        Scrapes paragraphs from a given news article URL.

        Args:
            web_url (str): The URL of the news article.

        Returns:
            list: A list of scraped paragraphs from the article, or None if an error occurs.
        """
    try:
        response = requests.get(web_url)
        response.encoding = 'utf-8'
        html = response.content

        # Creating a BeautifulSoup object from the HTML
        soup = BeautifulSoup(html, features="html.parser")

        # Find Title of Article
        head = soup.find('head')
        art_title = head.find('title') if head else None
        art_title = str(art_title.text.strip()) if art_title else None

        # Find all divs in the html
        divs = soup.find_all('div')

        p_list = []
        for div in divs:
            p_tags = div.find_all('p')
            for p in p_tags:
                p_tag = p.text if p else None
                if p_tag not in p_list and p_tag is not None:
                    p_list.append(p_tag)

        return p_list, art_title

    except requests.RequestException as e:
        print(f"Error fetching data from {web_url}: {e} ")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in Scraper: {e} ")


def preprocessor(paragraph_list):
    """
        Preprocesses a list of paragraphs into a DataFrame with a 'Sentence' column.

        Args:
            paragraph_list (list): A list of strings representing paragraphs.

        Returns:
            pd.DataFrame: A DataFrame containing a 'Sentence' column with split sentences.
        """
    try:
        sentence_list = []
        for paragraph in paragraph_list:
            sentences = paragraph.split('. ')  # Split by full stops with spaces
            filtered_sentences = [sentence for sentence in sentences if sentence.strip()]
            sentence_list.extend(filtered_sentences)

        processed_list = []
        for i in sentence_list:
            if len(str(i)) > 5:
                processed_list.append(i)

        df = pd.DataFrame(processed_list, columns=['Sentence'])
        pd.set_option('expand_frame_repr', False)
        return df

    except Exception as e:
        print(f"An unexpected error occurred in Preprocessor: {e} ")
        return pd.DataFrame(columns=['Sentence'])


def sentiment_analyzer(df, tokenizer, model):
    """
        Analyze sentiment of sentences using the pretrained model.

        Args:
            df (pd.DataFrame): DataFrame containing sentences.
            tokenizer: Tokenizer object.
            model: Pretrained model.

        Returns:
            pd.DataFrame: DataFrame containing sentiment analysis results.
        """
    try:
        for i in tqdm(df.index):
            sentence = df.loc[i, 'Sentence']

            # Pre-process input phrase
            inputs = tokenizer(sentence, padding=True, truncation=True, return_tensors='pt')

            # Estimate output
            output = model(**inputs)

            # Pass model output logits through a softmax layer.
            predictions = torch.nn.functional.softmax(output.logits, dim=-1)
            df.loc[i, 'Positive'] = predictions[0][0].tolist()
            df.loc[i, 'Negative'] = predictions[0][1].tolist()
            df.loc[i, 'Neutral'] = predictions[0][2].tolist()

        df = df[['Sentence', 'Positive', 'Negative', 'Neutral']]
        # print(tabulate(df, headers='keys', tablefmt='psql'))
        return df

    except Exception as e:
        print(f"An unexpected error occurred in Sentiment Analyzer: {e} ")
        return pd.DataFrame(columns=['Sentence', 'Positive', 'Negative', 'Neutral'])


def classifier(df):
    """
        Classify sentiment based on sentiment scores.

        Args:
            df (pd.DataFrame): DataFrame containing sentiment analysis results.

        Returns: str: Overall sentiment classification ('Very Negative', 'Slightly Negative', 'Neutral',
                                                        'Slightly Positive', or 'Very Positive').
    """

    try:
        positive = []
        negative = []
        neutral = []

        for i in tqdm(df.index):
            if df.loc[i, 'Positive'] < 0.15 and df.loc[i, 'Negative'] < 0.15:
                neutral.append(df.loc[i, 'Neutral'])
            elif df.loc[i, 'Positive'] > df.loc[i, 'Negative']:
                positive.append(df.loc[i, 'Positive'])
            elif df.loc[i, 'Negative'] > df.loc[i, 'Positive']:
                negative.append(df.loc[i, 'Negative'])

        # print(len(positive), len(negative), len(neutral))
        sentiment_score = (len(positive) - len(negative)) / len(df.index)
        value = None

        if -1 <= sentiment_score < -0.5:
            value = 'Very Negative'
        elif -0.5 <= sentiment_score < -0.1:
            value = 'Slightly Negative'
        elif -0.1 <= sentiment_score <= 0.1:
            value = 'Neutral'
        elif 0.1 < sentiment_score <= 0.5:
            value = 'Slightly Positive'
        elif 0.5 < sentiment_score <= 1:
            value = 'Very Positive'

        return value

    except Exception as e:
        print(f"An unexpected error occurred in Classifier: {e}")


def add_to_database(company, published_date, article_title, article_url, sentiment_value):
    """
        Add sentiment analysis results to the database.

        Args:
            company (str): Company name.
            published_date (date): published date of article.
            article_title (str): Title of the article.
            article_url (str): URL of the article.
            sentiment_value (str): Sentiment classification.
        """

    try:
        # Connect to MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create a table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS google_sentiment_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company VARCHAR(255),
                published_date DATE,
                article_title TEXT,
                article_url TEXT,
                sentiment VARCHAR(255)
            )
        ''')

        cursor.execute('''
            INSERT IGNORE INTO google_sentiment_results (company, published_date, article_title, article_url, sentiment)
            VALUES (%s, %s, %s, %s, %s)
        ''', (company, published_date, article_title, article_url, sentiment_value))

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        print(f"{company}, '{published_date} , '{article_title} , '{article_url}', {sentiment_value} saved to the "
              f"database.")

    except mysql.connector.Error as e:
        print(f"Error: {e}")


if __name__ == "__main__":

    try:
        data = import_data()
        if data:
            for row in data:
                company_name = row[0]
                p_date = row[1]
                url = row[2]
                scraped = web_scraper(url)
                title = scraped[1]
                paragraphs = scraped[0]
                if paragraphs:
                    sentence_df = preprocessor(paragraphs)
                    if not sentence_df.empty:
                        prediction = sentiment_analyzer(sentence_df, bert_tokenizer, pre_trained_model)
                        sentiment = classifier(prediction)
                        add_to_database(company_name, p_date, title, url, sentiment)
                        time.sleep(5)
                    else:
                        print(f"Could not find/retrieve data from {url}")
                else:
                    print(f"Could not scrap data from {url}")
        else:
            print("Failed to import data from the database")

    except Exception as f:
        print(f"An unexpected error occurred in execution : {f}")

    print("Execution has been completed!")
