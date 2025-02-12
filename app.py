from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import random
import hashlib

app = Flask(__name__)
app.secret_key = 'secretkey'  # Set a secret key for session management

# Load the questions data
with open('data/questions.json') as f:
    questions_data = json.load(f)

# Load user data (for simplicity, we're using a JSON file to store users)
with open('users/users.json') as f:
    users_data = json.load(f)


# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('start_quiz'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)

        # Check if the user exists and the password matches
        user = users_data.get(username)
        if user and user['password'] == hashed_password:
            session['username'] = username  # Store the username in session
            return redirect(url_for('start_quiz'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        if password != password_confirm:
            flash('Passwords do not match', 'danger')
        elif username in users_data:
            flash('Username already exists', 'danger')
        else:
            hashed_password = hash_password(password)
            users_data[username] = {'password': hashed_password}

            # Save the user data to the JSON file
            with open('users/users.json', 'w') as f:
                json.dump(users_data, f, indent=4)

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove user session
    return redirect(url_for('index'))


@app.route('/start_quiz')
def start_quiz():
    if 'username' not in session:
        return redirect(url_for('login'))

    session['score'] = 0  # Initialize score
    session['question_number'] = 0  # Start at the first question
    return redirect(url_for('quiz'))


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session:
        return redirect(url_for('login'))

    question_number = session.get('question_number', 0)

    if question_number < len(questions_data):
        question = questions_data[question_number]

        if request.method == 'POST':
            answer = request.form.get('answer')
            correct_answer = question['correct_answer']

            if answer == correct_answer:
                session['score'] += 1  # Increase score if answer is correct

            session['question_number'] += 1  # Move to next question
            return redirect(url_for('quiz'))

        return render_template('quiz.html', question=question, question_number=question_number + 1)

    else:
        return redirect(url_for('result'))


@app.route('/result')
def result():
    if 'username' not in session:
        return redirect(url_for('login'))

    score = session.get('score', 0)
    return render_template('result.html', score=score, total=len(questions_data))


if __name__ == '__main__':
    app.run(debug=True)
