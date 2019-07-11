# Author:  RADERMECKER Oskar, DINDIN Meryll
# Date:    09 July 2019
# Project: AsTeR

try: from service_WEB.imports import *
except: from imports import *

application = Flask(__name__)
# Apply static configuration
with open('config.yaml') as raw: crd = yaml.safe_load(raw)
application.secret_key = crd['secret_key']
SQL_URL = crd['sql_api']

# Index
@application.route('/')
@application.route('/home/')
def index():
    return render_template('home.html')

# About Aster
@application.route('/about')
def about():

    return render_template('about.html')

# Team
@application.route('/team')
def team():

    return render_template('team.html')

# Features
@application.route('/call_analysis')
def call_analysis():

    return render_template('call_analysis.html')

@application.route('/unit_dispatching')
def unit_dispatching():

    return render_template('unit_dispatching.html')

@application.route('/feedback_integration')
def feedback_integration():

    return render_template('feedback_integration.html')

@application.route('/backup_plans')
def backup_plans():

    return render_template('backup_plans.html')

# Additional test environment
@application.route('/test')
def test():

    return render_template('test.html')

# Register form class
class RegisterForm(Form):

    firstname = StringField('First Name', [validators.Length(min=2, max=50)])
    lastname = StringField('Last Name', [validators.Length(min=2, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.data_required(),
        validators.equal_to('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# Register page
@application.route('/register', methods=['GET', 'POST'])
def register():

    def register_user(profile, url):
    
        url = '/'.join([url, 'register'])
        prm = dict(zip(['username', 'password', 'first_name', 'last_name', 'email'], profile))
        req = requests.post(url, params=prm)
        return json.loads(req.content)

    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():

        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data

        result = register_user((username, password, first_name, last_name, email), SQL_URL)

        if not result['success']: 
            return render_template('register.html', error=result['reason'])
        else:
            flash('You are now registered. Log in to access your simulation dashboard!', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Login page
@application.route('/login', methods=['GET', 'POST'])
def login():

    def check_connection(profile, url):
    
        url = '/'.join([url, 'connect'])
        username, password = profile
        req = requests.post(url, params={'username': username, 'password': sha256_crypt.hash(password)})
        return json.loads(req.content)

    if request.method == 'POST':
        # Get form fields
        username = request.form['username']
        password = request.form['password']

        result = check_connection((username, password), SQL_URL)

        if result['success']:
            session['username'] = username
            session['logged_in'] = True
            flash('You are now logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error=result['reason'])

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to log in before you can access your dashboard!', 'danger')
            return redirect(url_for('login'))
    return wrap

# User Dashboard
@application.route('/dashboard')
@is_logged_in
def dashboard():

    return render_template('dashboard.html')

# User log out page
@application.route('/logout')
@is_logged_in
def logout():

    session.clear()
    flash('Successfully logged out', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':

    # application.run(host='127.0.0.1', port=8080)
    # application.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), threaded=True)
    application.run(debug=True)
