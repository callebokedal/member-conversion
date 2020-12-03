# pylint: disable=import-error
import pandas as pd
import numpy as np
import os, sys
from pathlib import Path
from datetime import date
import time 
from time import strftime

from utils import convert_countrycode, convert_mc_personnummer_to_io, convert_postnr, \
    clean_pii_comments, convert_mc_groups_to_io_groups, normalize_email, concat_special_cols, \
    normalize_postort, mc_family_to_id, concat_group_id, add_comment_info, \
    _read_mc_file, _read_io_file, _convert_mc_to_io_format, \
    convert_io_comment_to_mc_member_id, extract_mc_medlemsid, search_medlemsid_from_io

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

path = '/usr/src/app/files/'            # Required base path
path_out = '/usr/src/app/files/last/'   # Output path

#if len(sys.argv) < 4:
#    sys.exit("Illegal input arguments. Usage: convert_members.py <exported My Club members file> <exported My Club invoices file> <exported IO members file> [<e-mail file>]")
if len(sys.argv) > 1:
    cmd  = sys.argv[1]

if len(sys.argv) > 2:
    exp_mc_members_file  = sys.argv[2]
    validate_file(exp_mc_members_file, 2)

if len(sys.argv) > 3:
    exp_mc_invoices_file = sys.argv[3]
    validate_file(exp_mc_invoices_file, 3)

if len(sys.argv) > 4:
    exp_io_members_file  = sys.argv[4] 
    validate_file(exp_io_members_file, 4)

if len(sys.argv) > 5:
    cg_email_file = sys.argv[5]
    validate_file(cg_email_file, 5)

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
    mc_export_df = _read_mc_file(mc_file_name)
    stats("Antal medlemmar i MC: {} ({})".format(str(len(mc_export_df)), Path(mc_file_name).name))

    # Invoice info from My Club
    mc_invoice_df = pd.read_excel(mc_invoice_file, 
        usecols=['MedlemsID','Avgift','Summa','Summa betalt',
            'Familjemedlem 1','Familjemedlem 2','Familjemedlem 3','Familjemedlem 4','Familjemedlem 5','Familjemedlem 6'])
    stats("Antal fakturor i MC: {} ({})".format(str(len(mc_invoice_df)), Path(mc_invoice_file).name))
    # Merge in invoice details
    # Added later as special column
    # TODO Only for family head and not each person
    mc_export_df = mc_export_df.merge(mc_invoice_df, on='MedlemsID', how='left', suffixes=(None,'_inv'), validate = "one_to_one")

    # IO Import columns - for ref
    io_import_cols = ['Prova-på','Förnamn','Alt. förnamn','Efternamn','Kön','Nationalitet','IdrottsID','Födelsedat./Personnr.','Telefon mobil',
        'E-post kontakt','Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort',
        'Kontaktadress - Land','Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
        'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Medlemsnr.','Medlem sedan','Medlem t.o.m.','Övrig medlemsinfo',
        'Familj','Fam.Admin','Lägg till GruppID','Ta bort GruppID']

    # 1. Convert all MC members to IO Import format
    mc_in_io_format_df = _convert_mc_to_io_format(io_import_cols, mc_export_df, timestamp)
   
    # Export-4 last
    # Filter out only thos in group "Remaining migration"
    #mc_in_io_format_df['MissedGroup'] = np.where(mc_export_df['Grupper'].str.contains('Remaining migration'), 'True', 'False') 
    #mc_in_io_format_df = mc_in_io_format_df[mc_in_io_format_df.MissedGroup == "True"]

#    mc_in_io_format_df['Ta bort GruppID'] = mc_export_df[''] 

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
    stats("Enbart i MC: " + str(len(for_io_import_df.loc[for_io_import_df['_merge'] == 'left_only' ])))
    stats("I både MC och IO: " + str(len(for_io_import_df.loc[for_io_import_df['_merge'] == 'both' ])))
    stats("Antal med endast födelsedatum: " + str(len(for_io_import_df[for_io_import_df['Födelsedat./Personnr.'].str.len() == 8])))
    stats("Antal med fullt personnummer:  " + str(len(for_io_import_df[for_io_import_df['Födelsedat./Personnr.'].str.len() > 8])))
    save_file(for_io_import_file, for_io_import_df)
    stats("Sparat: " + for_io_import_file)

