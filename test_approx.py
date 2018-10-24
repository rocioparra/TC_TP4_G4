from appoximations import Butterworth, Chebyshev, InvChebyshev, Bessel
from scipy import signal
import matplotlib.pyplot as plt
import math
import numpy
from filter_template import GroupDelayTemplate, LowPassTemplate
from filtertypes import filter_factory
from numpy.polynomial import Polynomial
import numpy.polynomial.polynomial as poly
from group_delay import group_delay
from filter import Filter
from model import Model


m = Model()

print(m.get_available_filters())
print(m.get_approximations_for("High-pass"))
print(m.get_parameters_for("High-pass"))

m.add_filter("High-pass", "Chebyshev", [100, 10, 10, 50], 1, 25, 100, 0)
f.calculate_pzkn()
h = f.calculate_tf(f.denormalized_poles, f.denormalized_zeros, f.denormalized_k)

[w, mag, pha] = signal.bode(h)
plt.semilogx(w, -mag)
plt.grid(b=True)
plt.show()
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
#
#
# tau = 10e-3
# w_rg = 1000
# tolerance = 0.20
# filter = LowPassTemplate(wp=1, wa=100, alpha_p=5, alpha_a=10)
# approx = InvChebyshev()
# n = approx.get_min_n(filter)
#
# ppos, zpos, k = approx.pzk(n, filter)
#
# p = []
# z = []
# for pole in ppos:
#     p.append(pole)
#     if pole.imag > 0:
#         p.append(numpy.conj(pole))
# for zero in zpos:
#     z.append(zero)
#     if zero.imag > 0:
#         z.append(numpy.conj(zero))
#
# sys = signal.ZerosPolesGain(z, p, k)
# Hmia = sys.to_tf()
#
# wp = filter.wp
# wa = filter.wa
# alpha_a = filter.alpha_a
# alpha_p = filter.alpha_p
#
#
# w = numpy.logspace(start=0, stop=numpy.log10(wa), endpoint=True, base=10)
# [w, mag, _] = signal.bode(system=Hmia, w=w)
# wl = wp
# wh = wa
#
# at = -mag
#
# for i in range(len(w)):
#     if at[i] > alpha_p:
#         if i >= 1:
#             wl = w[i-1]
#         break
#
# for i in range(len(w)-1, -1, -1):
#     if at[i] < alpha_a:
#         if i < len(w)-1:
#             wh = w[i+1]
#         break
#
# k_h = wh/wa  # k_h <= 1
# k_l = wl/wp  # k_l >= 1
#
# norm = 50    # 0%    ->  k = k_l
#             # 100%  ->  k = k_h <= k_l
#             # x%    ->  k = k_h + (k_l-k_h) *x/100
#
# k_norm = k_h + (k_l-k_h) * norm / 100
#
# p = [pole/k_norm for pole in p]
# z = [zero/k_norm for zero in z]
# k = k * (k_norm**(len(z)-len(p)))
#
#
# sys = signal.ZerosPolesGain(z, p, k)
# Hmia = sys.to_tf()
# [w, mag, pha] = signal.bode(Hmia)
# plt.semilogx(w, -mag)
# plt.grid(b=True)
# plt.show()
#
#

# 0%:   w -> w1
# 100%: w -> w1 + delta
# x%:   w -> w1 + delta*x/100

# print(Hmia.num/Hmia.den[0])
# print(Hmia.den/Hmia.den[0])
#
#
#
#
# gd = -numpy.diff(pha)/numpy.diff(w)*math.pi/180
# w = numpy.delete(w, 0)
#
# plt.semilogx(w, gd)
# plt.grid(b=True)
# plt.show()
#
# gd = group_delay(w=w, p=p, z=z)
# plt.semilogx(w, gd)
# plt.grid(b=True)
# plt.show()
# # 135135,  135135,  62370,  17325,  3150,  378,  28,  1,
#
