import pandas as pd
import re

pd.set_option('display.max_columns', None) # force pandas to show all columns
pd.set_option('display.max_colwidth', None)  # show full content in each cell

def app():
    print('MEN --------------------------------------------------------------------------------------------------------')
    # .convert_dtypes()automatically converts into Modern Pandas nullable datatypes
    df = pd.read_csv('perfume/ebay_mens_perfume_data.csv').convert_dtypes()

    print(df.isna().sum())
    df['lastUpdated'] = pd.to_datetime(
        df['lastUpdated'].str.replace('PDT', "", regex=False),
        errors='coerce',
        utc=True)
    print(df.shape)
    print(df.dtypes)
    print(df[df.duplicated(keep=False)])
    print(df.loc[[47, 74, 77]])
    print('-----------------------------------------------------------------------------------------------------------')
    print(df[~df['priceWithCurrency'].str.strip().str.startswith('US')])
    df[['currency', 'price_temp']] = df['priceWithCurrency'].str.strip(
        ).str.replace(
        ',', '', regex=False
        ).str.extract(
            r'([A-Za-z]+)[^\d]*(\d+(?:\.\d+)?)'
        )

    df['price_temp'] = pd.to_numeric(
            df['price_temp'],
            errors='coerce'
        ).astype('Float64')

    df['currency'] = df['currency'].replace({
        'C': 'CAD', 
        'US': 'USD' # anything else stays unchanged
    })
    print(df['price_temp'].isna().sum())
    print((df['price'] == df['price_temp']).value_counts())
    df = df.drop(columns=['price_temp', 'priceWithCurrency'])
    df['sex'] = 'M'
    df['sex'] = df['sex'].astype('string')

    print('-----------------------------------------------------------------------------------------------------------')
    s = df['availableText'].str.strip().str.lower()
    s = s.str.replace(',', '', regex=False)
    s = s.str.replace('last one', '1 available', regex=False)
    s = s.str.replace('out of stock', '0 available', regex=False)
    df['availableText'] = s
    # clean = df['availableText'].str.split(r'[/(]')[0]
    df['A'] = pd.to_numeric(df['availableText'].str.extract(r'(\d+\.?\d*)\D*available')[0], errors='coerce').astype('Float64')
    df['lot'] = pd.to_numeric(df['availableText'].str.extract(r'\((\d+\.?\d*)\D*\)')[0], errors='coerce').astype('Float64')
    df['B'] = pd.to_numeric(df['availableText'].str.extract(r'(\d+\.?\d*)\ssold')[0], errors='coerce').astype('Float64')
    print(df[['A', 'lot', 'B']].isna().sum())
    # print(df[df[['A', 'B']].isna().any(axis=1)])
    print(df[((df['available'] != df['A']) | (df['sold'] != df['B'])) & (df['available'].notna()) & (df['sold'].notna())])
    print(df[df['lot'].notna()])
    print(df[df['A']==df['B']])
    mask = df['availableText'].str.contains("limited quantity available", case=False, na=False)
    print('TOTAL:', (df['A'].isna() & mask).sum())
    print(df[~mask & df['A'].isna()])
    mask = df['A'].notna() & df['lot'].notna()
    df.loc[mask, 'A'] = df['A'] * df['lot']
    df['available'] = df['A']
    df['sold'] = df['B']
    df = df.drop(columns=['A', 'B', 'lot'])
    print('-----------------------------------------------------------------------------------------------------------')

    df[['address', 'country']]= df['itemLocation'].str.rsplit(",", n=1, expand=True).apply(lambda x: x.str.strip())
    print(df.dtypes)
    print(df.head())
    print(df[['address', 'country']].isna().sum())
    print(df[df['country'].isna()])
    # by default dropna=True, auto filter out NaNs
    print(df['country'].value_counts(dropna=False))
    # vector column data type
    print("country NaN dtype: ", df[df['country'].isna()]['country'].dtypes)
    for x in df['country'].unique():
        print(repr(x), type(x))
    countries = df['country'].dropna().unique().tolist()
    countries.append('USA')
    print(countries)
    
    print('-----------------------------------------------------------------------------------------------------------')
    mask = df['address'].isin(countries) & (df['country'].isna())
    print(df[mask])
    for x in df.loc[mask, 'country']:
        print(repr(x), type(x))
    df.loc[mask, 'country'] = df['address']
    # # read_csv defaults Numpy datatypes (object regardless of str or Float64), normalize into Pandas "string" type
    # df['address'] = df['address'].astype('string')
    df.loc[mask, 'address'] = pd.NA # pandas NaN type
    print(df[mask])
    for x in df.loc[mask, 'address']:
        print(repr(x), type(x))
    print('-----------------------------------------------------------------------------------------------------------')
    # update mask(old one is stale) and country
    mask_after = df['address'].isin(countries) & (df['country'].isna())
    print(df[mask_after])
    for x in df.loc[mask_after, 'country']:
        print(repr(x), type(x))

    print('-----------------------------------------------------------------------------------------------------------')
    pattern = '|'.join(re.escape(c) for c in countries)
    mask_invalid_address = df['address'].str.contains(pattern, case=False, na=False)
    print("Invalid addresses count:", mask_invalid_address.sum())
    df['invalid_address'] = mask_invalid_address
    print(df.head())

    print('-----------------------------------------------------------------------------------------------------------')
    print(df['brand'].value_counts())
    print(df['type'].value_counts())
    df['brand'] = df['brand'].str.strip().str.lower()
    df['type'] = df['type'].str.strip().str.lower()


    print(df[df['lastUpdated'].isna()])

    return df

if __name__ == "__main__":
    app()