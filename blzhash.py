#-*- coding:utf8 -*-
import time, random
import ctypes as C

class HashTable(C.Structure):

    _fields_ = [
        ('hashA', C.c_int64),
        ('hashB', C.c_int64),
        ('exists', C.c_bool),
        ('opt', C.c_int64),
        ('info', C.c_char*64)
    ]

    def __init__(self, hashA, hashB, exists):
        self.hashA = hashA
        self.hashB = hashB
        self.exists = exists
        self.opt = 0


class HashString:


    def __init__(self):
        self.tableLength = 0
        self.cryptTable = (C.c_int * 0x500)()
        self.hashIndexTable = []

    def Init(self, tableLen=4194304): # 4M = 4 * 1024 * 1024 = 4194304
        now = time.time()
        self.InitCryptTable()
        self.tableLength = tableLen
        self.hashIndexTable = C.cast(C.create_string_buffer(C.sizeof(HashTable)*self.tableLength), C.POINTER(HashTable))
        # for i in xrange(self.tableLength):
        #     self.hashIndexTable[i].hashA = -1
        #     self.hashIndexTable[i].hashB = -1
        #     self.hashIndexTable[i].exists = False
        #     self.hashIndexTable[i].opt = 0
        print 'Init cost time; %fs' % (time.time()-now)

    def InitCryptTable(self):
        seed = 0x00100001L
        for index1 in range(0, 0x100):
            for i in range(0, 5):
                index2 = index1 + i * 0x100
                seed = (seed * 125 + 3) % 0x2aaaab
                temp1 = (seed * 0xffff) << 0x10
                seed = (seed * 125 + 3) % 0x2aaaab
                temp2 = (seed & 0xffff)
                self.cryptTable[index2] = (temp1 | temp2)

    def HashString(self, info, hashType):
        seed1 = 0x7fed7fed; seed2 = 0xeeeeeeee
        for c in info:
            #ch = c.upper()
            ch = c
            seed1 = self.cryptTable[(hashType << 8) + ord(ch)] ^ (seed1 + seed2)
            seed2 = ord(ch) + seed1 + seed2 + (seed2 << 5) + 3
        return seed1

    def IsHashed(self, info):
        hashOffset = 0; HashA = 1; HashB = 2
        hash = self.HashString(info, hashOffset)
        hashA = self.HashString(info, HashA)
        hashB = self.HashString(info, HashB)
        hashStart = hash % self.tableLength
        hashPos = hashStart

        while self.hashIndexTable[hashPos].exists:
            if self.hashIndexTable[hashPos].hashA==hashA and self.hashIndexTable[hashPos].hashB==hashB and \
                            self.hashIndexTable[hashPos].info==info:
                return hashPos
            else:
                hashPos = (hashPos + 1) % self.tableLength
            if hashPos == hashStart:
                break;

        return -1

    def Hash(self, info, opt=1):
        hashOffset = 0; HashA = 1; HashB = 2
        hash = self.HashString(info, hashOffset)
        hashA = self.HashString(info, HashA)
        hashB = self.HashString(info, HashB)
        hashStart = hash % self.tableLength
        hashPos = hashStart

        while self.hashIndexTable[hashPos].exists:
            hashPos = (hashPos + 1) % self.tableLength
            if hashPos == hashStart:
                return -1

        self.hashIndexTable[hashPos].exists = True
        self.hashIndexTable[hashPos].hashA = hashA
        self.hashIndexTable[hashPos].hashB = hashB
        self.hashIndexTable[hashPos].info = info
        self.hashIndexTable[hashPos].opt += opt

        return hashPos

    def UpdateHashOpt(self, hashPos, opt=0):
        if hashPos<0 or hashPos>self.tableLength:
            return False

        self.hashIndexTable[hashPos].opt += opt

        return True

    def LoadHashOpt(self, hashPos):
        if hashPos<0 or hashPos>self.tableLength:
            return False
        return self.hashIndexTable[hashPos].opt

def RandStr(seed, tmpLen):
    ran = ''
    seedLen = len(seed)
    for i in range(tmpLen):
        tmp = random.randint(0, seedLen-1) # inner is seedLen + 1
        ran += seed[tmp]
    return ran

# if __name__ == '__main__':
#     str = HashString()
#     str.Init()
#
#     print "==================insert========================"
#     for i in range(0, 2001):
#         tmpLen = random.randint(1, 20)
#         tmp = RandStr('0123456789abcdefghijklmopqrstuvwxyz', tmpLen)
#         print 'Current Hash String %s' % tmp
#         now = time.time()
#         pos = str.Hash(tmp)
#         print 'Hash cost time %fs, pos %d' % ((time.time() - now), pos)
#
#     print "===================query======================="
#     for i in range(0, 10000):
#         tmpLen = random.randint(1, 20)
#         tmp = RandStr('0123456789abcdefghijklmopqrstuvwxyz', tmpLen)
#         print 'Current Query String %s' % tmp
#         now = time.time()
#         pos = str.IsHashed(tmp)
#         print 'Query cost time %fs, pos %d' % ((time.time() - now), pos)


