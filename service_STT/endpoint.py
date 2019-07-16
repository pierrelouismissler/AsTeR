# Author:  DINDIN Meryll
# Date:    28 June 2019
# Project: AsTeR

from apis import *

# Defines the service APIs

api_IBM = Voice_IBM()
api_Rev = Voice_Rev()
api_GGC = Voice_GGC()

# Run Flask local server
app = Flask('STT')

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

if __name__ == '__main__':

    @app.route('/run', methods=['POST'])
    @filter_key
    def run_service():

        fle = request.files['audio_file']
        if not os.path.exists('.tmp'): os.mkdir('.tmp')
        nme = '/'.join(['./.tmp', secure_filename(fle.filename)])
        fle.save(nme)

        arg = dict(request.args)['api_type']
        if len(arg) == 1: arg = str(arg[0])
        if arg == 'Rev': req = api_Rev.request(nme)
        if arg == 'GGC': req = api_GGC.request(nme)
        if arg == 'IBM': req = api_IBM.request(nme)

        # Remove the audio file
        os.remove(nme)

        arg = {'status': 200, 'mimetype': 'application/json'}
        return Response(response=json.dumps(req), **arg)

    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), threaded=True)
    # app.run(host='127.0.0.1', port=8080, threaded=True)
