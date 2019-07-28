# Author:  DINDIN Meryll
# Date:    27 July 2019
# Project: AsTeR

try: from service_NLP.imports import *
except: from imports import *

class Senti_IBM:

    def __init__(self, credentials='configs/key_ibm.json'):

        with open(credentials, 'r') as raw: crd = json.load(raw)
        arg = {'iam_apikey': crd['key'], 'url': crd['url']}
        self.api = NaturalLanguageUnderstandingV1(version='2018-11-16', **arg)
        self.voc = list(pd.read_parquet('models/vocabulary.pq').index)
        
        sen = SentimentOptions(targets=self.voc)
        key = KeywordsOptions(sentiment=True, limit=10)
        self.fea = Features(sentiment=sen, keywords=key)

    def request(self, message):

        req = self.api.analyze(text=message, features=self.fea).get_result()
        emo = req['sentiment']['document']['score']
        wrd = [[e['text'], e['relevance']] for e in req['keywords']]
        
        return emo, wrd
    
class KeyWd_RAI:
    
    def __init__(self, credentials='configs/key_rapidai.json'):
        
        with open(credentials) as raw: key = json.load(raw)['key']
        self.h_1 = {"X-RapidAPI-Key": key}
        self.u_1 = "https://textanalysis-keyword-extraction-v1.p.rapidapi.com/keyword-extractor-text"
        self.h_2 = {"X-RapidAPI-Key": key, "Content-Type": "application/json"}
        self.u_2 = "https://microsoft-azure-text-analytics-v1.p.rapidapi.com/keyPhrases"
    
    def request(self, message):
        
        r_1 = requests.post(self.u_1, headers=self.h_1, data={"text": message, "wordnum": 10})
        r_1 = json.loads(r_1.content)['keywords']
        inp = {'documents': [{'language': 'en', 'id': 'string', 'text': message}]}
        r_2 = requests.post(self.u_2, headers=self.h_2, data=(str(inp)))
        r_2 = json.loads(r_2.content)['documents'][0]['keyPhrases']
        
        return r_1 + r_2
    
class GetClass:
    
    def __init__(self, directory='models'):
        
        self.r_f = joblib.load('/'.join([directory, 'rf_model.jb']))
        self.vec = joblib.load('/'.join([directory, 'vectorizer.jb']))
        
    def request(self, message):
        
        return self.r_f.predict(self.vec.transform([message]))[0]
    
class AnalyzeTranscript:
    
    def __init__(self, directory='.'):
        
        self.ibm = Senti_IBM(credentials='/'.join([directory, 'configs/key_ibm.json']))
        self.rai = KeyWd_RAI(credentials='/'.join([directory, 'configs/key_rapidai.json']))
        self.cls = GetClass(directory='/'.join([directory, 'models']))
        self.voc = pd.read_parquet('/'.join([directory, 'models/vocabulary.pq']))
        self.stp = set(joblib.load('/'.join([directory, 'models/stopwords.jb'])))
        
    @staticmethod
    def relevance_map(request):
        
        res = dict()
        for words, relevance in request:
            for word in words.split():
                res[word] = relevance

        return res

    def preprocess(self, message):
        
        # remove punctation
        res = message.translate(str.maketrans('', '', string.punctuation))
        # tokenize into words (all lower case)
        res = res.lower()
        # cast type
        res = res.encode('ascii', 'ignore').decode('ascii')

        lst = res.split() 
        lst = [w for w in lst if not w in self.stp]
        res = ' '.join(lst)

        return res
    
    def importance_from_vocabulary(self, word):

        try: return float(self.voc.loc[word].importance)
        except: return 0.0

    @staticmethod
    def importance_from_relevance(word, mapper):

        try: return mapper[word]
        except: return 0.0
    
    def run(self, message):
        
        new = self.preprocess(message)
        e,l = self.ibm.request(new)
        rai = self.rai.request(new)
        cls = self.cls.request(new)
        kys = list(np.unique(rai + [e[0] for e in l]))
        
        rev = self.relevance_map(l)
        i_v = np.asarray([self.importance_from_vocabulary(w) for w in new.split()])
        i_r = np.asarray([self.importance_from_relevance(w, rev) for w in new.split()])
        sco = np.sum(i_v*i_r)
        
        return {'emotion': e, 'score': sco, 'keysections': kys, 'class': cls}
