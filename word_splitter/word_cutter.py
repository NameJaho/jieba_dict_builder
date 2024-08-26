import jieba

import utils


class WordCutter:
    def __init__(self):
        pass

    @staticmethod
    def cut(text):
        words = jieba.lcut(text)
        return words


if __name__ == '__main__':
    sentences = [
'老师，你的王牌回来了;       #'
    ]
    word_cutter = WordCutter()
    for sentence in sentences:
        s = utils.split_into_phrases(sentence, [])
        print(''.join(word_cutter.cut(''.join(s))))
