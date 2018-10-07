import math
import cmath


def butterworth(wp, wa, alphaP, alphaA):
    wa_norm = wa/wp
    epsilon = math.sqrt(10**(alphaP/10-1))
    n = math.ceil(math.log10((10**(alphaA/10)-1)/epsilon)/2/math.log10(wa_norm))
    poles = []

    for i in range(1, n+1):
        poles.append(wp*cmath.exp(1j*(2*i+n-1)*math.pi/2/n)/epsilon**(1/n))
    return [n, poles, [], 1]