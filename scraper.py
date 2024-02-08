from urllib.request import urlopen
import mysql.connector
from bs4 import BeautifulSoup
from datetime import datetime
import json


def web_scraper(query):
    base_url = "https://news.google.com"

    page = urlopen(base_url + "/search?q=" + query)

    html_bytes = page.read()
    html_content = html_bytes.decode("utf-8")

    # Parse the HTML content of the page
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <article> tags
    articles = soup.find_all('article')

    list_of_articles = []
    # Process each article tag
    for article in articles:
        # Extract href value from the first <a> tag
        a_tag = article.find('a')
        link = a_tag['href'] if a_tag else None

        # Extract datetime value from the first <time> tag
        time_tag = article.find('time')
        raw_date = time_tag['datetime'] if time_tag else None
        date = datetime.fromisoformat(raw_date[:-1]).strftime('%Y-%m-%d')

        list_of_articles.append((date, base_url + link[1:]))

    # Save the links and dates to the MySQL database
    # save_to_database(query, list_of_articles)
    print(f"{len(list_of_articles)} articles on '{query}' saved to the database.")


def save_to_database(query, article_list):
    # Connect to MySQL database
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='Beta@22110266',
        database='shares'
    )
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            company_name VARCHAR(255),
            published_date DATE,
            article_link TEXT
        )
    ''')

    # Insert data into the table
    for date, link in article_list:
        cursor.execute('''
            INSERT IGNORE INTO articles (company_name, published_date, article_link)
            VALUES (%s, %s, %s)
        ''', (query, date, link))

    # Commit changes and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # search_query = input("Enter the search query: ")
    with open('companies.json', 'r') as file:
        data = json.load(file)

    for item in data['company']:
        web_scraper(item)
