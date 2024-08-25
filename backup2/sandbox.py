from trie_node import TrieNode
from trie import Trie
import json

text = '今天天气真好，好的不能再好'


def scan_text_and_insert_into_trie(text, trie):
    for i in range(len(text)):
        for length in range(2, 6):
            if i + length <= len(text):
                word = text[i:i + length]
                trie.add(word, 1, 1)
    return trie

# 创建一个前缀树实例
trie = Trie()

# 给定的文本
text = '今天天气真好，好的不能再好'

# 扫描文本并插入前缀树
trie = scan_text_and_insert_into_trie(text, trie)

trie_json = trie.trie_to_json(trie.root)
print(json.dumps(trie_json, ensure_ascii=False, indent=4))

