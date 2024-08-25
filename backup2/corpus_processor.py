import json
import pandas as pd
import os
import utils
from trie import Trie
import time
from collections import defaultdict


INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'
CONFIG_FILE = '../config/config.yaml'
JIEBA_DICT = 'source_dict/dict.txt'


class CorpusProcessor:
    def __init__(self):
        config = utils.load_config(CONFIG_FILE)

        self.blacklist = config['BLACKLIST']
        self.word_length_min = config['WORD_LENGTH']['min_len']
        self.word_length_max = config['WORD_LENGTH']['max_len']
        self.merged_trie = Trie()

    def extract_prefix_trie(self, phrases):
        prefix_trie = Trie()
        for phrase in phrases:
            for i in range(len(phrase)):
                for length in range(self.word_length_min, self.word_length_max):
                    if i + length <= len(phrase):
                        word = phrase[i:i + length]
                        prefix_trie.add(word)
        return prefix_trie

    def extract_post_trie(self, phrases):
        suffix_trie = Trie(is_suffix=True)
        for phrase in phrases:
            reversed_phrase = phrase[::-1]
            for i in range(len(reversed_phrase)):
                for length in range(self.word_length_min, self.word_length_max):
                    if i + length <= len(reversed_phrase):
                        reversed_word = reversed_phrase[i:i + length]
                        word = reversed_word[::-1]
                        suffix_trie.add(word)
        return suffix_trie

    @staticmethod
    def cost_time(func):
        def fun(*args, **kwargs):
            t = time.perf_counter()
            result = func(*args, **kwargs)
            print(f'func {func.__name__} cost time:{time.perf_counter() - t:.8f} s')
            return result

        return fun

    def extract_trie(self, content):
        phrases = utils.split_into_phrases(content)
        prefix_trie = self.extract_prefix_trie(phrases)
        suffix_trie = self.extract_post_trie(phrases)

        return prefix_trie, suffix_trie

    @staticmethod
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

    @staticmethod
    @cost_time
    def update_status_with_blacklist(trie, word_set):
        """
        遍历Trie中的所有单词，并根据jieba word_set更新status字段为1
        :param trie: 传入的prefix_trie
        :param word_set: 包含字典单词的集合
        """

        def _traverse(node):
            for word_info in node.words:
                if word_info['word'] in word_set:
                    word_info['status'] = 1
            for child in node.children.values():
                _traverse(child)

        _traverse(trie.root)

    @staticmethod
    def save_to_json(trie_json, filename, is_suffix=False):
        file_base_name = filename.split(".")[0]
        if is_suffix:
            output_filename = f'{file_base_name}_suffix_trie.json'
        else:
            output_filename = f'{file_base_name}_prefix_trie.json'

        output_file = os.path.join(OUTPUT_FOLDER, output_filename)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(trie_json, f, ensure_ascii=False, indent=4)

    @cost_time
    def convert_merged_trie(self):
        whitelist_words = self.load_dict_to_set(JIEBA_DICT)
        # 遍历目录中的所有文件
        for filename in os.listdir(INPUT_FOLDER):
            if filename.endswith('.csv'):
                prefix_trie = Trie(is_suffix=False)
                suffix_trie = Trie(is_suffix=True)

                file_path = os.path.join(INPUT_FOLDER, filename)
                print('Processing: ', file_path)

                try:
                    # 读取CSV文件
                    df = pd.read_csv(file_path)

                    # 检查是否存在 'content' 列
                    if 'content' in df.columns:
                        content_list = df['content'].tolist()
                        word_freq_dict = self.scan_words_to_dict(content_list)
                        grouped_dict = self.group_words_by_first_char(word_freq_dict)

                        content_prefix_trie = Trie(is_suffix=False)
                        # for content in content_list:
                        #content_prefix_trie, content_suffix_trie = self.extract_trie(content)
                        content_prefix_trie.parallel_batch_insert(grouped_dict, num_threads=4)
                        #suffix_trie.parallel_batch_insert(word_freq_dict, num_threads=4)
                        prefix_trie.merge(content_prefix_trie)
                        #suffix_trie.merge(content_suffix_trie)

                        print('Updating status')
                        cp.update_status_with_blacklist(prefix_trie, whitelist_words)

                        self.save_to_json(prefix_trie.trie_to_json(), filename)
                        self.save_to_json(suffix_trie.trie_to_json(), filename, is_suffix=True)
                    else:
                        print(f"Warning: {filename} missing 'content' column")
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                    print(f"Processing {filename} error: {str(e)}")

    @cost_time
    def scan_words_to_dict(self, content_list):
        """
        扫描所有内容并生成包含单词和词频的字典
        :param content_list: 内容列表
        :return: 包含单词和词频的字典
        """
        word_freq_dict = defaultdict(int)
        for content in content_list:
            phrases = utils.split_into_phrases(content)
            for phrase in phrases:
                for i in range(len(phrase)):
                    for length in range(self.word_length_min, self.word_length_max):
                        if i + length <= len(phrase):
                            word = phrase[i:i + length]
                            word_freq_dict[word] += 1
        return word_freq_dict

    @staticmethod
    @cost_time
    def group_words_by_first_char(word_freq_dict):
        """
        按首字分组单词
        :param word_freq_dict: 包含单词和词频的字典
        :return: 按首字分组的字典
        """
        grouped_dict = defaultdict(lambda: defaultdict(int))
        for word, term_freq in word_freq_dict.items():
            first_char = word[0]
            grouped_dict[first_char][word] = term_freq
        return grouped_dict


if __name__ == '__main__':
    cp = CorpusProcessor()

    cp.convert_merged_trie()
