import multiprocessing
multiprocessing.set_start_method('fork', force=True)
import math
from sage.all import *
from decimal import Decimal
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

with open("./key_17a08b7040db46308f8b9a19894f9f95.pem", "r") as f:
    data = RSA.import_key(f.read())

N = Integer(data.n)
e = data.e
ct = "249d72cd1d287b1a15a3881f2bff5788bc4bf62c789f2df44d88aae805b54c9a94b8944c0ba798f70062b66160fee312b98879f1dd5d17b33095feb3c5830d28"
print(f"N : {N}")
print(f"e : {e}")
print(f"ct: {ct}")

primes = []


def sieve(maximum=10000):
    # In general Sieve of Sundaram, produces primes smaller
    # than (2*x + 2) for a number given number x. Since
    # we want primes smaller than maximum, we reduce maximum to half
    # This array is used to separate numbers of the form
    # i+j+2ij from others where 1 <= i <= j
    marked = [False]*(int(maximum/2)+1)

    # Main logic of Sundaram. Mark all numbers which
    # do not generate prime number by doing 2*i+1
    for i in range(1, int((math.sqrt(maximum)-1)/2)+1):
        for j in range(((i*(i+1)) << 1), (int(maximum/2)+1), (2*i+1)):
            marked[j] = True

    # Since 2 is a prime number
    primes.append(2)

    # Print other primes. Remaining primes are of the
    # form 2*i + 1 such that marked[i] is false.
    for i in range(1, int(maximum/2)):
        if (marked[i] == False):
            primes.append(2*i + 1)

sieve()

print(f"Primes-size: {len(primes)}")

def get_primorial(n):
    result = 1
    for i in range(n):
        result = result * primes[i]
    return result

M = get_primorial(40)
print(f"M: {M}")

# n = p * q
# n = (k1 * M + pow(e, a1, M)) * (k2 * M + pow(e, a2, M))
# k1 * M = x V k2 * M = y
# n = (x + pow(e, a1, M)) * (y + pow(e, a2, M))
# n = x.y + x.pow(e, a2, M) + y.pow(e, a1, M) + pow(e, a1, M).pow(e, a2, M)

# https://github.com/mimoo/RSA-and-LLL-attacks/blob/master/coppersmith.sage
param = \
{
    512: {
        "n": 39,
        "a_max": 62,
        "k_max": 37,
        "M": 0x924cba6ae99dfa084537facc54948df0c23da044d8cabe0edd75bc6,
        "M_prime": 0x1b3e6c9433a7735fa5fc479ffe4027e13bea,
        "m": 5,
        "t": 6,
        "c_a": 0x80000
    },
    1024: {
        "n": 71,
        "a_max": 134,
        "k_max": 37,
        "M": 0x7923ba25d1263232812ac930e9683ac0b02180c32bae1d77aa950c4a18a4e660db8cc90384a394940593408f192de1a05e1b61673ac499416088382,
        "M_prime": 0x24683144f41188c2b1d6a217f81f12888e4e6513c43f3f60e72af8bd9728807483425d1e,
        "m": 4,
        "t": 5,
        "c_a": 0x40000000
    },
    2048: {
        "n": 126,
        "a_max": 434,
        "k_max": 53,
        "M": 0x7cda79f57f60a9b65478052f383ad7dadb714b4f4ac069997c7ff23d34d075fca08fdf20f95fbc5f0a981d65c3a3ee7ff74d769da52e948d6b0270dd736ef61fa99a54f80fb22091b055885dc22b9f17562778dfb2aeac87f51de339f71731d207c0af3244d35129feba028a48402247f4ba1d2b6d0755baff6,
        "M_prime": 0x16928dc3e47b44daf289a60e80e1fc6bd7648d7ef60d1890f3e0a9455efe0abdb7a748131413cebd2e36a76a355c1b664be462e115ac330f9c13344f8f3d1034a02c23396e6,
        "m": 7,
        "t": 8,
        "c_a": 0x400000000
    }
}


