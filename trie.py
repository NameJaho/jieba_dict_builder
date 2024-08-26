import multiprocessing
from utils import cost_time
from trie_node import TrieNode


class Trie:
    def __init__(self):
        self.root = TrieNode('')
        self.total_term_freq = 0
        # self.lock = threading.Lock()  # 使用锁来保证多线程安全

    def insert(self, word, term_freq, doc_freq, status):
        node = self.root
        for char in word:
            node = node.add_child(char)
        node.add_word_info(word, term_freq, doc_freq, status)
        self.total_term_freq += term_freq

    def bulk_insert(self, words):
        words.sort(key=lambda x: x['word'])

        with multiprocessing.Pool() as pool:
            pool.map(self._insert_wrapper, words)

    def _insert_wrapper(self, word_info):
        self.insert(word_info['word'], word_info['term_freq'], word_info['doc_freq'], word_info['status'])


    def search(self, word):
        node = self.root
        for char in word:
            node = node.get_child(char)
            if node is None:
                return False
        return node.is_end()

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            node = node.get_child(char)
            if node is None:
                return []
        return self._get_all_words(node)

    def _get_all_words(self, node):
        words = []
        if node.is_end():
            words.append(node.get_word_info())
        for child in node.children.values():
            words.extend(self._get_all_words(child))
        return words

    @property
    def all_words(self):
        return self._get_all_words(self.root)

    def get_total_term_freq(self):
        return self.total_term_freq

    def get_words_with_term_freq(self):
        words_with_term_freq = []

        def _dfs(node, path):
            if node.is_end_of_word:
                words_with_term_freq.append((path, node.word_info['term_freq']))
            for char, child_node in node.children.items():
                _dfs(child_node, path + char)

        _dfs(self.root, '')
        return words_with_term_freq

    def print_trie(self, node=None, prefix='', is_root=True):
        if node is None:
            node = self.root
        if is_root:
            print("Trie Structure:")
        if node.is_end():
            print(f"{prefix}{node.char} ({node.word_info})")
        else:
            print(f"{prefix}{node.char}")
        for child in node.children.values():
            self.print_trie(child, prefix + '  ', False)

    def get_words_containing(self, word, all_words):

        return [(w['word'], w['term_freq']) for w in all_words if word in w['word']]


if __name__ == '__main__':
    trie = Trie()
    trie.insert("apple", 5, 2, 0)
    trie.insert("app", 3, 1, 0)
    trie.insert("banana", 2, 1, 0)

    trie.print_trie(trie.root)
