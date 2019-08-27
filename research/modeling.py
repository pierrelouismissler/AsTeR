# Author:  DINDIN Meryll
# Date:    27 August 2019
# Project: AsTeR

try: from research.imports import *
except: from imports import *

class DataLoader:

    def __init__(self):

        # Launch intrinsic methods
        self._loads()
        self._clean()

    def _loads(self, directory='data', encoding='ISO-8859-1'):

        def load_file(filename, disaster):
            
            arg = {'skip_blank_lines': True, 'encoding': encoding}
            nme = '/'.join([directory, filename])
            dtf = pd.read_csv(nme, **arg)
            dtf['cat'] = disaster

            # Memory efficiency
            del arg, nme

            return dtf

        files = [
            ('2013_pakistan_eq.csv', 'eq'),
            ('2014_california_eq.csv', 'eq'),
            ('2014_chile_eq_en.csv', 'eq'),
            ('2014_ebola_virus.csv', 'virus'),
            ('2014_hurricane_odile.csv', 'storm'),
            ('2014_india_floods.csv', 'flood'),
            ('2014_mers_cf_labels.csv', 'virus'),
            ('2014_pakistan_floods_cf_labels.csv', 'flood'),
            ('2014_typhoon_hagupit_cf_labels.csv', 'storm'),
            ('2015_cyclone_pam_cf_labels.csv', 'storm'),
            ('2015_nepal_eq_cf_labels.csv', 'eq')
                ]

        drops = [
            '_unit_id', 
            '_unit_state',
            '_golden', 
            '_trusted_judgments',
            '_last_judgment_at', 
            'choose_one_category:confidence', 
            'choose_one_category_gold',
            'tweet_id'
                ]

        dtf = pd.concat([load_file(*fle) for fle in files])
        # Drop unneccessary columns
        dtf.drop(drops, axis=1, inplace=True)
        # Drop nan values
        dtf.dropna(inplace=True)
        
        self.dtf = dtf

        # Memory efficiency
        del files, drops, dtf

    def _clean(self):

        arg = {'value': '', 'regex': True}
        stp = set(stopwords.words("english"))

        # Remove non alpabetical/ numerical
        self.dtf = self.dtf.replace(to_replace=r'&amp;', **arg)
        self.dtf = self.dtf.replace(to_replace=r'&gt;', **arg)
        # Remove hyperlinks
        self.dtf = self.dtf.replace(to_replace=r'http\S+', **arg)
        # Remove usernames
        self.dtf = self.dtf.replace(to_replace=r'@\S+', **arg) 
        # Remove retweet
        self.dtf = self.dtf.replace(to_replace='RT :', **arg) 
        self.dtf = self.dtf.replace(to_replace='RT ', **arg)
        # Remove hashtags
        self.dtf = self.dtf.replace(to_replace='#', **arg)
        # Remove punctation
        self.dtf = self.dtf.replace(to_replace='[",:!?\\-]', **arg)
        # Tokenize into words (all lower case)
        self.dtf.tweet_text = self.dtf.tweet_text.str.lower()
        # Uniformize the type
        self.dtf.tweet_text = self.dtf.tweet_text.apply(lambda x: x.encode('ascii', 'ignore').decode('ascii'))
        # Remove stopwords
        self.dtf.tweet_text = self.dtf.tweet_text.str.split() 
        self.dtf.tweet_text = self.dtf.tweet_text.apply(lambda x: [item for item in x if item not in stp])
        self.dtf.tweet_text = self.dtf.tweet_text.apply(lambda x: ' '.join(x).strip())

    def split(self, test_size, random_state, shuffle=True, max_features=2000, filename=None):

        # Defines the sparse preprocessor (bag of words)
        arg = {'preprocessor': None, 'stop_words': None, 'max_features': max_features}
        sts = CountVectorizer(analyzer="word", tokenizer=None, **arg)

        # Split the data into train and test sets
        arg = {'test_size': test_size, 'random_state': random_state, 'shuffle': shuffle}
        x_t, x_v, y_t, y_v = train_test_split(self.dtf.tweet_text, self.dtf.choose_one_category, **arg)

        # Defines the bag of words
        b_t = sts.fit_transform(x_t).toarray()
        b_v = sts.transform(x_v).toarray()

        # Serialize the preprocessing
        if not filename is None: joblib.dump(sts, filename)

        return b_t, b_v, y_t, y_v