def update_medlemsid_in_io(mc_file_name, io_file_name):
    """
    Goal: Update all members with MC MedlemsID, in IO
    """
    # My Club Dataframe
    mc_read_df = _read_mc_file(mc_file_name)
    stats("Antal medlemmar i MC: {} ({})".format(str(len(mc_read_df)), Path(mc_file_name).name))

    # IO Import columns - for ref
    io_import_cols = ['Prova-på','Förnamn','Alt. förnamn','Efternamn','Kön','Nationalitet','IdrottsID','Födelsedat./Personnr.','Telefon mobil',
        'E-post kontakt','Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort',
        'Kontaktadress - Land','Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
        'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Medlemsnr.','Medlem sedan','Medlem t.o.m.','Övrig medlemsinfo',
        'Familj','Fam.Admin','Lägg till GruppID','Ta bort GruppID']

    # Convert all MC members to IO Import format
    for_io_import_df = _convert_mc_to_io_format(io_import_cols, mc_read_df, timestamp)
    stats("Antal medlemmar för IO: {}".format(len(for_io_import_df)))

    # Get IO dataframe
    io_read_df = _read_io_file(io_file_name)
    stats("Antal medlemmar i IO: {} ({})".format(str(len(io_read_df)), Path(io_file_name).name))

    # Get MedlemsID from IO - if we can find it
    io_read_df['MC_MedlemsID'] = [search_medlemsid_from_io(comment, medlemsnr)
        for comment, medlemsnr 
        in zip (io_read_df['Övrig medlemsinfo'], io_read_df['Medlemsnr.'])]

    # Filter away members that already have MedlemsID
    io_read_df = io_read_df[io_read_df['MC_MedlemsID'].isnull()]
    stats("Antal medlemmar utan MedlemsID i IO: {}".format(str(len(io_read_df))))

    # Skip for now
    if False:
        save_file(path + timestamp + '_membersid_before_io_import.xlsx', io_read_df)
        stats("Sparat: " + path + timestamp + '_membersid_before_io_import.xlsx')
        print(io_read_df.head())
        return


    # Map person to person between MC <-> IO
    merged_df = pd.merge(mc_read_df, io_read_df,
                     #on = 'Födelsedat./Personnr.',
                     left_on = 'Personnummer',
                     right_on = 'Födelsedat./Personnr.',
                     how = 'inner',
                     suffixes = ('_mc',''),
                     indicator = True)
    stats("Antal mergade medlemmar: {}".format(len(merged_df)))

    # Add MedlemsID from MC for new import
    merged_df['Övrig medlemsinfo'] = [add_comment_info(comment, member_id, date_today)
        for comment, member_id
        in zip(merged_df['Övrig medlemsinfo'] , merged_df['MedlemsID'])]

    # Set "Medlemsnr." to "MedlemsID" if not already set
    merged_df['Medlemsnr.'] = np.where(pd.isna(merged_df['Medlemsnr.']), merged_df['MedlemsID'], merged_df['Medlemsnr.'])

    # Export in "import" format
    io_import_cols = ['Typ','Målsman','Förnamn','Alt. förnamn','Efternamn','IdrottsID','Födelsedat./Personnr.','Kön','Nationalitet','Telefon mobil','E-post kontakt','Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort','Kontaktadress - Land','Folkbokföring - c/o adress','Folkbokföring - Gatuadress','Folkbokföring - Postnummer','Folkbokföring - Postort','Folkbokföring - Land','Folkbokföring - Kommunkod','Folkbokföring - Kommun','Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land','Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Roller','Behörighet','Övrig medlemsinfo','Grupp/Lag/Arbetsrum/Familj','Familj','Fam.Admin','Medlemsnr.','Medlem sedan','Medlem t.o.m.','Organisation','Registreringsdatum','Avslutningsdatum']
    io_for_import_df = merged_df.loc[:, io_import_cols]
    stats("Antal medlemmar for IO import: {}".format(len(io_for_import_df)))

    save_file(path + timestamp + '_membersid_for_io_import.xlsx', io_for_import_df)
    stats("Sparat: " + path + timestamp + '_membersid_for_io_import.xlsx')
    # print(for_io_import_df.head())
    return

    # Done?
   
    # Export-4 last
    # Filter out only thos in group "Remaining migration"
    #mc_in_io_format_df['MissedGroup'] = np.where(mc_export_df['Grupper'].str.contains('Remaining migration'), 'True', 'False') 
    #mc_in_io_format_df = mc_in_io_format_df[mc_in_io_format_df.MissedGroup == "True"]

