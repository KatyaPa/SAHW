import numpy as np
import os
from pandas import *
import seaborn as sns


def clac_math(ifmap,w,psum):
    return ifmap * w + psum

def calc_str(ifmap, w, psum):

    psum = '' if str(psum) is '0' else str(psum)
    mult = '' if str(ifmap) is '0' or str(w) is '0' else \
                    ' '.join([str(ifmap),'*',str(w)])
    plus = '' if mult is '' or psum is '' else '+'
    res =  str(0) if mult is '' and psum is '' else ' '.join([mult,plus,'<br>',psum])

    return res

class ProcessingElement(object):
    """Basic processing elemnt"""
    def __init__(self):
        self.current_weight = '0'
        self.next_weight    = '0'
        self.ifmap          = '0'
        self.psum           = '0'
        self.out_psum       = '0'
        self.out_ifmap      = '0'

    def step(self, in_ifmap, in_psum, calc_fn = calc_str):
        ''' Calculation'''
        self.out_psum  = calc_fn(self.ifmap, self.current_weight, self.psum)
        self.out_ifmap = self.ifmap
        ''' Sampling inputs'''
        self.ifmap = in_ifmap
        self.psum = in_psum

    def load_next_weight(self, weight):
        self.next_weight = weight

    def update_weight(self):
        self.current_weight = self.next_weight
        self.next_weight = 0


class SystolicArray(object):
    """SystolicArray."""
    def __init__(self, n_rows, n_cols):
        self.n_rows = n_rows
        self.n_cols = n_cols

        self.sa = np.empty((self.n_rows, self.n_cols), object)
        for i in xrange(self.n_rows):
            for j in xrange(self.n_cols):
                self.sa[i][j] =  ProcessingElement()

    def step(self, in_ifmaps):
        for i in xrange(self.n_rows):
            for j in xrange(self.n_cols):
                if i == 0 and j == 0:
                    self.sa[i][j].step(in_ifmaps[0], 0)
                elif i == 0:
                    self.sa[i][j].step(self.sa[i][j-1].out_ifmap, 0)
                elif j == 0:
                    self.sa[i][j].step(in_ifmaps[i], self.sa[i-1][j].out_psum)
                else:
                    self.sa[i][j].step(self.sa[i][j-1].out_ifmap,
                                        self.sa[i-1][j].out_psum)

    def load_next_weights(self, weights):
        for i in xrange(self.n_rows):
            for j in xrange(self.n_cols):
                self.sa[i][j].load_next_weight(weights[i][j])

    def update_weights(self):
        for i in xrange(self.n_rows):
            for j in xrange(self.n_cols):
                self.sa[i][j].update_weight()

    def show(self, keys=""):

        pandas.set_option('display.max_colwidth', 100)
        psum_mat = [[sa_e.out_psum for sa_e in sa_row] for sa_row in self.sa]
        df = DataFrame(psum_mat)

        def formatter(v):

            cm = sns.hls_palette(len(keys), h=.5, l=.4, s=.4).as_hex()
            cmap = dict(zip(keys, cm))

            span = '<span style="color: {}">{}</span>'.format
            return ''.join([span(cmap[s],s) if s in cmap
                else span("white",s) for s in v.split()])

        def bgcolor(v, color = "black"):
            return ['background-color: '+color for s in v]

        s = df.style.format(formatter).set_table_attributes("border=1")\
                .apply(bgcolor)

        open('some_file.html', 'a').write(s.render())



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
                    [''.join(['W[',str(i),str(j),',',str(r),str(c),']'])
                    for r in xrange(filter_size) for c in xrange(filter_size)])
        self.filters = np.array(self.filters)


if __name__ == "__main__":

    if os.path.isfile('some_file.html'):
        os.remove('some_file.html')

    data = Data(5, 7, 5, 3)
    # weights = [[''.join(['W[',str(i),str(j),',','00]']) for j in xrange(5)] for i in xrange(5)]
    # print np.array(weights)
    weights = data.filters[:,0].reshape(5,5)
    sa = SystolicArray(5,5)
    sa.load_next_weights(weights)
    sa.update_weights()
    keys = data.filters[:,0].tolist()
    # import pdb; pdb.set_trace()
    sa.show(keys)
    for ifmap in data.ifmaps.T:
        sa.step(ifmap)
        # print ("IFMAP:", ifmap.tolist())
        sa.show(keys)
