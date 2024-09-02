import math
from collections import defaultdict
from config.config_loader import ConfigLoader
import pandas as pd


class EntropyCalculator(ConfigLoader):
    def __init__(self):
        super().__init__()

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
        for char, freq in left_chars.items():
            if char:  # 检查字符是否为空
                left_neighbors[char] += freq

        # 遍历右邻字
        for char, freq in right_chars.items():
            if char:  # 检查字符是否为空
                right_neighbors[char] += freq

        # 计算左熵
        left_entropy = self.calculate_single_entropy(left_neighbors)
        # 计算右熵
        right_entropy = self.calculate_single_entropy(right_neighbors)

        if left_entropy < 0.2 or right_entropy < 0.2:
            entropy = 0.5
        else:
            entropy = (left_entropy + right_entropy) / 2

        # 返回左右熵的平均值
        return entropy

    def is_in_blacklist(self, term):
        pass

    def filter_by_entropy(self, df):
        results = []
        # iterate df
        for index, row in df.iterrows():
            term = row['term']
            term_freq = row['term_freq']
            doc_freq = row['doc_freq']
            left_chars = eval(row['left_chars'])
            right_chars = eval(row['right_chars'])

            # if self.is_in_blacklist(term):
            #     continue
            entropy = self.calculate_entropy(left_chars, right_chars)
            if entropy < 1.5:
                continue

            result_dict = {
                'term': term,
                'term_freq': term_freq,
                'doc_freq': doc_freq,
                'entropy': entropy
            }
            results.append(result_dict)
        return results

    def save_to_csv(self, results):
        result_df = pd.DataFrame(results, columns=['term', 'term_freq', 'doc_freq', 'entropy'])
        result_df.to_csv(self.output_file_path.entropy_result, index=False)


if __name__ == '__main__':
    entropy_calculator = EntropyCalculator()
    df = pd.read_csv(entropy_calculator.output_file_path.merged_ngrams)
    _results = entropy_calculator.filter_by_entropy(df)
    entropy_calculator.save_to_csv(_results)
