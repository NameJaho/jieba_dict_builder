import utils


class Trie:
    def __init__(self, blacklist, word_length_min=2, word_length_max=4):
        self.word_length_min = word_length_min
        self.word_length_max = word_length_max
        self.blacklist = blacklist  # 假设您有一个黑名单字符集
        self.total_words = 0
        self.trie_dict = {}

    def insert(self, word):
        if len(word) < self.word_length_min or len(word) > self.word_length_max:
            return

        first_char = word[0]
        if first_char not in self.trie_dict:
            self.trie_dict[first_char] = {}

        current_dict = self.trie_dict[first_char]
        if word not in current_dict:
            current_dict[word] = 0
        current_dict[word] += 1

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
