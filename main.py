from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import db_utils

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
TOTAL_PUSHUPS = 1000*(datetime.today().year - 2000)


@app.route('/', methods=['GET', 'POST'])
def login():
    c, conn = db_utils.database_connection()
    if request.method == 'POST':
        # Get the submitted form data
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists in the database
        c.execute('SELECT id FROM users WHERE username=? AND password=?', (username, password))
        user_id = c.fetchone()

        if user_id:
            # Store the user ID in the session
            session['user_id'] = user_id[0]
            return redirect(url_for('pushups'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/pushups', methods=['GET', 'POST'])
def pushups():
    user_id = session['user_id']
    c, conn = db_utils.database_connection()

    if request.method == 'POST':
        # Get the submitted form data
        count = int(request.form['pushups'])

        # Insert the push-up count for the user
        c.execute('INSERT INTO pushups (user_id, count) VALUES (?, ?)', (session['user_id'], count))
        conn.commit()

        # Redirect to the push-ups page
        return redirect(url_for('pushups'))

    result = db_utils.get_user(user_id)
    if not result:
        return redirect(url_for('login'))

    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Get the user's push-up data
    pushup_count = db_utils.get_user_pushup_count(user_id)
    pushup_count = 0 if not pushup_count else pushup_count

    # Calculate the number of push-ups remaining until the end of the year
    pushups_left = TOTAL_PUSHUPS - pushup_count
    # pushups_rate_required = round((TOTAL_PUSHUPS - pushup_count)/days_left)
    rate_required_every_day = calc_rate_required(days_to_end_of_year(), running_total=pushup_count)
    rate_required_weekdays = calc_rate_required(days_to_end_of_year(daily=False), running_total=pushup_count)
    
    c.execute('SELECT sum(count) FROM pushups WHERE user_id=? and date=date("now")', (session['user_id'],))
    pushups_today, = c.fetchall()[0]

    table_data = generate_table(user_id)

    return render_template(
        'home.html',
        pushup_count=pushup_count,
        pushups_left=pushups_left,
        rate_daily=rate_required_every_day,
        rate_weekdays=rate_required_weekdays,
        pushups_today=pushups_today,
        table_data=table_data
        )

def calc_rate_required(days_left, running_total):
    return round((TOTAL_PUSHUPS - running_total)/days_left)

def generate_table(user_id):
    return db_utils.get_count_per_day(user_id)

def days_to_end_of_year(daily=True):
    if daily:
        utcnow = datetime.utcnow()
        end_of_year = datetime(utcnow.year, 12, 31)
        return (end_of_year - utcnow).days
    else:
        # from datetime import date
        # from dateutil.rrule import rrule, WEEKDAYS
        # today = date.today()
        # end_of_year = date(today.year, 12, 31)
        # return sum(1 for _ in rrule(WEEKDAYS, dtstart=today, until=end_of_year))
        return 205

@app.route('/register', methods=['GET', 'POST'])
def register():
    c, conn = db_utils.database_connection()
    if request.method == 'POST':
        # Get the submitted form data
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the passwords match
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        # Insert the new user into the database
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Username already exists')

        # Redirect to the login page
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


def run():
    app.run()


if __name__ == '__main__':
    run()
