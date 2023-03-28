import numpy as np

class RandomNumberGenerator:
    def __init__(self, seed=None):
        
        # Parameters for two LCGs
        self.m1 = 2147483563
        self.a1 = 40014
        self.m2 = 2147483399
        self.a2 = 40692
        
        # Initialize state variables for two LCGs
        self.x1 = seed % self.m1
        self.x2 = seed % self.m2
    
    def random(self):
        # Generate two random integers using the two LCGs
        self.x1 = (self.a1 * self.x1) % self.m1
        self.x2 = (self.a2 * self.x2) % self.m2
        z = (self.x1 - self.x2) % (self.m1 - 1)
        
        # Convert to floating-point number in [0, 1)
        return z / (self.m1 - 1)

    def expovariate(self, y):
        # Generate a random variate from an exponential distribution with rate parameter y (lambda) using inverse CDF technique.
        return -np.log(1 - self.random()) / y
