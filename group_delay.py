def group_delay(w, p, z):
    gd = []

    for freq in w:
        delay = 0
        for zero in z:
            delay += zero.real / (zero.real ** 2 + (freq - zero.imag) ** 2)
        for pole in p:
            delay -= pole.real / (pole.real**2 + (freq - pole.imag) ** 2)
        gd.append(delay)

    return gd
