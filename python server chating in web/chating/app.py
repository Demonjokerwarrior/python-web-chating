
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'dmeonwarrior'  # Replace with a secure secret key

# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="joker",
        password="demon",
        database="chat_app",
        charset="utf8mb4",
        collation="utf8mb4_general_ci"
    )
    return conn

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form.get('action')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if action == 'login':
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                session['username'] = username
                session['user_id'] = user['id']  # Store user ID in session
                cursor.close()
                conn.close()
                return redirect(url_for('index'))
            return 'Invalid username or password', 401

        elif action == 'register':
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user:
                return 'Username already exists', 400

            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'username' not in session:
        return jsonify(success=False, message="Unauthorized"), 401

    username = session['username']
    message = request.form['message']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (username, message, user_id) VALUES (%s, %s, %s)", (username, message, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify(success=True)

@app.route('/get_messages', methods=['GET'])
def get_messages():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, message, timestamp FROM messages ORDER BY timestamp DESC")
    messages = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(messages=messages)

@app.route('/delete_message', methods=['POST'])
def delete_message():
    if 'username' not in session:
        return jsonify(success=False, message="Unauthorized"), 401

    message_id = request.form['message_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify if the message belongs to the logged-in user
    cursor.execute("SELECT username FROM messages WHERE id = %s", (message_id,))
    result = cursor.fetchone()

    if result and result[0] == session['username']:
        cursor.execute("DELETE FROM messages WHERE id = %s", (message_id,))
        conn.commit()
        success = True
    else:
        success = False

    cursor.close()
    conn.close()

    return jsonify(success=success)

if __name__ == '__main__':
    app.run(debug=True)
