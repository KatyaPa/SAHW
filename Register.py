class Register(object):

    def __init__(self, init_val='0'):
        self.val = init_val

    def step(self, next_val):
        self.val = next_val
