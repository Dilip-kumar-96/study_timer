from flask import Flask, jsonify
from datetime import datetime, date
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="dilip1231",
    host="localhost"
)


@app.route("/start_time", methods=['POST'])
def start_time():
    cursor = conn.cursor()
    cursor.execute("select max(entry_no) from study_timer.study_timer_table")
    last_entry_no = cursor.fetchall()
    last_entry_no = last_entry_no[0][0]
    cursor.execute("select * from study_timer.study_timer_table where entry_no = %s", (last_entry_no,))
    record = cursor.fetchall()
    if record[0][3] == None:  # checks if the end_time is none. if it is then timer has already started.
        return (jsonify({'message': 'timer has already started, please end it'}))
    cursor.execute(
        "insert into study_timer.study_timer_table (entry_date, start_time) values (current_date, current_time)")

    conn.commit()
    cursor.close()
    return (jsonify({'message': 'timer started'})), 201


@app.route("/end_time", methods=['POST'])
def end_time():
    cursor = conn.cursor()

    cursor.execute("select max(entry_no) from study_timer.study_timer_table")
    last_entry_no = cursor.fetchall()
    last_entry_no = last_entry_no[0][0]
    cursor.execute("select * from study_timer.study_timer_table where entry_no = %s", (last_entry_no,))
    record = cursor.fetchall()
    if record[0][3] != None:  # checks if the latest entry has ended or not. if it is ended it throws error.
        return (jsonify({'message': 'timer has already ended. Please start new one'}))

    cursor.execute("update study_timer.study_timer_table set end_time = current_time where entry_no = %s",
                   (last_entry_no,))
    cursor.execute("select * from study_timer.study_timer_table where entry_no = %s", (last_entry_no,))
    record = cursor.fetchall()
    record = record[0]
    start_time = record[2]
    end_time = record[3]
    time_spent = datetime.combine(date.min, end_time) - datetime.combine(date.min, start_time)
    time_spent = str(time_spent)
    time_spent = time_spent.split(".")[0]
    cursor.execute("update study_timer.study_timer_table set time_spent = %s where entry_no = %s",
                   (time_spent, last_entry_no))

    conn.commit()
    cursor.close()
    return (jsonify({'time spent': time_spent})), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
