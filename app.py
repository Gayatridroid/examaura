from flask import Flask, render_template_string, request, redirect
from flask_ngrok import run_with_ngrok
import sqlite3
from datetime import datetime

app = Flask(__name__)
run_with_ngrok(app)

# ---------------- DATABASE ---------------- #
def init_db():
    conn = sqlite3.connect("examaura.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    title TEXT,
                    content TEXT,
                    urgent INTEGER,
                    created_at TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

# ---------------- TEMPLATE ---------------- #
template = """
<!DOCTYPE html>
<html>
<head>
<title>Examaura</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap" rel="stylesheet">
<style>
body{
    margin:0;
    font-family:'Poppins',sans-serif;
    background:linear-gradient(135deg,#dbeafe,#e0e7ff);
}
.nav{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:15px 40px;
    background:#111827;
}
.logo{
    color:white;
    font-size:22px;
    font-weight:700;
}
.nav a{
    color:white;
    margin-left:20px;
    text-decoration:none;
}
.hero{
    text-align:center;
    padding:40px;
}
.card{
    background:white;
    margin:20px auto;
    padding:20px;
    width:80%;
    border-radius:15px;
    box-shadow:0 10px 25px rgba(0,0,0,0.1);
    transition:0.3s;
}
.card:hover{
    transform:translateY(-5px);
}
.badge{
    background:red;
    color:white;
    padding:3px 8px;
    border-radius:8px;
    font-size:12px;
}
.search{
    text-align:center;
    margin:20px;
}
input, textarea, select{
    padding:8px;
    width:100%;
    margin-top:5px;
}
button{
    background:#4f46e5;
    color:white;
    border:none;
    padding:10px 15px;
    border-radius:8px;
    cursor:pointer;
}
footer{
    text-align:center;
    padding:20px;
    background:#111827;
    color:white;
    margin-top:40px;
}
</style>
</head>
<body>

<div class="nav">
    <div class="logo">🚀 Examaura</div>
    <div>
        <a href="/">Home</a>
        <a href="/section/Engineering">Engineering</a>
        <a href="/section/UPSC">UPSC</a>
        <a href="/section/SSC">SSC</a>
        <a href="/section/Bharti">Bharti</a>
        <a href="/add">Admin</a>
    </div>
</div>

<div class="hero">
    <h1>Where Preparation Meets Power</h1>
</div>

<div class="search">
<form method="get" action="/search">
<input type="text" name="q" placeholder="Search exams, bharti, notes...">
<button type="submit">Search</button>
</form>
</div>

{% for post in posts %}
<div class="card">
    {% if post[4] == 1 %}
        <span class="badge">URGENT</span>
    {% endif %}
    <h2>{{post[2]}}</h2>
    <p>{{post[3]}}</p>
    <small>Category: {{post[1]}} | {{post[5]}}</small>
</div>
{% endfor %}

<footer>
Examaura © 2026 | Built by Gayuu
</footer>

</body>
</html>
"""

# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    conn = sqlite3.connect("examaura.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts ORDER BY id DESC")
    posts = c.fetchall()
    conn.close()
    return render_template_string(template, posts=posts)

@app.route('/section/<category>')
def section(category):
    conn = sqlite3.connect("examaura.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE category=? ORDER BY id DESC", (category,))
    posts = c.fetchall()
    conn.close()
    return render_template_string(template, posts=posts)

@app.route('/search')
def search():
    query = request.args.get('q')
    conn = sqlite3.connect("examaura.db")
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE title LIKE ? OR content LIKE ?", 
              ('%'+query+'%', '%'+query+'%'))
    posts = c.fetchall()
    conn.close()
    return render_template_string(template, posts=posts)

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        category = request.form['category']
        title = request.form['title']
        content = request.form['content']
        urgent = 1 if request.form.get('urgent') == 'on' else 0
        created_at = datetime.now().strftime("%d %b %Y")

        conn = sqlite3.connect("examaura.db")
        c = conn.cursor()
        c.execute("INSERT INTO posts (category,title,content,urgent,created_at) VALUES (?,?,?,?,?)",
                  (category,title,content,urgent,created_at))
        conn.commit()
        conn.close()
        return redirect('/')

    return """
    <h2>Add Content - Examaura Admin</h2>
    <form method='post'>
    Category:
    <select name='category'>
        <option>Engineering</option>
        <option>UPSC</option>
        <option>SSC</option>
        <option>Bharti</option>
    </select><br><br>
    Title:<br>
    <input type='text' name='title'><br><br>
    Content:<br>
    <textarea name='content'></textarea><br><br>
    Mark as Urgent:
    <input type='checkbox' name='urgent'><br><br>
    <button type='submit'>Publish</button>
    </form>
    """

app.run()
