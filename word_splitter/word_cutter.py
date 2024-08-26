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
'因为某种原因我们得到了几天的假期 终于决定去爬山啦遇到了超级美的七彩祥云希望我的某人可以驾着七彩祥云来接我'
    ]
    word_cutter = WordCutter()
    for sentence in sentences:
        s = utils.split_into_phrases(sentence, [])
        print(''.join(word_cutter.cut(''.join(s))))
