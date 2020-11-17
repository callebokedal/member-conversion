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

# Validation util
def validate_file(file_name, nr):
    if not Path(file_name).exists():
        sys.exit("Illegal file (" + str(int(nr)) + ")")

    fpath = Path(file_name).resolve()
    if not str(fpath).startswith(path):
        sys.exit("Illegal file path (" + str(int(nr)) + ")")

path = '/usr/src/app/files/' # Required base path
#if len(sys.argv) < 4:
#    sys.exit("Illegal input arguments. Usage: convert_members.py <exported My Club members file> <exported My Club invoices file> <exported IO members file> [<e-mail file>]")
if len(sys.argv) > 1:
    exp_mc_members_file  = sys.argv[1]
    validate_file(exp_mc_members_file, 1)

if len(sys.argv) > 2:
    exp_mc_invoices_file = sys.argv[2]
    validate_file(exp_mc_invoices_file, 2)

if len(sys.argv) > 3:
    exp_io_members_file  = sys.argv[3] 
    validate_file(exp_io_members_file, 3)

if len(sys.argv) > 4:
    cg_email_file = sys.argv[4]
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
    io_read_cols = ['Förnamn','Alt. förnamn','Efternamn','Kön','Nationalitet','IdrottsID','Födelsedat./Personnr.','Telefon mobil',
        'E-post kontakt','Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort',
        'Kontaktadress - Land','Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
        'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Medlemsnr.','Medlem sedan','Medlem t.o.m.','Övrig medlemsinfo',
        'Familj','Fam.Admin']
    io_read_df = pd.read_excel(io_file_name, 
        usecols= io_read_cols,
        dtype = {'Telefon mobil': 'string', 'Telefon bostad': 'string', 'Telefon arbete': 'string', 'Hemtelefon': 'string', 
            'Medlemsnr.': 'string', 'Mobiltelefon': 'string', 'Arbetstelefon': 'string', 'Övrig medlemsinfo': 'string'},
        converters = {'E-post kontakt':normalize_email, 'E-post privat':normalize_email,
            'Personnummer':convert_mc_personnummer_to_io, 
            'Kontakt 1 epost':normalize_email, 
            'Postnummer':convert_postnr, 'Postort':normalize_postort}) # IO Columns
    stats("Antal inlästa från IO: {} ({})".format(str(len(io_read_df)), Path(io_file_name).name))

    # CG e-mail file - file with updated e-mails (partial)
    cg_read_df = pd.read_excel(cg_email_file, 
        usecols=['Förnamn', 'Efternamn', 'Personnummer','E-post'],
        converters = {'Personnummer':convert_mc_personnummer_to_io, 'E-post':normalize_email}) # CG Columns
    stats("Antal inlästa från CG: {} ({})".format(str(len(cg_read_df)), Path(cg_email_file).name))

    # Match inner on Personnummer = only exact matches

    # 1. Convert all MC members to IO Import format
    io_import_cols = ['Förnamn','Alt. förnamn','Efternamn','Kön','Nationalitet','IdrottsID','Födelsedat./Personnr.','Telefon mobil',
        'E-post kontakt','Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort',
        'Kontaktadress - Land','Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
        'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Medlemsnr.','Medlem sedan','Medlem t.o.m.','Övrig medlemsinfo',
        'Familj','Fam.Admin']
    matches_df = pd.DataFrame(columns=io_import_cols)
    matches_df = pd.merge(io_read_df, cg_read_df,
                     left_on = 'Födelsedat./Personnr.',
                     right_on = 'Personnummer',
                     how = 'inner',
                     suffixes = ('','_cg'))
    stats("Antal med matchande personnummer: {}".format(str(len(matches_df))))
    # Add missing, neccessary for import, columns - as nan
    matches_df[['Prova-på','Ta bort GruppID']] = np.nan

    # Only match on full personnummer - not safe to use birthdate
    matches_df = matches_df[matches_df['Personnummer'].str.len() == 13]
    stats("Antal med matchande (fullständiga) personnummer: {}".format(str(len(matches_df))))

    # Test for matching e-mail or not
    matches_df['Update e-mail?'] = np.where(matches_df['E-post'] == matches_df['E-post kontakt'], False, True)

    # Keep only rows with newer e-mail
    matches_df = matches_df[matches_df['Update e-mail?'] == True]
    stats("Antal med nya e-poster: {}".format(str(len(matches_df))))

    # Save old e-mail to comment
    matches_df['Övrig medlemsinfo'] = [add_email_to_comment(comment, old_email, date_today)
        for comment, old_email
        in zip(matches_df['Övrig medlemsinfo'] , matches_df['E-post kontakt'])]

    # Update e-mail
    matches_df['E-post kontakt'] = matches_df['E-post']

    # Add specific group for these posts
    matches_df['Lägg till GruppID'] = '580125' # EpostUppdaterad

    # Keep only columns to import
    #matches_df = matches_df[['Förnamn', 'Efternamn', 'Födelsedat./Personnr.','E-post kontakt','E-post privat','Övrig medlemsinfo','Lägg till GruppID']]
    matches_df = matches_df[['Prova-på','Förnamn','Alt. förnamn','Efternamn','Kön','Nationalitet','IdrottsID','Födelsedat./Personnr.','Telefon mobil',
        'E-post kontakt','Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort',
        'Kontaktadress - Land','Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
        'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Medlemsnr.','Medlem sedan','Medlem t.o.m.','Övrig medlemsinfo',
        'Familj','Fam.Admin','Lägg till GruppID','Ta bort GruppID']]

    io_email_filename = path + date_today + '_io_e-mail_update.xlsx'
    save_file(io_email_filename, matches_df)
    stats("Antal att uppdatera i IO: {} ({})".format(str(len(matches_df)), Path(io_email_filename).name))

