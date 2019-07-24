# Author:  DINDIN Meryll
# Date:    24 July 2019
# Project: AsTeR

import uuid
import numpy as np
import pandas as pd

from shapely.geometry import Point
from shapely.geometry import shape

class SimulationCalls:

    def __init__(self, map_center, map_radius, n_steps, \
        call_centers=None, background_call_centers=None, max_calls=250,\
        random_simulation=None, random_centers=10, random_seed=0):
        # Set randomness
        np.random.seed(random_seed)

        # Geography
        self.map_center=map_center
        self.map_radius=map_radius

        # Simulation parameters
        self.n_steps=n_steps
        self.max_calls=max_calls

        # Random similation / Debug mode
        self.random_simulation=random_simulation
        self.random_centers=random_centers
    
        if random_simulation:
            self.epicenters = self._epicenter_gen(map_center, map_radius, random_centers)
            self.background_epicenters = None
        else:
            self.epicenters = np.array([np.array(v) for (k,v) in call_centers.items()])
            self.background_epicenters = np.array([np.array(v) for (k,v) in background_call_centers.items()])

    def run(self):

        self.all_calls = self._all_calls_gen(self.epicenters, self.background_epicenters)
        return self.all_calls

    def _epicenter_gen(self, center, nb_points):
        """
        Draw random samples from a multivariate normal distribution with spherical covariance.
        Typical usage: generate specific approximate locations from which calls are coming.
        Input:
            center: distribution mean
            radius: distribution standard deviation
            nb_points: int. number of samples drawn
        Return:
            distribution: np.array
        """
        return np.random.multivariate_normal(center, self.map_radius*np.identity(2), nb_points)

    def _calls_gen(self, centers, calls_per_center):
        """
        Generates a set number of calls taken from a multivariate distribution around each center.
        Input:
            centers: np.array of size (n*2). Coordinates of centers.
            calls_per_center: np.array like of size n. Number of calls for each center.
        Return:
            all_calls: pd.DataFrame. Randomly generated calls.
        """
        n=len(centers)
        all_calls = []
        for i in range(n):
            center_radius = np.random.normal(loc=self.map_radius, scale=self.map_radius/10)
            center_calls = self._epicenter_gen(centers[i,:], calls_per_center[i])
            all_calls.append(center_calls)
        all_calls = np.concatenate(all_calls)
        all_calls = pd.DataFrame(all_calls, columns=['latitude', 'longitude'])
        
        all_calls['time'] = np.random.randint(low=0, high=self.n_steps, size=len(all_calls))
        
        return all_calls

    def _all_calls_gen(self, epicenters, background_epicenters=None):
        """
        Generates a set number of calls taken from a multivariate distribution around each center.
        Input:
            centers: np.array of size (n*2). Coordinates of centers.
            calls_per_center: np.array like of size n. Number of calls for each center.
        Return:
            all_calls: pd.DataFrame. Randomly generated calls.
        """
        nb_calls_epicenter = np.random.randint(low=1, high=self.max_calls, size=len(epicenters))
        all_calls = self._calls_gen(epicenters, nb_calls_epicenter)
        
        if not background_epicenters is None:
            nb_calls_epicenter = np.random.randint(low=5, high=self.max_calls, size=len(background_epicenters))
            background_calls = self._calls_gen(background_epicenters, nb_calls_epicenter)
            all_calls = pd.concat([all_calls, background_calls], axis=0)
            
        return all_calls
    
class BayAreaFilter:
    
    _ID = ['s7830z.7', 's7830z.10', 's7830z.20']
    
    def __init__(self, shape_file='graphs/bayarea.json'):
        
        self.zones = []
        for poly in pd.read_json(shape_file, lines=True).features.values[0]:
            if poly['id'] in self._ID: self.zones.append(poly['geometry'])
                
    def cast_inbay(self, longitude, latitude):
    
        inbay, point = False, Point(longitude, latitude)
        for zone in self.zones: inbay = inbay | point.within(shape(zone))

        return inbay
    
    def run(self, simulations):
        
        res = []
        for i, row in simulations.iterrows():
            res.append(self.cast_inbay(row.longitude, row.latitude))
        
        return simulations[np.asarray(res)]
    
    @staticmethod
    def random_phone():
        n = '0000000000'
        a = str(np.random.choice([747, 213, 310, 323, 818, 424]))
        b = '{:03d}'.format(np.random.randint(0, 1000))
        c = '{:04d}'.format(np.random.randint(0, 10000))
        return a + '-' + b + '-' + c

    def yamlify(self, simulations):
        
        for i, row in simulations.iterrows():
            print('- call_id: {}'.format(uuid.uuid4().hex))
            print('  phone_number: {}'.format(self.random_phone()))
            print('  longitude: {}'.format(row.longitude))
            print('  latitude: {}'.format(row.latitude))
            print('  occurence: {}'.format(row.time))

if __name__ == '__main__':

    map_radius = 5e-4
    map_center = (37.7649, -122.4194)
    call_centers = {'Central Richmond': (37.778453, -122.491263),
                    'Bernal Heights': (37.737023, -122.4165579),
                    'Daly City': (37.687242, -122.470412),
                    'Russian Hill': (37.800439, -122.419592),
                    'Sausalito': (37.858326, -122.485150),
                    'Oakland': (37.805166, -122.273354),
                    'Piedmont': (37.825557, -122.232404),
                    'Berkeley': (37.867640, -122.267804)}
    epicenters = {'Central Richmond': (37.778453, -122.491263)}

    arg = {'call_centers': call_centers, 'background_call_centers': epicenters}
    sim = SimulationCalls(map_center, map_radius, 100, max_calls=500, **arg)
    dtf = sim.run()
    flt = BayAreaFilter(shape_file='graphs/bayarea.json')
    dtf = flt.run(dtf)
    flt.yamlify(dtf)