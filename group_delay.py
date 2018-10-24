import math


def group_delay(w, p, z):
    gd = []
    deltas = []

    for freq in w:
        delay = 0
        for zero in z:
            if zero.real == 0 and zero.imag == freq:
                delta = next((d for d in deltas if d[0] == freq), None)
                if delta is None:
                    delta = [freq, math.pi]  # cada delta es un salto de pi
                else:
                    deltas.remove(delta)
                    delta[1] += math.pi
                deltas.append(delta)
            else:
                delay += zero.real / (zero.real ** 2 + (freq - zero.imag) ** 2)

        for pole in p:
            delay -= pole.real / (pole.real**2 + (freq - pole.imag) ** 2)
        gd.append(delay)

    return gd, deltas
