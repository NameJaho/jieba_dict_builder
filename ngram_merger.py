import csv
import pandas as pd
from pandarallel import pandarallel
import warnings
from config.config_loader import ConfigLoader

warnings.filterwarnings("ignore")


class NgramMerger(ConfigLoader):
    def __init__(self):
        super().__init__()

    def merge_ngrams(self):
        pass

