# Author:  DINDIN Meryll
# Date:    28 June 2019
# Project: AsTeR

from apis import *

# Defines the service APIs

api_IBM = Voice_IBM()
api_Rev = Voice_Rev()
api_GGC = Voice_GGC()

# Run Flask local server

if __name__ == '__main__':

    app = Flask('STT')

    @app.route('/run', methods=['POST'])
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

        arg = {'status': 200, 'mimetype': 'application/json'}
        return Response(response=json.dumps(req), **arg)

    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), threaded=True)
