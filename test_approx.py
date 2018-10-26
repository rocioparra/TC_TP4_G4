from model import Model
from matplotlib import pyplot as plt
from appoximations import approximation_factory
# from filter_template import LowPassTemplate, BandPassTemplate
from filter_template import GroupDelayTemplate, TemplateParameters
from filtertypes import GroupDelay
from scipy import signal
import numpy
import math
from group_delay import group_delay


# m = Model()
# s, id = m.add_filter("Band-pass", "Inverse Chebyshev", [500, 100, 200, 1, 20], 1, 25, 100, 50)
# #m.f.auto_stage_decomposition(.1, 15)
# print(s)
# m.get_plot(id, "Step response", False)


tau = 10e-3
w_rg = 600
tolerance = 0.20
params = TemplateParameters(wrg=w_rg, tau=tau, tol=tolerance)
template = GroupDelayTemplate(param=params, q_max=100, n_min=1, n_max=25)
f = GroupDelay(template=template, approx="Bessel")
f.calculate_pzkn()
tf = f.calculate_tf(f.denormalized_poles, f.denormalized_zeros, f.denormalized_k)

[w, mag, pha] = signal.bode(tf)
plt.semilogx(w, -mag)
plt.grid(b=True)
plt.show()
print(tf.num/tf.den[0])
print(tf.den/tf.den[0])

gd = -numpy.diff(pha)/numpy.diff(w)*math.pi/180
w = numpy.delete(w, 0)

plt.semilogx(w, gd)
plt.grid(b=True)
plt.show()

gd = group_delay(w=w, p=p, z=z)
plt.semilogx(w, gd)
plt.grid(b=True)
plt.show()

#
# f.normalize()
# approx = approximation_factory("Bessel")
# n = approx.get_min_n(f.normalized_template)
# ppos, z, k = approx.pzk(n, f.normalized_template)
#
# p = []
# for pole in ppos:
#     p.append(pole)
#     if pole.imag > 0:
#         p.append(numpy.conj(pole))
#
#
#
# z = f.normalized_zeros
# k = f.k
#
# t0 = 1
# k /= tau ** n
#
# sys = signal.ZerosPolesGain([], p, k)
# Hmia = sys.to_tf()
# [w, mag, pha] = signal.bode(Hmia)
# plt.semilogx(w, -mag)
# plt.grid(b=True)
# plt.show()
# print(Hmia.num/Hmia.den[0])
# print(Hmia.den/Hmia.den[0])
#
# gd = -numpy.diff(pha)/numpy.diff(w)*math.pi/180
# w = numpy.delete(w, 0)
#
# plt.semilogx(w, gd)
# plt.grid(b=True)
# plt.show()

# gd = group_delay(w=w, p=p, z=z)
# plt.semilogx(w, gd)
# plt.grid(b=True)
# plt.show()

#
# p_denorm = []
# k_denorm = k
#
# for pole in ppos:
#     p_denorm.append(pole/tau)
#     k_denorm /= tau
#     if pole.imag > 0:
#         p_denorm.append(numpy.conj(pole)/tau)
#         k_denorm /= tau
#
# #f.re_add_complex(p_denorm)
#
# sys = signal.ZerosPolesGain([], p_denorm, k_denorm)
# Hmia = sys.to_tf()
# [w, mag, pha] = signal.bode(Hmia)
# plt.semilogx(w, -mag)
# plt.grid(b=True)
# plt.show()
# print(Hmia.num/Hmia.den[0])
# print(Hmia.den/Hmia.den[0])
#
# gd = -numpy.diff(pha)/numpy.diff(w)*math.pi/180
# w = numpy.delete(w, 0)
#
# plt.semilogx(w, gd)
# plt.grid(b=True)
# plt.show()
#
# gd, _ = group_delay(w=w, p=p_denorm, z=z)
# plt.semilogx(w, gd)
# plt.grid(b=True)
# plt.show()
#
# poles = []
# zeros = []
# k
#
# for pole in ppos:
#     denorm_p, denorm_z, k_factor = f.denormalize_one_pole(pole)
#     poles.append(denorm_p)
#     zeros.append(denorm_z)
#     k *= k_factor
#
#
# sys = signal.ZerosPolesGain([], p_denorm, k_denorm)
# Hmia = sys.to_tf()
# [w, mag, pha] = signal.bode(Hmia)
# plt.semilogx(w, -mag)
# plt.grid(b=True)
# plt.show()
# print(Hmia.num/Hmia.den[0])
# print(Hmia.den/Hmia.den[0])
#
#
# gd = -numpy.diff(pha)/numpy.diff(w)*math.pi/180
# w = numpy.delete(w, 0)
#
# plt.semilogx(w, gd)
# plt.grid(b=True)
# plt.show()
#
# gd, _ = group_delay(w=w, p=p_denorm, z=z)
# plt.semilogx(w, gd)
# plt.grid(b=True)
# plt.show()