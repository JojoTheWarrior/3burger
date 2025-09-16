def bezout(a, b):
    if a == 0:
        return (0, 1)
    x1, y1 = bezout(b%a, a)
    return (y1 - ((b // a) * x1), x1)

def fastPow(base, exp, mdl):
    ret = 1
    while exp:
        if exp & 1:
            ret = (ret * base) % mdl
        base = (base * base) % mdl
        exp >>= 1
    return ret

def decrypt(encrypted_str):
    p = 1000000009
    q = 7290343271
    tot_n = 7290343328322746160
    n = p * q
    d = 4993249937736084049

    return fastPow(int(encrypted_str), d, n)