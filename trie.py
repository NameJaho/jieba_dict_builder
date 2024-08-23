import utils
import os
import json


class Trie:
    def __init__(self, blacklist, word_length_min=2, word_length_max=4):
        self.word_length_min = word_length_min
        self.word_length_max = word_length_max
        self.blacklist = blacklist
        self.total_words = 0    # number of scan words
        self.total_docs = 0     # number of documents
        self.total_chars = 0    # number of characters
        self.trie_dict = {}

    @staticmethod
    def is_word_in_sub_words(sub_words, target_word):
        for item in sub_words:
            if target_word == item['word']:
                return True
        return False

    @staticmethod
    def find_matching_word(sub_words, target_word):
        for item in sub_words:
            if item['word'] == target_word:
                return item
        return None

    def insert(self, word):
        if len(word) < self.word_length_min or len(word) > self.word_length_max:
            return

        first_char = word[0]
        if first_char not in self.trie_dict:
            self.trie_dict[first_char] = {}

        # 获取当前单词的首字对应的字典
        node = self.trie_dict[first_char]

        # 如果该字典没有 'sub_words' 列表则初始化
        if not node.get('sub_words'):
            node['sub_words'] = []
        sub_words = node['sub_words']

        # 如果当前单词没有在sub_words中出现则初始化字典
        if not self.is_word_in_sub_words(sub_words, word):
            sub_word = {'word': word, 'word_freq': 0, 'doc_freq': 0}
            sub_words.append(sub_word)

        sub_word = self.find_matching_word(sub_words, word)

        sub_word['word_freq'] += 1

        # 文频 doc_freq 每贴只计算一次
        if sub_word['doc_freq'] == 0:
            sub_word['doc_freq'] = 1

        self.total_words += 1

    def extract_words(self, content):
        phrases = utils.split_into_phrases(content)

        for phrase in phrases:
            for i in range(len(phrase)):
                for j in range(self.word_length_min, self.word_length_max + 1):
                    if i + j <= len(phrase):
                        word = phrase[i:i + j]
                        if word[0] not in self.blacklist:
                            self.insert(word)

        return self.trie_dict

    def load_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            trie_dict_list = json.load(f)
            trie_dict = {}
            for item in trie_dict_list:
                for first_char, sub_trie in item.items():
                    if first_char not in trie_dict:
                        trie_dict[first_char] = {}
                    for word, count in sub_trie.items():
                        if word not in trie_dict[first_char]:
                            trie_dict[first_char][word] = 0
                        trie_dict[first_char][word] += count
        trie = Trie(self.blacklist, self.word_length_min, self.word_length_max)
        trie.trie_dict = trie_dict
        return trie

    def merge_trie(self, other_trie):
        for first_char, sub_trie in other_trie.trie_dict.items():
            if first_char not in self.trie_dict:
                self.trie_dict[first_char] = {}
            for word, count in sub_trie.items():
                if word not in self.trie_dict[first_char]:
                    self.trie_dict[first_char][word] = 0
                self.trie_dict[first_char][word] += count

        self.total_words += other_trie.total_words


