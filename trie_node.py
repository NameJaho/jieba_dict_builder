class TrieNode:
    def __init__(self, char):
        self.char = char
        self.children = {}
        self.is_end_of_word = False  # 标记该节点是否是单词的结尾
        self.word_info = None  # 存储该节点对应的单词信息（如果该节点是单词的结尾）

    def add_child(self, char):
        if char not in self.children:
            self.children[char] = TrieNode(char)
        return self.children[char]

    def get_child(self, char):
        return self.children.get(char)

    def add_word_info(self, word, term_freq, doc_freq, status):
        # status = 0 表示状态未知
        self.word_info = {'word': word, 'term_freq': term_freq, 'doc_freq': doc_freq, 'status': status}
        self.is_end_of_word = True  # 标记该节点是单词的结尾

    def get_word_info(self):
        return self.word_info

    def is_end(self):
        return self.is_end_of_word
