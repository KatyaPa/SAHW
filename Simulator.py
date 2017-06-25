import os
import SystolicArray as sa
import Data as dt

class Simulator(object):

    def __init__(self,n_ifmaps, ifmap_size, n_ofmaps, filter_size):
        self.data = dt.Data(n_ifmaps, ifmap_size, n_ofmaps, filter_size)
        self.sa   = sa.SystolicArray(n_ifmaps,n_ofmaps)

if __name__ == "__main__":

    n_ifmaps    = 5
    ifmap_size  = 7
    n_ofmaps    = 5
    filter_size = 3

    sim = Simulator(n_ifmaps, ifmap_size, n_ofmaps, filter_size)

    if os.path.isfile('some_file.html'): os.remove('some_file.html')

    weights = sim.data.filters[:,0].reshape(n_ifmaps,n_ofmaps)
    keys    = map(lambda x: x['data'], sim.data.filters[:,0])

    ifmap_warmup = ['0']*n_ifmaps
    print("Warm up phase")
    for weight in weights.T[::-1]:
        sim.sa.step(ifmap_warmup, weight)
        sim.sa.show(keys)

    print("Data phase")
    for ifmap, weight in zip(sim.data.ifmaps.T,weights.T):
       sim.sa.step(ifmap, weight)
       sim.sa.show(keys)