#    mc_in_io_format_df['Ta bort GruppID'] = mc_export_df[''] 

    # 2. Compare MC data with current IO data
    # Todo
    #comp_df = mc_in_io_format_df[['Förnamn','Alt. förnamn','Efternamn','Födelsedat./Personnr.','Kön','Nationalitet','Telefon mobil','E-post kontakt',
    #    'Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort','Kontaktadress - Land',
    #    'Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
    #    'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Övrig medlemsinfo','Familj','Fam.Admin','Medlem sedan','Medlem t.o.m.']].compare(
    #        for_io_import_df[['Förnamn','Alt. förnamn','Efternamn','Födelsedat./Personnr.','Kön','Nationalitet','Telefon mobil','E-post kontakt',
    #    'Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort','Kontaktadress - Land',
    #    'Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
    #    'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Övrig medlemsinfo','Familj','Fam.Admin','Medlem sedan','Medlem t.o.m.']])

    #df1 = mc_in_io_format_df[['Förnamn','Efternamn','Födelsedat./Personnr.','Kön','Medlem sedan']].copy()
    #print(df1.axes)
    #df2 = for_io_import_df[['Förnamn','Efternamn','Födelsedat./Personnr.','Kön','Medlem sedan']].copy()
    #print(df2.axes)
    #comp_df = df1.compare(df2)
    #save_file('/usr/src/app/files/' + date_today + '_mc-io_comparison.xlsx', comp_df)
    
    # 3. Save file with all members from MC in correct format (still need to cross check with IO!)
    save_file(path + timestamp + '_all_mc_in_io_format.xlsx', for_io_import_df)
    stats("Sparat: " + path + timestamp + '_all_mc_in_io_format.xlsx')

    # 4. Merge
    
    # Current members in IdrottOnline
    for_io_import_df = pd.read_excel(io_file_name, 
        usecols=['Födelsedat./Personnr.'],
        dtype = {
        'Telefon mobil': 'string', 'Telefon bostad': 'string', 'Telefon arbete': object, 'Medlemsnr.': 'string'},
        converters = {'E-post kontakt':normalize_email, 'E-post privat':normalize_email, 'E-post arbete':normalize_email}) # IO columns
    stats("Antal medlemmar i IO: " + str(len(for_io_import_df)) + " (" + Path(io_file_name).name + ")")

    # TODO: Finish below
    return

    # For import
    # TODO Remove this later!
    # This is already handled by how = 'left' below - so we can assign 'Medlemsnr.' without risking overwrite
    # mc_in_io_format_df['Medlemsnr.'] = mc_export_df['MedlemsID'] 
    # TODO Remove this later!
    # Filter - only non-existing in IO (solved by how = 'left')
    # Label: 'Export-1' - For members updated '2020-11-16_01.20'
    #for_io_import_df = pd.merge(mc_in_io_format_df, for_io_import_df,
    #                 on = 'Födelsedat./Personnr.',
    #                 how = 'left',
    #                 suffixes = ('_mc','_io'),
    #                 indicator = True)


    # Label: 'Export-2' - Current members in IO updated in IO with new data from MC
    for_io_import_df = pd.merge(mc_read_df, for_io_import_df,
                     #on = 'Födelsedat./Personnr.',
                     on = 'Personnummer',
                     how = 'right',
                     suffixes = ('_mc','_io'),
                     indicator = True)

    # Filter - only with full personnummer
    for_io_import_df = for_io_import_df[for_io_import_df['Födelsedat./Personnr.'].str.len() > 8]

    # Filter - only MC
    for_io_import_df = for_io_import_df[for_io_import_df['_merge'] == "right_only" ]

    for_io_import_file = path + timestamp + '_for_io_import.xlsx'
    stats("Antal för import till IO:   " + str(len(for_io_import_df)) + " (" + Path(for_io_import_file).name + ")")
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
    io_read_df = _read_io_file(io_file_name, io_read_cols)
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

