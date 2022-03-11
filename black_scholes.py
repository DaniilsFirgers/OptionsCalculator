
from math import log, sqrt, exp
from scipy.stats import norm


class BlackSholes:
    """Calculates a fair call/put option price according to the BlackSholes formula"""
    def __init__(self, s, k, t, r, sigma):
        self.Spot = s
        self.Strike = k
        self.Maturity = t
        self.Rate = r
        self.Volatility = sigma
        self.d1()
        self.d2()

    def d1(self) -> float:
        return log((self.Spot/self.Strike)+(self.Rate+self.Volatility**2/2)*self.Maturity)/\
                   (self.Volatility*sqrt(self.Maturity))

    def d2(self) -> float:
        return self.d1() - self.Volatility*sqrt(self.Maturity)

    def call(self) -> float:
        return self.Spot*norm.cdf(self.d1()) - self.Strike*exp(-self.Rate*self.Maturity)*norm.cdf(self.d2())

    def put(self) -> float:
        return self.Strike*exp(-self.Rate*self.Maturity)*norm.cdf(-self.d2()) - self.Spot*norm.cdf(-self.d1())
