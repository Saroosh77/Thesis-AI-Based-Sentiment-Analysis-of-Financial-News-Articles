import requests
import mysql.connector
from db_config import db_config
from bs4 import BeautifulSoup
from datetime import datetime
import json


def web_scraper(query):
    base_url = f"https://www.google.com/search?q={query}&tbm=nws"

    response = requests.get(base_url)
    response.encoding = 'utf-8'
    html_content = response.content

    # Parse the HTML content of the page
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <div> tags
    articles = soup.find_all('div')

    list_of_articles = []
    # Process each article tag
    for article in articles:
        # Extract href value from the first <a> tag
        a_tag = article.find('a')
        link = a_tag['href'] if a_tag else None
        link = str(link)
        # clean string and append into the list
        if 'http' in link and '.google.com' not in link:
            start_index = link.find('http')
            end_index = link.find('&')
            link = link[start_index:end_index]
            if link not in list_of_articles:
                list_of_articles.append(link)

    # Save the links to the MySQL database
    save_to_database(query, list_of_articles)
    print(f"{len(list_of_articles)} articles on '{query}' saved to the database.")
    print(list_of_articles)


def save_to_database(query, article_list):
    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            company_name VARCHAR(255),
            article_link TEXT
        )
    ''')

    # Insert data into the table
    for link in article_list:
        cursor.execute('''
            INSERT IGNORE INTO articles (company_name, article_link)
            VALUES (%s, %s)
        ''', (query, link))

    # Commit changes and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # search_query = input("Enter the search query: ")
    with open('companies.json', 'r') as file:
        data = json.load(file)

    for item in data['company']:
        web_scraper(item)
