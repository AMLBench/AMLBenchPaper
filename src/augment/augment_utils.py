import random
import numpy

def random_clipped_amounts(bottom, top, total):
    current = 0
    amounts = []
    while current < total:
        new_amount = random.randint(bottom, top)
        if current + new_amount > total:
            new_amount = total - current
        amounts.append(new_amount)
        current += new_amount
    return amounts

def random_distributed_amounts(n_values, total):
    random_values = numpy.random.rand(n_values)
    return numpy.round((total / sum(random_values)) * random_values).astype(int)
