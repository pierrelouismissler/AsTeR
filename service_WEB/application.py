# Author:  RADERMECKER Oskar, DINDIN Meryll, MISSLER Pierre-Louis
# Date:    09 July 2019
# Project: AsTeR


try: from service_WEB.imports import *
except: from imports import *

# from map_attributes import GoogleMaps
# from map_attributes import Map
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

# Load credentials
with open('configs/config.yaml') as raw: crd = yaml.safe_load(raw)
SQL_URL = crd['sql_api']
API_KEY = crd['api_key']
# Secure application
application = Flask(__name__)
application.secret_key = crd['secret_key']
GoogleMaps(application, key=crd['googlemaps_api'])

class EmergencyUnit:
    def __init__(self, unit_id, type, name, lat, lng):
        self.unit_id = unit_id
        self.type = type
        self.name = name
        self.lat = lat
        self.lng = lng

dispatched_units = (
    EmergencyUnit(unit_id='patrol03', type='Police',      name='Police Patrol 3',     lat=37.419687, lng=-121.862749),
    EmergencyUnit(unit_id='amb07',    type='Ambulance',   name='Ambulance Unit 7',    lat=37.415902, lng=-122.142975),
    EmergencyUnit(unit_id='fire22',   type='Firefighter', name='Firefighter Unit 22', lat=37.4300,   lng=-122.1400)
)

# Index
@application.route('/')
@application.route('/home/')
def index():

    return render_template('home.html')

# About AsTeR
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

    def register_user(profile, api_key, url):
        
        url = '/'.join([url, 'register'])
        header = {'apikey': api_key}
        prm = dict(zip(['username', 'password', 'firstname', 'lastname', 'email'], profile))
        req = requests.post(url, headers=header, params=prm)
        
        return json.loads(req.content)

    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():

        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data

        result = register_user((username, password, first_name, last_name, email), API_KEY, SQL_URL)

        if not result['success']:
            return render_template('register.html', error=result['reason'])
        else:
            flash('You are now registered. Log in to access your simulation dashboard!', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Login page
@application.route('/login', methods=['GET', 'POST'])
def login():

    def check_connection(profile, api_key, url):
        
        warnings.simplefilter('ignore')
        
        url = '/'.join([url, 'connect'])
        username, password = profile
        header = {'apikey': api_key}
        params = {'username': username, 'password': sha256_crypt.hash(password)}
        req = requests.post(url, headers=header, params=params)
        
        return json.loads(req.content)

    if request.method == 'POST':
        # Get form fields
        username = request.form['username']
        password = request.form['password']

        result = check_connection((username, password), API_KEY, SQL_URL)

        if result['success']:
            session['username'] = username
            session['first_name'] = result['first_name']
            session['last_name'] = result['last_name']
            session['logged_in'] = True
            flash('You are now logged in!', 'success')
            return redirect(url_for('dashboard_summary'))
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


# Summary Dashboard
@application.route('/dashboard/summary')
@is_logged_in
def dashboard_summary():

    all_markers = []
    colours = {'Police': 'blue', 'Ambulance': 'red', 'Firefighter': 'yellow'}

    for dispatched_unit in dispatched_units:
        all_markers.append(
            {'icon': 'http://maps.google.com/mapfiles/ms/icons/{colour}-dot.png'.format(colour=colours.get(dispatched_unit.type)),
             'lat': dispatched_unit.lat,
             'lng': dispatched_unit.lng,
             'infobox': "<b>" + str(dispatched_unit.name) + "</b>"}
        )

    routeCoordinates = []
    for t in open('route_coordinates.txt').read().split('\n'):
        a, b = t.strip('()').split(',')
        routeCoordinates.append((float(b), float(a)))

    flightPath = [{
        'path': routeCoordinates,
        'geodesic': True,
        'strokeColor': '#FF0000',
        'strokeOpacity': 1.0,
        'strokeWeight': 2
    }]

    dispatched_map = Map(
        identifier="dispatched_units",
        lat=37.4419,
        lng=-122.1419,
        maptype='TERRAIN',
        style="height:600px;width:600px;margin:0;",
        markers=all_markers,
        polylines=flightPath,
        streetview_control=False,
        full_screen_control=False,
        maptype_control=False,
        fit_markers_to_bounds=True
    )



    return render_template('dashboard/dashboard_summary.html', dispatched_map=dispatched_map)

# Calls Dashboard
@application.route('/dashboard/calls')
@is_logged_in
def dashboard_calls():

    return render_template('dashboard/dashboard_calls.html')

# Units Dashboard
@application.route('/dashboard/units')
@is_logged_in
def dashboard_units():

    return render_template('dashboard/dashboard_units.html')

# User log out page
@application.route('/logout')
@is_logged_in
def logout():

    session.clear()
    flash('Successfully logged out', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':

    # application.run(host='127.0.0.1', port=8080)
    application.run(debug=True)
