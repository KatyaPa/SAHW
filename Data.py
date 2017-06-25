import numpy as np

class Data(object):

    def __init__(self, n_ifmaps, ifmap_size, n_ofmaps,filter_size):
        self.ifmaps = list()
        self.filters = list()

        for i in xrange(n_ifmaps):
            self.ifmaps.append([str(0)]*i +
                [''.join(['IF[',str(i),',',str(r),str(c),']'])
                    for r in xrange(ifmap_size) for c in xrange(ifmap_size)]
                                            + [str(0)]*(n_ifmaps-i-1))
        self.ifmaps = np.array(self.ifmaps)

        for i in xrange(n_ifmaps):
            for j in xrange(n_ofmaps):
                self.filters.append(
                    [{'addr':j, 'data':''.join(['W[',str(i),str(j),',',str(r),str(c),']'])}
                    for r in xrange(filter_size) for c in xrange(filter_size)])
        self.filters = np.array(self.filters)
