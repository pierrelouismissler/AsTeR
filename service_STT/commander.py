# Author:  DINDIN Meryll
# Date:    28 June 2019
# Project: AsTeR

import os
import json
import requests
import numpy as np
import pandas as pd

# Needed for visualisation
try: import matplotlib.pyplot as plt
except: pass

class Commander:

    def __init__(self, voice_path, config={}):

        self.config = config
        self.voice_path = voice_path
        # Transform the file to a single channel
        self._singularize()

    def _singularize(self):
    
        # Use FFMPEG to separate the channels
        tmp = self.voice_path.split('/')[-1]
        out = tmp.split('.')[0] + '_single.' + tmp.split('.')[1]
        out = '/'.join(self.voice_path.split('/')[:-1] + [out])

        # Extract channels
        try: os.system('ffmpeg -y -i {} -map_channel 0.0.0 {}'.format(self.voice_path, out))
        except: pass

        # Overwrite the files
        if os.path.exits(out): 
            os.remove(self.voice_path)
            os.rename(out, self.voice_path)

    def get_transcript(self, api_type='IBM'):

        fle = {'audio_file': open(self.voice_path, 'rb')}
        req = requests.post(self.config['url'], files=fle, params={'api_type': api_type})

        try: return json.loads(req.content)
        except: return None

    def draw(self, request, title=None, figsize=(18,6)):

        df = pd.DataFrame.from_dict(request)
        fig, ax = plt.subplots(figsize=figsize)

        begin, stops, names = df.starts.values, df.ends.values, df.words.values
        # Create the base line
        start, stop = min(begin), max(stops)
        ax.plot((start, stop), (0, 0), 'k', alpha=.5)

        for ii, (iname, istart, istop) in enumerate(zip(names, begin, stops)):

            level = np.asarray([0.3, 0.6])[ii % 2]
            vert = 'top' if level < 0 else 'bottom'
            ax.scatter(istart, 0, s=100, facecolor='salmon', edgecolor='crimson', zorder=9999)
            ax.plot((istart, istart), (0, 1), c='dodgerblue', alpha=.5)
            ax.bar(istart, level, width=istop-istart, align='edge', color='tomato', alpha=0.0)
            arg = {'horizontalalignment': 'center', 'verticalalignment': vert}
            ax.text(istart + (istop-istart)/2, level, iname, fontsize=14, backgroundcolor=(0, 0, 0, 0), rotation=90, **arg)

        fig.suptitle(title, fontsize=16)
        fig.autofmt_xdate()
        plt.setp((ax.get_yticklabels() + ax.get_yticklines() + list(ax.spines.values())), visible=False)
        plt.show()
        ax.bar(istop, level, width=1000, align='edge', color='lightblue', alpha=0.5)
