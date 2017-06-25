import numpy as np
import os
from pandas import *
import seaborn as sns
import webbrowser


def clac_math(ifmap,w,psum):
    return ifmap * w + psum

def calc_str(ifmap, w, psum):

    psum = '' if str(psum) is '0' else str(psum)
    mult = '' if str(ifmap) is '0' or str(w) is '0' else \
                    ' '.join([str(ifmap),'*',str(w)])
    plus = '' if mult is '' or psum is '' else '+'
    res =  str(0) if mult is '' and psum is '' else ' '.join([mult,plus,'<br>',psum])

    return res

class Register(object):

    def __init__(self, init_val='0'):
        self.val = init_val

    def step(self, val):
        self.val = val

class ProcessingElement(object):
    """Basic processing elemnt"""
    def __init__(self, pe_id):
        self.cached_weight  = {'odd': Register(), 'even': Register()}
        self.ifmap          = {'data': Register(), 'epoch': Register('even')}
        self.psum           = Register()
        self.weight         = {'addr': Register(), 'data': Register(),
                               'epoch': Register('even')}
        self.id             = pe_id
        self.ifmap_out      = {'data': '0', 'epoch': 'even'}
        self.weight_out     = {'addr': 0, 'data':'0', 'epoch' : 'even'}
        self.psum_out       = '0'


    def step(self, ifmap_in, weight_in, psum_in, calc_fn = calc_str):
        ''' Calculation'''
        for key in self.ifmap.keys(): self.ifmap_out[key]  = self.ifmap[key].val
        for key in self.weight.keys(): self.weight_out[key] = self.weight[key].val
        current_weight = self.cached_weight[self.ifmap['epoch'].val].val
        self.psum_out   = calc_fn(self.ifmap['data'].val, current_weight, self.psum.val)

        ''' Sampling'''
        for key in self.ifmap.keys(): self.ifmap[key].step(ifmap_in[key])
        for key in self.weight.keys(): self.weight[key].step(weight_in[key])
        self.psum.step(psum_in)
        if self.weight['addr'].val == self.id:
            #import pdb; pdb.set_trace()
            epoch = self.weight['epoch'].val
            self.cached_weight[epoch].step(self.weight['data'].val)



class SystolicArray(object):
    """SystolicArray."""
    def __init__(self, n_rows, n_cols):
        self.n_rows = n_rows
        self.n_cols = n_cols

        self.sa = np.empty((self.n_rows, self.n_cols), object)
        for i in xrange(self.n_rows):
            for j in xrange(self.n_cols):
                self.sa[i][j] =  ProcessingElement(j)

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



class Data(object):

    def __init__(self, n_ifmaps, ifmap_size, n_ofmaps,filter_size):
        self.ifmaps = list()
        self.filters = list()

        for i in xrange(n_ifmaps):
            self.ifmaps.append([{'data':str(0), 'epoch':'even'}]*i +
                [{'data': ''.join(['IF[',str(i),',',str(r),str(c),']']), 'epoch':'even'}
                    for r in xrange(ifmap_size) for c in xrange(ifmap_size)]
                                            + [{'data':str(0), 'epoch':'even'}]*(n_ifmaps-i-1))
        self.ifmaps = np.array(self.ifmaps)

        for i in xrange(n_ifmaps):
            for j in xrange(n_ofmaps):
                self.filters.append(
                    [{'addr':j, 'data':''.join(['W[',str(i),str(j),',',str(r),str(c),']']),
                    'epoch' :'even'}
                    for r in xrange(filter_size) for c in xrange(filter_size)])
        self.filters = np.array(self.filters)


if __name__ == "__main__":

    if os.path.isfile('some_file.html'):
        os.remove('some_file.html')

    n_ifmaps    = 5
    ifmap_size  = 7
    n_ofmaps    = 5
    filter_size = 3

    data    = Data(n_ifmaps, ifmap_size, n_ofmaps, filter_size)
    weights = data.filters[:,0].reshape(n_ifmaps,n_ofmaps)
    sa      = SystolicArray(n_ifmaps,n_ofmaps)
    keys    = map(lambda x: x['data'], data.filters[:,0])
    # sa.show(keys)

    ifmap_warmup = [{'data':'0', 'epoch':'even'}]*n_ifmaps
    print("Warm up phase")
    for weight in weights.T[::-1]:
        sa.step(ifmap_warmup, weight)
        sa.show(keys)

    print("Data phase")
    for ifmap, weight in zip(data.ifmaps.T,weights.T):
       sa.step(ifmap, weight)
       sa.show(keys)

    ## webbrowser.open_new('/Users/katia.patkin/MLHW/some_file.html')
