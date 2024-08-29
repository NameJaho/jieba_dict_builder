import utils
import pandas as pd
import math

CONFIG_FILE = 'config/config.yaml'
CHAR_FREQ_FILE = 'output/char_freq.csv'
WORD_FREQ_FILE = 'output/word_freq.csv'
ENTROPY_CHAR_FREQ_FILE = 'output/char_freq_entropy.csv'


class MICalculator:
    def __init__(self):
        config = utils.load_config(CONFIG_FILE)
        self.blacklist = config['BLACKLIST']

    def find_char_frequency(self, char):
        df = pd.read_csv(CHAR_FREQ_FILE)
        # 找到对应的词频
        frequency = df.loc[df['single_char'] == char, 'count'].iloc[0] if char in df['single_char'].values else 0
        return frequency

    def find_word_frequency(self, word):
        df = pd.read_csv(WORD_FREQ_FILE)
        # 找到所有包含输入词的词频之和
        frequency = df[df['term'].str.contains(word, regex=False)]['term_freq'].sum()
        return frequency

    def calculate_mutual_information(self, term):
        term_freq = self.find_word_frequency(term)

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
            return 0

        # 计算概率
        p_term = term_freq / total_freq
        p_chars = {char: freq / total_freq for char, freq in char_freq_dict.items()}

        # 计算互信息 判断凝固度
        mi = math.log(p_term / math.prod(p_chars.values()), 2)

        # print(f"Mutual information for term '{term}': {mi}")
        return mi
