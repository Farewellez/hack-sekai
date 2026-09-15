
import os
import binascii
import progressbar
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

''' 

Utility functions

'''

# using PKCS#7 padding scheme
def add_padding(p):
    padding_len = 16-(len(p)%16)

    if padding_len == 0:
        return p + 16*b'\x00'
    else:
        return p + chr(padding_len)*padding_len

def validate_padding(p):
    # if the last block is incomplete
    if len(p)%16 != 0:
        return 0

    val = p[-1]
    if val > 16:
        return 0

    # check whether the number of paddings is correct
    for x in p[-val:]:
        if x != val:
            return 0

    return 1

# xoring two byte literals
def xor(a, b) :
    return bytes(x ^ y for x, y in zip(a, b))

def log(msg,byte_str):
    print(msg+":"+binascii.hexlify(byte_str).decode("ascii"))

def log_hex(msg,hex_str):
    print(msg+":"+":".join("{:02x}".format(ord(c)) for c in hex_str))


''' 

PoC

'''
def aes_encrypt(p,v):
    backend = default_backend()
    key = b'\x6B'*16
    log("Key", key)
    log("IV", v)
    log("Plaintext in hex",p.encode('ascii'))

    cipher = Cipher(algorithms.AES(key), modes.CBC(v), backend=backend)
    p_padding = add_padding(p)
    log("After Padding:",p_padding.encode('ascii'))
    encryptor = cipher.encryptor()
    c = encryptor.update(p_padding.encode('ascii')) + encryptor.finalize()
    print("Ciphertext:"+binascii.hexlify(c).decode("ascii"))
    return c


def aes_padding_oracle(c, v):
    key = b'\x6B'*16
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(v), backend=backend)
    decryptor = cipher.decryptor()
    p = decryptor.update(c) + decryptor.finalize()
    # print(p)
    # print("[+]decrypted:"+binascii.hexlify(p).decode("ascii"))
    return validate_padding(p)

def attack(c,v):
    c_hex = binascii.hexlify(c)
    # print(f"chex: {c_hex}")
    # split ciphertext by block
    c_blk = [c_hex[i:i+32] for i in range(0,len(c_hex),32)]

    combined_result = b""
    bar = progressbar.ProgressBar(maxval=len(c_blk))
    
    bar.start()
    # decrypt block by block
    for i_blk in range(len(c_blk)):
        if i_blk+2<= len(c_blk):
            c1 = binascii.unhexlify(c_blk[-2-i_blk])
            c2 = binascii.unhexlify(c_blk[-1-i_blk])
        else:
            # if decrypting the first block in ciphertext, use IV as the previous block
            c1 = v
            c2 = binascii.unhexlify(c_blk[0])
        blk_result = b""
        # decrypt character by character 
        for i in range(16):
            count = 0
            found_str = b''
            # try all possible chars (0-255)
            for j in range(0,256):
                # construct blocks to be xorred with c1
                blk1 = b'\x00'*(15-i)+(i+1).to_bytes(1,'big')*(i+1)
                blk2 = b'\x00'*(15-i)+j.to_bytes(1,'big')+blk_result 
                
                # ciphertext to be queried 
                concat = xor(xor(c1,blk1),blk2) + c2
                
                # query the padding oracle
                if aes_padding_oracle(concat,v)==1:
                    # take down how many 'good' paddings have been found for this position
                    count = count+1
                    if i!=j:
                        # save possible candidates
                        # notice: there is no need to save the candidate character when i==j
                        #     since we can always find that in the outer loop
                        found_str = j.to_bytes(1,'big')
            # Case 1: count > 1, meaning there are two possible plaintext chars
            #         always choose the one found when i!=j
            # Case 2: count==1 and found_str!=b'', meaning the only plaintext char we found is
            #         when i!=j
            if(count>1 or (count==1 and found_str!=b'')):
                blk_result = found_str+blk_result
            elif(count==0):
                # hopefully this will never happen
                print("Decryption failed")
                break
            # Case 3: count==1, the plaintext char must be from i==j
            else:
                blk_result = (i+1).to_bytes(1,'big')+blk_result
        #print("Block "+str(len(c_blk)-i_blk)+" decrypted: "+blk_result.decode('ascii'))
        combined_result=blk_result + combined_result
        bar.update(i_blk)
    bar.finish()
    return combined_result


'''

Main

'''
p = input("Enter plaintext:")
v = b"\x11\x22\x33\x44\x55\x66\x77\x88\x99\xAA\xBB\xCC\xDD\xEE\xFF\x00"
c = aes_encrypt(p,v)
print("Decrypted plaintext:"+attack(c,v).decode('ascii'))
