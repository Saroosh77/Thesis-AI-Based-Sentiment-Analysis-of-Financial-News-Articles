import time
import logging
import torch.nn.functional as F
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import mysql.connector as dbconnector
from db_config import db_config
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
FINBERT_MODEL = "ProsusAI/finbert"
SLEEP_TIME = 2  # seconds between requests

# Create a tokenizer object
bert_tokenizer = AutoTokenizer.from_pretrained(FINBERT_MODEL)

# Fetch the pretrained model
finbert_model = AutoModelForSequenceClassification.from_pretrained(FINBERT_MODEL)


def import_data() -> List[Tuple[str, str, str, str]]:
    """
        Imports data containing company names and related news article details from the database.

        Returns:
            list: A list of tuples containing company name, published date, title of article and article URL.
        """
    try:
        conn = dbconnector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''SELECT company_name, published_date, article_title, article_url FROM onvista_articles''')
        query = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        return query

    except dbconnector.Error as e:
        logging.error(f"Database error in import_data: {e}")
        return []


def web_scraper(web_url: str) -> Optional[List[str]]:
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
        html = str(response.content)

        # Creating a BeautifulSoup object from the HTML
        soup = BeautifulSoup(html, features="html.parser")

        # Find all divs in the html
        divs = soup.find_all('div')

        paragraph_list = []
        for div in divs:
            p_tags = div.find_all('p')
            for p in p_tags:
                paragraph_text = p.text if p else None
                if paragraph_text not in paragraph_list and paragraph_text is not None:
                    paragraph_list.append(paragraph_text)

        return paragraph_list

    except requests.RequestException as e:
        logging.error(f"Request error fetching data from {web_url}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred in Scraper: {e}")
        return None


def preprocessor(paragraph_list: List[str]) -> pd.DataFrame:
    """
        Preprocesses a list of paragraphs into a DataFrame with a 'Sentence' column.

        Args:
            paragraph_list (list): A list of strings representing paragraphs.

        Returns:
            pd.DataFrame: A DataFrame containing a 'Sentence' column with split sentences.
        """
    try:
        if not paragraph_list:
            return pd.DataFrame(columns=['Sentence'])
        
        sentence_list = []
        for paragraph in paragraph_list:
            sentences = paragraph.split('. ')  # Split by full stops with spaces
            filtered_sentences = [sentence for sentence in sentences if sentence.strip()]
            sentence_list.extend(filtered_sentences)

        processed_list = []
        for sentence in sentence_list:
            if len(str(sentence)) > 5:
                processed_list.append(sentence)

        df = pd.DataFrame(processed_list, columns=['Sentence'])
        pd.set_option('expand_frame_repr', False)
        return df

    except Exception as e:
        logging.error(f"An unexpected error occurred in Preprocessor: {e}")
        return pd.DataFrame(columns=['Sentence'])


def sentiment_analyzer(df: pd.DataFrame, tokenizer, model) -> pd.DataFrame:
    """
        Analyze sentiment of sentences using the pretrained model.

        Args:
            df (pd.DataFrame): DataFrame containing sentences.
            tokenizer: Tokenizer object.
            model: Deep learning model 'FinBERT'.

        Returns:
            pd.DataFrame: DataFrame containing sentiment analysis results.
        """
    try:
        for i in tqdm(df.index):
            sentence = df.loc[i, 'Sentence']

            # Pre-process input phrase
            input_tensors = tokenizer(sentence, padding=True, truncation=True, return_tensors='pt')

            # Estimate output
            output = model(**input_tensors)

            # Pass model output logits through a softmax layer.
            predictions = F.softmax(output.logits, dim=-1)
            df.loc[i, 'Positive'] = predictions[0][0].tolist()
            df.loc[i, 'Negative'] = predictions[0][1].tolist()
            df.loc[i, 'Neutral'] = predictions[0][2].tolist()

        df = df[['Sentence', 'Positive', 'Negative', 'Neutral']]
        return df

    except Exception as e:
        logging.error(f"An unexpected error occurred in Sentiment Analyzer: {e}")
        return pd.DataFrame(columns=['Sentence', 'Positive', 'Negative', 'Neutral'])


def classify_sentence(pos, neg, neu) -> str[str, str, str]:
    """
    Improved sentence-level sentiment classification.
    
    Args:
        pos: positive score (0-1)
        neg: negative score (0-1)
        neu: neutral score (0-1)
    
    Returns:
        label: 'positive', 'negative', or 'neutral'
        compound_score: float between -1 and 1
        confidence: float between 0 and 1
    """
    # Calculate compound score to get a continous score

    compound_score = (pos - neg) / (pos + neg + 1e-6) # avoid division by zero

    # Calculate confidence (How "sure" is the model that it's NOT neutral?)

    polarity_strength = pos + neg # total emotional content
    dominance = abs(pos - neg) # how clearly one side wins
    confidence = polarity_strength * dominance

    # Classify with Adaptive Thresholds

    is_neutral = (
        neu > 0.5 or                        # neutral dominates
        (polarity_strength < 0.2) or        # very low emotional content
        (dominance < 0.1 and neu > 0.3) or  # pos ≈ neg and decent neutral
        confidence < 0.02                   # very low confidence
    )

    if is_neutral:
        sentiment = 'neutral'
    elif pos > neg:
        sentiment = 'positive'
    else:
        sentiment = 'negative'

    return sentiment, compound_score, confidence
    
def categorize_score(score) -> str:
    """
    Categorization with 5 tiers.
    """
    thresholds = [
        (-1.0,  -0.45,  'very negative'),
        (-0.45,  -0.05, 'slightly negative'),
        (-0.1,  0.1, 'neutral'),
        ( 0.1,  0.45,  'slightly positive'),
        ( 0.45,   1.0,  'very positive'),
    ]
    
    for low, high, sentiment in thresholds:
        if low <= score < high:
            return sentiment
    return 'very positive'  # edge case: score = 1.0

def classifier(df: pd.DataFrame) -> Optional[str]:
    """
        Classify sentiment based on sentiment scores.

        Args:
            df (pd.DataFrame): DataFrame containing sentiment analysis results.

        Returns: str: Overall sentiment classification ('Very Negative', 'Slightly Negative', 'Neutral',
                                                        'Slightly Positive', or 'Very Positive').
    """
    try:
        if df.empty:
            return 'No result'
        
        positive = []
        negative = []
        neutral = []

        for i in tqdm(df.index):
            if df.loc[i, 'Positive'] < 0.15 and df.loc[i, 'Negative'] < 0.15:
                neutral.append(df.loc[i, 'Neutral'])
            elif df.loc[i, 'Positive'] > df.loc[i, 'Negative']:
                positive.append(df.loc[i, 'Positive'])
            elif df.loc[i, 'Positive'] < df.loc[i, 'Negative']:
                negative.append(df.loc[i, 'Negative'])

        total_sentences = len(df.index)
        if total_sentences == 0:
            return 'Neutral'
        
        sentiment_score = (len(positive) - len(negative)) / total_sentences
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
        logging.error(f"An unexpected error occurred in Classifier: {e}")
        return None


def add_to_database(company: str, published_date, article_title: str, article_url: str, sentiment_value: Optional[str]):
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
        conn = dbconnector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS onvista_sentiment_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company VARCHAR(255),
                published_date DATE,
                article_title TEXT,
                article_url TEXT,
                sentiment VARCHAR(255)
            )
        ''')

        cursor.execute('''
            INSERT IGNORE INTO onvista_sentiment_results (company, published_date, article_title, article_url, sentiment)
            VALUES (%s, %s, %s, %s, %s)
        ''', (company, published_date, article_title, article_url, sentiment_value))

        conn.commit()
        cursor.close()
        conn.close()

        logging.info(f"{company}, {published_date}, {article_title}, {article_url}, {sentiment_value} saved to the database.")

    except dbconnector.Error as e:
        logging.error(f"Database error: {e}")


if __name__ == "__main__":
    try:
        data = import_data()
        if data:
            for row in data:
                company_name = row[0]
                published_date = row[1]
                title = row[2]
                url = row[3]
                paragraphs = web_scraper(url)
                if paragraphs:
                    sentence_df = preprocessor(paragraphs)
                    if not sentence_df.empty:
                        prediction = sentiment_analyzer(sentence_df, bert_tokenizer, finbert_model)
                        sentiment = classifier(prediction)
                        if sentiment:
                            add_to_database(company_name, published_date, title, url, sentiment)
                        else:
                            logging.warning(f"Could not classify sentiment for {url}")
                        time.sleep(SLEEP_TIME)
                    else:
                        logging.warning(f"Could not find/retrieve data from {url}")
                else:
                    logging.warning(f"Could not scrape data from {url}")
        else:
            logging.error("Failed to import data from the database")

    except Exception as e:
        logging.error(f"An unexpected error occurred in execution: {e}")

    logging.info("Execution has been completed!")
