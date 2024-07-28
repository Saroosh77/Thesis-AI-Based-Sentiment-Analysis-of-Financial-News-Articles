from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import mysql.connector
from db_config import db_config

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/api/login', methods=['POST'])
@cross_origin(origins="http://localhost:4200")  # Allow only this origin
def login():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            return jsonify({'message': 'Request Content-Type must be application/json'}), 400

        email = data['email']
        password = data['password']

        if not email or not password:
            return jsonify({'message': 'Missing email or password'}), 400

    # Connect to MySQL database
        connect = mysql.connector.connect(**db_config)
        cursor = connect.cursor()
        # Validate Credentials
        cursor.execute('SELECT * FROM user WHERE email = %s AND userpassword = %s', (email, password))
        account = cursor.fetchone()
        cursor.close()
        connect.close()

        if account:
            return jsonify({'message': 'Login Successful'}), 200
        else:
            return jsonify({'message': 'Invalid Credentials'}), 401

    except mysql.connector.Error as err:
        return jsonify({'message': 'Database error: ' + str(err)}), 500
    except Exception as e:
        print(f"An unexpected error occurred in Login: {e} ")


@app.route('/api/google/results', methods=['GET'])
@cross_origin(origins="http://localhost:4200")  # Allow only this origin
def get_google_search_results():
    try:

        connect = mysql.connector.connect(**db_config)
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM google_sentiment_results')
        results = cursor.fetchall()
        cursor.close()
        connect.close()

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

    except mysql.connector.Error as e:
        print(f"Database Error in Google Results: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred in Google Results: {e} ")


@app.route('/api/google/articles', methods=['GET'])
@cross_origin(origins="http://localhost:4200")  # Allow only this origin
def get_google_articles():
    try:
        connect = mysql.connector.connect(**db_config)
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM google_news_articles')
        results = cursor.fetchall()
        cursor.close()
        connect.close()

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

    except mysql.connector.Error as e:
        print(f"Database Error in google articles: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred in google articles: {e} ")


@app.route('/api/onvista/results', methods=['GET'])
@cross_origin(origins="http://localhost:4200")  # Allow only this origin
def get_onvista_results():
    try:
        connect = mysql.connector.connect(**db_config)
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM onvista_sentiment_results')
        results = cursor.fetchall()
        cursor.close()
        connect.close()

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

    except mysql.connector.Error as e:
        print(f"Database Error in onvista results: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred in onvista results: {e} ")


@app.route('/api/onvista/articles', methods=['GET'])
@cross_origin(origins="http://localhost:4200")  # Allow only this origin
def get_onvista_articles():
    try:
        connect = mysql.connector.connect(**db_config)
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM onvista_articles')
        results = cursor.fetchall()
        cursor.close()
        connect.close()

        rows = []
        for row in results:
            item = {
                'id': row[0],
                'company': row[1],
                'published_date': row[2],
                'article_url': row[4],
            }
            rows.append(item)

        return jsonify(rows)

    except mysql.connector.Error as e:
        print(f"Database Error in onvista articles: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred in onvista articles: {e} ")


if __name__ == '__main__':
    app.run(debug=True)
