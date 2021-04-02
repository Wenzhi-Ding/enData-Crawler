import multiprocessing
import os
from timeit import default_timer as timer

import moviesearch
import pandas as pd

# This is to get Top 250 movies from Douban
# i7-8750H (6cores, 12threads): 138.13s
if __name__ == '__main__':
    ts = timer()
    code_lst = list(set(moviesearch.DoubanInfo().get_code()))
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    df = pd.concat(pool.map(moviesearch.DoubanInfo().get_detail, code_lst, chunksize=1), axis=1).T
    df.set_index("Douban_Rank").sort_index().to_csv('%sDouban Top 250.csv' % (os.getcwd() + os.sep), encoding='utf_8_sig')

    print("Total time: %.2f seconds" % (timer() - ts))
