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
    '是封校学生了;一起看电影；一起玩picopark，一起打僵尸'
    ]
    word_cutter = WordCutter()
    for sentence in sentences:
        s = utils.split_into_phrases(sentence, [])
        print(word_cutter.cut(''.join(s)))
