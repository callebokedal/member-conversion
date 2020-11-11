import pandas as pd
import numpy as np
import os

from utils import convert_countrycode, convert_personnummer, convert_postnr, clean_pii_comments

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
    df = pd.read_excel(file_name, dtype = {
        'Hemtelefon': object, 'Mobiltelefon': object, 'Arbetstelefon': object, # My Club columns
        'Telefon mobil': object, 'Telefon bostad': object, 'Telefon arbete': object, 'Telefon mobil': object, 'Medlemsnr.': object}) # IO columns
    return df

def read_id_file(file_name):
    """
    Read file with member id and personnummer
    """
    df = pd.read_csv(file_name, header=None, names=['MedlemsID', 'Personnummer2'], dtype = {'Personnummer2': object})    
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
    Save to Excel file
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

def from_mc_to_io(mc_file_name, io_file_name):
    """
    Takes a My Club All members file and converts to IdrottOnline Import Excel
    """
    # My Club Dataframe
    mc_df = read_file(mc_file_name)
    # Normalize fields
    mc_df['E-post'] = mc_df['E-post'].map(lambda x: x if type(x)!=str else x.lower()) # .astype('string').apply(lambda x:x.lower())
    mc_df['Kontakt 1 epost'] = mc_df['Kontakt 1 epost'].map(lambda x: x if type(x)!=str else x.lower())
    mc_df['Postort'] = mc_df['Postort'].map(lambda x: x if type(x)!=str else x.title())
    mc_df['Postnummer'] = mc_df['Postnummer'].apply(convert_postnr)

    io_in_df = read_file(io_file_name)
    # Normalize fields
    io_in_df['E-post kontakt'] = io_in_df['E-post kontakt'].map(lambda x: x if type(x)!=str else x.lower())
    io_in_df['E-post privat'] = io_in_df['E-post privat'].map(lambda x: x if type(x)!=str else x.lower())
    io_in_df['E-post arbete'] = io_in_df['E-post arbete'].map(lambda x: x if type(x)!=str else x.lower())

    # My Club output columns - for ref
    # Note! It seems like My Club uses different names on import vs export!
    # According to export:          'Kontakt 1 förnamn'
    # According to import template: 'Förnamn kontaktperson1'
    mc_df_cols = ['Förnamn',
        'Efternamn',
        'För- och efternamn',
        'Personnummer',
        'Födelsedatum (YYYY-MM-DD)',
        'LMA/Samordningsnummer',
        'Ålder',
        'Kön (flicka/pojke)',
        'Kön (W/M)',
        'Nationalitet',
        'c/o',
        'Adress',
        'Postnummer',
        'Postort',
        'Land',
        'Hemtelefon',
        'Mobiltelefon',
        'Arbetstelefon',
        'E-post',
        'Medlemstyp',
        'MedlemsID',
        'Ständig medlem',
        'Datum registrerad',
        'Senast ändrad',
        'Autogiromedgivande',
        'Kommentar',
        'Aktiviteter totalt',
        'Aktiviteter år 2020',
        'Aktiviteter år 2019',
        'Aktiviteter år 2018',
        'Aktiviteter år 2017',
        'Aktiviteter år 2016',
        'Grupper',
        'Alla grupper',
        'Roller',
        'Gruppkategorier',
        'Föreningsnamn',
        'Familj',
        'Allergier',
        'Cirkusledarutbildning',
        'Cirkusskoleledare',
        'Friluftslivsledarutbildning',
        'Frisksportlöfte',
        'Har frisksportmail',
        'Hedersmedlem',
        'Ingen tidning tack',
        'Klätterledarutbildning',
        'Frisksportutbildning',
        'Trampolinutbildning',
        'Utmärkelse',
        'Belastningsregisterutdrag OK',
        'Kontakt 1 förnamn',
        'Kontakt 1 efternamn',
        'Kontakt 1 hemtelefon',
        'Kontakt 1 mobiltelefon',
        'Kontakt 1 arbetstelefon',
        'Kontakt 1 epost']

    # IO Import columns - for ref
    io_out_cols = ['Prova-på','Förnamn','Alt. förnamn','Efternamn','Kön','Nationalitet','IdrottsID','Födelsedat./Personnr.','Telefon mobil',
        'E-post kontakt','Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort',
        'Kontaktadress - Land','Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
        'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Medlemsnr.','Medlem sedan','Medlem t.o.m.','Övrig medlemsinfo',
        'Familj','Fam.Admin','Lägg till GruppID','Ta bort GruppID']

    # 1. Convert all MC members to IO Import format
    # TODO: IO Export and IO Import labels differ... ex: "Folkbokföring - Gatuadress" vs "Kontaktadress - Gatuadress" ???
    io_out_df = pd.DataFrame(columns=io_out_cols)
