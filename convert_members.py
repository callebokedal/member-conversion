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
def read_file(file_name):
    """
    Read and return Excel file as df
    """
    df = pd.read_excel(file_name, dtype = {'Hemtelefon': object, 'Mobiltelefon': object, 'Arbetstelefon': object})
    return df

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
    df.to_excel(file_name, index=False)
    return df

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
                #print(name)
                i_df = read_id_file(path + "/" + name)
                m_df = read_file(path + "/" + name.replace('.txt','.xls'))
                merged_df = merge_dfs(m_df, i_df, 'MedlemsID', 'left')
                save_file(path + "/" + name.replace('-excel.txt','-merged.xlsx'), merged_df)

    it.close()

def convert_members(mc_file_name, io_file_name):
    """
    Takes a My Club All members file and convert to IdrottOnline Import Excel
    """
    # My Club Dataframe
    mc_df = read_file(mc_file_name)

    io_in_df = read_file(io_file_name)

    # IO Output Dataframe
    io_out_cols = ['Prova-på','Förnamn','Alt. förnamn','Efternamn','Kön','Nationalitet','IdrottsID','Födelsedat./Personnr.','Telefon mobil','E-post kontakt','Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort','Kontaktadress - Land','Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land','Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Medlemsnr.','Medlem sedan','Medlem t.o.m.','Övrig medlemsinfo','Familj','Fam.Admin','Lägg till GruppID','Ta bort GruppID']
    io_out_df = pd.DataFrame(columns=io_out_cols)

    print(mc_df)
    print(io_in_df)
    print(io_out_df)

# Action 
convert_members('/usr/src/app/files/MyClub_all_member_export.xls','/usr/src/app/files/2020-11-08_all-io-members.xlsx')

#process_files('/usr/src/app/files')

print("done handle_members.py")