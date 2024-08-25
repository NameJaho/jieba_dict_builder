import threading
import queue
from trie_node import TrieNode
from collections import defaultdict


class Trie:
    def __init__(self, is_suffix=False):
        self.root = TrieNode('')
        self.is_suffix = is_suffix

    def get_key_char(self, word):
        if self.is_suffix:
            key_char = word[-1]
        else:
            key_char = word[0]
        return key_char

    # insert new word
    # def insert(self, word, term_freq=1):
    #     key_char = self.get_key_char(word)
    #     node = self.root.add_child(key_char)
    #     node.add_word(word, term_freq, 1)

        # insert new word
    def insert(self, key_char, word_info):
        node = self.root.add_child(key_char)
        node.words.append(word_info)

    # update existing word by adding 1 to term_freq
    def update(self, word):
        key_char = self.get_key_char(word)
        node = self.root.get_child(key_char)
        if node:
            for word_info in node.words:
                if word_info['word'] == word:
                    word_info['term_freq'] += 1
                    break

    def search_words(self, first_char):
        node = self.root.get_child(first_char)
        if node is None:
            return []
        return node.get_words()

    def search_word(self, word):
        key_char = self.get_key_char(word)
        words = self.search_words(key_char)
        for word_info in words:
            if word_info['word'] == word:
                return word_info
        return None

    # def add(self, word):
    #     key_char = self.get_key_char(word)
    #
    #     node = self.root.get_child(key_char)
    #
    #     if node:
    #         word_exists = False
    #         for word_info in node.words:
    #             if word_info['word'] == word:
    #                 self.update(word)
    #                 word_exists = True
    #                 break
    #         if not word_exists:
    #             self.insert(word)
    #     else:
    #         self.insert(word)

    def update_status(self, word, status):
        """
        更新指定单词的status字段
        :param word: 要更新的单词
        :param status: 新的status值
        """
        word_info = self.search_word(word)
        word_info['status'] = status

    def merge(self, other_trie):
        self._merge_nodes(self.root, other_trie.root)

    def _merge_nodes(self, node, other_node):
        for char, other_child_node in other_node.children.items():
            if char in node.children:
                self._merge_nodes(node.children[char], other_child_node)
            else:
                node.children[char] = other_child_node
        for other_word_info in other_node.words:
            word_exists = False
            for word_info in node.words:
                if word_info['word'] == other_word_info['word']:
                    word_info['term_freq'] += other_word_info['term_freq']
                    word_info['doc_freq'] += other_word_info['doc_freq']
                    word_exists = True
                    break
            if not word_exists:
                node.words.append(other_word_info)

    def trie_to_json(self):
        node = self.root
        json_node = {}
        for char, child_node in node.children.items():
            json_node[char] = [
                {'word': word_info['word'], 'term_freq': word_info['term_freq'], 'doc_freq': word_info['doc_freq'], 'status': word_info['status']}
                for word_info in child_node.words
            ]
        return json_node

    def batch_insert(self, word_freq_dict):
        for key_char, word_info_list in word_freq_dict.items():
            for word_info in word_info_list:
                self.insert(key_char, word_info)

    def parallel_batch_insert(self, word_freq_dict, num_threads=4):
        def worker():
            while True:
                word_freq_chunk = q.get()
                if word_freq_chunk is None:
                    break
                self.batch_insert(word_freq_chunk)
                q.task_done()

        q = queue.Queue()
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)

        chunk_size = len(word_freq_dict) // num_threads
        items = list(word_freq_dict.items())
        for i in range(num_threads):
            start = i * chunk_size
            end = start + chunk_size if i < num_threads - 1 else len(items)
            q.put(dict(items[start:end]))

        q.join()

        for i in range(num_threads):
            q.put(None)
        for t in threads:
            t.join()