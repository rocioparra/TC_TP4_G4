from appoximations import Butterworth, Chebyshev, InvChebyshev, Bessel
from scipy import signal
import matplotlib.pyplot as plt
import math
import numpy
from filter_template import GroupDelayTemplate

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

t = GroupDelayTemplate(w_rg=6, tolerance=.20)
approx = Bessel()

n = approx.get_min_n(t)
[ppos, zpos, k] = approx.pzk(n, t)
p = []
z = []
if n % 2 == 1:
    p.append(ppos.pop(len(ppos)-1))
for i in range(len(ppos)):
    p.append(ppos[i])
    p.append(numpy.conj(ppos[i]))
for i in range(len(zpos)):
    z.append(zpos[i])
    z.append(numpy.conj(zpos[i]))

sys = signal.ZerosPolesGain(z, p, k)
Hmia = sys.to_tf()
[w, mag, pha] = signal.bode(Hmia)
plt.semilogx(w, -mag)
plt.grid(b=True)
plt.show()


