from federatedsecure.services.simon.accumulators.accumulator import Accumulator

class AccumulatorFindKRank(Accumulator):

    def __init__(self, _=None):
        self.samples = None
        self.array = None
        self.k = None
        self.a = None
        self.b = None

    @staticmethod
    def deserialize(dictionary):
        accumulator = AccumulatorFindKRank()
        accumulator.samples = dictionary['samples']
        accumulator.array = dictionary['array']
        accumulator.k = dictionary['k']
        accumulator.a = dictionary['a']
        accumulator.b = dictionary['b']
        return accumulator

    def serialize(self):
        return {'samples': self.samples,
                'array': self.array,
                'k': self.k,
                'a': self.a,
                'b': self.b}

    def add(self, other):
        self.samples = self.samples + other.samples
        self.array = self.array + other.array
        self.k = self.k
        self.a = min(self.a, other.a)
        self.b = max(self.b, other.b)

    def update(self, data):
        self.samples = len(data['array'])
        self.array = data['array']
        self.k = data['k']
        self.a = data['a']
        self.b = data['b']

    def finalize(self):
        pass
