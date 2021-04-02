import os

import pandas as pd

# This is to merge Top 250 from Douban and IMDb into one file.
path = os.getcwd() + os.sep

db = pd.read_csv('%sDouban Top 250.csv' % path).set_index("IMDb_Name")
im = pd.read_csv('%sIMDb Top 250.csv' % path).set_index("IMDb_Name")

df = pd.concat([db, im], axis=1, sort=False)
df.insert(0, 'IMDb_Name', df.index)
df["IMDb_Rating"] = df.apply(lambda x: x.IMDb_Rating_IM if x.IMDb_Rating_IM > 0 else x.IMDb_Rating_DB, axis=1)
df.drop(["IMDb_Rating_DB", "IMDb_Rating_IM"], inplace=True, axis=1)
df.to_csv('%sCombine Douban & IMDb.csv' % path, encoding='utf_8_sig', index=False)
