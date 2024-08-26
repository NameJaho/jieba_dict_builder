import pandas as pd

import utils
from word_splitter.word_cutter import WordCutter

CONFIG_FILE = '../config/config.yaml'


class Scanner():
    def __init__(self):
        self.wc = WordCutter()
        config = utils.load_config(CONFIG_FILE)
        self.blacklist = config['BLACKLIST']

    def init_data(self):
        df = pd.read_csv('../input/random_user_10w.csv')
        return df

    @staticmethod
    def generate_combinations(s, direction='left', max_length=4):
        results = []
        if direction == 'left':
            # 从左至右生成组合
            for i in range(1, min(len(s), max_length) + 1):
                results.append(s[:i])
        elif direction == 'right':
            # 从右至左生成组合
            for i in range(len(s), len(s) - min(len(s), max_length), -1):
                results.append(s[i - 1:])
        return [i for i in results if len(i) > 1]

    # 提取长度不超过4的所有组合
    def extract_combinations(self, words, index):
        center = words[index]
        max_length = 4  # 剩余可用的字符长度
        combinations = []

        # 向左搜索
        if index > 0:
            left_str = ""
            for i in range(index - 1, -1, -1):
                if len(words[i]) + len(left_str) <= max_length:
                    left_str = words[i] + left_str
                else:
                    break

            combinations.extend(self.generate_combinations(left_str + center, 'right'))

        # 向右搜索
        if index < len(words) - 1:
            right_str = ""

            for j in range(index + 1, len(words)):
                if len(words[j]) + len(right_str) <= max_length:
                    right_str += words[j]
                else:
                    break
            combinations.extend(self.generate_combinations(center + right_str, 'left'))
        return combinations

    def scan_data(self, words):
        result = {}
        for index, word in enumerate(words):

            if len(word) == 1:
                result[word] = []
                r = self.extract_combinations(words, index)
                result[word] = r
        return result

    def main(self):
        df = self.init_data()
        df.dropna(subset=['final_content'], inplace=True)
        sample = df.sample(100)
        sample['words'] = sample['final_content'].apply(
            lambda x: self.wc.cut(''.join(utils.split_into_phrases(x, self.blacklist))))
        sample['keywords'] = sample['words'].apply(lambda x: self.scan_data(x))
        sample.to_csv('../output/keywords.csv', index=False)


if __name__ == '__main__':
    s = Scanner()
    s.main()
