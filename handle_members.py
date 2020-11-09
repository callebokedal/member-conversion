import pandas as pd
import os

path = '/usr/src/app'

def list_all_files(path):
    """
    List all files in path
    """
    with os.scandir(path) as it:
        for entry in it:
            print(entry.name)

# Dataframe for members
members=None
def read_file(file_name):
    """
    Test to read Excel via pandas
    """
    ##df = pd.read_excel(file_name, sheetname='Sheet1')
    df = pd.read_excel(file_name)

    #print("Column headings:")
    #print(df.columns)
    #print(df['Ingen tidning tack'])
    # print(df)
    return df

id_df=None
def read_id_file(file_name):
    """
    Read file with member id and personnummer
    """
    df = pd.read_csv(file_name, header=None, names=['MedlemsID', 'Personnummer2'])
    #print(df)
    return df


# Get mapping of id <-> pnr
id_df = read_id_file("./files/Senior-excel.txt")
# print(id_df)
#print(id_df.dtypes)
# MedlemsID       int64
# Personnummer    int64

# Get members from file
members = read_file("./files/Senior-excel.xls")
        
# Merge full personnumer into members
# https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
def merge_dfs(df1, df2, on, dir = 'left'):
    """
    Merge dataframes based on 'MedlemsID'
    """
    merged_df = pd.merge(df1, df2, 
                     on = on,
                     how = dir)
    #merged_df.drop(right_name)
    return merged_df


# Action - merge records
mdf = merge_dfs(members, id_df, 'MedlemsID', 'left')
print(mdf)

print("done handle_members.py")