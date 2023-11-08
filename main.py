import sqlite3
import uuid
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

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

@app.route("/api/report/<report_name>", methods=['GET'])
def get_report(report_name):
    date_from = request.args.get('from')
    date_to = request.args.get('to')

    # Connect to the database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Calculate the total number of days in the date range
    total_days = (datetime.fromisoformat(date_to) - datetime.fromisoformat(date_from)).days + 1

    # Prepare the response dictionary
    response = {"users": [], "dailyAverage": 0}

    # Get the sum of online time for all user activity in the range and count of records
    cursor.execute('''
        SELECT SUM(online_time), COUNT(*)
        FROM UserActivity
        WHERE date BETWEEN ? AND ?
    ''', (date_from, date_to))
    total_online_time, total_records = cursor.fetchone()

    # Compute global daily average
    if total_records > 0:
        response["dailyAverage"] = calculate_daily_average(total_online_time, total_records)

    # Aggregate data for each user
    cursor.execute('SELECT id FROM Users')
    for user_id, in cursor.fetchall():
        cursor.execute('''
            SELECT date, SUM(online_time) as daily_online_time
            FROM UserActivity 
            WHERE user_id = ? AND date BETWEEN ? AND ?
            GROUP BY date
        ''', (user_id, date_from, date_to))
        user_activity = cursor.fetchall()

        user_daily_average = 0  # Default to 0 if there's no user activity
        if user_activity:  # Make sure there is activity data
            user_total_online_time = sum(record[1] for record in user_activity)
            user_daily_average = calculate_daily_average(user_total_online_time, total_days)

        # Add user metrics to the response
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
    app.run(debug=True)