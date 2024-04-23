import mysql.connector
from bs4 import BeautifulSoup
import requests
from db_config import db_config


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


def search_and_save_articles(url):
    # base_url = "https://www.bbc.com/news/business-68364690"

    # Send a GET request to the Google News search page
    response = requests.get(url)
    response.encoding = 'utf-8'
    text = response.content
    # Parse the HTML content of the page
    soup = BeautifulSoup(text, 'html.parser')
    # print(soup.text)
    divs = soup.find_all('div')
    # print(divs)
    # Extract links and dates from the search results
    paras = []
    for d in divs:
        p = d.find('p')
        p_tag = p.text if p else None
        if p_tag not in paras and p_tag is not None:
            paras.append(p_tag)

    # for i in paras:
    #     print("*"+i)
    return paras


if __name__ == "__main__":
    url_list = import_article_links()

    try:
        for i in url_list:
            print("--------------------")
            print(search_and_save_articles(i[0]))
    except requests.RequestException as e:
        print(f"Connection timed out: {e}")
    except Exception as e:
        print(f"Error: {e}")








































#
# # lists
# urls = []
#
#
# # function created
# def scrape(art):
#     # getting the request from url
#     r = requests.get(art)
#
#     # converting the text
#     s = BeautifulSoup(r.text, "html.parser")
#
#     for i in s.find_all("a"):
#
#         href = i.attrs['href']
#
#         if href.startswith("/"):
#             art = art + href
#
#             if art not in urls:
#                 urls.append(art)
#                 print(art)
#                 # calling itself
#                 scrape(art) SoaBEf
#
#             # main function
#
#
# if __name__ == "__main__":
#     query = input("Enter the search query: ")
#
#     # website to be scraped
#     site = "https://www.google.com/search?&q=" + query + "&tbm=nws"
#
#     # calling function
#     scrape(site)
#
#
#
#
#
#










































# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# # import requests
# from bs4 import BeautifulSoup
# import mysql.connector
# from datetime import datetime
# import time
#
#
# def search_and_save_articles(query, num_results=5):
#     base_url = f"https://news.google.com/search?q={query}"
#
#     # Set up Chrome WebDriver with headless mode
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
#     driver = webdriver.Chrome(options=chrome_options)
#
#     # Send a GET request to the Google News search page
#     driver.get(base_url)
#
#     # Introduce a delay to allow JavaScript content to load
#     time.sleep(2)
#
#     # Get the HTML content of the page after JavaScript execution
#     html_content = driver.page_source
#
#     # Parse the HTML content of the page
#     soup_parser = BeautifulSoup(html_content, 'html.parser')
#
#     # Extract links and dates from the search results
#     links_and_dates = []
#     for result in soup_parser.find_all('div', class_='tF2Cxc'):
#         link = result.find('a')['href']
#         print(link)
#         date_str = result.find('span', class_='WG9SHc').text.strip()
#         date = parse_date(date_str)
#         print(date)
#         links_and_dates.append((link, date))
#
#     print(links_and_dates)
#
#     # Save the links and dates to the MySQL database
#     save_to_database(query, links_and_dates[:num_results])
#     print(f"{num_results} articles on '{query}' saved to the database.")
#
#     # Close the WebDriver
#     driver.quit()
#
#
# def parse_date(date_str):
#     # Convert the date string to a datetime object
#     return datetime.strptime(date_str, "%b %d, %Y").date()
#
#
# def save_to_database(query, links_and_dates):
#     # Connect to MySQL database
#     conn = mysql.connector.connect(
#         host='127.0.0.1',
#         user='root',
#         password='Beta@22110266',
#         database='shares'
#     )
#     cursor = conn.cursor()
#
#     # Create a table if it doesn't exist
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS articles (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             query VARCHAR(255),
#             link TEXT,
#             date DATE
#         )
#     ''')
#
#     # Insert data into the table
#     for link, date in links_and_dates:
#         cursor.execute('''
#             INSERT INTO articles (query, link, date)
#             VALUES (%s, %s, %s)
#         ''', (query, link, date))
#
#     # Commit changes and close the connection
#     conn.commit()
#     conn.close()
#
#
# if __name__ == "__main__":
#     search_query = input("Enter the search query: ")
#     search_and_save_articles(search_query)
