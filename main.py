import sqlite3
from datetime import datetime
import json

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

DB_NAME = "records.db"

app = FastAPI()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        riding_date TEXT DEFAULT CURRENT_TIMESTAMP,
        lesson_type TEXT NOT NULL,
        lesson_time TEXT DEFAULT CURRENT_TIMESTAMP,
        instructor_name TEXT NOT NULL,
        horse_name TEXT NOT NULL,
        horse_memo TEXT NOT NULL,
        body TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()
    print("DB initialized.")

def load_options():
    with open("private_options.json", "r", encoding="utf-8") as f:
        return json.load(f)

def build_options_html(items):
    html = '<option value="">選択してください</option>\n'

    for item in items:
        html += f'<option value="{item}">{item}</option>\n'

    return html

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def index():
    options = load_options()

    lesson_type_options = build_options_html(options["lesson_types"])
    lesson_time_options = build_options_html(options["lesson_times"])
    instructor_name_options = build_options_html(options["instructor_names"])
    horse_name_options = build_options_html(options["horse_names"])

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    SELECT record_id, riding_date, lesson_type, lesson_time, instructor_name,
    horse_name, horse_memo, body
    From records
    ORDER BY record_id DESC
    """)

    records = cur.fetchall()
    conn.close()

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Riding Records</title>
    </head>
    <body>
        <h1>Riding Records</h1>
        <h2>Latest Ride</h2>
        <form action="/records" method="post" onsubmit="return validateForm();">
            <p>
                日付:<br>
                <input type="date" name="riding_date"/>
            </p>
            <p>
                レッスン名:<br>
                <select id="lesson_type" name="lesson_type" required>
                    {lesson_type_options}
                </select>
            </p>
            <p>
                レッスン時間:<br>
                <select id="lesson_time" name="lesson_time" required>
                    {lesson_time_options}
                </select>
            </p>
            <p>
                指導員名:<br>
                <select id="instructor_name" name="instructor_name" required>
                    {instructor_name_options}
                </select>
            </p>
            <p>
                馬匹名:<br>
                <select id="horse_name" name="horse_name" required>
                    {horse_name_options}
                </select>
            </p>
            <p>
                馬匹備考:<br>
                <input type="text" id="horse_memo" name="horse_memo" placeholder="入力してください">
            </p>
            <p>
                騎乗記録:<br>
                <textarea name="body" rows="5" cols="60" placeholder="入力してください"></textarea>
            </p>
            <button type="submit">記録</button>
        </form>

        <hr>

        <h2>記録一覧</h2>
    """

    for record in records:
        record_id, riding_date, lesson_type, lesson_time, instructor_name, horse_name, horse_memo, body = record
        html += f"""
        <div style="border:1px solid #ccc; padding:10px; margin:10px;">
            <h3>日付: {riding_date}</h3>
            <p><strong>レッスン名:</strong> {lesson_type}</p>
            <p><strong>レッスン時間:</strong> {lesson_time}</p>
            <p><strong>指導員名:</strong> {instructor_name}</p>
            <p><strong>馬匹名:</strong> {horse_name}</p>
            <p><strong>馬匹メモ:</strong> {horse_memo}</p>
            <p>{body}</p>
            <form action="/records/{record_id}/delete" method="post"
                  onsubmit="return confirm('この記録を削除しますか？')">
                <button type="submit">削除</button>
            </form>
        </div>
        """
    html += """
    <script>
    function validateForm() {
        const ridingDate = document.querySelector('input[name="riding_date"]').value;
        const lessonType = document.querySelector('select[name="lesson_type"]').value;
        const lessonTime = document.querySelector('select[name="lesson_time"]').value;
        const instructorName = document.querySelector('select[name="instructor_name"]').value;
        const horseName = document.querySelector('select[name="horse_name"]').value;
        const horseMemo = document.querySelector('input[name="horse_memo"]').value;
        const body = document.querySelector('textarea[name="body"]').value;

        if (!ridingDate) {
            alert("日付を入力してください");
            return false;
        }
        if (!lessonType) {
            alert("レッスン名を入力してください");
            return false;
        }
        if (!lessonTime) {
            alert("レッスン時間を入力してください");
            return false;
        }
        if (!instructorName) {
            alert("指導員名を入力してください");
            return false;
        }
        if (!horseName) {
            alert("馬匹名を入力してください");
            return false;
        }
        if (!horseMemo.trim()) {
            alert("馬匹備考を入力してください");
            return false;
        }
        if (!body.trim()) {
            alert("本文を入力してください");
            return false;
        }

        return true;
    }
    </script>
    </body>
    </html>
    """
    return html
@app.post("/records")
def create_record(
    riding_date: str = Form(...),
    lesson_type: str = Form(...),
    lesson_time: str = Form(...),
    instructor_name: str = Form(...),
    horse_name: str = Form(...),
    horse_memo: str = Form(...),
    body: str = Form(...)
):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO records (riding_date, lesson_type, lesson_time, instructor_name, horse_name, horse_memo, body)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        riding_date,
        lesson_type,
        lesson_time,
        instructor_name,
        horse_name,
        horse_memo,
        body
    ))

    conn.commit()
    conn.close()

    return HTMLResponse(
    content='<meta http-equiv="refresh" content="0; url=/" />',
    status_code=303
)

@app.post("/records/{record_id}/delete")
def delete_record(record_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM records
    WHERE record_id = ?
    """, (record_id,))

    conn.commit()
    conn.close()

    return HTMLResponse(
    content='<meta http-equiv="refresh" content="0; url=/" />',
    status_code=303
)