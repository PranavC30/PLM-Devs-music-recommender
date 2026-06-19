import pandas as pd

pattern_vals = [
    'T2cPWVBI', '1T2cPWVBI', '0T2cPWVBI', 'A1T2cPWVBI', 'B1T2cPWVBI',
    'C1T2cPWVBI', 'D1T2cPWVBI', 'E1T2cPWVBI', 'F1T2cPWVBI', 'G1T2cPWVBI',
    'H1T2cPWVBI', 'J1T2cPWVBI', 'K1T2cPWVBI', 'L1T2cPWVBI', 'M1T2cPWVBI',
    'N1T2cPWVBI', 'O1T2cPWVBI', 'P1T2cPWVBI', 'Q1T2cPWVBI', 'R1T2cPWVBI',
    'S1T2cPWVBI', 'T1T2cPWVBI', 'U1T2cPWVBI', 'V1T2cPWVBI', 'W1T2cPWVBI',
    'X1T2cPWVBI', 'Y1T2cPWVBI', 'Z1T2cPWVBI'
]

df = pd.read_csv('data/songs.csv')
placeholders = df[df['URL'].apply(lambda u: any(p in u for p in pattern_vals))]
print('placeholder count:', len(placeholders))
print('unique placeholder URLs:', placeholders['URL'].nunique())
print('sample placeholders:')
print(placeholders[['Song','URL']].head(20).to_string(index=False))
