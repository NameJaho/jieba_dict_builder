import pandas as pd
import os
import utils
from utils import cost_time
from trie import Trie
from word_scanner import WordScanner
from collections import defaultdict, Counter
import math


INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'
CONFIG_FILE = 'config/config.yaml'
JIEBA_DICT = 'source_dict/dict.txt'


class CorpusProcessor:
    def __init__(self):
        config = utils.load_config(CONFIG_FILE)

        self.word_length_min = config['WORD_LENGTH']['min_len']
        self.word_length_max = config['WORD_LENGTH']['max_len']
        self.doc_freq_threshold = config['VALIDATION']['doc_freq_threshold']
        self.term_freq_threshold = config['VALIDATION']['term_freq_threshold']
        self.word_scanner = WordScanner()

    @staticmethod
    @cost_time
    def load_dict_to_set(dict_file_path, word_length_min, word_length_max):
        """
        读取jieba字典文件并将其转换为集合
        :param dict_file_path: 字典文件路径
        :param word_length_min: 最小词长
        :param word_length_max: 最大词长
        :return: 包含字典单词的集合
        """
        word_set = set()
        with open(dict_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) > 0:
                    word = parts[0]
                    if word_length_min <= len(word) <= word_length_max:
                        word_set.add(word)
        return word_set

    def filter_words(self, word_info_list):
        """
        根据文档频率和词频筛选需要检查的词
        :param word_info_list: 词信息列表
        :return: 筛选后的词信息列表
        """
        filtered_word_info_list = [word_info for word_info in word_info_list if
                                   word_info['doc_freq'] >= self.doc_freq_threshold and
                                   word_info['term_freq'] >= self.term_freq_threshold and
                                   self.word_length_min <= len(word_info['word']) <= self.word_length_max]
        return filtered_word_info_list

    @cost_time
    def convert_file_to_trie(self, filename):
        file_trie = Trie()
        file_path = os.path.join(INPUT_FOLDER, filename)

        print('Processing: ', file_path)
        df = pd.read_csv(file_path)

        content_list = df['content'].tolist()
        jieba_word_set = self.load_dict_to_set(JIEBA_DICT, self.word_length_min, self.word_length_max)
        word_info_list = self.word_scanner.generate_word_info_list(content_list, jieba_word_set)

        for word_info in word_info_list:
            word = word_info['word']
            term_freq = word_info['term_freq']
            doc_freq = word_info['doc_freq']
            status = word_info['status']
            file_trie.insert(word, term_freq, doc_freq, status)

        filtered_word_info_list = self.filter_words(word_info_list)
        self.validate_words(filtered_word_info_list, file_trie)

        return file_trie

    @cost_time
    def validate_words(self, word_info_list, trie):
        """
        判断status=0的词是否合理，如果合理则将status设为1，否则设为-1
        :param word_info_list: 词信息列表
        :param trie: 前缀树
        """
        for word_info in word_info_list:
            if word_info['status'] == 0:
                word = word_info['word']
                entropy = self.calculate_entropy(word, trie)
                #print(word, entropy, word_info['doc_freq'], word_info['term_freq'])
                if entropy > 1.5:  # 假设阈值为1.5
                    word_info['status'] = 1
                else:
                    word_info['status'] = -1

    def calculate_entropy(self, word, trie):
        left_neighbors = defaultdict(int)
        right_neighbors = defaultdict(int)

        # 获取所有包含目标词的词及其频率
        containing_words = trie.get_words_containing(word)

        for w, term_freq in containing_words:
            index = w.index(word)
            if index > 0:
                left_neighbor = w[index - 1]
                left_neighbors[left_neighbor] += term_freq
            if index + len(word) < len(w):
                right_neighbor = w[index + len(word)]
                right_neighbors[right_neighbor] += term_freq

        # 计算左熵
        left_entropy = self.calculate_single_entropy(left_neighbors)

        # 计算右熵
        right_entropy = self.calculate_single_entropy(right_neighbors)

        # 返回左右熵的平均值
        return (left_entropy + right_entropy) / 2

    @staticmethod
    def calculate_single_entropy(neighbors):
        if not neighbors:
            return 0
        total_freq = sum(neighbors.values())
        return -sum((freq / total_freq) * math.log(freq / total_freq) for freq in neighbors.values())


if __name__ == '__main__':
    corpus_processor = CorpusProcessor()
    _filename = 'sample1.csv'  # 替换为你的CSV文件名
    _trie = corpus_processor.convert_file_to_trie(_filename)
    #_trie.print_trie()
