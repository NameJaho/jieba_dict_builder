import time

import pandas as pd
from utils import cost_time
from ngram_scanner import NgramScanner
from neighbour_scanner import NeighbourScanner
from entropy_calculator import EntropyCalculator
from char_freq_counter import KeywordCounter
from mi_calculator import MICalculator
from config.config_loader import ConfigLoader
from loguru import logger
import pickle


class WordDiscoverer(ConfigLoader):
    def __init__(self):
        super().__init__()
        self.ngram_scanner = NgramScanner()
        self.neighbour_scanner = NeighbourScanner()
        self.entropy_calculator = EntropyCalculator()
        self.char_freq_counter = KeywordCounter()
        self.mi_calculator = MICalculator()

    @cost_time
    def process(self):
        chunksize = 20 ** 6  # 每次读取100万行
        chunks = pd.read_csv('xhs_3000w.csv', chunksize=chunksize)

        # chunks = pd.read_csv(self.input_file_path.input_file, chunksize=chunksize)
        for index, chunk in enumerate(chunks):
            chunk.dropna(subset=['content'],inplace=True)
            start_time = time.time()
            chunk.rename(columns={'note_id': 'doc_id'}, inplace=True)
            logger.info(f"rename chunk index 〖{index}〗 time taken: {time.time()- start_time} seconds")

            # Step 1: processing ngrams
            logger.info('Scanning ngrams...')
            start_time = time.time()
            ngrams_dict = self.ngram_scanner.scan_to_dict(chunk=True, df=chunk)
            end_time = time.time()
            logger.info(f"ngram_scanner.scan_to_dict chunk index 〖{index}〗 time taken: {end_time- start_time} seconds")
            pickle.dump(ngrams_dict, open(self.output_file_path.ngrams_dict.replace('.pkl', f'_{index}.pkl'), 'wb'))
            logger.info(f"pickle dump ngrams_dict {index} time taken: {time.time()- end_time} seconds")
            logger.info(f'Generated {len(ngrams_dict)} ngrams...')
            end_time = time.time()

            # Step 2: processing left chars and right chars
            logger.info('Scanning neighbours...')
            neighbours_dict = self.neighbour_scanner.scan_to_dict(ngrams_dict)
            logger.info(f'neighbour_scanner.scan_to_dict chunk index 〖{index}〗 time taken: {time.time()- end_time} seconds')
            logger.info(f'Generated {len(neighbours_dict)} neighbours...')
            neighbours_dict.save_pkl(neighbours_dict, self.output_file_path.neighbours_dict.replace('.pkl', f'_{index}.pkl'))
            logger.info(f"pickle dump neighbours_dict {index} time taken: {time.time()- end_time} seconds")
            #
            # # Step 3: calculate entropy
            # logger.info('Calculating entropy...')
            # # entropy_input = pickle.load(open(self.output_file_path.neighbours_dict, 'rb'))
            # entropy_results = self.entropy_calculator.filter_by_entropy(neighbours_dict)
            # self.entropy_calculator.save_to_csv(entropy_results,chunk_index=index)
            # logger.info(f'Filtered {len(entropy_results)} ngrams with entropy > {self.filter.entropy_threshold}...')
            # break
        #
        # # Step 4: calculate char freq
        # logger.info('Calculating char freq...')
        # self.char_freq_counter.run()
        #
        # # Step 5: calculate mi
        # logger.info('Calculating mi...')
        # entropy_df = pd.DataFrame(entropy_results,
        #                           columns=['term', 'term_freq', 'doc_freq', 'entropy', 'left_entropy', 'right_entropy'])
        # entropy_df.dropna(inplace=True)
        # mi_results = self.mi_calculator.filter_by_mi(entropy_df)
        # self.mi_calculator.save_to_csv(mi_results)
        # logger.info('Process completed...')


if __name__ == '__main__':
    word_discoverer = WordDiscoverer()
    word_discoverer.process()
