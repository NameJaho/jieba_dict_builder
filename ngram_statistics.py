from collections import defaultdict

class NgramStatistics:
    def __init__(self):
        pass

    @staticmethod
    def aggregate_words(words):
        aggregated = defaultdict(lambda: {
            'term_freq': 0,
            'doc_freq': 0,
            'status': 0,
            'left_chars': defaultdict(int),
            'right_chars': defaultdict(int)
        })

        doc_freq_set = defaultdict(set)

        for entry in words:
            word = entry['word']
            doc_id = entry['doc_id']
            left_char = entry['left_char']
            right_char = entry['right_char']

            # 更新词频
            aggregated[word]['term_freq'] += 1

            # 更新文档频率
            doc_freq_set[word].add(doc_id)

            # 更新左侧字符频率
            aggregated[word]['left_chars'][left_char] += 1

            # 更新右侧字符频率
            aggregated[word]['right_chars'][right_char] += 1

        # 计算文档频率
        for word in aggregated:
            aggregated[word]['doc_freq'] = len(doc_freq_set[word])

        # 将字符频率字典转换为列表
        for word in aggregated:
            aggregated[word]['left_chars'] = [{'char': char, 'freq': freq} for char, freq in aggregated[word]['left_chars'].items()]
            aggregated[word]['right_chars'] = [{'char': char, 'freq': freq} for char, freq in aggregated[word]['right_chars'].items()]

        # 转换为普通字典
        aggregated = {word: dict(stats) for word, stats in aggregated.items()}

        return aggregated


if __name__ == '__main__':
    ngram_stat = NgramStatistics()
    _words = [
        # 月满大江: term_freq:4; doc_freq:3; left:吃1,荐2,来1; right:牛1,家3
        # 吃饭: term_freq:1; doc_freq:1; left:你1; right:没1
        {'word': '月满大江', 'left_char': '吃', 'right_char': '牛', 'doc_id': '0001'},
        {'word': '月满大江', 'left_char': '荐', 'right_char': '家', 'doc_id': '0001'},
        {'word': '月满大江', 'left_char': '荐', 'right_char': '家', 'doc_id': '0002'},
        {'word': '月满大江', 'left_char': '来', 'right_char': '家', 'doc_id': '0003'},
        {'word': '吃饭', 'left_char': '你', 'right_char': '没', 'doc_id': '0004'},
    ]

    result = ngram_stat.aggregate_words(_words)
    print(result)