def sync_special_fields_from_mc_to_io(mc_file_name, mc_invoice_file, io_file_name):
    """
    Sync forgotten special fileds from MC and IO
    """
    # Get data from latest MC export
    mc_read_df = _read_mc_file(mc_file_name)
    stats("Antal inlästa från MC: {} ({})".format(str(len(mc_read_df)), Path(mc_file_name).name))

    # Invoice info from My Club
    mc_invoice_df = pd.read_excel(mc_invoice_file, 
        usecols=['MedlemsID','Avgift'])
    stats("Antal fakturor i MC:  " + str(len(mc_invoice_df)) + " (" + Path(mc_invoice_file).name + ")")
    # Merge in invoice details
    mc_read_df = mc_read_df.merge(mc_invoice_df, on='MedlemsID', how='left', suffixes=(None,'_inv'), validate = "one_to_one")
    
    # Add missing, neccessary for import, columns - as nan
    mc_read_df[['Prova-på', 'Ta bort GruppID']] = np.nan
    mc_read_df['Lägg till GruppID'] = ""

    # Also - add ONLY special columns as groupIDs
    # Be sure to uodate via import, DON'T overwrite
    mc_read_df['Lägg till GruppID'] = [
        concat_special_cols("", cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb, avgift) 
                            for cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb, avgift
        in zip(mc_read_df['Cirkusledarutbildning'], 
            mc_read_df['Frisksportlöfte'], 
            mc_read_df['Hedersmedlem'], 
            mc_read_df['Ingen tidning tack'], 
            mc_read_df['Frisksportutbildning'], 
            mc_read_df['Trampolinutbildning'], 
            mc_read_df['Avgift'])]

    # Get data from latest IO export
    io_read_df = _read_io_file(io_file_name)
    # print(io_read_df.columns)
    stats("Antal inlästa från IO: {} ({})".format(str(len(io_read_df)), Path(io_file_name).name))

    merged_df = pd.merge(mc_read_df, io_read_df,
        left_on = 'Personnummer',
        right_on = 'Födelsedat./Personnr.',
        #left_on = ['Personnummer','Förnamn','Efternamn'], # Finns personer med felstavade namn
        #right_on = ['Födelsedat./Personnr.','Förnamn','Efternamn'], # Finns personer med felstavade namn
        how = 'inner',
        suffixes = ('_mc',''))
    stats("Antal match på personnummer/datum: {}".format(str(len(merged_df))))

    # Filter away members with incomplete 'personnummer'
    merged_df = merged_df[merged_df['Personnummer'].str.len() == 13]
    stats("Antal med fullständiga personnummer: {:>4}".format(str(len(merged_df))))

    # Filter away those originating from MC (= have group "MC_Import")
    merged_df = merged_df[merged_df['Grupp/Lag/Arbetsrum/Familj'].str.contains('MC_Import', na="") != True]
    stats("Antal med ursprung från MC: {}".format(str(len(merged_df))))

    # Convert MC groups to IO GroupID's
    # Already done... in earlier export
    # merged_df['Lägg till GruppID'] = merged_df['Grupper'].apply(convert_mc_groups_to_io_groups) 

    # Add special group 'MC_SpecialFält'
    # We know that all groups are non-empty, we can just add a the end
    # TODO Kolla detta
    #merged_df['Lägg till GruppID'] = merged_df['Lägg till GruppID'].apply(lambda x : x + ', 580266')

    # Retain columns to be used for import only
    export_cols = ['Prova-på', 'Förnamn', 'Alt. förnamn', 'Efternamn', 'Kön', 'Nationalitet', 'IdrottsID', 
        'Födelsedat./Personnr.', 'Telefon mobil', 'E-post kontakt', 'Kontaktadress - c/o adress', 'Kontaktadress - Gatuadress', 
        'Kontaktadress - Postnummer', 'Kontaktadress - Postort', 'Kontaktadress - Land', 'Arbetsadress - c/o adress', 
        'Arbetsadress - Gatuadress', 'Arbetsadress - Postnummer', 'Arbetsadress - Postort', 'Arbetsadress - Land', 'Telefon bostad', 
        'Telefon arbete', 'E-post privat', 'E-post arbete', 'Medlemsnr.', 'Medlem sedan', 'Medlem t.o.m.', 'Övrig medlemsinfo', 
        'Familj', 'Fam.Admin', 'Lägg till GruppID', 'Ta bort GruppID']
    merged_df = merged_df[export_cols]

    sync_specials_filename = path_out + timestamp + '_sync_specials_update.xlsx'
    save_file(sync_specials_filename, merged_df)
    stats("Antal att uppdatera i IO: {} ({})".format(str(len(merged_df)), Path(sync_specials_filename).name))


