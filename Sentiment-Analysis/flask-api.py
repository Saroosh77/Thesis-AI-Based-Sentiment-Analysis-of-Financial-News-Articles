from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from db_config import db_config

app = Flask(__name__)
CORS(app)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    if not email or not password:
        return jsonify(({'message': 'Missing email or password'})), 400

    # Connect to MySQL database
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # Validate Credentials
        cursor.execute('SELECT * FROM user WHERE email = %s AND userpassword = %s', (email, password))
        account = cursor.fetchone()

        if account:
            return jsonify({'message': 'Login Successful'}), 200
        else:
            return jsonify({'message': 'Invalid Credentials'}), 401

    except mysql.connector.Error as err:
        return jsonify({'message': 'Database error: ' + str(err)}), 500


if __name__ == '__main__':
    app.run(debug=True)