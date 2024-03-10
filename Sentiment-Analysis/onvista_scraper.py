import requests
import mysql.connector
from db_config import db_config
from bs4 import BeautifulSoup
from datetime import datetime
import json


def web_scraper():
    try:
        base_url = f"https://www.onvista.de/news/finder?entityType=STOCK&entityValue=81348"

        response = requests.get(base_url)
        response.encoding = 'utf-8'
        html_content = response.content

        # Parse the HTML content of the page
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all <div> tags
        divs = soup.find_all('div')

        list_of_articles = []
        # Process each article tag
        for div in divs:
            # Extract href value from the first <a> tag
            a_tag = div.find('a')
            link = a_tag['href'] if a_tag else None
            link = str(link)
            title = a_tag.text.strip() if a_tag else None
            link_datetime = div.find('time')
            link_date = link_datetime['title'] if link_datetime else None
            # clean string and append into the list
            if '/news/' in link and '/news/finder' not in link:
                if (link_date, title, link) not in list_of_articles:
                    list_of_articles.append((link_date, title, link))

        for i in list_of_articles:
            print(i)
        return list_of_articles

    except requests.RequestException as e:
        print(f"Error fetching data from url: {e} ")
        return None
    except Exception as e:
        print(f"An unexpected error occurred in Scraper: {e} ")


def save_to_database(query, article_list):
    try:
        # Connect to MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create a table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_articles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_name VARCHAR(255),
                published_date DATE,
                news_title TEXT,
                news_url TEXT
            )
        ''')

        # Insert data into the table
        for link_date, title, link, in article_list:
            date = datetime.strptime(link_date, "%d.%m.%Y").date()
            cursor.execute('''
                INSERT IGNORE INTO news_articles (published_date, company_name, news_title, news_url)
                VALUES (%s, %s, %s, %s)
            ''', (date, query, title, "https://www.onvista.de/"+link))

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        print(f"{len(article_list)} articles on '{query}' saved to the database.")

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return []


if __name__ == "__main__":
    # search_query = input("Enter the search query: ")

    articles = web_scraper()
    save_to_database('Deutsche Bank', articles)