def sync_groups_from_mc_to_io(mc_file_name, mc_invoice_file, io_file_name):
    """
    Sync groupes between MC and IO
    """
    # Get data from latest MC export
    mc_read_df = _read_mc_file(mc_file_name)
    stats("Antal inlästa från MC: {} ({})".format(str(len(mc_read_df)), Path(mc_file_name).name))

    # Invoice info from My Club
    mc_invoice_df = pd.read_excel(mc_invoice_file,  
        dtype = {'MedlemsID': 'string'}, 
        usecols=['MedlemsID','Avgift','Summa','Summa betalt'])
        #usecols=['MedlemsID','Avgift','Summa','Summa betalt',
        #    'Familjemedlem 1','Familjemedlem 2','Familjemedlem 3','Familjemedlem 4','Familjemedlem 5','Familjemedlem 6'])
    stats("Antal fakturor i MC:  {} ({})".format(str(len(mc_invoice_df)), Path(mc_invoice_file).name))
    # Merge in invoice details
    # Added later as special column
    mc_read_df = mc_read_df.merge(mc_invoice_df, on='MedlemsID', how='left', suffixes=(None,'_inv'), validate = "one_to_one")

    # Get data from latest IO export
    io_read_df = _read_io_file(io_file_name)
    # print(io_read_df.columns)
    stats("Antal inlästa från IO: {} ({})".format(str(len(io_read_df)), Path(io_file_name).name))

    # Get MedlemsID from IO - if we can find it
    io_read_df['MC_MedlemsID'] = [search_medlemsid_from_io(comment, medlemsnr)
        for comment, medlemsnr 
        in zip (io_read_df['Övrig medlemsinfo'], io_read_df['Medlemsnr.'])]

    merged_df = pd.merge(mc_read_df, io_read_df,
        left_on = 'MedlemsID',
        right_on = 'MC_MedlemsID',
        #left_on = 'Personnummer',
        #right_on = 'Födelsedat./Personnr.',
        how = 'inner',
        suffixes = ('_mc',''))
    stats("Antal lika (på MedlemsID): {}".format(str(len(merged_df))))

    # Filter away members with incomplete 'personnummer'
    #merged_df = merged_df[merged_df['Personnummer'].str.len() == 13]
    stats("Antal med fullständiga personnummer: {}".format(str(len(merged_df))))

    # Filter away those originating from MC (= have group "MC_Import")
    #merged_df = merged_df[merged_df['Grupp/Lag/Arbetsrum/Familj'].str.contains('MC_Import', na="") != True]
    stats("Antal utan MC-grupper i IO: {}".format(str(len(merged_df))))

    # Add missing, neccessary for import, columns - as nan
    merged_df[['Prova-på', 'Ta bort GruppID']] = np.nan

    # Convert MC groups to IO GroupID's
    #merged_df['Lägg till GruppID'] = merged_df['Grupper'].apply(convert_mc_groups_to_io_groups) 

    # Add special group 'MC_GruppViaMC' 580242
    # Add MC_Alla (580600)
    # We know that all groups are non-empty, we can just add at the end
    # merged_df['Lägg till GruppID'] = merged_df['Lägg till GruppID'].apply(lambda x : x + ', 580600')

    # Also - add ONLY special columns as groupIDs
    # Be sure to uodate via import, DON'T overwrite
    merged_df['Lägg till GruppID'] = [
        concat_special_cols("", cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb, avgift) 
                            for cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb, avgift
        in zip(merged_df['Cirkusledarutbildning'], 
            merged_df['Frisksportlöfte'], 
            merged_df['Hedersmedlem'], 
            merged_df['Ingen tidning tack'], 
            merged_df['Frisksportutbildning'], 
            merged_df['Trampolinutbildning'], 
            merged_df['Avgift'])]

    # Retain columns to be used for import only
    export_cols = ['Prova-på', 'Förnamn', 'Alt. förnamn', 'Efternamn', 'Kön', 'Nationalitet', 'IdrottsID', 
        'Födelsedat./Personnr.', 'Telefon mobil', 'E-post kontakt', 'Kontaktadress - c/o adress', 'Kontaktadress - Gatuadress', 
        'Kontaktadress - Postnummer', 'Kontaktadress - Postort', 'Kontaktadress - Land', 'Arbetsadress - c/o adress', 
        'Arbetsadress - Gatuadress', 'Arbetsadress - Postnummer', 'Arbetsadress - Postort', 'Arbetsadress - Land', 'Telefon bostad', 
        'Telefon arbete', 'E-post privat', 'E-post arbete', 'Medlemsnr.', 'Medlem sedan', 'Medlem t.o.m.', 'Övrig medlemsinfo', 
        'Familj', 'Fam.Admin', 'Lägg till GruppID', 'Ta bort GruppID']
    merged_df = merged_df[export_cols]

    # sync_groups_filename = path + date_today + '_sync_groups_update.xlsx'
    sync_groups_filename = path_out + timestamp + '_sync_groups_update.xlsx'
    save_file(sync_groups_filename, merged_df)
    stats("Antal att uppdatera i IO: {} ({})".format(str(len(merged_df)), Path(sync_groups_filename).name))


