# Self-contained demo: simulate messy metadata, clean it, and plot the result.
import os
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SEX_MAP = {'m': 'male', 'male': 'male', 'man': 'male', 'f': 'female', 'female': 'female', 'woman': 'female'}
CONDITION_MAP = {'tumor': 'tumour', 'tumour': 'tumour', 'cancer': 'tumour', 'control': 'control', 'ctrl': 'control', 'normal': 'control', 'healthy': 'control'}
WORD_NUMBERS = {'forty': 40, 'fifty': 50, 'sixty': 60}


def norm_text(value, mapping):
    if pd.isna(value):
        return None
    key = re.sub(r'[^a-z]', '', str(value).strip().lower())
    return mapping.get(key, None)


def parse_numeric(value):
    if pd.isna(value):
        return None
    text = str(value).strip().lower()
    for word, num in WORD_NUMBERS.items():
        if word in text:
            return float(num)
    match = re.search(r'\d+(?:\.\d+)?', text)
    return float(match.group()) if match else None


def simulate(n=200, seed=1):
    rng = np.random.default_rng(seed)
    sex_variants = ['M', 'male', 'Male ', 'F', 'female', 'woman', 'unknown', '']
    cond_variants = ['tumor', 'Tumour', 'CANCER', 'control', 'ctrl', 'Normal', 'healthy', '???']
    age_variants = ['45', '45 years', '45y', 'forty', 'NA', '60.0']
    df = pd.DataFrame({
        'sample_id': ['S%03d' % i for i in range(n)],
        'sex': rng.choice(sex_variants, n),
        'condition': rng.choice(cond_variants, n),
        'age': rng.choice(age_variants, n),
    })
    return df


def main():
    os.makedirs('figures', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    df = simulate()

    clean = df.copy()
    clean['sex'] = df['sex'].apply(lambda v: norm_text(v, SEX_MAP))
    clean['condition'] = df['condition'].apply(lambda v: norm_text(v, CONDITION_MAP))
    clean['age'] = df['age'].apply(parse_numeric)

    fields = ['sex', 'condition', 'age']
    before_unique = [df[f].astype(str).str.strip().nunique() for f in fields]
    after_unique = [clean[f].dropna().nunique() for f in fields]
    unresolved = [int(clean[f].isna().sum()) for f in fields]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    x = np.arange(len(fields))
    w = 0.35
    axes[0].bar(x - w / 2, before_unique, w, label='before', color='#c0504d')
    axes[0].bar(x + w / 2, after_unique, w, label='after', color='#4f81bd')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(fields)
    axes[0].set_ylabel('distinct values')
    axes[0].set_title('Vocabulary collapse after cleaning')
    axes[0].legend()

    axes[1].bar(x, unresolved, color='#f79646')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(fields)
    axes[1].set_ylabel('unresolved rows')
    axes[1].set_title('Rows flagged for human review')

    fig.tight_layout()
    fig.savefig('figures/demo.png', dpi=120)

    summary = pd.DataFrame({
        'field': fields,
        'distinct_before': before_unique,
        'distinct_after': after_unique,
        'unresolved_rows': unresolved,
    })
    summary.to_csv('results/summary.csv', index=False)
    print(summary.to_string(index=False))
    print('Saved figures/demo.png and results/summary.csv')


if __name__ == '__main__':
    main()
