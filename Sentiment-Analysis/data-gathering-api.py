import requests
import mysql.connector
from datetime import datetime


def create_stock_table(cursor):
    """
    Create a MySQL table to store stock data if it doesn't exist.
    """
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            date DATE NOT NULL,
            open_price FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume BIGINT,
            UNIQUE KEY unique_date_symbol (date, symbol)
        )
    ''')


def insert_stock_data(cursor, symbol, date, open_price, high, low, close, volume):
    """
    Insert stock data into the MySQL table.
    """
    try:
        cursor.execute('''
                INSERT IGNORE INTO stocks (symbol, date, open_price, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (symbol, date, open_price, high, low, close, volume))
        print(f"Inserted data for {symbol} on {date}")
    except mysql.connector.errors.DataError as e:
        print(f"Error inserting data: {e}")
    except mysql.connector.errors.IntegrityError as e:
        # Handle integrity error (duplicate key)
        print(f"Skipping duplicate data for {symbol} on {date}")


def get_alpha_vantage_data(api_key, symbol, interval='monthly', output_size='full'):
    """
    Get monthly stock data from Alpha Vantage API.

    Parameters:
        - api_key (str): Your Alpha Vantage API key.
        - symbol (str): Stock symbol (e.g., 'AAPL' for Apple).
        - interval (str): Time interval for data (default is 'monthly').
        - output_size (str): Output size of the data (default is 'full').

    Returns:
        - dict: Parsed JSON response containing stock data.
    """
    base_url = "https://alpha-vantage.p.rapidapi.com/query" #"https://www.alphavantage.co/query"
    endpoint = "TIME_SERIES_MONTHLY"
    headers = {
        "X-RapidAPI-Key": "d756508072mshd140edd7d85a97fp1a92bbjsn80ecec882cea",
        "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"
    }
    params = {
        'function': endpoint,
        'symbol': symbol,
        'datatype': 'json'
        # 'interval': interval,
        # 'outputsize': output_size,
        # 'apikey': api_key,
    }

    response = requests.get(base_url,headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


if __name__ == "__main__":
    api_key = 'd756508072mshd140edd7d85a97fp1a92bbjsn80ecec882cea' #'6T3MX24SK6M53FLP'  # Alpha Vantage API key
    symbols = ['AAPL', 'GOOGL', 'MSFT']  # Symbols for Apple, Google, and Microsoft

    # Connect to MySQL database
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='Beta@22110266',
        database='shares'
    )

    # Create a cursor
    cursor = conn.cursor()

    # Create the stocks table if it doesn't exist
    create_stock_table(cursor)

    # Fetch and store monthly stock data for each symbol
    for symbol in symbols:
        stock_data = get_alpha_vantage_data(api_key, symbol, interval='monthly', output_size='full')

        if stock_data:
            monthly_series = stock_data.get('Monthly Time Series')
            if monthly_series:
                for date, info in monthly_series.items():
                    # Convert date to a more suitable format for MySQL
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%Y-%m-%d')

                    # Insert data into the MySQL table
                    insert_stock_data(
                        cursor,
                        symbol,
                        formatted_date,
                        float(info['1. open']),
                        float(info['2. high']),
                        float(info['3. low']),
                        float(info['4. close']),
                        int(info['5. volume'])
                    )

    # Commit changes and close the database connection
    conn.commit()
    conn.close()