def check_status(mc_file_name, io_file_name):
    """
    Check status between MC and IO

    NOTE! This function is probably not correct all the way to the end righ now
    """
    # Get data from latest MC export
    mc_read_df = _read_mc_file(mc_file_name)
    stats("Antal inlästa från MC: {:>4} ({})".format(str(len(mc_read_df)), Path(mc_file_name).name))

    # Get data from latest IO export
    io_read_df = _read_io_file(io_file_name)
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

def sync_last_ones(mc_file_name, mc_invoice_file, io_file_name):
    """
    Export last ones from My Club to IO.
    - Those which have incomplete personnummer
    """
    # Get data from latest MC export
    mc_read_df = _read_mc_file(mc_file_name)
    stats("Antal inlästa från MC: {:>4} ({})".format(str(len(mc_read_df)), Path(mc_file_name).name))

    # Invoice info from My Club
    mc_invoice_df = pd.read_excel(mc_invoice_file,  
        dtype = {'MedlemsID': 'string'}, 
        usecols=['MedlemsID','Avgift','Summa','Summa betalt',
            'Familjemedlem 1','Familjemedlem 2','Familjemedlem 3','Familjemedlem 4','Familjemedlem 5','Familjemedlem 6'])
    stats("Antal fakturor i MC:  {} ({})".format(str(len(mc_invoice_df)), Path(mc_invoice_file).name))
    # Merge in invoice details
    # Added later as special column
    mc_read_df = mc_read_df.merge(mc_invoice_df, on='MedlemsID', how='left', suffixes=(None,'_inv'), validate = "one_to_one")

    # Get data from latest IO export
    io_read_df = _read_io_file(io_file_name)
    # print(io_read_df.columns)
    stats("Antal inlästa från IO: {:>4} ({})".format(str(len(io_read_df)), Path(io_file_name).name))

    # Stats about personnummer
    stats("Antal med ofullständiga personnummer I MC: {:>4} st".format(str(len(mc_read_df[mc_read_df['Personnummer'].str.len() == 8]))))
    stats("Antal med ofullständiga personnummer I IO: {:>4} st".format(str(len(io_read_df[io_read_df['Födelsedat./Personnr.'].str.len() == 8]))))
    stats("Antal med  fullständiga personnummer I MC: {:>4} st".format(str(len(mc_read_df[mc_read_df['Personnummer'].str.len() == 13]))))
    stats("Antal med  fullständiga personnummer I IO: {:>4} st".format(str(len(io_read_df[io_read_df['Födelsedat./Personnr.'].str.len() == 13]))))

    # Merge on all 'Personnummer','Förnamn','Efternamn'
    print("MC " + "> Merge (left: pnr+fn+en) <".center(40, "-") + " IO")
    merged_df = pd.merge(mc_read_df, io_read_df,
        left_on = ['Personnummer','Förnamn','Efternamn'],
        right_on = ['Födelsedat./Personnr.','Förnamn','Efternamn'],
        how = 'left',
        suffixes = ('_mc','_io'),
        indicator = True)
    stats("Antal efter merge: {:>8}".format(str(len(merged_df))))
    stats("Antal lika (på personnummer): {:>12} (fullst. + icke fullständiga)".format(str(len(merged_df))))

    # Number of members with complete personnummer
    stats("Antal med  fullständiga personnummer: {:>4}".format(str(len(merged_df[merged_df['Personnummer'].str.len() == 13]))))
    stats("Antal med ofullständiga personnummer: {:>4}".format(str(len(merged_df[merged_df['Personnummer'].str.len() == 8]))))

    # Filter only on members with incomplete 'personnummer'
    print(" Filter: Endast ofullständiga ".center(46, "-"))
    #merged_df = merged_df[merged_df['Personnummer'].str.len() == 8]
    #stats("Antal med ofullständiga personnummer: {:>4}".format(str(len(merged_df))))

    stats("Antal endast i MC: {:>8}".format(str(len(merged_df.loc[merged_df['_merge'] == 'left_only' ]))))
    stats("Antal endast i IO: {:>8}".format(str(len(merged_df.loc[merged_df['_merge'] == 'right_only' ]))))
    stats("Antal i båda:      {:>8}".format(str(len(merged_df.loc[merged_df['_merge'] == 'both' ]))))

    # Filter away those originating from MC (= have group "MC_Import")
    #merged_df = merged_df[merged_df['Grupp/Lag/Arbetsrum/Familj'].str.contains('MC_Import', na="") != True]
    #stats("Antal utan MC-grupper i IO: {:>3}".format(str(len(merged_df))))

    # Convert to import format

    # IO Import columns - for ref
    io_import_cols = ['Prova-på','Förnamn','Alt. förnamn','Efternamn','Kön','Nationalitet','IdrottsID','Födelsedat./Personnr.','Telefon mobil',
        'E-post kontakt','Kontaktadress - c/o adress','Kontaktadress - Gatuadress','Kontaktadress - Postnummer','Kontaktadress - Postort',
        'Kontaktadress - Land','Arbetsadress - c/o adress','Arbetsadress - Gatuadress','Arbetsadress - Postnummer','Arbetsadress - Postort','Arbetsadress - Land',
        'Telefon bostad','Telefon arbete','E-post privat','E-post arbete','Medlemsnr.','Medlem sedan','Medlem t.o.m.','Övrig medlemsinfo',
        'Familj','Fam.Admin','Lägg till GruppID','Ta bort GruppID']

    # 1. Convert all MC members to IO Import format
    #mc_in_io_format_df = _convert_mc_to_io_format(io_import_cols, merged_df, timestamp)
    mc_in_io_format_df = pd.DataFrame(columns=io_import_cols)
