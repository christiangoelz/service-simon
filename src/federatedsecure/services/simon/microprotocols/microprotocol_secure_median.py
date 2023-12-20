import math as _math

from federatedsecure.services.simon.caches.cache import Cache
from federatedsecure.services.simon.caches.additive import CacheAdditive
from federatedsecure.services.simon.microprotocols.microprotocol import Microprotocol

"""
Implements FIND-RANKED-ELEMENT-MULTIPARTY from [1].

[1] Aggarwal, G., Mishra, N. & Pinkas, B. Secure Computation of the Median
(and Other Elements of Specified Ranks). J Cryptol 23, 373–401 (2010).
https://doi.org/10.1007/s00145-010-9059-9
"""


class MicroprotocolSecureMedian(Microprotocol):

    def __init__(self, microservice, properties, myself):
        super().__init__(microservice, properties, myself)
        self.n = self.network.count
        self.array = None
        self.digits_after = None
        self.even = None

        self.initialize_chaches()
        self.initialize_stages()

    def initialize_chaches(self):
        self.register_cache('input', Cache())
        self.register_cache('samples', CacheAdditive(minimum=self.n))
        self.register_cache('digits_after', Cache())
        self.register_cache('range', Cache())

    def initialize_stages(self):
        self.register_stage(0, ['input'], self.stage_0)
        self.register_stage(1, ['digits_after'], self.stage_1)
        self.register_stage(2, ['samples', 'range'], self.stage_2)

    def stage_0(self, args):
        max_decimals = self._max_decimals(args['input']['array'])
        self.array = args['input']['array']
        self.network.broadcast(args['input']['samples'], 'samples')
        self.start_pipeline('MinimumMaximum',
                            'digits_after',
                            [{'minimum': 0,
                            'maximum': max_decimals}])
        return 1, None

    def stage_1(self, args):
        self.digits_after = args['digits_after']['maximum']
        self.array = [num * (10**self.digits_after) for num in self.array]
        self.start_pipeline('MinimumMaximum',
                            'range',
                            [{'minimum': min(self.array),
                            'maximum': max(self.array)}])
        return 2, None

    def stage_2(self, args):
        if args['samples'] % 2 == 0:
            ks = [args['samples'] // 2, (args['samples'] // 2) + 1]
            self.register_stage(3, ['samples','k0','k1'], self.stage_3)
            self.even = True
        else:
            ks = [args['samples'] // 2 + 1]
            self.register_stage(3, ['samples','k0'], self.stage_3)
            self.even = False

        for i, k in enumerate(ks):
            self.register_cache(f'k{i}', Cache())
            self.start_pipeline('FindKRank',
                                f'k{i}', 
                                [{'array': self.array,
                                'k': k,
                                'a': args['range']['minimum'],
                                'b': args['range']['maximum']}])
        return 3, None

    def stage_3(self,args):
        k0 = args['k0']['item'] / (10**self.digits_after)
        if self.even:
            k1 = args['k1']['item'] / (10**self.digits_after)
            median = (k0 + k1)/ 2
        else:
            median = k0
        return -1, {'inputs': self.n,
                    'result': {
                        'samples': args['samples'],
                        'median': median}}

    def _max_decimals(self, array):
        return max(len(str(num).split('.')[1]) if '.' in str(num) else 0 for num in array)
