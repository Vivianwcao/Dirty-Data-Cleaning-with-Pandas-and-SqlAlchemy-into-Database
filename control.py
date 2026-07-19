from men import app as app_men
from women import app as app_women

import pandas as pd
from pandas.api.types import is_extension_array_dtype
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/data_cleaning")


def app():
    df_men = app_men()
    df_women = app_women()
    print(
        "CONTROL -------------------------------------------------------------------------------------------------------"
    )
    # stack rows
    df = pd.concat(
        [df_men, df_women], axis=0, join="outer", ignore_index=True
    ).sort_values("type")
    df["brand"] = (
        df["brand"].str.replace("~", "", regex=False).str.strip().replace("", pd.NA)
    )
    df["type"] = (
        df["type"].str.replace(r"[^a-zA-Z\s,]", "", regex=True).replace("", pd.NA)
    )
    df["staging_id"] = range(1, len(df) + 1)
    df = df.rename(
        columns={"lastUpdated": "last_updated", "itemLocation": "item_location"}
    )
    # remove availableText
    df = df[
        [
            "brand",
            "title",
            "type",
            "price",
            "available",
            "sold",
            "last_updated",
            "item_location",
            "currency",
            "sex",
            "address",
            "country",
            "invalid_address",
            "staging_id",
        ]
    ]

    # True → Pandas extension dtype
    # False → normal NumPy dtype or non-array
    for x in df.columns:
        print(repr(x), is_extension_array_dtype(df[x]))

    # brand : perfume is 1:M relationship
    brands_df = df[["brand"]].dropna().drop_duplicates(keep="first")
    print("brands_df", brands_df.head(20))

    print(
        "-----------------------------------------------------------------------------------------------------------"
    )
    # type : perfume is M:M relationship

    junction_df = df[["staging_id", "type"]].dropna()
    junction_df["type"] = junction_df["type"].str.split(",")

    junction_df = junction_df.explode("type")
    junction_df["type"] = junction_df["type"].str.strip().replace("", pd.NA)
    junction_df = junction_df.dropna(subset=["type"])
    print(junction_df.head(20))

    types_df = junction_df["type"].to_frame().drop_duplicates()
    print(types_df.head(20))

    print(df.columns)

    print(
        "-----------------------------------------------------------------------------------------------------------"
    )

    try:
        with engine.begin() as connection:
            df.to_sql(
                name="staging_perfumes",
                con=connection,
                if_exists="append",
                index=False,
            )

            junction_df.to_sql(
                name="staging_perfume_types_junction",
                con=connection,
                if_exists="append",
                index=False,
            )

            brands_df.to_sql(
                name="perfume_brands",
                con=connection,
                if_exists="append",
                index=False,
            )

            types_df.to_sql(
                name="perfume_types",
                con=connection,
                if_exists="append",
                index=False,
            )
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    app()
