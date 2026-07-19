import pandas as pd
import numpy as np
import re

pd.set_option('display.max_columns', None) # force pandas to show all columns
pd.set_option('display.max_colwidth', None)  # show full content in each cell
# pd.set_option('display.width', None)         # prevent line wrapping issues

def app():
    print('WOMEN -----------------------------------------------------------------------------------------------------')
    # .convert_dtypes()automatically converts into Modern Pandas nullable datatypes
    df = pd.read_csv("perfume/ebay_womens_perfume_data.csv").convert_dtypes()

    print(df[df.duplicated(keep=False)])
    df.drop_duplicates(keep='last', inplace=True)

    print("NA_SUM: ", df.isna().sum())
    print("SHAPE: ", df.shape)
    print("UNIQUE: ", df.nunique())
    print("NA_VALUE_COUNT: ", df.isna().value_counts())

    print('--------------------------------------------------------------------------')

    print(df.head())

    # retrospective checking the failed datetime conversions
    failed = [19, 20, 536, 537, 559, 565, 566, 55, 569, 61, 574, 577, 579, 580, 586, 594, 83, 87, 608, 623, 624, 628, 629, 639, 130, 645, 137, 656, 667, 157, 669, 674, 682, 174, 177, 706, 710, 711, 727, 740, 741, 236, 752, 242, 760, 761, 779, 797, 802, 291, 804, 296, 815, 318, 835, 844, 856, 875, 878, 886, 375, 376, 899, 904, 397, 411, 940, 942, 944, 434, 947, 438, 440, 956, 455, 456, 969, 990, 992, 497, 505, 509]
    failed_mask = df.index.isin(failed)
    print("FAILED BEFORE: ", df[failed_mask])

    list_before = df.index[df['lastUpdated'].isna()].tolist()
    print("BEFORE to_datetime: ", list_before)

    df['lastUpdated'] = pd.to_datetime(
        df['lastUpdated'].str.replace('PDT', "", regex=False), 
        errors='coerce',
        utc=True)
    list_after = df.index[df['lastUpdated'].isna()].tolist()        
    print("AFTER to_datetime: ", list_after)

    diff = list(set(list_after) - set(list_before))
    print("Failed_datetime_index: ", diff)

    
    print("FAILED AFTER: ", df[failed_mask])
    print('--------------------------------------------------------------------------')

    print(df['priceWithCurrency'].str.strip().str.startswith('US', na=False).value_counts())
    currency = df['priceWithCurrency'].str.split(r'\$', n=1, expand=True)[0]
    currency = currency.str.strip()

    # currency = df['priceWithCurrency'].str.extract(r'^[^$]*')[0].str.strip()
    # currency = df['priceWithCurrency'].str.replace(r'\$.*', '', regex=True).str.strip()

    print("ALL US?: ", (currency == "US").sum())
    df['currency'] = currency.replace({'US': "USD"})
    # check if 'priceWithCurrency' has the same numeric values as price
    df['price_extracted'] = (
        df['priceWithCurrency']
        .str.extract(r'([-+]?\d*\.?\d+)')
        .astype('Float64')       
    )
    print(df[['price', 'price_extracted']])
    print("DTYPES: ", df.dtypes)

    mask = df['price'] != df['price_extracted']
    mask = ~np.isclose(df['price'], df['price_extracted'], rtol=1e-5, atol=1e-8, equal_nan=True)
    print('Not matching price rows: ', df[mask].value_counts())
    df = df.drop(columns=["price_extracted", 'priceWithCurrency'])

    print('--------------------------------------------------------------------------')
    df['availableText'] = df['availableText'].str.strip().str.replace(',', '', regex=False).str.lower()
    print(df[(df['availableText'] == "") | df['availableText'].isna()].value_counts())
    print('--------------------------------------------------------------------------')

    df['A'] = pd.to_numeric(
        df['availableText'].str.extract(r'[^\d]*(\d+(?:\.\d+)?)[^\d/(]*[/(]?')[0],
        errors='coerce'
    )
    df['lots'] = pd.to_numeric(
        df['availableText'].str.extract(r'\((\d+(?:\.\d+)?)[^\d]*')[0],
        errors='coerce'
    )
    df['B'] = pd.to_numeric(
        df['availableText'].str.extract(r'\/\s+(\d+(?:\.\d+)?)')[0], 
        errors='coerce'
    )
    df.loc[
        df['availableText'].str.contains('Out of Stock', case=False, na=False),
        'A'
    ]=0
    df.loc[
        df['availableText'].str.contains('Last One', case=False, na=False),
        'A'
    ]=1
    mask = df['lots'].notna() & df['A'].notna()
    # 2 .loc lookups on "A"
    df.loc[mask, 'A'] *= df.loc[mask, 'lots']

    print('--------------------------------------------------------------------------')
    print(df[['A', 'lots', 'B']].isna().sum())
    print("available NaN: ", df['available'].isna().sum())
    print("sold NaN: ", df['sold'].isna().sum())

    print('--------------------------------------------------------------------------')
    print(df[df['available'].isna() & (df['A'].notna())])
    print('--------------------------------------------------------------------------')
    print(df[df['sold'].isna() & (df['B'].notna())])
    print('--------------------------------------------------------------------------')
    print(df[df['A'].isna()])
    print('--------------------------------------------------------------------------')
    print(df[df['B'].isna()])
    print('--------------------------------------------------------------------------')

    mask = (df['available'] != df['A']) & (df['available'].notna())
    print(mask.value_counts())
    print(df[mask])
    print('--------------------------------------------------------------------------')

    mask = (df['sold'] != df['B']) & (df['sold'].notna())
    print(df[mask])
    print('--------------------------------------------------------------------------')
    df['available'] = df['A']
    df['sold'] = df['B']
    df = df.drop(columns=['A', 'B', 'lots'])
    df['sex'] = 'F'
    df['sex'] = df['sex'].astype('string')
    print(df[df['available'].isna()])
    print(df[df['sold'].isna()])
    
    print('--------------------------------------------------------------------------')
    df[['address', 'country']] = df['itemLocation'].str.rsplit(',', n=1, expand=True).apply(lambda col: col.str.strip())
    print(df.columns)
    print(df[['country', 'address']].isna().sum())
    print(df[df['country'].isna()])
    print(df[df['country'].str.contains('United States')])
    print(df[~df['country'].isin(['United States', 'Canada'])])
    df['country'] = df['country'].replace('Estados Unidos', 'United States')
    # list of known countries, include NaNs for analysis
    print(df['country'].value_counts(dropna=False))
    # flag rows where address contains a country name
    # drop NaNs before Numpy unique method
    countries = (df['country'].dropna().unique().tolist())
    countries.append('USA')
    print(countries)
    # re.escape() escapes any special characters (. ^ $ * + ? { } [ ] \ | ( )) so they're treated as literals.
    pattern = '|'.join(re.escape(c) for c in countries)
    # na=False — when the address is NaN, instead of returning NaN (which would make the column mixed bool/NaN type), 
    # it returns False. Meaning "no, this NaN address does not contain a country name." 
    # Without it you'd get NaN in your boolean column which causes type issues downstream.
    mask_invalid_address = df['address'].str.contains(pattern, case=False, na=False)
    df['invalid_address'] = mask_invalid_address
    # print flagged rows
    print(mask_invalid_address.value_counts())
    print(df[df['invalid_address']])
    print(df.dtypes)

    print('--------------------------------------------------------------------------')
    print(len(df['brand'].unique().tolist()))
    print(len(df['type'].unique().tolist()))
    df['brand'] = df['brand'].str.strip().str.lower()
    df['type'] = df['type'].str.strip().str.lower()

    return df

# “If this file is being executed directly, run the entry function.
# If this file is only being imported by another file, do not run it automatically.”
# directly executed file → __name__ == "__main__"
# imported file → __name__ == filename/module name for eg. __women__
if __name__ == "__main__":
    app()