def add_email_to_comment(comment, old_email, timestamp):
    """
    Append comment field with old email
    """
    if pd.isna(old_email):
        return comment
    end = "[[Old: {}]][[Uppdaterad: {}]]".format(old_email, timestamp)
    if pd.isna(comment):
        comment = end
    else:
        comment = "{} {}".format(comment, end)
    return comment

def compare_email(email1, email2):
    """
    Compare e-mails. Return 'same' or 'differ'
    """
    return 'same' if email1 == email2 else 'differ'

def sync_groups_from_mc_to_io(mc_file_name, io_file_name):
    """
    Sync groupes between MC and IO
    """
    # Get data from latest MC export
    mc_read_df = pd.read_excel(mc_file_name, 
        dtype = {'Telefon mobil': 'string', 'Telefon bostad': 'string', 'Telefon arbete': 'string', 'Hemtelefon': 'string', 
            'MedlemsID': 'string', 'Mobiltelefon': 'string', 'Arbetstelefon': 'string', 'Övrig medlemsinfo': 'string'},
        converters = {'E-post kontakt':normalize_email, 'E-post privat':normalize_email,
            'Personnummer':convert_mc_personnummer_to_io, 
            'Kontakt 1 epost':normalize_email, 
            'Postnummer':convert_postnr, 'Postort':normalize_postort}) # MC Columns
    stats("Antal inlästa från MC: {} ({})".format(str(len(mc_read_df)), Path(mc_file_name).name))

    # Get data from latest IO export
    io_read_df = pd.read_excel(io_file_name, 
        #usecols= io_read_cols,
        dtype = {'Telefon mobil': 'string', 'Telefon bostad': 'string', 'Telefon arbete': 'string', 'Hemtelefon': 'string', 
            'Medlemsnr.': 'string', 'Mobiltelefon': 'string', 'Arbetstelefon': 'string', 'Övrig medlemsinfo': 'string'},
        converters = {'E-post kontakt':normalize_email, 'E-post privat':normalize_email,
            'Personnummer':convert_mc_personnummer_to_io, 
            'Kontakt 1 epost':normalize_email, 
            'Postnummer':convert_postnr, 
            'Kontaktadress - Postort':normalize_postort,
            'Postort':normalize_postort}) # IO Columns
    # print(io_read_df.columns)
    stats("Antal inlästa från IO: {} ({})".format(str(len(io_read_df)), Path(io_file_name).name))

    merged_df = pd.merge(mc_read_df, io_read_df,
        left_on = 'Personnummer',
        right_on = 'Födelsedat./Personnr.',
        how = 'inner',
        suffixes = ('_mc',''))
    stats("Antal lika (på personnummer): {}".format(str(len(merged_df))))

    # Filter away members with incomplete 'personnummer'
    merged_df = merged_df[merged_df['Personnummer'].str.len() == 13]
    stats("Antal med fullständiga personnummer: {}".format(str(len(merged_df))))

    # Filter away those originating from MC (= have group "MC_Import")
    merged_df = merged_df[merged_df['Grupp/Lag/Arbetsrum/Familj'].str.contains('MC_Import', na="") != True]
    stats("Antal utan MC-grupper i IO: {}".format(str(len(merged_df))))

    # Add missing, neccessary for import, columns - as nan
    merged_df[['Prova-på', 'Ta bort GruppID']] = np.nan

    # Convert MC groups to IO GroupID's
    merged_df['Lägg till GruppID'] = merged_df['Grupper'].apply(convert_mc_groups_to_io_groups) 

    # Add special group 'MC_GruppViaMC'
    # We know that all groups are non-empty, we can just add a the end
    merged_df['Lägg till GruppID'] = merged_df['Lägg till GruppID'].apply(lambda x : x + ', 580242')

    # Retain columns to be used for import only
    export_cols = ['Prova-på', 'Förnamn', 'Alt. förnamn', 'Efternamn', 'Kön', 'Nationalitet', 'IdrottsID', 
        'Födelsedat./Personnr.', 'Telefon mobil', 'E-post kontakt', 'Kontaktadress - c/o adress', 'Kontaktadress - Gatuadress', 
        'Kontaktadress - Postnummer', 'Kontaktadress - Postort', 'Kontaktadress - Land', 'Arbetsadress - c/o adress', 
        'Arbetsadress - Gatuadress', 'Arbetsadress - Postnummer', 'Arbetsadress - Postort', 'Arbetsadress - Land', 'Telefon bostad', 
        'Telefon arbete', 'E-post privat', 'E-post arbete', 'Medlemsnr.', 'Medlem sedan', 'Medlem t.o.m.', 'Övrig medlemsinfo', 
        'Familj', 'Fam.Admin', 'Lägg till GruppID', 'Ta bort GruppID']
    merged_df = merged_df[export_cols]

    # sync_groups_filename = path + date_today + '_sync_groups_update.xlsx'
    sync_groups_filename = path + timestamp + '_sync_groups_update.xlsx'
    save_file(sync_groups_filename, merged_df)
    stats("Antal att uppdatera i IO: {} ({})".format(str(len(merged_df)), Path(sync_groups_filename).name))