#    io_out_df['Prova-på'] = mc_df['']  # Not used in MC?
    io_out_df['Förnamn'] = mc_df['Förnamn']
#    io_out_df['Alt. förnamn'] = mc_df['']  # Found none in MC
    io_out_df['Efternamn'] = mc_df['Efternamn']
    io_out_df['Kön'] = mc_df['Kön (flicka/pojke)']
    io_out_df['Nationalitet'] = mc_df['Nationalitet'].replace('SE','Sverige')
#    io_out_df['IdrottsID'] = mc_df[''] 
    io_out_df['Födelsedat./Personnr.'] = mc_df['Personnummer'].astype('string').apply(convert_personnummer) 
    io_out_df['Telefon mobil'] = mc_df['Mobiltelefon']
    io_out_df['E-post kontakt'] = mc_df['E-post'] 
    io_out_df['Kontaktadress - c/o adress'] = mc_df['c/o']
    io_out_df['Kontaktadress - Gatuadress'] = mc_df['Adress']
    io_out_df['Kontaktadress - Postnummer'] = mc_df['Postnummer'].astype('string').apply(convert_postnr)
    io_out_df['Kontaktadress - Postort'] = mc_df['Postort']
    io_out_df['Kontaktadress - Land'] = mc_df['Land'].apply(convert_countrycode)
#    io_out_df['Arbetsadress - c/o adress'] = mc_df['']
#    io_out_df['Arbetsadress - Gatuadress'] = mc_df['']
#    io_out_df['Arbetsadress - Postnummer'] = mc_df['']
#    io_out_df['Arbetsadress - Postort'] = mc_df['']
#    io_out_df['Arbetsadress - Land'] = mc_df['']
    io_out_df['Telefon bostad'] = mc_df['Hemtelefon']
    io_out_df['Telefon arbete'] = mc_df['Arbetstelefon']
#    io_out_df['E-post privat'] = mc_df['Kontakt 1 epost']
#    io_out_df['E-post arbete'] = mc_df['']
#    io_out_df['Medlemsnr.'] = mc_df['']
    io_out_df['Medlem sedan'] = mc_df['Datum registrerad']
    io_out_df['MC_Senast ändrad'] = mc_df['Datum registrerad']
#    io_out_df['Medlem t.o.m.'] = mc_df['']
    io_out_df['Övrig medlemsinfo'] = mc_df['Kommentar'].astype('string').apply(clean_pii_comments) # Special handling - not for all clubs
    io_out_df['Familj'] = mc_df['Familj']
    io_out_df['Fam.Admin'] = mc_df[''] 
#    io_out_df['Lägg till GruppID'] = mc_df[''] # TODO
#    io_out_df['Ta bort GruppID'] = mc_df[''] # TODO

    # 2. Compare MC data with current IO data
    # Todo

    # 3. Save export
    # TODO: Still fields left to work with
    save_file('/usr/src/app/files/mc-converted-for-import.xlsx', io_out_df)

    # 4. Merge test
    # TODO: Just testing
    mc_io_merged_df = pd.merge(io_in_df, io_out_df, 
                     on = 'Födelsedat./Personnr.',
                     how = 'outer',
                     suffixes = ('_io','_mc'),
                     indicator = True)

    save_file('/usr/src/app/files/mc-conv-vs-io-export.xlsx', mc_io_merged_df)

    #print(mc_df)
    #print(io_in_df)
    #print(io_out_df)


def from_io_to_mc(io_file_name, mc_file_name):
    """
    Takes a IdrottOnline file and converts into a My Club Import Excel file
    """
    """
    My Club import columns
    'Förnamn',
    'Efternamn',
    'Adress',
    'Postnummer',
    'Postadress',
    'Personnummer',
    'Hemtelefon medlem',
    'Hemtelefon kontaktperson1',
    'Hemtelefon kontaktperson2',
    'Mobiltelefon medlem',
    'Mobiltelefon kontaktperson1',
    'Mobiltelefon kontaktperson2',
    'Epost medlem',
    'Epost kontaktperson1',
    'Epost kontaktperson2',
    'Lag',
    'Medlemstyp',
    'Kön',
    'Förnamn kontaktperson1',
    'Efternamn kontaktperson1',
    'Förnamn kontaktperson2',
    'Efternamn kontaktperson2',
    'Extra 1',
    'Extra 2',
    'Extra 3',
    'Extra 4',
    'Extra 5',
    """
    pass

# Action 
# convert_members(mc_file_name, io_file_name):
from_mc_to_io('/usr/src/app/files/2020-11-11_MyClub_all_member_export.xls','/usr/src/app/files/2020-11-11_all-io-members2.xlsx')

#process_files('/usr/src/app/files')

print("done handle_members.py")