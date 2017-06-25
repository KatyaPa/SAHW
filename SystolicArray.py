import numpy as np
from pandas import *
import seaborn as sns
import ProcessingElement as pe

class SystolicArray(object):
    """SystolicArray."""
    def __init__(self, n_rows, n_cols):
        self.n_rows = n_rows
        self.n_cols = n_cols

        self.sa = np.empty((self.n_rows, self.n_cols), object)
        for i in xrange(self.n_rows):
            for j in xrange(self.n_cols):
                self.sa[i][j] =  pe.ProcessingElement(j)

    def step(self, ifmaps_in, weights_in):
        for i in xrange(self.n_rows):
            for j in xrange(self.n_cols):
                ifmap_in = ifmaps_in[i] if j == 0 else self.sa[i][j-1].ifmap_out
                psum_in = '0' if i == 0 else self.sa[i-1][j].psum_out
                weight_in = weights_in[i] if j == 0 else self.sa[i][j-1].weight_out
                self.sa[i][j].step(ifmap_in, weight_in, psum_in)

    def show(self, keys=""):

        pandas.set_option('display.max_colwidth', 100)
        # psum_mat = [[sa_e.cached_weight['even'].val for sa_e in sa_row] for sa_row in self.sa]
        psum_mat = [[sa_e.psum_out for sa_e in sa_row] for sa_row in self.sa]
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
