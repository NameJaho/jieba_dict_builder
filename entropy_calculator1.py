import math
from collections import defaultdict
import csv

import pandas as pd

import utils
import csv


CONFIG_FILE = 'config/config.yaml'


class EntropyCalculator:
    def __init__(self):
        config = utils.load_config(CONFIG_FILE)
        self.blacklist = config['BLACKLIST']

    def is_in_blacklist(self, term):
        return any(char in self.blacklist for char in term)

    @staticmethod
    def calculate_single_entropy(neighbors):
        if not neighbors:
            return 0
        total_freq = sum(neighbors.values())
        return -sum((freq / total_freq) * math.log(freq / total_freq) for freq in neighbors.values())

    def calculate_entropy(self, left_chars, right_chars):
        left_neighbors = defaultdict(int)
        right_neighbors = defaultdict(int)

        # 遍历左邻字
        for char_info in left_chars:
            char = char_info['char']
            freq = char_info['freq']
            if char:  # 检查字符是否为空
                left_neighbors[char] += freq

        # 遍历右邻字
        for char_info in right_chars:
            char = char_info['char']
            freq = char_info['freq']
            if char:  # 检查字符是否为空
                right_neighbors[char] += freq

        # 计算左熵
        left_entropy = self.calculate_single_entropy(left_neighbors)
        # print(left_entropy)
        # 计算右熵
        right_entropy = self.calculate_single_entropy(right_neighbors)
        # print(right_entropy)

        entropy = (left_entropy + right_entropy) / 2
        if left_entropy < 0.2 or right_entropy < 0.2:
            entropy = 1
        # 返回左右熵的平均值
        return entropy

    def find_char_frequency(self, char):
        df = pd.read_csv(self.output_file_path.char_freq)
        # 找到对应的词频
        frequency = df.loc[df['word'] == char, 'count'].iloc[0] if char in df['word'].values else 0
        return frequency

    def find_word_frequency(self, word):
        df = pd.read_csv(WORD_FREQ_FILE)
        # 找到所有包含输入词的词频之和
        frequency = df[df['ngram'].str.contains(word, regex=False)]['count'].sum()
        return frequency

    def calculate_mutual_information(self, term):
        term_freq = self.find_word_frequency(term)

        # 获取词的每个字符
        chars = list(term)

        # 计算总频率
        total_freq = term_freq
        char_freqs = {}

        # 获取每个字符的全局词频
        for char in chars:
            char_freq = self.find_char_frequency(char)
            if char_freq is not None:
                char_freqs[char] = char_freq
                total_freq += char_freq

        if total_freq == 0 or term_freq == 0:
            return 0

        # 计算概率
        p_term = term_freq / total_freq
        p_chars = {char: freq / total_freq for char, freq in char_freqs.items()}

        # 计算互信息 判断凝固度
        mi = math.log(p_term / math.prod(p_chars.values()), 2)

        # print(f"Mutual information for term '{term}': {mi}")
        return mi


if __name__ == '__main__':
    entropy_calculator = EntropyCalculator()
    entropy_results = []

    with open('output/terms_data.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            term = row['term']
            term_freq = int(row['term_freq'])
            left_chars = eval(row['left_chars'])
            right_chars = eval(row['right_chars'])
            if term == '北京':
                print(term_freq)
                print(left_chars)
                print(right_chars)

            if entropy_calculator.is_in_blacklist(term):
                continue

            entropy = entropy_calculator.calculate_entropy(left_chars, right_chars)
            if entropy < 1.5 or len(term.strip()) <= 1:
                continue

            mi = entropy_calculator.calculate_mutual_information(term)

            if mi > -4.5:
                print(f'term: {term}, entropy: {entropy}, mi: {mi}')
                entropy_results.append({'term': term, 'entropy': entropy, 'mi': mi})

    # 将结果保存到新的CSV文件
    with open('output/final_words.csv', mode='w', encoding='utf-8', newline='') as file:
        fieldnames = ['term', 'entropy', 'mi']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in entropy_results:
            writer.writerow(result)
