import sqlite3
import uuid
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, abort, render_template

app = Flask(__name__)
DATABASE_NAME = 'global_metrics_reports.db'

def calculate_daily_average(total_online_time, number_of_days):
    if number_of_days > 0:
        return total_online_time / number_of_days
    return 0

def setup_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id TEXT PRIMARY KEY
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserActivity (
            user_id TEXT NOT NULL,
            online_time INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES Users(id)
        )
    ''')

    cursor.execute('DELETE FROM Users')
    user_ids = [str(uuid.uuid4()) for _ in range(10)]
    cursor.executemany('INSERT INTO Users (id) VALUES (?)', [(user_id,) for user_id in user_ids])

    cursor.execute('DELETE FROM UserActivity')
    today = datetime.now().date()
    for user_id in user_ids:
        for days_ago in range(15):
            date = today - timedelta(days=days_ago)
            online_time = random.randint(10, 86400)
            cursor.execute('INSERT INTO UserActivity (user_id, online_time, date) VALUES (?, ?, ?)',
                           (user_id, online_time, date.isoformat()))

    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('main.html')

@app.route("/api/report/<report_name>", methods=['GET'])
def get_report(report_name):
    date_from = request.args.get('from')
    date_to = request.args.get('to')

    if not date_from or not date_to:
        abort(400, description="Missing 'from' or 'to' date parameters.")

    try:
        date_from_obj = datetime.fromisoformat(date_from)
        date_to_obj = datetime.fromisoformat(date_to)
    except ValueError:
        abort(400, description="Invalid date format. Use 'YYYY-MM-DD'.")

    total_days = (date_to_obj - date_from_obj).days + 1

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    response = {"users": [], "dailyAverage": 0}

    cursor.execute('''
        SELECT SUM(online_time), COUNT(*)
        FROM UserActivity
        WHERE date BETWEEN ? AND ?
    ''', (date_from, date_to))
    total_online_time, total_records = cursor.fetchone()

    if total_records > 0:
        response["dailyAverage"] = calculate_daily_average(total_online_time, total_records)

    cursor.execute('SELECT id FROM Users')
    for user_id, in cursor.fetchall():
        cursor.execute('''
            SELECT date, SUM(online_time) as daily_online_time
            FROM UserActivity 
            WHERE user_id = ? AND date BETWEEN ? AND ?
            GROUP BY date
        ''', (user_id, date_from, date_to))
        user_activity = cursor.fetchall()

        user_daily_average = 0
        if user_activity:
            user_total_online_time = sum(record[1] for record in user_activity)
            user_daily_average = calculate_daily_average(user_total_online_time, total_days)

        user_metric = {
            "userId": user_id,
            "metrics": [
                {"dailyAverage": user_daily_average}
            ]
        }
        response["users"].append(user_metric)

    conn.close()
    return jsonify(response)

if __name__ == '__main__':
    setup_database()
    app.run(host='0.0.0.0', port=5000, debug=False)