#    mc_in_io_format_df['Prova-på'] = mc_export_df['']  # Not used in MC?
    mc_in_io_format_df['Förnamn'] = merged_df['Förnamn']
#    mc_in_io_format_df['Alt. förnamn'] = mc_export_df['']  # Found none in MC
    mc_in_io_format_df['Efternamn'] = merged_df['Efternamn']
    mc_in_io_format_df['Kön'] = merged_df['Kön (flicka/pojke)']
    mc_in_io_format_df['Nationalitet'] = merged_df['Nationalitet_mc'].replace('SE','Sverige')
#    mc_in_io_format_df['IdrottsID'] = mc_export_df[''] 
    mc_in_io_format_df['Födelsedat./Personnr.'] = merged_df['Personnummer'] #.astype('string').apply(convert_personnummer) 
    mc_in_io_format_df['Telefon mobil'] = merged_df['Mobiltelefon']
    mc_in_io_format_df['E-post kontakt'] = merged_df['E-post'] 
    mc_in_io_format_df['Kontaktadress - c/o adress'] = merged_df['c/o']
    mc_in_io_format_df['Kontaktadress - Gatuadress'] = merged_df['Adress']
    mc_in_io_format_df['Kontaktadress - Postnummer'] = merged_df['Postnummer'].astype('string').apply(convert_postnr)
    mc_in_io_format_df['Kontaktadress - Postort'] = merged_df['Postort']
    mc_in_io_format_df['Kontaktadress - Land'] = merged_df['Land'].apply(convert_countrycode)
#    mc_in_io_format_df['Arbetsadress - c/o adress'] = mc_export_df['']
#    mc_in_io_format_df['Arbetsadress - Gatuadress'] = mc_export_df['']
#    mc_in_io_format_df['Arbetsadress - Postnummer'] = mc_export_df['']
#    mc_in_io_format_df['Arbetsadress - Postort'] = mc_export_df['']
#    mc_in_io_format_df['Arbetsadress - Land'] = mc_export_df['']
    mc_in_io_format_df['Telefon bostad'] = merged_df['Hemtelefon']
    mc_in_io_format_df['Telefon arbete'] = merged_df['Arbetstelefon']
#    mc_in_io_format_df['E-post privat'] = mc_export_df['Kontakt 1 epost']
#    mc_in_io_format_df['E-post arbete'] = mc_export_df['']
    
    mc_in_io_format_df['Medlem sedan'] = merged_df['Datum registrerad']
    mc_in_io_format_df['MC_Senast ändrad'] = merged_df['Senast ändrad']
