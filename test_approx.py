from appoximations import Butterworth
from scipy import signal
import math

wp = 1
wa = 20
alpha_p = 10*math.log10(2)
alpha_a = 100

butter = Butterworth()
n = butter.get_min_n(butter, wp=wp, wa=wa, alpha_a=alpha_a, alpha_p=alpha_p)
[p, z, k] = butter.pzk(butter, alpha_p=alpha_p, n=n)
sys = signal.ZerosPolesGain(z, p, k)
Hmia = sys.to_tf()


[N, D] = signal.butter(N=n, Wn=wp, output='ba', analog=True)
Hposta = signal.TransferFunction(N, D)


print(Hposta.num, Hposta.den)
print(Hmia.num, Hmia.den)
