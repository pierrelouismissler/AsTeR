# Author:  DINDIN Meryll
# Date:    09 July 2019
# Project: AsTeR

try: from service_SQL.schema import *
except: from schema import *

try: from service_SQL.graphs import *
except: from graphs import *

app = Flask('SQL')
app.config['SQLALCHEMY_DATABASE_URI'] = format_url('sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# Change application context to avoid conflict
with app.app_context(): dtb.init_app(app)

# API key filter
def filter_key(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):
        # Load API keys
        with open('configs/api_keys.yaml') as raw: keys = yaml.safe_load(raw)['keys']
        # Check security
        if request.headers.get('apikey') and request.headers.get('apikey') in keys:
            return function(*args, **kwargs)
        else: 
            arg = {'status': 200, 'mimetype': 'application/json'}
            msg = {'success': False, 'reason': 'Wrong api key provided'}
            return Response(response=json.dumps(msg), **arg)

    return decorated_function

# Obtain the transcript from the STT service
def get_transcript(audio_path, key):

    fle = {'audio_file': open(audio_path, 'rb')}
    url = '/'.join(['http://servicesql-comedic-wallaby.mybluemix.net', 'run'])
    req = requests.post(url, headers={'apikey': key}, files=fle, params={'api_type': 'IBM'})

    try: return json.loads(req.content)
    except: return None

# Determines and updates the paths
grp = Trajectory('graphs/sanfrancisco.jb')

if __name__ == '__main__':

    @app.route('/connect', methods=['POST'])
    @filter_key
    def connect():

        boo, req = False, parse_arguments(request)
        arg = {'status': 200, 'mimetype': 'application/json'}
        usr = User.query.filter_by(username=req['username']).first()

        if usr is None:
            boo = False
            err = 'Username is not registered'            
        elif not sha256_crypt.verify(usr.password, req['password']):
            boo = False
            err = 'Password was wrongly inputed'
        else:
            boo = True
            err = 'None'

        msg = {'username': req['username'], 'success': boo, 'reason': err}
        if boo: msg.update({'first_name': usr.firstname, 'last_name': usr.lastname})
        return Response(response=json.dumps(msg), **arg)

    @app.route('/register', methods=['POST'])
    @filter_key
    def register():

        req = parse_arguments(request)
        arg = {'status': 200, 'mimetype': 'application/json'}
        
        usr = User.query.filter_by(username=req['username']).first()
        if not usr is None:
            msg = {'username': req['username'], 'success': False, 'reason': 'Username is already used'}
            return Response(response=json.dumps(msg), **arg)

        eml = User.query.filter_by(email=req['email']).first()
        if not eml is None:
            msg = {'username': req['username'], 'success': False, 'reason': 'Email adress is already used'}
            return Response(response=json.dumps(msg), **arg)

        dtb.session.add(User(**req))
        dtb.session.commit()
        msg = {'username': req['username'], 'success': True, 'reason': 'None'}
        return Response(response=json.dumps(msg), **arg)

    @app.route('/get_call', methods=['POST'])
    @filter_key
    def get_call():

        res, arg = dict(), parse_arguments(request)
        lst = Call.query.filter(Call.time <= arg['timing'])

        for call in lst:
            req = call.__dict__.copy()
            for key in ['call_id', '_sa_instance_state']: del req[key]
            res[call.call_id] = req

        arg = {'status': 200, 'mimetype': 'application/json'}
        return Response(response=json.dumps(res), **arg)

    @app.route('/get_unit', methods=['POST'])
    @filter_key
    def get_unit():

        def update_units():

            lst = Unit.query.all()
            for unit in [unit for unit in lst if unit.target != 'none']:
                pos = grp.closest_key(unit.latitude, unit.longitude)
                obj = grp.closest_key(*[float(x) for x in unit.target.split(':')])
                # Update object
                setattr(unit, 'path', '|'.join(grp.shortest_path(pos, obj)))
                dtb.session.add(unit)
                dtb.session.commit()
                # Memory efficiency
                del pos, obj

        update_units()
        res, lst = dict(), Unit.query.all()

        for unit in lst:
            req = unit.__dict__.copy()
            for key in ['unit_id', '_sa_instance_state']: del req[key]
            res[unit.unit_id] = req

        arg = {'status': 200, 'mimetype': 'application/json'}
        return Response(response=json.dumps(res), **arg)

    @app.route('/add_unit', methods=['POST'])
    @filter_key
    def add_unit():

        req = parse_arguments(request)
        arg = {'status': 200, 'mimetype': 'application/json'}

        unt = Unit.query.filter_by(unit_id=req['unit_id']).first()
        if not unt is None: 
            msg = {'success': False, 'reason': 'Unit ID is already used'}
            return Response(response=json.dumps(msg), **arg)

        dtb.session.add(Unit(**req))
        dtb.session.commit()
        msg = {'unit_id': req['unit_id'], 'success': True, 'reason': 'None'}
        return Response(response=json.dumps(msg), **arg)

    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), threaded=True)
    # app.run(host='127.0.0.1', port=8080, threaded=True)