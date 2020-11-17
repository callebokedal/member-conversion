import pandas as pd
import numpy as np
import os, sys
from pathlib import Path
from datetime import date
import time 
from time import strftime

from utils import convert_countrycode, convert_mc_personnummer_to_io, convert_postnr, \
    clean_pii_comments, convert_mc_groups_to_io_groups, normalize_email, concat_special_cols, \
    normalize_postort, mc_family_to_id, concat_group_id, add_comment_info

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
if len(sys.argv) == 5:
    cg_email_file = sys.argv[4]

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
if len(sys.argv) == 5:
    validate_file(cg_email_file, 4)


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
            'E-post':normalize_email, 'Kontakt 1 epost':normalize_email, 
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

    # My Club output columns - for ref
    mc_export_df_cols = ['Förnamn','Efternamn','För- och efternamn','Personnummer','Födelsedatum (YYYY-MM-DD)','LMA/Samordningsnummer',
        'Ålder','Kön (flicka/pojke)','Kön (W/M)','Nationalitet','c/o','Adress','Postnummer','Postort','Land','Hemtelefon','Mobiltelefon',
        'Arbetstelefon','E-post','Medlemstyp','MedlemsID','Ständig medlem','Datum registrerad','Senast ändrad','Autogiromedgivande',
        'Kommentar','Aktiviteter totalt','Aktiviteter år 2020','Aktiviteter år 2019','Aktiviteter år 2018','Aktiviteter år 2017',
        'Aktiviteter år 2016','Grupper','Alla grupper','Roller','Gruppkategorier','Föreningsnamn','Familj','Allergier',
        'Cirkusledarutbildning','Cirkusskoleledare','Friluftslivsledarutbildning','Frisksportlöfte','Har frisksportmail','Hedersmedlem',
        'Ingen tidning tack','Klätterledarutbildning','Frisksportutbildning','Trampolinutbildning','Utmärkelse','Belastningsregisterutdrag OK',
        'Kontakt 1 förnamn','Kontakt 1 efternamn','Kontakt 1 hemtelefon','Kontakt 1 mobiltelefon','Kontakt 1 arbetstelefon','Kontakt 1 epost']

    # IO Import columns - for ref
    io_import_cols = ['Prova-på','Förnamn','Alt. förnamn','Efternamn','Kön','Nationalitet','IdrottsID','Födelsedat./Personnr.','Telefon mobil',
        'E-post kontakt','Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort',
        'Kontaktadress - Land','Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
        'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Medlemsnr.','Medlem sedan','Medlem t.o.m.','Övrig medlemsinfo',
        'Familj','Fam.Admin','Lägg till GruppID','Ta bort GruppID']

    # 1. Convert all MC members to IO Import format
    mc_in_io_format_df = pd.DataFrame(columns=io_import_cols)
#    mc_in_io_format_df['Prova-på'] = mc_export_df['']  # Not used in MC?
    mc_in_io_format_df['Förnamn'] = mc_export_df['Förnamn']
#    mc_in_io_format_df['Alt. förnamn'] = mc_export_df['']  # Found none in MC
    mc_in_io_format_df['Efternamn'] = mc_export_df['Efternamn']
    mc_in_io_format_df['Kön'] = mc_export_df['Kön (flicka/pojke)']
    mc_in_io_format_df['Nationalitet'] = mc_export_df['Nationalitet'].replace('SE','Sverige')
#    mc_in_io_format_df['IdrottsID'] = mc_export_df[''] 
    mc_in_io_format_df['Födelsedat./Personnr.'] = mc_export_df['Personnummer'] #.astype('string').apply(convert_personnummer) 
    mc_in_io_format_df['Telefon mobil'] = mc_export_df['Mobiltelefon']
    mc_in_io_format_df['E-post kontakt'] = mc_export_df['E-post'] 
    mc_in_io_format_df['Kontaktadress - c/o adress'] = mc_export_df['c/o']
    mc_in_io_format_df['Kontaktadress - Gatuadress'] = mc_export_df['Adress']
    mc_in_io_format_df['Kontaktadress - Postnummer'] = mc_export_df['Postnummer'].astype('string').apply(convert_postnr)
    mc_in_io_format_df['Kontaktadress - Postort'] = mc_export_df['Postort']
    mc_in_io_format_df['Kontaktadress - Land'] = mc_export_df['Land'].apply(convert_countrycode)
#    mc_in_io_format_df['Arbetsadress - c/o adress'] = mc_export_df['']
#    mc_in_io_format_df['Arbetsadress - Gatuadress'] = mc_export_df['']
#    mc_in_io_format_df['Arbetsadress - Postnummer'] = mc_export_df['']
#    mc_in_io_format_df['Arbetsadress - Postort'] = mc_export_df['']
#    mc_in_io_format_df['Arbetsadress - Land'] = mc_export_df['']
    mc_in_io_format_df['Telefon bostad'] = mc_export_df['Hemtelefon']
    mc_in_io_format_df['Telefon arbete'] = mc_export_df['Arbetstelefon']
