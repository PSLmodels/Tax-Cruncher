import pandas as pd
from taxcrunch.multi_cruncher import Batch
import numpy as np
import os

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

data_dict = {
    'year': [2026],
    'mstat': [1, 2],
    'page': [0],
    'sage': [0],
    'depx': list(range(0, 5)),
    'dep13': [0],
    'dep17': [0],
    'dep18': [0],
    'pwages': list(range(0, 505000, 5000)),
    'swages': [0],
    'dividends': [0],
    'intrec': [0],
    'stcg': [0],
    'ltcg': [0],
    'otherprop': [0],
    'nonprop': [0],
    'pensions': [0],
    'gssi': [0],
    'ui': [0],
    'proptax': [0],
    'otheritem': list(range(0, 51000, 1000)),
    'childcare': [0],
    'mortgage': list(range(0, 51000, 1000))
}

combos = [(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w)
          for a in data_dict['year']
          for b in data_dict['mstat']
          for c in data_dict['page']
          for d in data_dict['sage']
          for e in data_dict['depx']
          for f in data_dict['dep13']
          for g in data_dict['dep17']
          for h in data_dict['dep18']
          for i in data_dict['pwages']
          for j in data_dict['swages']
          for k in data_dict['dividends']
          for l in data_dict['intrec']
          for m in data_dict['stcg']
          for n in data_dict['ltcg']
          for o in data_dict['otherprop']
          for p in data_dict['nonprop']
          for q in data_dict['pensions']
          for r in data_dict['gssi']
          for s in data_dict['ui']
          for t in data_dict['proptax']
          for u in data_dict['otheritem']
          for v in data_dict['childcare']
          for w in data_dict['mortgage']]

df_combos = pd.DataFrame(combos)
df_combos.iloc[:, 5] = df_combos.iloc[:, 4]
df_combos.iloc[:, 6] = df_combos.iloc[:, 4]
df_combos.iloc[:, 7] = df_combos.iloc[:, 4]
df_combos.iloc[:, 9] = np.where(
    df_combos.iloc[:, 1] == 2, df_combos.iloc[:, 8], 0)
df_combos.insert(0, 'RECID', df_combos.index + 1)

df_combos.columns = range(df_combos.shape[1])

cols = ['ID', 'year', 'mstat', 'page', 'sage', 'depx', 'dep13', 'dep17', 'dep18', 'pwages', 'swages', 'dividends', 'intrec',
        'stcg', 'ltcg', 'otherprop', 'nonprop', 'pensions', 'gssi', 'ui', 'proptax', 'otheritem', 'childcare', 'mortgage']
df_named = df_combos.copy()
df_named.columns = cols

b = Batch(df_combos)

baseline = b.create_table()
tcja_ext = b.create_table(
    reform_file=os.path.join(CURRENT_PATH, 'TCJA_ext.json'))

baseline_merged = baseline.merge(df_named, on='ID')
keep = ['ID', 'Individual Income Tax', 'Wages',
        'depx', 'mstat', 'otheritem', 'mortgage']
df_baseline_temp = baseline_merged[keep]
df_baseline = df_baseline_temp.rename(
    columns={'Individual Income Tax': 'itax base'})

df_merge_temp = df_baseline.merge(
    tcja_ext[['ID', 'Individual Income Tax']], on='ID')
df = df_merge_temp.rename(columns={'Individual Income Tax': 'itax ext'})

df.to_csv('cruncher_data.csv', index=False)
