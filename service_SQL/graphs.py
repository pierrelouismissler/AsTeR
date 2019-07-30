# Author:  DINDIN Meryll
# Date:    18 July 2019
# Project: AsTeR

try: from service_SQL.imports import *
except: from imports import *

class CityGraph:
    
    def __init__(self, shapefile):
        
        self.rds = geopandas.read_file(shapefile)
        
        self.dtf = []

        print('> Nodes extraction:')
        for line in tqdm.tqdm(self.rds.geometry.values):
            for idx, component in enumerate(list(line.coords)):
                x_1, y_1 = component
                try:
                    x_2, y_2 = list(line.coords)[idx+1]
                    distance = np.sqrt(np.square(x_2 - x_1) + np.square(y_2 - y_1))
                    self.dtf.append([x_1, y_1, x_2, y_2, distance])
                except: pass
                try:
                    x_2, y_2 = list(line.coords)[idx-1]
                    distance = np.sqrt(np.square(x_2 - x_1) + np.square(y_2 - y_1))
                    self.dtf.append([x_1, y_1, x_2, y_2, distance])
                except: pass

        self.dtf = pd.DataFrame(self.dtf, columns=['from_x', 'from_y', 'to_x', 'to_y', 'distance'])
        self.dtf = self.dtf.drop_duplicates()
        self.dtf['point_id'] = self.dtf.index
        
    def unify_points(self):
        
        print('> Nodes unification:')
        for row in tqdm.tqdm(self.dtf.values):
            tmp = self.dtf[(self.dtf.from_x == row[0]) & (self.dtf.from_y == row[1])]
            self.dtf.loc[tmp.index, 'point_id'] = min(tmp.point_id)
            
    def build_graph(self, dump=None):
        
        self.unify_points()
        graph = dict()

        print('> Build edges:')
        for point_id in tqdm.tqdm(self.dtf.point_id.unique()):
            point = self.dtf[self.dtf.point_id == point_id].values[0]
            edges = dict()
            for row in self.dtf[self.dtf.point_id == point_id].values:
                edges['{}:{}'.format(row[2], row[3])] = row[4] 
            graph['{}:{}'.format(point[0], point[1])] = edges
            
        if not (dump is None): joblib.dump(graph, dump)
        else: return graph

class Trajectory:

    def __init__(self, graphfile):

        self.G = joblib.load(graphfile)

    def update_graph(self, key, weight):

        old = self.G[key]
        for key in old.keys(): old[key] = weight
        self.G[key] = old

    def closest_key(self, longitude, latitude):

        keys = [(float(e.split(':')[0]), float(e.split(':')[1])) for e in self.G.keys()]
        dist = np.sum(np.abs(np.asarray(keys) - np.asarray([longitude, latitude])), axis=1)
        clos = keys[dist.argmin()]

        return '{}:{}'.format(clos[0], clos[1])

    def shortest_path(self, origin, goal):

        inf = float('inf')
        D = {origin: 0}
        Q = PQDict(D)
        P = {}
        U = set(self.G.keys())

        while U:

            (v, d) = Q.popitem()
            D[v] = d
            U.remove(v)
            if v == goal: break

            for w in self.G[v]:
                if w in U:
                    d = D[v] + self.G[v][w]
                    if d < Q.get(w, np.inf):
                        Q[w] = d
                        P[w] = v

        v = goal
        path = [v]

        while v != origin:
            v = P[v]
            path.append(v) 

        path.reverse()

        return path
