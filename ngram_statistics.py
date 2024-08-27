from collections import defaultdict, Counter
import pandas as pd


class NgramStatistics:
    def __init__(self):
        pass

    @staticmethod
    def aggregate_words(words, min_doc_freq=30):
        # 第一步：统计文档频率
        doc_freq_set = defaultdict(set)

        for entry in words:
            word = entry['word']
            doc_id = entry['doc_id']
            doc_freq_set[word].add(doc_id)

        # 过滤出文档频率大于等于 min_doc_freq 的词
        filtered_words = {word: freq for word, freq in doc_freq_set.items() if len(freq) >= min_doc_freq}

        # 第二步：统计词频和其他字段
        aggregated = defaultdict(lambda: {
            'term_freq': 0,
            'doc_freq': 0,
            'status': 0,
            'left_chars': Counter(),
            'right_chars': Counter()
        })

        for entry in words:
            word = entry['word']
            if word in filtered_words:
                doc_id = entry['doc_id']
                left_char = entry['left_char']
                right_char = entry['right_char']

                # 更新词频
                aggregated[word]['term_freq'] += 1

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

    @staticmethod
    def save_to_csv(aggregated):
        rows = []
        for term, info in aggregated.items():
            row = {
                'term': term,
                'term_freq': info['term_freq'],
                'doc_freq': info['doc_freq'],
                'status': info['status'],
                'left_chars': info['left_chars'],  # 转换为 JSON 字符串
                'right_chars': info['right_chars']  # 转换为 JSON 字符串
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # 将 DataFrame 保存为 CSV 文件
        csv_file_path = 'output/terms_data.csv'
        df.to_csv(csv_file_path, index=False)


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

    result = ngram_stat.aggregate_words(_words, min_doc_freq=1)
    print(result)