class Experiment:

    _INIT = 50
    _OPTI = 0

    def __init__(self, name=str(int(time.time()))):

        self._id = name
        self.obj = 'classification'
        self.dir = 'experiments/{}'.format(self._id)
        if not os.path.exists(self.dir): os.mkdir(self.dir)
        self.log = Logger('/'.join([self.dir, 'logs.log']))
        self.dtb = DataLoader()

    def single(self, model, test_size=0.2, random_state=42, threads=cpu_count(), weights=False):

        self.log.info('Launch training for {} model'.format(model))
        self.log.info('Use {} concurrent threads\n'.format(threads))

        # Split the data for validation
        fle = '/'.join([self.dir, 'baggs.jb'])
        x_t, x_v, y_t, y_v = self.dtb.split(test_size, random_state, filename=fle)
        # Defines the problem
        prb = Prototype(x_t, x_v, y_t, y_v, model, self.obj, 'acc', threads=threads, weights=weights)
        # Launch the Bayesian optimization
        opt = Bayesian(prb, prb.loadBoundaries(), self.log, seed=random_state)
        opt.run(n_init=self._INIT, n_iter=self._OPTI)

        # Serialize the configuration file
        cfg = {'strategy': 'single', 'model': model, 'id': self._id, 'optimization': 'bayesian'}
        cfg.update({'random_state': random_state, 'threads': threads, 'test_size': test_size})
        cfg.update({'trial_init': self._INIT, 'trial_opti': self._OPTI})
        cfg.update({'best_score': prb.bestScore(), 'validation_metric': 'acc'})
        nme = '/'.join([self.dir, 'config.json'])
        with open(nme, 'w') as raw: json.dump(cfg, raw, indent=4, sort_keys=True)

        # Serialize parameters
        prm = prb.bestParameters()
        nme = '/'.join([self.dir, 'params.json'.format(model)])
        with open(nme, 'w') as raw: json.dump(prm, raw, indent=4, sort_keys=True)

    def saveModel(self):

        # Extract the parameters
        with open('/'.join([self.dir, 'config.json']), 'r') as raw: cfg = json.load(raw)
        with open('/'.join([self.dir, 'params.json']) , 'r') as raw: prm = json.load(raw)
        # Split the data for validation
        arg = {'test_size': cfg['test_size'], 'random_state': cfg['random_state']}
        x_t, x_v, y_t, y_v = self.dtb.split(**arg, shuffle=True)
        # Defines the problem
        arg = {'threads': cfg['threads']}
        prb = Prototype(x_t, x_v, y_t, y_v, cfg['model'], self.obj, 'acc', **arg)
        prb = prb.fitModel(prm, cfg['random_state'])

        # Serialize the model
        joblib.dump(prb, '/'.join([self.dir, 'model.jb']))

    def getModel(self):

        return joblib.load('/'.join([self.dir, 'model.jb']))

    def evaluateModel(self, model=None):

        if model is None: model = joblib.load('/'.join([self.dir, 'model.jb']))

        # Extract the parameters
        with open('/'.join([self.dir, 'config.json']), 'r') as raw: cfg = json.load(raw)
        with open('/'.join([self.dir, 'params.json']) , 'r') as raw: prm = json.load(raw)
        # Split the data for validation
        arg = {'test_size': cfg['test_size'], 'random_state': cfg['random_state']}
        _, x_v, _, y_v = self.dtb.split(**arg, shuffle=True)

        y_p = model.predict(x_v)
        lab = ['accuracy', 'f1 score', 'precision', 'recall', 'kappa']
        sco = np.asarray([
            accuracy_score(y_v, y_p),
            f1_score(y_v, y_p, average='weighted'),
            precision_score(y_v, y_p, average='weighted'),
            recall_score(y_v, y_p, average='weighted'),
            cohen_kappa_score(y_v, y_p)])
        cfm = confusion_matrix(y_v, y_p)

        plt.figure(figsize=(18,4))
        grd = gridspec.GridSpec(1, 3)

        arg = {'y': 1.1, 'fontsize': 14}
        plt.suptitle('General Classification Performances for Experiment {}'.format(self._id), **arg)

        ax0 = plt.subplot(grd[0, 0])
        crs = cm.Greens(sco)
        plt.bar(np.arange(len(sco)), sco, width=0.4, color=crs)
        for i,s in enumerate(sco): plt.text(i-0.15, s-0.05, '{:1.2f}'.format(s))
        plt.xticks(np.arange(len(sco)), lab)
        plt.xlabel('metric')
        plt.ylabel('percentage')

        ax1 = plt.subplot(grd[0, 1:])
        sns.heatmap(cfm, annot=True, fmt='d', axes=ax1, cbar=False, cmap="Greens")
        plt.ylabel('y_true')
        plt.xlabel('y_pred')

        plt.tight_layout()
        plt.show()

    def getImportances(self, model=None, n_display=30):

        if model is None: 
            model = joblib.load('/'.join([self.dir, 'model.jb']))
            baggs = joblib.load('/'.join([self.dir, 'baggs.jb']))

        imp = model.feature_importances_ / np.sum(model.feature_importances_)
        imp = pd.DataFrame(np.vstack((baggs.get_feature_names(), imp)).T, columns=['feature', 'importance'])
        imp = imp.sort_values(by='importance', ascending=False)
        imp = imp[:n_display]

        # Set the style of the axes and the text color
        plt.rcParams['axes.edgecolor'] = 'black'
        plt.rcParams['axes.linewidth'] = 0.8
        plt.rcParams['xtick.color'] = '#333F4B'
        plt.rcParams['ytick.color'] = '#333F4B'
        plt.rcParams['text.color'] = '#333F4B'

        # Numeric placeholder for the y axis
        rge = list(range(1, len(imp.index)+1))

        fig, ax = plt.subplots(figsize=(18,10))
        arg = {'y': 0.9, 'fontsize': 12}
        plt.suptitle('{} Most Important Features for Experiment {}'.format(n_display, self._id), **arg)
        # Create for each feature an horizontal line 
        plt.hlines(y=rge, xmin=0, xmax=imp.importance.values.astype('float'), color='salmon', alpha=0.4, linewidth=5)
        # Create for each feature a dot at the level of the percentage value
        plt.plot(imp.importance.values.astype('float'), rge, "o", markersize=5, color='red', alpha=0.3)

        # Set labels
        ax.set_xlabel('importance', fontsize=14, fontweight='black', color = '#333F4B')
        ax.set_ylabel('')
        # Set axis
        ax.tick_params(axis='both', which='major', labelsize=12)
        plt.yticks(rge, imp.feature)
        # Change the style of the axis spines
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['left'].set_smart_bounds(True)
        ax.spines['bottom'].set_smart_bounds(True)
        # Set the spines position
        ax.spines['bottom'].set_position(('axes', -0.04))
        ax.spines['left'].set_position(('axes', 0.015))
        plt.show()

    def buildVocabulary(self, model=None):

        if model is None: 
            model = joblib.load('/'.join([self.dir, 'model.jb']))
            baggs = joblib.load('/'.join([self.dir, 'baggs.jb']))

        dtf = model.feature_importances_ / np.sum(model.feature_importances_)
        dtf = pd.DataFrame(np.vstack((baggs.get_feature_names(), dtf)).T, columns=['feature', 'importance'])
        dtf.set_index('feature', inplace=True)
        msk = np.asarray([np.any([c.isdigit() for c in w]) for w in dtf.index])
        dtf = dtf[~msk]
        exi = np.asarray([w in set(words.words()) for w in tqdm.tqdm(dtf.index)])
        dtf = dtf[exi]

        # Serialize the resulting filtered vocabulary
        dtf.to_parquet('/'.join([self.dir, 'vocab.pq']))

if __name__ == '__main__':

    # Initialize the arguments
    prs = argparse.ArgumentParser()    
    prs.add_argument('-m', '--mod', help='ModelType', type=str, default='LGB')
    prs.add_argument('-s', '--sze', help='TestSizes', type=float, default=0.2)
    prs.add_argument('-r', '--rnd', help='RandomSte', type=int, default=42)
    prs.add_argument('-c', '--cpu', help='NumOfCpus', type=int, default=cpu_count())
    prs.add_argument('-w', '--wei', help='UseWeight', type=bool, default=False)
    prs = prs.parse_args()

    exp = Experiment('1566922625')
    # Run a single-shot learning
    exp.single(prs.mod, test_size=prs.sze, random_state=prs.rnd, threads=prs.cpu, weights=prs.wei)
    exp.saveModel()
    exp.buildVocabulary()
