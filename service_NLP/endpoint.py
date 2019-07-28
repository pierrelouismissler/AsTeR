# Author:  DINDIN Meryll
# Date:    27 July 2019
# Project: AsTeR

try: from service_NLP.runner import *
except: from runner import *

# Run Flask local server
application = Flask('NLP')
# Defines the API
api = AnalyzeTranscript()

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

@application.route('/run', methods=['POST'])
@filter_key
def run_service():

    arg = dict(request.args)['message']
    if len(arg) == 1: arg = str(arg[0])

    # Get the analysis running
    req = api.run(arg)

    arg = {'status': 200, 'mimetype': 'application/json'}
    return Response(response=json.dumps(req), **arg)

if __name__ == '__main__':

    application.run()
    # application.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), threaded=True)
    # application.run(host='127.0.0.1', port=8080, threaded=True)