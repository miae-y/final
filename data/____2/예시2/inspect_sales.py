import pandas as pd
from pathlib import Path
p = Path('sales_2025.csv')
if not p.exists():
    raise FileNotFoundError(p)
df = pd.read_csv(p)
print('shape', df.shape)
print('cols', list(df.columns))
print(df.dtypes.to_string())
print('\nhead\n', df.head(5).to_string(index=False))
print('\nunique counts\n', df.nunique().to_string())
print('\nregion counts\n', df['지역'].value_counts().to_string())
print('\nchannel counts\n', df['채널'].value_counts().to_string())
print('\norder status counts\n', df['주문상태'].value_counts().to_string())
print('\nsales describe\n', df['매출액'].describe().to_string())
print('\nprice describe\n', df['판매단가'].describe().to_string())
print('\nreturn rows', df[df['주문상태']!='정상'].shape)
