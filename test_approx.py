from appoximations import Butterworth, Chebyshev, InvChebyshev, Bessel
from scipy import signal
import matplotlib.pyplot as plt
import math
import numpy
from filter_template import GroupDelayTemplate, LowPassTemplate
from filtertypes import GroupDelay
from numpy.polynomial import Polynomial
import numpy.polynomial.polynomial as poly
from group_delay import group_delay


# wp = 1
# wa = 2
# alpha_p = 10*math.log10(2)
# alpha_a = 10
#
# approx = Butterworth()
# approx = Chebyshev()
# approx = InvChebyshev()
#
# n = approx.get_min_n(wa_norm=wa, alpha_a=alpha_a, alpha_p=alpha_p)
# [ppos, zpos, k] = approx.pzk(alpha_p=alpha_a, n=n, wa_norm=wa)
# p = []
# z = []
# if n % 2 == 1:
#     p.append(ppos.pop(len(ppos)-1))
# for i in range(len(ppos)):
#     p.append(ppos[i])
#     p.append(numpy.conj(ppos[i]))
# for i in range(len(zpos)):
#     z.append(zpos[i])
#     z.append(numpy.conj(zpos[i]))
#
# sys = signal.ZerosPolesGain(z, p, k)
# Hmia = sys.to_tf()
#
#
# [N, D] = signal.cheby2(N=n, rs=alpha_a, Wn=wa, output='ba', analog=True)
# Hposta = signal.TransferFunction(N, D)
#
# [w, mag, pha] = signal.bode(Hmia)
# plt.semilogx(w, -mag)
# plt.grid(b=True)
# plt.show()
#
# [w, mag, pha] = signal.bode(Hposta)
# plt.semilogx(w, -mag)
# plt.grid(b=True)
# plt.show()
#
# print(Hposta.num, Hposta.den)
# print(Hmia.num, Hmia.den)


tau = 10e-3
w_rg = 1000
tolerance = 0.20
filter = LowPassTemplate(wp=1, wa=10, alpha_p=5, alpha_a=80)
approx = InvChebyshev()
n = approx.get_min_n(filter)

ppos, zpos, k = approx.pzk(n, filter)

p = []
z = []
for pole in ppos:
    p.append(pole)
    if pole.imag > 0:
        p.append(numpy.conj(pole))
for zero in zpos:
    z.append(zero)
    if zero.imag > 0:
        z.append(numpy.conj(zero))

sys = signal.ZerosPolesGain(z, p, k)
Hmia = sys.to_tf()
[w, mag, pha] = signal.bode(Hmia)
plt.semilogx(w, -mag)
plt.grid(b=True)
plt.show()
print(Hmia.num/Hmia.den[0])
print(Hmia.den/Hmia.den[0])

gd = -numpy.diff(pha)/numpy.diff(w)*math.pi/180
w = numpy.delete(w, 0)

plt.semilogx(w, gd)
plt.grid(b=True)
plt.show()

gd = group_delay(w=w, p=p, z=z)
plt.semilogx(w, gd)
plt.grid(b=True)
plt.show()
# 135135,  135135,  62370,  17325,  3150,  378,  28,  1,

