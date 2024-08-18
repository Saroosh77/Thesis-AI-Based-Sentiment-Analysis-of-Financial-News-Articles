import requests
import mysql.connector
from db_config import db_config
from bs4 import BeautifulSoup
from datetime import datetime
import json


def web_scraper(query):
    base_url = "https://news.google.com"
    search_url = f"/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(base_url+search_url)
    response.encoding = 'utf-8'
    html_content = response.content
    # Parse the HTML content of the page
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <div> tags
    articles = soup.find_all('article')
    list_of_articles = []
    # Process each article tag
    for article in articles:
        # Extract href value from the first <a> tag
        a_tag = article.find('a')
        link = a_tag['href'] if a_tag else None
        d_tag = article.find('time')
        l_date = d_tag['datetime'] if d_tag else None
        date_obj = datetime.strptime(l_date, "%Y-%m-%dT%H:%M:%SZ")
        article_date = date_obj.strftime("%Y-%m-%d")
        if link:
            article_url = base_url + link[1:]
            if article_url not in list_of_articles:
                list_of_articles.append((article_date, article_url))

    # Save the links to the MySQL database
    if list_of_articles:
        save_in_google_news(query, list_of_articles)
        print(f"{len(list_of_articles)} articles on '{query}' saved to the database.")
        print(list_of_articles)
    else:
        print("No articles were scraped.")


def save_in_google_news(query, article_list):
    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS google_news_articles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            company_name VARCHAR(255),
            published_date DATE,
            article_url TEXT
        )
    ''')

    # Insert data into the table
    for url in article_list:
        cursor.execute('''
            INSERT IGNORE INTO google_news_articles (company_name, published_date, article_url)
            VALUES (%s, %s, %s)
        ''', (query, url[0], url[1]))

    # Commit changes and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # search_query = input("Enter the search query: ")
    with open('companies.json', 'r') as file:
        data = json.load(file)

    for item in data['company']:
        print(item)
        web_scraper(item)
