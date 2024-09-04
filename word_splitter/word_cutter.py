import re

import jieba
import utils
import jieba.posseg as pseg

# jieba.enable_parallel()
jieba.initialize()  # 预加载字典


class WordCutter:
    def __init__(self):
        pass

    @staticmethod
    def cut(text):
        words = jieba.lcut(text)
        return words

    @staticmethod
    def pos_seg(text):
        words = pseg.cut(text, HMM=False)
        return [[word, flags] for word, flags in words]


if __name__ == '__main__':
    sentences = [
        """开榴莲 15 8一斤 60块的小榴莲 最终开出来924克的肉"""
    ]
    word_cutter = WordCutter()
    for sentence in sentences:
        s = utils.split_into_phrases(sentence,
                                     ['的', '一', '了', '是', '我', '不', '在', '人', '们', '有', '来', '他', '这',
                                      '上', '着', '个', '到', '啦', '呢', '说',
                                      '就', '去', '得', '也', '和', '那', '要', '下', '看', '时', '过', '出', '啊',
                                      '么', '起', '你', '都', '把', '好', '还',
                                      '没', '为', '又', '可', '只', '以', '会', '样', '年', '想', '能', '中', '十',
                                      '从', '自', '前', '它', '后', '然', '走',
                                      '很', '像', '见', '两', '用', '她', '国', '进', '成', '回', '什', '边', '作',
                                      '对', '而', '己', '些', '现', '候', '向',
                                      '给', '才', '与', '吗', '哦', '最', '让', '吧', '太', '更', '最', '至', '啥',
                                      '但', '之', '于', '与', '其', '篇', '多', '哪', '次', '小', '大',
                                      '再', '等', '里', '挺', '被', '吃', '种', '做', '呀'])
        strip_ = re.sub(r'[^\u4e00-\u9fa5a-z0-9A-Z\s]', ' ', sentence)
        print(strip_)
        print(word_cutter.pos_seg(strip_))