def check_status(mc_file_name, io_file_name):
    """
    Check status between MC and IO
    """
    # Get data from latest MC export
    mc_read_df = pd.read_excel(mc_file_name, 
        dtype = {'Telefon mobil': 'string', 'Telefon bostad': 'string', 'Telefon arbete': 'string', 'Hemtelefon': 'string', 
            'MedlemsID': 'string', 'Mobiltelefon': 'string', 'Arbetstelefon': 'string', 'Övrig medlemsinfo': 'string'},
        converters = {'E-post kontakt':normalize_email, 'E-post privat':normalize_email,
            'Personnummer':convert_mc_personnummer_to_io, 
            'Kontakt 1 epost':normalize_email, 
            'Postnummer':convert_postnr, 'Postort':normalize_postort}) # MC Columns
    stats("Antal inlästa från MC: {:>4} ({})".format(str(len(mc_read_df)), Path(mc_file_name).name))

    # Get data from latest IO export
    io_read_df = pd.read_excel(io_file_name, 
        #usecols= io_read_cols,
        dtype = {'Telefon mobil': 'string', 'Telefon bostad': 'string', 'Telefon arbete': 'string', 'Hemtelefon': 'string', 
            'Medlemsnr.': 'string', 'Mobiltelefon': 'string', 'Arbetstelefon': 'string', 'Övrig medlemsinfo': 'string'},
        converters = {'E-post kontakt':normalize_email, 'E-post privat':normalize_email,
            'Personnummer':convert_mc_personnummer_to_io, 
            'Kontakt 1 epost':normalize_email, 
            'Postnummer':convert_postnr, 
            'Kontaktadress - Postort':normalize_postort,
            'Postort':normalize_postort}) # IO Columns
    # print(io_read_df.columns)
    stats("Antal inlästa från IO: {:>4} ({})".format(str(len(io_read_df)), Path(io_file_name).name))

    # Stats about personnummer
    stats("Antal med ofullständiga personnummer I MC: {:>4}".format(str(len(mc_read_df[mc_read_df['Personnummer'].str.len() == 8]))))
    stats("Antal med ofullständiga personnummer I IO: {:>4}".format(str(len(io_read_df[io_read_df['Födelsedat./Personnr.'].str.len() == 8]))))

    merged_df = pd.merge(mc_read_df, io_read_df,
        left_on = ['Personnummer','Förnamn','Efternamn'],
        right_on = ['Födelsedat./Personnr.','Förnamn','Efternamn'],
        how = 'outer',
        suffixes = ('_mc','_io'),
        indicator = True)
    stats("Antal lika (på personnummer): {:>12} (fullst. + icke fullständiga)".format(str(len(merged_df))))

    # Number of members with complete personnummer
    stats("Antal med  fullständiga personnummer: {:>4}".format(str(len(merged_df[merged_df['Personnummer'].str.len() == 13]))))

    # Filter away members with incomplete 'personnummer'
    merged_df = merged_df[merged_df['Personnummer'].str.len() == 8]
    stats("Antal med ofullständiga personnummer: {:>4}".format(str(len(merged_df))))

    # Filter away those originating from MC (= have group "MC_Import")
    #merged_df = merged_df[merged_df['Grupp/Lag/Arbetsrum/Familj'].str.contains('MC_Import', na="") != True]
    #stats("Antal utan MC-grupper i IO: {:>3}".format(str(len(merged_df))))

    # Add missing, neccessary for import, columns - as nan
    merged_df[['Prova-på', 'Ta bort GruppID']] = np.nan

    # Convert MC groups to IO GroupID's
    merged_df['Lägg till GruppID'] = merged_df['Grupper'].apply(convert_mc_groups_to_io_groups) 

    # Add special group 'MC_GruppViaMC'
    # We know that all groups are non-empty, we can just add a the end
    merged_df['Lägg till GruppID'] = merged_df['Lägg till GruppID'].apply(lambda x : x + ', 580242')

    # Retain columns to be used for import only
    # Disable for now
    if False:
        export_cols = ['Prova-på', 'Förnamn', 'Alt. förnamn', 'Efternamn', 'Kön', 'Nationalitet', 'IdrottsID', 
            'Födelsedat./Personnr.', 'Telefon mobil', 'E-post kontakt', 'Kontaktadress - c/o adress', 'Kontaktadress - Gatuadress', 
            'Kontaktadress - Postnummer', 'Kontaktadress - Postort', 'Kontaktadress - Land', 'Arbetsadress - c/o adress', 
            'Arbetsadress - Gatuadress', 'Arbetsadress - Postnummer', 'Arbetsadress - Postort', 'Arbetsadress - Land', 'Telefon bostad', 
            'Telefon arbete', 'E-post privat', 'E-post arbete', 'Medlemsnr.', 'Medlem sedan', 'Medlem t.o.m.', 'Övrig medlemsinfo', 
            'Familj', 'Fam.Admin', 'Lägg till GruppID', 'Ta bort GruppID']
        merged_df = merged_df[export_cols]

    check_status_filename = path + timestamp + '_check_status_update.xlsx'
    save_file(check_status_filename, merged_df)
    stats("Antal kvar att uppdatera: {:>5} ({})".format(str(len(merged_df)), Path(check_status_filename).name))

# Action 
print(" Start ".center(80, "-"))
# Export-1 - Move non-existing members in IO from MC to IO
# Use conver_members.sh
# from_mc_to_io(exp_mc_members_file, exp_mc_invoices_file, exp_io_members_file)

# Export-2 - Update IO members in IO with newer e-mails from MC
# Use update_email.sh
# update_io_email_from_mc(exp_io_members_file, cg_email_file)

# Export-3 - Map groups in MC and IO 
# Use sync_groups.sh
#sync_groups_from_mc_to_io(exp_mc_members_file, exp_io_members_file)

# Check the rest
# TODO Check member with non-complete personnummer
check_status(exp_mc_members_file, exp_io_members_file)

print ("Tidsåtgång: " + str(round((time.time() - start_time),1)) + " s")
print((" Klart (" + strftime("%Y-%m-%d %H:%M") + ") ").center(80, "-"))
