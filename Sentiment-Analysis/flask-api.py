from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from db_config import db_config

app = Flask(__name__)
CORS(app)
connect = mysql.connector.connect(**db_config)


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    if not email or not password:
        return jsonify(({'message': 'Missing email or password'})), 400

    # Connect to MySQL database
    try:
        cursor = connect.cursor()
        # Validate Credentials
        cursor.execute('SELECT * FROM user WHERE email = %s AND userpassword = %s', (email, password))
        account = cursor.fetchone()
        cursor.close()

        if account:
            return jsonify({'message': 'Login Successful'}), 200
        else:
            return jsonify({'message': 'Invalid Credentials'}), 401

    except mysql.connector.Error as err:
        return jsonify({'message': 'Database error: ' + str(err)}), 500


@app.route('/api/google/results', methods=['GET'])
def get_google_search_results():
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM google_search_results')
    results = cursor.fetchall()
    cursor.close()

    rows = []
    for row in results:
        item = {
            'id': row[0],
            'company': row[1],
            'published_date': row[2],
            'article_title': row[3],
            'article_url': row[4],
            'sentiment': row[5]
        }
        rows.append(item)

    return jsonify(rows)


@app.route('/api/google/articles', methods=['GET'])
def get_google_articles():
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM google_news_articles')
    results = cursor.fetchall()
    cursor.close()

    rows = []
    for row in results:
        item = {
            'id': row[0],
            'company': row[1],
            'published_date': row[2],
            'article_url': row[3],
        }
        rows.append(item)

    return jsonify(rows)


@app.route('/api/onvista/results', methods=['GET'])
def get_onvista_results():
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM onvista_sentiment_results')
    results = cursor.fetchall()
    cursor.close()

    rows = []
    for row in results:
        item = {
            'id': row[0],
            'company': row[1],
            'published_date': row[2],
            'article_title': row[3],
            'article_url': row[4],
            'sentiment': row[5]
        }
        rows.append(item)

    return jsonify(rows)


@app.route('/api/onvista/articles', methods=['GET'])
def get_onvista_articles():
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM onvista_articles')
    results = cursor.fetchall()
    cursor.close()

    rows = []
    for row in results:
        item = {
            'id': row[0],
            'company': row[1],
            'published_date': row[2],
            'article_title': row[3],
            'article_url': row[4],
        }
        rows.append(item)

    return jsonify(rows)


if __name__ == '__main__':
    app.run(debug=True)
