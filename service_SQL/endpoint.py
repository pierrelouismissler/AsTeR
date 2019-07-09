# Author:  DINDIN Meryll
# Date:    09 July 2019
# Project: AsTeR

try: from service_SQL.schema import *
except: from schema import *

app = Flask('SQL')
app.config['SQLALCHEMY_DATABASE_URI'] = format_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# Change application context to avoid conflict
with app.app_context(): dtb.init_app(app)

if __name__ == '__main__':

    @app.route('/connect', methods=['POST'])
    def connect():

        result, arg = False, dict(request.args)
        usr = User.query.filter_by(username=arg['username']).first()
        if not (usr is None) and (usr.password == arg['password']): result = True

        arg = {'status': 200, 'mimetype': 'application/json'}
        return Response(response=json.dumps({'allow_connection': result}), **arg)

    #app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), threaded=True)
    app.run(host='127.0.0.1', port=8080)