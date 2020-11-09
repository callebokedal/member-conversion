import pandas as pd
import os

path = '/usr/src/app'

def list_files(path):
    """
    List files in path
    """
    files = os.listdir(path)
    for f in files:
        print(f)

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
    df = pd.read_csv(file_name, header=None, names=['MedlemsID2', 'Personnummer2'])
    #print(df)
    return df

#list_files(path)
#list_all_files(path)

# Get mapping of id <-> pnr
id_df = read_id_file("./files/Senior-excel.txt")
# print(id_df)
#print(id_df.dtypes)
# MedlemsID       int64
# Personnummer    int64

members = read_file("./files/Senior-excel.xls")
#print(members.dtypes)

def merge_data(mem_df, id_df):
    """
    Obsolete! Use merge_dfs instead
    Merges dataframe of members with data from id dataframe
    """
    mem_df['FullPNr'] = '' # pd.NA
    print(mem_df)

    for row in mem_df.loc[:, ['MedlemsID', 'Personnummer', 'FullPNr', 'Uppdaterad', 'Förnamn']].itertuples():
        print(row)
        # print(row.MedlemsID)
        #print(mem_df['MedlemsID'] == row.MedlemsID)

        # df.loc[['viper', 'sidewinder'], ['shield']] = 50
        #print(row.Personnummer)
        mem_df.at[row.Index,'FullPNr'] = 'test'

    print(mem_df)
        
def merge_dfs(df1, df2, left_name, right_name, dir = 'left'):
    """
    Merge dataframes based on 'MedlemsID'
    """
    merged_df = pd.merge(df1, df2, 
                     left_on = left_name, 
                     right_on = right_name, 
                     how = dir)
    return merged_df


#merge_data(members, id_df)

mdf = merge_dfs(members, id_df, 'MedlemsID','MedlemsID2', 'left')
print(mdf)


print("done test.py")