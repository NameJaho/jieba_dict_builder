import pandas as pd
import math
from config.config_loader import ConfigLoader
from pandarallel import pandarallel
from utils import cost_time

pandarallel.initialize(progress_bar=True, verbose=2)


class MICalculator(ConfigLoader):
    def __init__(self):
        super().__init__()

    def find_char_frequency(self, char):
        df = pd.read_csv(self.output_file_path.char_freq)
        # 找到对应的词频
        frequency = df.loc[df['word'] == char, 'count'].iloc[0] if char in df['word'].values else 0
        return frequency

    def calculate_mutual_information(self, term, term_freq):
        # 获取词的每个字符
        chars = list(term)

        # 计算总频率
        total_freq = term_freq
        char_freq_dict = {}

        # 获取每个字符的全局词频
        for char in chars:
            char_freq = self.find_char_frequency(char)
            if char_freq is not None:
                char_freq_dict[char] = char_freq
                total_freq += char_freq

        if total_freq == 0 or term_freq == 0:
            return 0, 0

        # 计算概率
        p_term = term_freq / total_freq
        p_chars = {char: freq / total_freq for char, freq in char_freq_dict.items()}
        weight = math.prod([(1 - term_freq / freq) for freq in char_freq_dict.values()])
        if weight == 0:
            print(term, term_freq, char_freq_dict)
            # return 0, 0
        # 计算互信息 判断凝固度
        mi = math.log(p_term / math.prod(p_chars.values()), 2)
        weighted_mi = math.log(p_term / math.prod(p_chars.values()) / weight, 2)
        return mi, weighted_mi

    @cost_time
    def filter_by_mi(self, df):
        df[['mi', 'weighted_mi']] = df.parallel_apply(
            lambda row: self.calculate_mutual_information(row['term'], row['term_freq']),
            axis=1, result_type='expand')
        return df

    def save_to_csv(self, df):
        df.to_csv(self.output_file_path.mi_result, index=False)


if __name__ == '__main__':
    mi_calculator = MICalculator()
    _df = pd.read_csv(mi_calculator.output_file_path.entropy_result)
    _df.dropna(inplace=True)
    print(len(_df))
    _results = mi_calculator.filter_by_mi(_df)
    mi_calculator.save_to_csv(_results)
