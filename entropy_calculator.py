import math
import re
import pickle
from collections import defaultdict
from config.config_loader import ConfigLoader
from utils import cost_time


class EntropyCalculator(ConfigLoader):
    def __init__(self):
        super().__init__()

    @staticmethod
    def calculate_single_entropy(neighbors):
        if not neighbors:
            return 0
        total_freq = sum(neighbors.values())
        return -sum((freq / total_freq) * math.log2(freq / total_freq) for freq in neighbors.values())

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
        # 计算右熵
        right_entropy = self.calculate_single_entropy(right_neighbors)

        # if left_entropy < 0.2 or right_entropy < 0.2:
        #     entropy = 0.5
        # else:
        entropy = (left_entropy + right_entropy) / 2

        # 返回左右熵的平均值
        return entropy, left_entropy, right_entropy

    def contains_bad_word(self, word):
        for bad_word in self.filter.bad_words:
            if bad_word in word:
                return True
            # 检查是否包含英文字母
        if re.search(r'[a-zA-Z]', word):
            return True
            # 检查是否包含数字
        if re.search(r'\d', word):
            return True
        return False

    def contains_ignore_word(self, term):
        for ignore_word in self.filter.ignore_words:
            ignore_rule = 'end' if ignore_word.endswith('|') else 'start'
            if ignore_word in term:
                if ignore_rule == 'end':
                    if term.endswith(ignore_word):
                        return True

                elif ignore_rule == 'start':
                    if term.startswith(ignore_word):
                        return True

        return False

    @cost_time
    def filter_by_entropy(self, data):
        results = []
        # iterate data
        for item in data:
            term = item['term']
            term_freq = item['term_freq']
            doc_freq = item['doc_freq']
            left_chars = item['left_chars']
            right_chars = item['right_chars']

            if self.contains_bad_word(term):
                continue

            if self.contains_ignore_word(term):
                continue

            entropy, left_entropy, right_entropy = self.calculate_entropy(left_chars, right_chars)
            entropy_threshold = self.filter.entropy_threshold
            if left_entropy < entropy_threshold or right_entropy < entropy_threshold:
                continue

            result_dict = {
                'term': term,
                'term_freq': term_freq,
                'doc_freq': doc_freq,
                'entropy': entropy,
                'left_entropy': left_entropy,
                'right_entropy': right_entropy
            }
            results.append(result_dict)
        return results

    def save_to_csv(self, results, chunk_index=None):
        import pandas as pd
        result_df = pd.DataFrame(results, columns=['term', 'term_freq', 'doc_freq', 'entropy', 'left_entropy', 'right_entropy'])
        entropy_result = self.output_file_path.entropy_result
        if chunk_index:
            entropy_result = entropy_result.replace('.csv', f'_{chunk_index}.csv')
        result_df.to_csv(entropy_result, index=False)


if __name__ == '__main__':
    entropy_calculator = EntropyCalculator()
    with open('output/neighbours_dict.pkl', 'rb') as f:
        data = pickle.load(f)
    print(len(data))
    _results = entropy_calculator.filter_by_entropy(data)
    print(len(_results))
    entropy_calculator.save_to_csv(_results)
