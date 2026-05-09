from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'devops2026'

def get_db():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASS', 'root'),
        database=os.environ.get('DB_NAME', 'taskdb')
    )
# this line is for testing pipeline
@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = cursor.fetchall()
    db.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']
        status = request.form['status']
        if not title:
            flash('Title is required!', 'error')
            return redirect(url_for('add_task'))
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO tasks (title, description, priority, status) VALUES (%s, %s, %s, %s)",
                       (title, description, priority, status))
        db.commit()
        db.close()
        flash('Task added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_task.html')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']
        status = request.form['status']
        cursor.execute("UPDATE tasks SET title=%s, description=%s, priority=%s, status=%s WHERE id=%s",
                       (title, description, priority, status, task_id))
        db.commit()
        db.close()
        flash('Task updated!', 'success')
        return redirect(url_for('index'))
    cursor.execute("SELECT * FROM tasks WHERE id=%s", (task_id,))
    task = cursor.fetchone()
    db.close()
    return render_template('edit_task.html', task=task)

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    db.commit()
    db.close()
    flash('Task deleted!', 'success')
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE title LIKE %s OR description LIKE %s",
                   (f'%{query}%', f'%{query}%'))
    tasks = cursor.fetchall()
    db.close()
    return render_template('index.html', tasks=tasks, search_query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
