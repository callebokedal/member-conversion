import pandas as pd

df = pd.DataFrame(
    columns=["key", "ref", "name", "value"],
    data=[
        ["k1", None, "N1", "A"],
        [None, "k1", "N2", "B"],
        [None, "k1", "N3", "C"],
        ["k2", None, "N4", "D"],
        ["k3", None, "N5", "E"],
        [None, "k3", "N6", "F"],
        [None, "k3", "N7", "G"],
    ],
)

print(df)
ind = df["key"].isna()
df1 = df.loc[~ind]
df2 = df.loc[ind]
print(ind)
print(df1)
print(df2)

combo = (
    df1.merge(df2[["ref", "name", "value"]], left_on="key", right_on="ref", how="left")
    .fillna("")
    .groupby("key")
    .agg(name=pd.NamedAgg("name_y", ":".join), value=pd.NamedAgg("value_y", ":".join))
)
print(combo)

for c in ["name", "value"]:
    dx = combo[c].str.split(":", expand=True).add_prefix(c)
    df1 = df1.merge(dx, left_on="key", right_index=True)

print(df1)