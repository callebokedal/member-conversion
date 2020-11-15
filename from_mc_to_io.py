import pandas as pd
import numpy as np
import os, sys
from pathlib import Path
from datetime import date
import time 
from time import strftime

from utils import convert_countrycode, convert_mc_personnummer_to_io, convert_postnr, \
    clean_pii_comments, convert_mc_groups_to_io_groups, simply_lower, concat_special_cols, \
    normalize_postort, mc_family_to_id, concat_group_id

"""
Script to export members from My Cloud and import in Idrott Online
"""

# Update to correct timezone
os.environ["TZ"] = "Europe/Stockholm"
time.tzset()

today = date.today()
date_today = today.strftime("%Y-%m-%d")
timestamp = str(strftime("%Y-%m-%d_%H.%M")) # Timestamp to use for filenames

# Remeber start time
start_time = time.time()

path = '/usr/src/app/files/' # Required base path
if len(sys.argv) < 4:
    sys.exit("Illegal input arguments. Usage: convert_members.py <exported My Club members file> <exported My Club invoices file> <exported IO members file> [<e-mail file>]")
exp_mc_members_file  = sys.argv[1]
exp_mc_invoices_file = sys.argv[2]
exp_io_members_file  = sys.argv[3] 

# Validation util
def validate_file(file_name, nr):
    if not Path(file_name).exists():
        sys.exit("Illegal file (" + str(int(nr)) + ")")

    fpath = Path(file_name).resolve()
    if not str(fpath).startswith(path):
        sys.exit("Illegal file path (" + str(int(nr)) + ")")

# Validate input
validate_file(exp_mc_members_file, 1)
validate_file(exp_mc_invoices_file, 2)
validate_file(exp_io_members_file, 3)

def save_file(file_name, df):
    """
    Save to Excel file
    """
    df.to_excel(file_name, index=False)
    return df

def stats(text):
    """
    Utility function to print stats. Easy to disable...
    """
    if True:
        print(text)


