import re
import utils
import math
from utils import cost_time
from collections import defaultdict, Counter

CONFIG_FILE = 'config/config.yaml'
JIEBA_DICT = 'source_dict/dict.txt'


class WordScanner:
    def __init__(self):
        config = utils.load_config(CONFIG_FILE)

        self.blacklist = config['BLACKLIST']
        self.word_length_min = config['WORD_LENGTH']['min_len']
        self.word_length_max = config['WORD_LENGTH']['max_len']

    @staticmethod
    @cost_time
    def load_dict_to_set(dict_file_path):
        """
        读取jieba字典文件并将其转换为集合
        :param dict_file_path: 字典文件路径
        :return: 包含字典单词的集合
        """
        word_set = set()
        with open(dict_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) > 0:
                    word = parts[0]
                    word_set.add(word)
        return word_set

    def scan_words_to_dict(self, content_list):
        """
        扫描所有内容并生成包含单词和词频的字典
        :param content_list: 内容列表
        :return: 包含单词和词频的字典
        """
        word_freq_dict = defaultdict(int)
        doc_freq_dict = defaultdict(int)
        processed_contents = set()

        for content in content_list:
            content_words = set()
            phrases = utils.split_into_phrases(content)
            for phrase in phrases:
                for i in range(len(phrase)):
                    for length in range(self.word_length_min, self.word_length_max + 1):
                        if i + length <= len(phrase):
                            word = phrase[i:i + length]
                            word_freq_dict[word] += 1
                            content_words.add(word)
            for word in content_words:
                doc_freq_dict[word] += 1

        return word_freq_dict, doc_freq_dict

    # @cost_time
    # def generate_word_info_list(self, content_list):
    #     word_freq_dict, doc_freq_dict = self.scan_words_to_dict(content_list)
    #     word_info_list = [{'word': word, 'term_freq': freq, 'doc_freq': doc_freq_dict[word], 'status': 0}
    #                       for word, freq in word_freq_dict.items()]
    #     return word_info_list
    @cost_time
    def generate_word_info_list(self, content_list, jieba_word_set):
        word_freq_dict, doc_freq_dict = self.scan_words_to_dict(content_list)
        # jieba_word_set = self.load_dict_to_set(JIEBA_DICT, self.word_length_min, self.word_length_max)
        word_info_list = [{'word': word, 'term_freq': freq, 'doc_freq': doc_freq_dict[word],
                           'status': 2 if word in jieba_word_set else 0}
                          for word, freq in word_freq_dict.items()]

        return word_info_list


if __name__ == '__main__':
    word_scanner = WordScanner()
    _content_list = [
        '今天天气不错，今天心情也很好',
        '昨天天气不如今天好'
    ]
    _word_info_list = word_scanner.generate_word_info_list(_content_list)
    print(_word_info_list)