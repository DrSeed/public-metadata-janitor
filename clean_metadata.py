# Command-line metadata cleaner for messy public genomics sample tables.
import argparse
import re
import pandas as pd

SEX_MAP = {
    'm': 'male', 'male': 'male', 'man': 'male', 'f': 'female',
    'female': 'female', 'woman': 'female'
}

CONDITION_MAP = {
    'tumor': 'tumour', 'tumour': 'tumour', 'cancer': 'tumour',
    'control': 'control', 'ctrl': 'control', 'normal': 'control',
    'healthy': 'control'
}

WORD_NUMBERS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
}


def norm_text(value, mapping):
    # Lowercase, strip, and map free text to a controlled vocabulary.
    if pd.isna(value):
        return None
    key = str(value).strip().lower()
    key = re.sub(r'[^a-z]', '', key)
    return mapping.get(key, None)


def parse_numeric(value):
    # Pull the first number out of a messy string, handling word numbers.
    if pd.isna(value):
        return None
    text = str(value).strip().lower()
    for word, num in WORD_NUMBERS.items():
        if word in text:
            return float(num)
    match = re.search(r'\d+(?:\.\d+)?', text)
    if match:
        return float(match.group())
    return None


def clean_frame(df):
    report = []
    out = df.copy()
    if 'sex' in out.columns:
        out['sex'] = df['sex'].apply(lambda v: norm_text(v, SEX_MAP))
    if 'condition' in out.columns:
        out['condition'] = df['condition'].apply(lambda v: norm_text(v, CONDITION_MAP))
    if 'age' in out.columns:
        out['age'] = df['age'].apply(parse_numeric)
    for col in out.columns:
        n_bad = out[col].isna().sum()
        if n_bad:
            report.append({'column': col, 'unresolved': int(n_bad)})
    return out, pd.DataFrame(report)


def main():
    parser = argparse.ArgumentParser(description='Clean messy sample metadata.')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--report', default='cleaning_report.csv')
    args = parser.parse_args()
    df = pd.read_csv(args.input)
    clean, report = clean_frame(df)
    clean.to_csv(args.output, index=False)
    report.to_csv(args.report, index=False)
    print('Wrote', args.output, 'and', args.report)


if __name__ == '__main__':
    main()