def from_mc_to_io(mc_file_name, mc_invoice_file, io_file_name):
    """
    Takes a My Club All members file and converts to IdrottOnline Import Excel
    """
    # My Club Dataframe
    mc_export_df = pd.read_excel(mc_file_name, 
        dtype = {'Hemtelefon': 'string', 'Mobiltelefon': 'string', 'Arbetstelefon': 'string'},
        converters = {'Personnummer':convert_mc_personnummer_to_io, 
            'E-post':simply_lower, 'Kontakt 1 epost':simply_lower, 
            'Postnummer':convert_postnr, 'Postort':normalize_postort}) # My Club columns
    stats("Antal medlemmar i MC: " + str(len(mc_export_df)) + " (" + Path(mc_file_name).name + ")")

    # Invoice info from My Club
    mc_invoice_df = pd.read_excel(mc_invoice_file, 
        usecols=['MedlemsID','Avgift','Summa','Summa betalt',
            'Familjemedlem 1','Familjemedlem 2','Familjemedlem 3','Familjemedlem 4','Familjemedlem 5','Familjemedlem 6'])
    stats("Antal fakturor i MC:  " + str(len(mc_invoice_df)) + " (" + Path(mc_invoice_file).name + ")")
    # Merge in invoice details
    # Added later as special column
    # TODO Only for family head and not each person
    mc_export_df = mc_export_df.merge(mc_invoice_df, on='MedlemsID', how='left', suffixes=(None,'_inv'), validate = "one_to_one")

    # Current members in IdrottOnline
    io_current_df = pd.read_excel(io_file_name, dtype = {
        'Telefon mobil': 'string', 'Telefon bostad': 'string', 'Telefon arbete': object, 'Medlemsnr.': 'string'},
        converters = {'E-post kontakt':simply_lower, 'E-post privat':simply_lower, 'E-post arbete':simply_lower}) # IO columns
    stats("Antal medlemmar i IO: " + str(len(io_current_df)) + " (" + Path(io_file_name).name + ")")

    # My Club output columns - for ref
    mc_export_df_cols = ['Förnamn',
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
    io_import_cols = ['Prova-på','Förnamn','Alt. förnamn','Efternamn','Kön','Nationalitet','IdrottsID','Födelsedat./Personnr.','Telefon mobil',
        'E-post kontakt','Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort',
        'Kontaktadress - Land','Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
        'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Medlemsnr.','Medlem sedan','Medlem t.o.m.','Övrig medlemsinfo',
        'Familj','Fam.Admin','Lägg till GruppID','Ta bort GruppID']

    # 1. Convert all MC members to IO Import format
    io_import_df = pd.DataFrame(columns=io_import_cols)
#    io_import_df['Prova-på'] = mc_export_df['']  # Not used in MC?
    io_import_df['Förnamn'] = mc_export_df['Förnamn']
#    io_import_df['Alt. förnamn'] = mc_export_df['']  # Found none in MC
    io_import_df['Efternamn'] = mc_export_df['Efternamn']
    io_import_df['Kön'] = mc_export_df['Kön (flicka/pojke)']
    io_import_df['Nationalitet'] = mc_export_df['Nationalitet'].replace('SE','Sverige')
#    io_import_df['IdrottsID'] = mc_export_df[''] 
    io_import_df['Födelsedat./Personnr.'] = mc_export_df['Personnummer'] #.astype('string').apply(convert_personnummer) 
    io_import_df['Telefon mobil'] = mc_export_df['Mobiltelefon']
    io_import_df['E-post kontakt'] = mc_export_df['E-post'] 
    io_import_df['Kontaktadress - c/o adress'] = mc_export_df['c/o']
    io_import_df['Kontaktadress - Gatuadress'] = mc_export_df['Adress']
    io_import_df['Kontaktadress - Postnummer'] = mc_export_df['Postnummer'].astype('string').apply(convert_postnr)
    io_import_df['Kontaktadress - Postort'] = mc_export_df['Postort']
    io_import_df['Kontaktadress - Land'] = mc_export_df['Land'].apply(convert_countrycode)
#    io_import_df['Arbetsadress - c/o adress'] = mc_export_df['']
#    io_import_df['Arbetsadress - Gatuadress'] = mc_export_df['']
#    io_import_df['Arbetsadress - Postnummer'] = mc_export_df['']
#    io_import_df['Arbetsadress - Postort'] = mc_export_df['']
#    io_import_df['Arbetsadress - Land'] = mc_export_df['']
    io_import_df['Telefon bostad'] = mc_export_df['Hemtelefon']
    io_import_df['Telefon arbete'] = mc_export_df['Arbetstelefon']
#    io_import_df['E-post privat'] = mc_export_df['Kontakt 1 epost']
#    io_import_df['E-post arbete'] = mc_export_df['']
#    io_import_df['Medlemsnr.'] = mc_export_df['MedlemsID'] # TODO
    io_import_df['Medlem sedan'] = mc_export_df['Datum registrerad']
    io_import_df['MC_Senast ändrad'] = mc_export_df['Senast ändrad']
#    io_import_df['Medlem t.o.m.'] = mc_export_df['']
    io_import_df['Övrig medlemsinfo'] = mc_export_df['Kommentar'].astype('string').apply(clean_pii_comments) # Special handling - not for all clubs
#   io_import_df['Familj'] = mc_export_df['Familj']
#    io_import_df['Fam.Admin'] = mc_export_df[''] 
    io_import_df['Lägg till GruppID'] = mc_export_df['Grupper'].apply(convert_mc_groups_to_io_groups) 
    # Also - add special columns as groupIDs
    io_import_df['Lägg till GruppID'] = [concat_special_cols(groups, cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb, avgift) 
        for groups, cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb, avgift
        in zip(io_import_df['Lägg till GruppID'], mc_export_df['Cirkusledarutbildning'], mc_export_df['Frisksportlöfte'], 
            mc_export_df['Hedersmedlem'], mc_export_df['Ingen tidning tack'], mc_export_df['Frisksportutbildning'], 
            mc_export_df['Trampolinutbildning'], mc_export_df['Avgift'])]
    # Also - add family info as groups
    # 2020-11-15 Disabled - since IO does not handle this according to documentation...
    if False:
        mc_export_df['Familj'] = mc_export_df['Familj'].apply(mc_family_to_id)
        io_import_df['Lägg till GruppID'] = [concat_group_id(groups, family_id) 
            for groups, family_id 
            in zip(io_import_df['Lägg till GruppID'], mc_export_df['Familj'])]

    #print("df_test: ")
    #print(io_import_df['Lägg till GruppID'])
    #print(df_test)

#    io_import_df['Ta bort GruppID'] = mc_export_df[''] # TODO

    # 2. Compare MC data with current IO data
    # Todo
    #comp_df = io_import_df[['Förnamn','Alt. förnamn','Efternamn','Födelsedat./Personnr.','Kön','Nationalitet','Telefon mobil','E-post kontakt',
    #    'Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort','Kontaktadress - Land',
    #    'Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
    #    'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Övrig medlemsinfo','Familj','Fam.Admin','Medlem sedan','Medlem t.o.m.']].compare(
    #        io_current_df[['Förnamn','Alt. förnamn','Efternamn','Födelsedat./Personnr.','Kön','Nationalitet','Telefon mobil','E-post kontakt',
    #    'Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort','Kontaktadress - Land',
    #    'Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
    #    'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Övrig medlemsinfo','Familj','Fam.Admin','Medlem sedan','Medlem t.o.m.']])

    #df1 = io_import_df[['Förnamn','Efternamn','Födelsedat./Personnr.','Kön','Medlem sedan']].copy()
    #print(df1.axes)
    #df2 = io_current_df[['Förnamn','Efternamn','Födelsedat./Personnr.','Kön','Medlem sedan']].copy()
    #print(df2.axes)
    #comp_df = df1.compare(df2)
    #save_file('/usr/src/app/files/' + date_today + '_mc-io_comparison.xlsx', comp_df)
    
    # 3. Save export
    save_file(path + timestamp + '_mc-for-io-import.xlsx', io_import_df)
    stats("Sparat: " + path + timestamp + '_mc-for-io-import.xlsx')

    # 4. Merge test
    mc_io_merged_df = pd.merge(io_current_df, io_import_df, 
                     on = 'Födelsedat./Personnr.',
                     how = 'outer',
                     suffixes = ('_io','_mc'),
                     indicator = True)
    mc_io_merged_file = path + timestamp + '_mc-io-merged.xlsx'
    stats("Antal sammanfogade:   " + str(len(mc_io_merged_df)) + " (" + Path(mc_io_merged_file).name + ")")
    #stats("Finns i båda: ") + mc_io_merged_df.groupby("_merge"))
    #merge_grouped = mc_io_merged_df.groupby(['_merge'])
    #print(mc_io_merged_df.filter(items=['_merge']))
    #stats(merge_grouped._merge.count())
    # df[df['var1'].str.len()>3]
    stats("Enbart i MC: " + str(len(mc_io_merged_df.loc[mc_io_merged_df['_merge'] == 'right_only' ])))
    stats("Enbart i IO: " + str(len(mc_io_merged_df.loc[mc_io_merged_df['_merge'] == 'left_only' ])))
    stats("I både MC och IO: " + str(len(mc_io_merged_df.loc[mc_io_merged_df['_merge'] == 'both' ])))
    stats("Antal med endast födelsedatum: " + str(len(mc_io_merged_df[mc_io_merged_df['Födelsedat./Personnr.'].str.len() == 8])))
    stats("Antal med fullt personnummer:  " + str(len(mc_io_merged_df[mc_io_merged_df['Födelsedat./Personnr.'].str.len() > 8])))
    save_file(mc_io_merged_file, mc_io_merged_df)
    stats("Sparat: " + mc_io_merged_file)

    #print(mc_export_df)
    #print(io_current_df)
    #print(io_import_df)


# Action 
# convert_members(mc_file_name, io_file_name):
print(" Start ".center(80, "-"))
#from_mc_to_io('/usr/src/app/files/2020-11-14_MyClub_all_member_export.xls',
#    '/usr/src/app/files/2020-11-13_MyClub_invoice_export.xls',
#    '/usr/src/app/files/2020-11-11_all-io-members2.xlsx')
from_mc_to_io(exp_mc_members_file, exp_mc_invoices_file, exp_io_members_file)

#process_files('/usr/src/app/files')

print ("Tidsåtgång: " + str(round((time.time() - start_time),1)) + " s")
print((" Klart (" + strftime("%Y-%m-%d %H:%M") + ") ").center(80, "-"))
