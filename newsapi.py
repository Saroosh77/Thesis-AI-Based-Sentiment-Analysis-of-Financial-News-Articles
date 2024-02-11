import mysql.connector
import requests
import json


def get_articles(query):

    url = ('https://newsapi.org/v2/everything?'
           'q='+query+'&'
           'from=2024-02-01&'
           'sortBy=relevancy&'
           'language=en&'
           'apiKey=ba395040b81f4055a741b1a7440d87fe')

    response = requests.get(url)
    res = response.json()

    ar_list = []
    for article in res['articles']:
        ar_list.append((article['publishedAt'], article['title'], article['url']))

    save_to_database(query, ar_list)
    print(f"{len(ar_list)} articles on '{query}' saved to the database.")


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
        CREATE TABLE IF NOT EXISTS api_articles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            published_date DATE,
            company_name VARCHAR(255),
            title TEXT,
            article_url TEXT
        )
    ''')

    # Insert data into the table
    for date, title, link in article_list:
        cursor.execute('''
            INSERT IGNORE INTO api_articles (published_date, company_name, title, article_url)
            VALUES (%s, %s, %s, %s)
        ''', (date, query, title, link))

    # Commit changes and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    with open('companies.json', 'r') as f:
        data = json.load(f)

    for i in data['company']:
        get_articles(i)
