#coding:utf8

from math import log
import ctypes as C
from blzhash import HashString

class WordLenMap(C.Structure):

    _fields_ = [
        ('wordlen', C.c_int * 16)
    ]

    def __init__(self):
        self.wordlen = C.c_int * 16

    def add(self, ikeylen):
        if self.wordlen[ikeylen] == 0:
            self.wordlen[ikeylen] = ikeylen


class WordDic(object):
    """
    key: unicode encoding
    """

    def __init__(self, hash_size=3145728):
        self.HASH_SIZE = hash_size
        self.step = 8
        self.wordlenmap = C.cast(C.create_string_buffer(C.sizeof(WordLenMap)*65536), C.POINTER(WordLenMap))
        #self.word_list = C.cast(C.create_string_buffer(C.sizeof(Word)*self.HASH_SIZE), C.POINTER(Word))
        self.hash_list = HashString()
        self.hash_list.Init(self.HASH_SIZE)

    # def get_hash(self, key, len, i):
    #     n = 0
    #     for ii in xrange(len):
    #         n = (n<<5) + n + ord(key[ii])
    #     return ((n & (self.HASH_SIZE - 1)) + i * (n | 0xffffffff)) & (self.HASH_SIZE - 1)

    def load_dic(self, dic_path):
        with open(dic_path, 'rb') as dic_file:
            for line in dic_file:
                line_unicode = line.decode('utf8')
                line_split = line_unicode.split(u'\t')
                buffer = line_split[0]
                weight = int(line_split[1])
                ikeylen = len(buffer)

                if weight > 500:
                    value = (int)(8 * log((float)((weight - 500) * 0.4 + 500 + 100)))
                elif weight < 2:
                    value = (int)(log((float)(weight + 10)))
                else:
                    value = (int)(8 * log((float)(weight + 100)))

                pos = self.hash_list.Hash(buffer.encode('utf8'), value)
                self.wordlenmap[ord(buffer[0])].add(ikeylen)

    def segment(self, sentence):
        seg_sentence = []
        senlen = len(sentence)
        seg_pos = (C.c_int * senlen)()
        for i in xrange(senlen):
            seg_pos[i] = 1

        for i in range(senlen):
            for ikeylen in self.wordlenmap[ord(sentence[i])].wordlen[::-1]:
                if ikeylen == 0:
                    continue

                k = 0
                if i + ikeylen > senlen:
                    continue

                buffer = sentence[i:i+ikeylen]

                if self.hash_list.IsHashed(buffer.encode('utf8')) != -1:
                    seg_pos[i] = ikeylen
                    i += ikeylen
                    break

        pre_pos = 0; next_pos = 0
        chinese = True
        while pre_pos < senlen:
            if next_pos != senlen:
                if seg_pos[next_pos] == 1:
                    if ord(sentence[next_pos]) > 32 and ord(sentence[next_pos]) < 127:
                        chinese = False
                        next_pos += 1
                        continue

            if chinese:
                next_pos += seg_pos[next_pos]
            else:
                chinese = True

            seg_sentence.append(sentence[pre_pos:next_pos])
            pre_pos = next_pos

        return '/'.join(seg_sentence)

def test_dic():
    import time
    text = u"""【人民银行增加支农再贷款额度200亿元】近日人民银行对部分分支行增加支农再贷款额度200亿元，引导农村金融机构扩大涉农信贷投放，同时采取有效措施，进一步加强支农再贷款管理，促进降低“三农”融资成本。"""

    file_path = 'sogou.dic_utf8'
    s = time.time()
    wd = WordDic()
    print 'init cost time: ', time.time()-s, 's'

    s = time.time()
    wd.load_dic(file_path)
    print 'load dic cost time: ', time.time()-s, 's'

    s = time.time()
    segSent = wd.segment(text)
    print segSent
    print 'seg sentence cost time: ', time.time() - s, 's'

test_dic()