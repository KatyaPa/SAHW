import numpy as np

class Data(object):

    def __init__(self, n_ifmaps, ifmap_size, n_ofmaps, filter_size):
        self.n_ifmaps = n_ifmaps
        self.ifmap_size = ifmap_size
        self.n_ofmaps = n_ofmaps
        self.filter_size = filter_size
        self.ifmaps = self.genIfmaps()
        self.filters = self.genFilters()

        self.ifmapAlign()
        self.ifmapPadding()
        self.filterPadding()

        # import pdb; pdb.set_trace()


    def genEl(self,el,i,j,r,c):
        return ''.join([el,'[',str(i),str(j),',',str(r),str(c),']'])

    def genIfmaps(self):
        return [[self.genEl('IF',i,'',r,c)for r in xrange(self.ifmap_size)
                    for c in xrange(self.ifmap_size)]
                        for i in xrange(self.n_ifmaps)]

    def genFilters(self):
        keys = ['addr','data']
        return [[[dict(zip(keys,[j, self.genEl('W',i,j,r,c)]))
                    for j in reversed(xrange(self.n_ofmaps))]
                        for i in xrange(self.n_ifmaps)]
                            for r in xrange(self.filter_size)
                                for c in xrange(self.filter_size)]

    def ifmapAlign(self):
        self.ifmaps = [['0']*i + ifmap for i,ifmap in enumerate(self.ifmaps)]

    def ifmapPadding(self):
        self.ifmaps = [['0']*self.n_ofmaps + ifmap for ifmap in self.ifmaps]
        max_len = max(map(lambda x: len(x), self.ifmaps))
        self.ifmaps = [ifmap + ['0']*(max_len-len(ifmap))
                        for ifmap in self.ifmaps]

    def filterPadding(self):
        max_len = len(self.ifmaps[0])
        pad = {'data': '0', 'addr': -1}

        self.filters = [[row + [pad]*(max_len - len(row)) for row in _filter]
                            for _filter in self.filters]