#    mc_in_io_format_df['E-post privat'] = mc_export_df['Kontakt 1 epost']
#    mc_in_io_format_df['E-post arbete'] = mc_export_df['']
    
    mc_in_io_format_df['Medlem sedan'] = mc_export_df['Datum registrerad']
    mc_in_io_format_df['MC_Senast ändrad'] = mc_export_df['Senast ändrad']
#    mc_in_io_format_df['Medlem t.o.m.'] = mc_export_df['']
    mc_in_io_format_df['Övrig medlemsinfo'] = mc_export_df['Kommentar'].astype('string').apply(clean_pii_comments) # Special handling - not for all clubs
    # Add special info to 'Övrig medlemsinfo' - MC MedlemsInfo and execution time
    mc_in_io_format_df['Övrig medlemsinfo'] = [add_comment_info(comment, member_id, timestamp)
        for comment, member_id
        in zip(mc_in_io_format_df['Övrig medlemsinfo'] , mc_export_df['MedlemsID'])]

#   mc_in_io_format_df['Familj'] = mc_export_df['Familj']
#   mc_in_io_format_df['Fam.Admin'] = mc_export_df[''] 
    mc_in_io_format_df['Lägg till GruppID'] = mc_export_df['Grupper'].apply(convert_mc_groups_to_io_groups) 
    # Also - add special columns as groupIDs
    mc_in_io_format_df['Lägg till GruppID'] = [concat_special_cols(groups, cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb, avgift) 
        for groups, cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb, avgift
        in zip(mc_in_io_format_df['Lägg till GruppID'], mc_export_df['Cirkusledarutbildning'], mc_export_df['Frisksportlöfte'], 
            mc_export_df['Hedersmedlem'], mc_export_df['Ingen tidning tack'], mc_export_df['Frisksportutbildning'], 
            mc_export_df['Trampolinutbildning'], mc_export_df['Avgift'])]
    # Also - add family info as groups
    # 2020-11-15 Disabled - since IO does not handle this according to documentation...
    if False:
        mc_export_df['Familj'] = mc_export_df['Familj'].apply(mc_family_to_id)
        mc_in_io_format_df['Lägg till GruppID'] = [concat_group_id(groups, family_id) 
            for groups, family_id 
            in zip(mc_in_io_format_df['Lägg till GruppID'], mc_export_df['Familj'])]

