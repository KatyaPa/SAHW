import Register as reg

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
    def __init__(self, pe_id):
        self.cached_weight  = {'odd': reg.Register(), 'even': reg.Register()}
        self.ifmap          = {'data': reg.Register(), 'epoch': reg.Register('even')}
        self.psum           = reg.Register()
        self.weight         = {'addr': reg.Register(), 'data': reg.Register(),
                               'epoch': reg.Register('even')}
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
