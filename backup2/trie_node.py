class TrieNode:
    def __init__(self, char):
        self.char = char
        self.children = {}
        self.words = []  # 存储以该节点为前缀的单词及其词频和文频

    def add_child(self, char):
        if char not in self.children:
            self.children[char] = TrieNode(char)
        return self.children[char]

    def get_child(self, char):
        return self.children.get(char)

    def add_word(self, word, term_freq, doc_freq):
        # status = 0 表示状态未知
        word_info = {'word': word, 'term_freq': term_freq, 'doc_freq': doc_freq, 'status': 0}
        self.words.append(word_info)

    def get_words(self):
        return self.words
