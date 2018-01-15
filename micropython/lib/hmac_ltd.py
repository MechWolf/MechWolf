"""

Title: A "keyed-hash message authentication code" implementation in pure python.

edited from: https://github.com/brschdr/python-hmac
                only supports sha256; doesn't support hexdigest since uhashlib doesn't

License: This code is in Public Domain or MIT License, choose suitable one for you.

Description: This HMAC implementation is in accordance with RFC 2104 specification.
             User supplied "key" and "message" must be a Python Byte Object.
"""

try:
    import uhashlib as _hashlib
except ImportError:
    import hashlib as _hashlib

class HMAC:

        def __init__(self,key,message,hash_h):
                
                """ key and message must be byte object """
                
                self.i_key_pad = bytearray()
                self.o_key_pad = bytearray()
                self.key = key 
                self.message = message 
                self.blocksize = 64
                self.hash_h = hash_h
                self.init_flag = False


        def init_pads(self):
                """ creating inner padding and outer padding """
                
                for i in range(self.blocksize):
                        self.i_key_pad.append(0x36 ^ self.key[i])
                        self.o_key_pad.append(0x5c ^ self.key[i])


        def init_key(self):   
                """ key regeneration """
                
                if len(self.key) > self.blocksize:
                        self.key = bytearray(_hashlib.md5(key).digest())
                elif len(self.key) < self.blocksize:
                        i = len(self.key)
                        while i < self.blocksize:
                                self.key += b"\x00"
                                i += 1


        def digest(self):
                """ returns a digest, byte object. """

                if self.init_flag == False:
                        self.init_key()
                        self.init_pads()
                        self.init_flag = True
                
                return self.hash_h(bytes(self.o_key_pad)+self.hash_h(bytes(self.i_key_pad)+self.message).digest()).digest()

def new(key, msg = None, digestmod = None):
    return HMAC(key, msg, digestmod)
