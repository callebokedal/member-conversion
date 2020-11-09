import pandas as pd
import numpy as np
import os

path = '/usr/src/app/files'

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
    Read and return Excel file as df
    """
    df = pd.read_excel(file_name, dtype = {'Hemtelefon': object, 'Mobiltelefon': object, 'Arbetstelefon': object})
    return df

id_df=None
def read_id_file(file_name):
    """
    Read file with member id and personnummer
    """
    df = pd.read_csv(file_name, header=None, names=['MedlemsID', 'Personnummer2'], dtype = {'Personnummer2': object})

    # Fix dtype problem - we don't want scientific value out
    
    #print(df)
    return df
 
# Merge full personnumer into members
def merge_dfs(df1, df2, on, dir = 'left'):
    """
    Merge dataframes based on column 'on'
    """
    merged_df = pd.merge(df1, df2, 
                     on = on,
                     how = dir,
                     validate = 'one_to_one')
    return merged_df

def save_file(file_name, df):
    """
    Save to Excel file.
    Feature: Personnummer2 is in format string, else scentific output format
    """
    ##with ExcelWriter(file_name) as writer:
    ##    df.to_excel(writer)
    # df["Personnummer2"] = df["Personnummer2"].astype('int64') # Funkar inte
    # df["Personnummer2"] = df["Personnummer2"].astype('object') # Funkar inte
    #df["Personnummer2"] = df["Personnummer2"].astype('string') # Funkar men string
    #df["Personnummer2"] = df["Personnummer2"].astype('float64') # 
    #df["Hemtelefon"] = df["Hemtelefon"].astype('string') 
    df.to_excel(file_name, index=False)
    return df

# file = path + 'files/Senior-excel.txt'

def process_files(path):
    """
    Process list fo files. Merges full personnummer with existing My Club Member files
    Expected filenames:
    - <Group>-excel.txt
    - <Group>-excel.xls
    Output:
    - <Group>-merged.xlsx
    """
    with os.scandir(path) as it:
        for entry in it:
            i_df = None
            m_df = None
            merged_df = None
            name = entry.name
            if entry.is_file() and name.endswith('-excel.txt'): 
                print(name)
                i_df = read_id_file(path + "/" + name)
                m_df = read_file(path + "/" + name.replace('.txt','.xls'))
                merged_df = merge_dfs(m_df, i_df, 'MedlemsID', 'left')
                save_file(path + "/" + name.replace('-excel.txt','-merged.xlsx'), merged_df)

    it.close()

# Action 

# Get mapping of id <-> pnr
#id_df = read_id_file(path + "/Senior-excel.txt")

# Get members from file
#members = read_file(path + "/Senior-excel.xls")

# Merge
#mdf = merge_dfs(members, id_df, 'MedlemsID', 'left')
#print(mdf['Personnummer2'])
#print(mdf['Personnummer2'].dtypes)

# Save result
#result = save_file(path + "/Senior-merged.xlsx", mdf)
#print(result['Personnummer2'])
#print(result['Personnummer2'].dtypes)

process_files('/usr/src/app/files')

print("done handle_members.py")