from dotenv import load_dotenv
import os

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

# finding rsa variables
load_dotenv()

P = int(os.getenv("PRIME_P"))
Q = int(os.getenv("PRIME_Q"))
N = P*Q
TOTIENT = (P-1)*(Q-1)
E = 2
while sum(x * y for x, y in zip(bezout(TOTIENT, E), (TOTIENT, E))) != 1:
    E += 1
D = bezout(TOTIENT, E)[1]

def decrypt(encrypted_str):
    return fastPow(int(encrypted_str), D, N)