def coppersmith_howgrave_univariate(pol, N, beta, mm, tt, XX,algo='LLL'):
    """
    Coppersmith revisited by Howgrave-Graham
    
    finds a solution if:
    * b|N, b >= N^beta , 0 < beta <= 1
    * |x| < XX
    """
    #
    # init
    #
    dd = pol.degree()
    nn = dd * mm + tt
    
    #
    # checks
    #
    if not 0 < beta <= 1 :
        raise ValueError("beta should belongs in (0, 1]")

    if not pol.is_monic():
        raise ArithmeticError("Polynomial must be monic.")

    
    #
    # Coppersmith revisited algo for univariate
    #

    # change ring of pol and x
    polZ = pol.change_ring(ZZ)
    x = polZ.parent().gen()

    # compute polynomials
    gg = []
    for ii in range(mm):
        for jj in range(dd):
            gg.append((x * XX)**jj * N**(mm - ii) * polZ(x * XX)**ii)
    for ii in range(tt):
        gg.append((x * XX)**ii * polZ(x * XX)**mm)
    
    # construct lattice B
    BB = Matrix(ZZ, nn)
    
    for ii in range(nn):
        for jj in range(ii+1):
            BB[ii, jj] = gg[ii][jj]

    if algo == 'LLL':
    # LLL
        BB = BB.LLL(early_red=True, use_siegel=True)
    else:
        BB = BB.BKZ(early_red=True, use_siegel=True)

    # transform shortest vector in polynomial    
    new_pol = 0
    for ii in range(nn):
        new_pol += x**ii * BB[0, ii] / XX**ii

    # factor polynomial
    potential_roots = new_pol.roots()

    return [i[0] for i in potential_roots]

class Worker(multiprocessing.Process):
    def run(self):
        try:
            # Fetch parameters according to key size
            N, keylength, start, stop, factors_queue, manager,algo = self._args
            M_prime = param[keylength]['M_prime']
            beta = 0.5 
            mm = param[keylength]['m']
            tt = param[keylength]['t']

            # Uses decimal for arbitrary floating point precision
            # XX = int((2*pow(N, Decimal(beta))) / M_prime) 
            XX = (2 * isqrt(int(N)) + 1) // M_prime

            # Bruteforce until p, q are found
            a_prime = start
            while a_prime < stop:
                if manager.finished:
                    break 
                
                # Construct polynomial
                m_inv = int(inverse_mod(M_prime, N))
                k_tmp = int(pow(65537, a_prime, M_prime))
                known_part_pol = int(k_tmp * m_inv)
                F = PolynomialRing(Zmod(N), implementation='NTL', names=('x',))
                (x,) = F._first_ngens(1)
                pol = x + known_part_pol

                # Get roots of polynomial using coppersmith
                roots = coppersmith_howgrave_univariate(pol, N, beta, mm, tt, XX, algo=algo)

                # Check if roots are p, q
                for root in roots:
                    factor1 = k_tmp + abs(root) * M_prime
                    if mod(N, factor1) == 0:
                        factor2 = N // factor1
                        factors_queue.put((factor1, factor2))
                        print ("[+] p, q", factor1, factor2)
                        manager.finished = True
                        return
                a_prime += 1

        except KeyboardInterrupt as e:
            print ("[-] Ctrl+C issued ...")
            print ("[-] Terminating ...")
            sys.exit(0)

def roca(N, cpus=1,algo='LLL'):
    
    # Key is not always of perfect size, infer from size
    keylength = int(log(N, 2))
    if keylength < 1000 :
        keylength = 512
    elif  keylength < 2000 :
        keylength = 1024 
    elif keylength < 4000 :
        keylength = 2048 
    else:
        keylength = 4096 

    # Parrallelization options  
    processes = []
    manager = multiprocessing.Manager()
    manager.finished = False
    factors_queue = multiprocessing.Queue()
    
    # bruteforce
    M_prime = param[keylength]['M_prime']
    c_prime = discrete_log(N, Mod(65537, M_prime))
    ord_prime = Zmod(M_prime)(65537).multiplicative_order()
    
    top = (c_prime + ord_prime)/2
    
    # Spawn processes
    for i in range(1, cpus+1):
        if i == 1:
            start, stop = floor(c_prime/2), floor(top / cpus)
        else:
          start, stop = floor(top * (i-1) / cpus), floor(top * i / cpus)    
        w = Worker(args=(N, keylength, start, stop, factors_queue, manager,algo))
        w.start()
        processes.append(w)

    # When factors are found, fetch them from queue
    factors = factors_queue.get()
    
    for i in processes:
        i.join()
    
    # Return p, q in list
    return [int(f) for f in factors]

if __name__ == "__main__":
    p,q = roca(N)
    phi = (p - 1) * (q - 1)
    d = pow(e,-1,phi)
    key = RSA.construct((int(N), int(e), int(d)))
    cipher = PKCS1_OAEP.new(key)
    flag = cipher.decrypt(bytes.fromhex(ct))
    print(f"Flag: {flag.decode()}")