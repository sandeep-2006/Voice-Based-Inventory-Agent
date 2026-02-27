from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import sqlite3
from faster_whisper import WhisperModel
from inventory_db import init_db, update_inventory, log_voice_command
from regex import extract_info

# 1️⃣ Create Flask app first
app = Flask(__name__)
app.secret_key = "secret_key_for_session"

# Upload folder
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load Whisper Model
model = WhisperModel("medium", device="cpu", compute_type="int8")
init_db()

# 2️⃣ Define all routes AFTER app is created

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    conn.close()
    if user:
        session['user'] = username
        session['role'] = user[0]
        return redirect(url_for('worker_view' if user[0] == 'worker' else 'manager_view'))
    return "Invalid Credentials"

# Worker and manager views
@app.route('/worker')
def worker_view():
    if session.get('role') != 'worker': return redirect(url_for('login'))
    return render_template('worker.html')

@app.route('/manager')
def manager_view():
    if session.get('role') != 'manager': return redirect(url_for('login'))
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventory")
    stock = cur.fetchall()
    cur.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = cur.fetchall()
    conn.close()
    return render_template('manager.html', stock=stock, logs=logs)

# Voice processing
@app.route('/process_audio', methods=['POST'])
def process_audio():
    audio = request.files['audio']
    path = os.path.join(UPLOAD_FOLDER, "voice.wav")
    audio.save(path)

    # 1️⃣ Transcribe audio with Whisper
    segments, _ = model.transcribe(path, task="translate")
    text = " ".join([s.text for s in segments])

    # 2️⃣ Extract quantity, unit, item, action from text
    qty, unit, item, action = extract_info(text)

    # 3️⃣ Update database AND get updated quantity
    item, new_qty = update_inventory(qty, unit, item, action)

    # 4️⃣ Log the voice command (optional)
    log_voice_command(text, f"{new_qty} {unit} of {item} ({action})")

    # 5️⃣ Prepare a note to show to the user
    note = f"Database updated: {new_qty} {unit} of {item} ({action})"

    # 6️⃣ Return JSON including the transcript and the note
    return jsonify({"transcript": text, "note": note})

# Manager API for inventory & logs
@app.route('/api/inventory')
def api_inventory():
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM inventory")
    rows = cur.fetchall()
    conn.close()
    data = [{"item": r[0], "quantity": r[1], "unit": r[2]} for r in rows]
    return jsonify(data)

@app.route('/api/logs')
def api_logs():
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    rows = cur.fetchall()
    conn.close()
    data = [{"id": r[0], "timestamp": r[1], "raw_text": r[2], "extracted_info": r[3]} for r in rows]
    return jsonify(data)

@app.route('/api/clear_logs', methods=['POST'])
def api_clear_logs():
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM logs")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='logs'")  # reset autoincrement
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)