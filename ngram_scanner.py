import pandas as pd
import warnings
import utils
from word_splitter.word_cutter import WordCutter

warnings.filterwarnings("ignore")

CONFIG_FILE = 'config/config.yaml'
INPUT_FILE = 'input/random_user_10w.csv'


class NgramScanner:
    def __init__(self):
        self.wc = WordCutter()
        config = utils.load_config(CONFIG_FILE)
        self.blacklist = config['BLACKLIST']
        self.word_length_max = config['WORD_LENGTH']['max_len']

    @staticmethod
    def preprocess():
        df = pd.read_csv(INPUT_FILE)
        df.dropna(subset=['final_content'], inplace=True)
        df = df[:100]
        return df

    def cut_words(self, df):
        df['words'] = df['final_content'].apply(
            lambda x: self.wc.cut(''.join(utils.split_into_phrases(x, self.blacklist))))
        return df

    # 返回最长单词
    def find_max_length_word(self, words, index, direction):
        next_char = ""

        if direction == 'left':
            start_index = index - 1
            end_index = -1
            step = -1
        else:
            start_index = index + 1
            end_index = len(words)
            step = 1

        for i in range(start_index, end_index, step):
            if len(words[i]) + len(next_char) <= self.word_length_max:
                if direction == 'left':
                    next_char = words[i] + next_char
                else:
                    next_char += words[i]
            else:
                break

        return next_char

    @staticmethod
    def generate_ngrams(word, direction='left', max_length=4):
        results = []
        if direction == 'left':
            # 从左至右生成组合
            for i in range(1, min(len(word), max_length) + 1):
                results.append(word[:i])
        elif direction == 'right':
            # 从右至左生成组合
            for i in range(len(word), len(word) - min(len(word), max_length), -1):
                results.append(word[i - 1:])
        return [i for i in results if len(i) > 1]

    # extract ngrams from both side
    def extract_ngrams(self, words, index):
        key_char = words[index]

        ngrams = []

        # 向左搜索
        if index > 0:
            next_char = self.find_max_length_word(words, index, 'left')
            ngrams.extend(self.generate_ngrams(next_char + key_char, 'right'))

        # 向右搜索
        if index < len(words) - 1:
            next_char = self.find_max_length_word(words, index, 'right')
            ngrams.extend(self.generate_ngrams(key_char + next_char, 'left'))

        return ngrams

    def scan(self, words):
        result = {}
        for index, word in enumerate(words):
            if len(word) == 1:
                ngrams = self.extract_ngrams(words, index)
                result[word] = ngrams
        return result


if __name__ == '__main__':
    scanner = NgramScanner()
    df = scanner.preprocess()
    df = scanner.cut_words(df)
    df['keywords'] = df['words'].apply(lambda x: scanner.scan(x))
    print(df.head(10))
