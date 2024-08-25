from trie_node import TrieNode


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, is_new_document=False):
        """将单词插入到Trie树中，并根据是否是新文档更新文频"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.freq += 1

        # 如果是新文档，并且之前没有在这个文档中出现过，则增加文频
        if is_new_document and not node.in_current_document:
            node.doc_freq += 1
            node.in_current_document = True

    def search(self, word):
        """搜索单词，返回它的词频和文频"""
        node = self.root
        for char in word:
            if char not in node.children:
                return 0, 0
            node = node.children[char]
        return node.freq, node.doc_freq

    def update(self, word, count, is_new_document=False):
        """更新单词的频次，并根据是否是新文档更新文频"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.freq += count

        if is_new_document and not node.in_current_document:
            node.doc_freq += 1
            node.in_current_document = True

    def merge(self, other_trie):
        """合并另一棵Trie树"""

        def merge_nodes(node1, node2):
            for char, child_node2 in node2.children.items():
                if char in node1.children:
                    merge_nodes(node1.children[char], child_node2)
                else:
                    node1.children[char] = child_node2
            node1.freq += node2.freq
            node1.doc_freq += child_node2.doc_freq

        merge_nodes(self.root, other_trie.root)

    def reset_document_flags(self):
        """重置节点中的文档标记，这样可以在处理下一个文档时重新计算文频"""

        def reset_flags(node):
            node.in_current_document = False
            for child in node.children.values():
                reset_flags(child)

        reset_flags(self.root)

    def collect_words_with_min_freq(self, min_freq):
        """收集词频和文频大于等于 min_freq 的单词"""
        result = {}

        def collect(node, prefix):
            if node.freq >= min_freq:
                result[prefix] = (node.freq, node.doc_freq)
            for char, child_node in node.children.items():
                collect(child_node, prefix + char)

        collect(self.root, "")
        return result
