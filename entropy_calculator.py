import math
from collections import defaultdict


class EntropyCalculator:
    @staticmethod
    def calculate_single_entropy(neighbors):
        if not neighbors:
            return 0
        total_freq = sum(neighbors.values())
        return -sum((freq / total_freq) * math.log(freq / total_freq) for freq in neighbors.values())

    def calculate_entropy(self, word, trie, all_words):
        left_neighbors = defaultdict(int)
        right_neighbors = defaultdict(int)

        # 获取所有包含目标词的词及其频率
        containing_words = trie.get_words_containing(word, all_words)

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


if __name__ == '__main__':
    print(math.log(9/100)*9/100)