#    mc_in_io_format_df['Medlem t.o.m.'] = mc_export_df['']
    mc_in_io_format_df['Övrig medlemsinfo'] = merged_df['Kommentar'].astype('string').apply(clean_pii_comments) # Special handling - not for all clubs
    # Add special info to 'Övrig medlemsinfo' - MC MedlemsInfo and execution time
    mc_in_io_format_df['Övrig medlemsinfo'] = [add_comment_info(comment, member_id, timestamp)
        for comment, member_id
        in zip(mc_in_io_format_df['Övrig medlemsinfo'] , merged_df['MedlemsID'])]

#   mc_in_io_format_df['Familj'] = mc_export_df['Familj']
#   mc_in_io_format_df['Fam.Admin'] = mc_export_df[''] 
    mc_in_io_format_df['Lägg till GruppID'] = merged_df['Grupper'].apply(convert_mc_groups_to_io_groups) 
    # Also - add special columns as groupIDs
    mc_in_io_format_df['Lägg till GruppID'] = [concat_special_cols(groups, cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb, avgift) 
        for groups, cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb, avgift
        in zip(mc_in_io_format_df['Lägg till GruppID'], merged_df['Cirkusledarutbildning'], merged_df['Frisksportlöfte'], 
            merged_df['Hedersmedlem'], merged_df['Ingen tidning tack'], merged_df['Frisksportutbildning'], 
            merged_df['Trampolinutbildning'], merged_df['Avgift'])]
    # Also - add family info as groups
    # 2020-11-15 Disabled - since IO does not handle this according to documentation...
    if False:
        merged_df['Familj'] = merged_df['Familj'].apply(mc_family_to_id)
        mc_in_io_format_df['Lägg till GruppID'] = [concat_group_id(groups, family_id) 
            for groups, family_id 
            in zip(mc_in_io_format_df['Lägg till GruppID'], merged_df['Familj'])]

    # Extra info
    mc_in_io_format_df['_merge'] = merged_df['_merge']

    # Add missing, neccessary for import, columns - as nan
    mc_in_io_format_df[['Prova-på', 'Ta bort GruppID']] = np.nan
    #merged_df[['Prova-på', 'Ta bort GruppID']] = np.nan
    #print(merged_df['Grupper'].head())

    # Req. for incomplete personnummer:
    # "namn, födelsedatum (år, månad, dag), kön, nationalitet och minst en angiven adress"

    last_filename = path_out + timestamp + '_5-err_import.xlsx'
    save_file(last_filename, mc_in_io_format_df)
    #print(mc_in_io_format_df)
    #save_file(last_filename, merged_df)
    stats("Antal kvar att uppdatera: {:>5} ({})".format(str(len(mc_in_io_format_df)), Path(last_filename).name))
    #stats("Antal kvar att uppdatera: {:>5} ({})".format(str(len(merged_df)), Path(last_filename).name))

# Action 
print(" Start ".center(80, "-"))
# Export-1 - Move non-existing members in IO from MC to IO
# Use convert_members.sh
if "convert" == cmd:
    from_mc_to_io(exp_mc_members_file, exp_mc_invoices_file, exp_io_members_file)

# Export-2 - Update IO members in IO with newer e-mails from MC
# Use update_email.sh
if "update_email" == cmd:
    update_io_email_from_mc(exp_io_members_file, cg_email_file)

# Export-3 - Map groups in MC and IO 
# Use sync_groups.sh
if "sync_groups" == cmd:
    sync_groups_from_mc_to_io(exp_mc_members_file, exp_mc_invoices_file, exp_io_members_file)

# Check the rest
# TODO Check member with non-complete personnummer
if "check_status" == cmd:
    check_status(exp_mc_members_file, exp_io_members_file)

# Fix special fields as well
#sync_special_fields_from_mc_to_io(exp_mc_members_file, exp_mc_invoices_file, exp_io_members_file)

# Export-4 - All with incomplete personnummer
if "sync_last" == cmd:
    sync_last_ones(exp_mc_members_file, exp_mc_invoices_file, exp_io_members_file)

if "update_medlemsid" == cmd:
    update_medlemsid_in_io(exp_mc_members_file, exp_io_members_file)

print ("Tidsåtgång: " + str(round((time.time() - start_time),1)) + " s")
print((" Klart (" + strftime("%Y-%m-%d %H:%M") + ") ").center(80, "-"))