#    mc_in_io_format_df['Ta bort GruppID'] = mc_export_df[''] # TODO

    # 2. Compare MC data with current IO data
    # Todo
    #comp_df = mc_in_io_format_df[['Förnamn','Alt. förnamn','Efternamn','Födelsedat./Personnr.','Kön','Nationalitet','Telefon mobil','E-post kontakt',
    #    'Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort','Kontaktadress - Land',
    #    'Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
    #    'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Övrig medlemsinfo','Familj','Fam.Admin','Medlem sedan','Medlem t.o.m.']].compare(
    #        io_current_df[['Förnamn','Alt. förnamn','Efternamn','Födelsedat./Personnr.','Kön','Nationalitet','Telefon mobil','E-post kontakt',
    #    'Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort','Kontaktadress - Land',
    #    'Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
    #    'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Övrig medlemsinfo','Familj','Fam.Admin','Medlem sedan','Medlem t.o.m.']])

    #df1 = mc_in_io_format_df[['Förnamn','Efternamn','Födelsedat./Personnr.','Kön','Medlem sedan']].copy()
    #print(df1.axes)
    #df2 = io_current_df[['Förnamn','Efternamn','Födelsedat./Personnr.','Kön','Medlem sedan']].copy()
    #print(df2.axes)
    #comp_df = df1.compare(df2)
    #save_file('/usr/src/app/files/' + date_today + '_mc-io_comparison.xlsx', comp_df)
    
    # 3. Save file with all members from MC in correct format (still need to cross check with IO!)
    save_file(path + timestamp + '_all_mc_in_io_format.xlsx', mc_in_io_format_df)
    stats("Sparat: " + path + timestamp + '_all_mc_in_io_format.xlsx')

    # 4. Merge
    
    # Current members in IdrottOnline
    io_current_df = pd.read_excel(io_file_name, 
        usecols=['Födelsedat./Personnr.'],
        dtype = {
        'Telefon mobil': 'string', 'Telefon bostad': 'string', 'Telefon arbete': object, 'Medlemsnr.': 'string'},
        converters = {'E-post kontakt':normalize_email, 'E-post privat':normalize_email, 'E-post arbete':normalize_email}) # IO columns
    stats("Antal medlemmar i IO: " + str(len(io_current_df)) + " (" + Path(io_file_name).name + ")")

    # For import
    # TODO Remove this later!
    # This is already handled by how = 'left' below - so we can assign 'Medlemsnr.' without risking overwrite
    # mc_in_io_format_df['Medlemsnr.'] = mc_export_df['MedlemsID'] 
    # TODO Remove this later!
    # Filter - only non-existing in IO (solved by how = 'left')
    # Label: 'Export-1' - For members updated '2020-11-16_01.20'
    #for_io_import_df = pd.merge(mc_in_io_format_df, io_current_df,
    #                 on = 'Födelsedat./Personnr.',
    #                 how = 'left',
    #                 suffixes = ('_mc','_io'),
    #                 indicator = True)

    # Label: 'Export-2' - Current members in IO updated in IO with new data from MC
    for_io_import_df = pd.merge(mc_in_io_format_df, io_current_df,
                     on = 'Födelsedat./Personnr.',
                     how = 'right',
                     suffixes = ('_mc','_io'),
                     indicator = True)

    # Filter - only with full personnummer
    for_io_import_df = for_io_import_df[for_io_import_df['Födelsedat./Personnr.'].str.len() > 8]

    # Filter - only MC
    for_io_import_df = for_io_import_df[for_io_import_df['_merge'] == "right_only" ]

    for_io_import_file = path + timestamp + '_for_io_import.xlsx'
    stats("Antal för import till IO:   " + str(len(for_io_import_df)) + " (" + Path(for_io_import_file).name + ")")
    #stats("Finns i båda: ") + for_io_import_df.groupby("_merge"))
    #merge_grouped = for_io_import_df.groupby(['_merge'])
    #print(for_io_import_df.filter(items=['_merge']))
    #stats(merge_grouped._merge.count())
    # df[df['var1'].str.len()>3]
    #stats("Enbart i MC: " + str(len(for_io_import_df.loc[for_io_import_df['_merge'] == 'right_only' ])))
    stats("Enbart i MC: " + str(len(for_io_import_df.loc[for_io_import_df['_merge'] == 'left_only' ])))
    stats("I både MC och IO: " + str(len(for_io_import_df.loc[for_io_import_df['_merge'] == 'both' ])))
    stats("Antal med endast födelsedatum: " + str(len(for_io_import_df[for_io_import_df['Födelsedat./Personnr.'].str.len() == 8])))
    stats("Antal med fullt personnummer:  " + str(len(for_io_import_df[for_io_import_df['Födelsedat./Personnr.'].str.len() > 8])))
    save_file(for_io_import_file, for_io_import_df)
    stats("Sparat: " + for_io_import_file)

def update_io_email_from_mc(io_file_name, cg_email_file):
    """
    Create import file where existing IO members get newer e-mails from MC and CG file - based on update date
    """
    # IO df
    io_read_df = pd.read_excel(io_file_name, 
        usecols=['Förnamn', 'Efternamn', 'Födelsedat./Personnr.','E-post kontakt','E-post privat'],
        dtype = {'Hemtelefon': 'string', 'Mobiltelefon': 'string', 'Arbetstelefon': 'string'},
        converters = {'E-post kontakt':normalize_email, 'E-post privat':normalize_email}) # IO Columns
    stats("Antal inlästa från IO: {} ({})".format(str(len(io_read_df)), Path(io_file_name).name))

    # CG e-mail file - file with updated e-mails
    cg_read_df = pd.read_excel(cg_email_file, 
        usecols=['Förnamn', 'Efternamn', 'Personnummer','E-post'],
        converters = {'Personnummer':convert_mc_personnummer_to_io, 'E-post':normalize_email}) # CG Columns
    stats("Antal inlästa från CG: {} ({})".format(str(len(cg_read_df)), Path(cg_email_file).name))

    matches_df = pd.merge(io_read_df, cg_read_df,
                     left_on = 'Födelsedat./Personnr.',
                     right_on = 'Personnummer',
                     how = 'right',
                     suffixes = ('_io','_cg'),
                     indicator = True)
    print(matches_df)


# Action 
print(" Start ".center(80, "-"))
# Export-1 - Move non-existing members in IO from MC to IO
#from_mc_to_io(exp_mc_members_file, exp_mc_invoices_file, exp_io_members_file)

# Export-2 - Update IO members in IO with newer e-mails from MC
update_io_email_from_mc(exp_io_members_file, cg_email_file)

print ("Tidsåtgång: " + str(round((time.time() - start_time),1)) + " s")
print((" Klart (" + strftime("%Y-%m-%d %H:%M") + ") ").center(80, "-"))
