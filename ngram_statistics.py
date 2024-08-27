from collections import defaultdict


class NgramStatistics:
    def __init__(self):
        pass

    @staticmethod
    def aggregate_words(words):
        # 初始化统计字典
        aggregated = {
            'word': words[0]['word'],
            'term_freq': 0,
            'doc_freq': 0,
            'status': 0,
            'left_chars': defaultdict(int),
            'right_chars': defaultdict(int)
        }

        # 用于记录文档频率
        doc_freq_set = set()

        # 遍历输入列表进行统计
        for entry in words:
            # 更新词频
            aggregated['term_freq'] += 1

            # 更新文档频率
            doc_freq_set.add(entry['doc_id'])

            # 更新左侧字符频率
            aggregated['left_chars'][entry['left_char']] += 1

            # 更新右侧字符频率
            aggregated['right_chars'][entry['right_char']] += 1

        # 计算文档频率
        aggregated['doc_freq'] = len(doc_freq_set)

        # 将字符频率字典转换为列表
        aggregated['left_chars'] = [{'char': char, 'freq': freq} for char, freq in aggregated['left_chars'].items()]
        aggregated['right_chars'] = [{'char': char, 'freq': freq} for char, freq in aggregated['right_chars'].items()]

        return aggregated


if __name__ == '__main__':
    ngram_stat = NgramStatistics()
    _words = [
        # term_freq:4; doc_freq:3; left:吃1,荐2,来1; right:牛1,家3
        {'word': '月满大江', 'left_char': '吃', 'right_char': '牛', 'doc_id': '0001'},
        {'word': '月满大江', 'left_char': '荐', 'right_char': '家', 'doc_id': '0001'},
        {'word': '月满大江', 'left_char': '荐', 'right_char': '家', 'doc_id': '0002'},
        {'word': '月满大江', 'left_char': '来', 'right_char': '家', 'doc_id': '0003'},
    ]

    result = ngram_stat.aggregate_words(_words)
    print(result)
