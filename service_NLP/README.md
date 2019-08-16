# (Dis)AsTeR - Natural Language Processing Service

This submodule specifically implements the NLP API as we need it. The current micro-service is integrated on the web through a *Cloud Foundry Python Application*, which gives us some flexibility regarding network architecture. Ultimately, this service is the first one to be used after an emergency call is received, and will be plugged to the micro-service *service_NLP* to determine its priority / keywords. 

## Clound Foundry Application

```bash
cf api https://api.ng.bluemix.net
cf auth xxx xxx
cf push
cf logs serviceSTT --recent
```

![SERVICE](./figures/service.png)

## API Usage

```python
def get_priority(message, api_key, url):
    
    warnings.simplefilter('ignore')
    
    url = '/'.join([url, 'run'])
    header = {'apikey': api_key}
    params = {'message': message}
    req = requests.post(url, headers=header, params=params)
    
    return json.loads(req.content)
```

There are major entities in this folder that do not have been pushed on GitHub: the trained **count vectorizer**, used on the preprocessed tweets we mention in the _/research_ directory; the trained **random forest** to classify the type of emergency based on the _classes_ also presented in _/research_.

## Example

```python
{
	'emotion': -0.946692,
	'score': 0.0,
 	'keysections': ['cat', 'tree'],
 	'class': 'not_related_or_irrelevant'
}
```

## Scoring System

In the output example presented above, you'll find different items constituting our approach: a **vocabulary** defined by the feature importances of our trained random forest; an API-based keywords extraction; an API-based emotion determination, based on the defined vocabulary. The final score is a **scaled dot product** of the vocabulary importances and the extracted keywords, with a scaling being dependent on the type of emergency detected.