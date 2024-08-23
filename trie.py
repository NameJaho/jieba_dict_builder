import utils
import os
import json


class Trie:
    def __init__(self, blacklist, word_length_min=2, word_length_max=5):
        self.trie_dict = None
        self.word_length_min = word_length_min
        self.word_length_max = word_length_max
        self.blacklist = blacklist
        self.total_words = 0  # number of scan words
        self.total_docs = 0  # number of documents
        self.total_chars = 0  # number of characters

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
            self.trie_dict[first_char] = []

        # 获取当前单词的首字对应的字典
        node = self.trie_dict[first_char]

        # 如果当前单词没有在sub_words中出现则初始化字典
        if not self.is_word_in_sub_words(node, word):
            sub_word = {'word': word, 'word_freq': 0, 'doc_freq': 1}
            node.append(sub_word)

        sub_word = self.find_matching_word(node, word)

        sub_word['word_freq'] += 1

        self.total_words += 1

    def extract_words(self, content):
        self.trie_dict = {}
        phrases = utils.split_into_phrases(content)

        for phrase in phrases:
            for i in range(len(phrase)):
                for j in range(self.word_length_min, self.word_length_max + 1):
                    if i + j <= len(phrase):
                        word = phrase[i:i + j]
                        if word[0] not in self.blacklist:
                            self.insert(word)

        return self.trie_dict

    # 扫描trie_dict, 去除不合理的成词
    @staticmethod
    def filter_words(trie_dict, word_length, min_word_freq):
        return {word: info for word, info in trie_dict.items()
                if len(word) == word_length and info["word_freq"] >= min_word_freq}

    def remove_inferior_words(self, trie_dict, shorter_words, longer_words):
        words_to_remove = set()

        for shorter_word, shorter_info in shorter_words.items():
            for longer_word, longer_info in longer_words.items():
                if shorter_word in longer_word and shorter_info["word_freq"] <= longer_info["word_freq"]:
                    words_to_remove.add(shorter_word)
                    break

            # 检查是否存在一组更长的词的 word_freq 之和等于当前词的 word_freq
            self._check_sum_of_longer_words(shorter_word, shorter_info, longer_words, words_to_remove)

        for word in words_to_remove:
            if word in trie_dict:
                del trie_dict[word]

        return trie_dict

    @staticmethod
    def _check_sum_of_longer_words(shorter_word, shorter_info, longer_words, words_to_remove):
        def _find_combinations(target, _longer_words_list):
            dp = [False] * (target + 1)
            dp[0] = True
            for word, info in _longer_words_list:
                freq = info["word_freq"]
                for j in range(target, freq - 1, -1):
                    if dp[j - freq]:
                        dp[j] = True
            return dp[target]

        longer_words_list = [(word, info) for word, info in longer_words.items() if shorter_word in word]
        if _find_combinations(shorter_info["word_freq"], longer_words_list):
            words_to_remove.add(shorter_word)

    def revise(self, trie_dict, min_word_length=2, max_word_length=5, revise_threshold=10):
        for word_length in range(min_word_length, max_word_length):
            shorter_words = self.filter_words(trie_dict, word_length, revise_threshold)
            longer_words = self.filter_words(trie_dict, word_length + 1, 1)
            trie_dict = self.remove_inferior_words(trie_dict, shorter_words, longer_words)

        return trie_dict

    def load_from_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as my_file:
            trie_dict_list = json.load(my_file)
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

    @staticmethod
    def merge_trie(datasets):
        # 创建一个新的字典来存储更新后的词频
        updated_data = {}

        # 遍历数据中的每个词汇和对应的词频
        for data in datasets:
            for key, words in data.items():
                for word_info in words:
                    word = word_info['word']
                    freq = word_info['word_freq']
                    doc_freq = word_info['doc_freq']

                    # 检查词汇是否已经在更新的字典中
                    if word in updated_data:
                        updated_data[word]['word_freq'] += freq  # 累加词频
                        updated_data[word]['doc_freq'] += doc_freq
                    else:
                        updated_data[word] = {'word_freq': freq, 'doc_freq': doc_freq}
        return dict(sorted(updated_data.items(), key=lambda item: item[1]['word_freq'], reverse=True))


if __name__ == '__main__':
    with open('output/sample3.csv.json', 'r', encoding='utf8') as f:
        data = json.load(f)

    trie = Trie([''], 2, 4)
    print(trie.merge_trie(data))
