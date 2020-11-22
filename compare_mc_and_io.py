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
    compare_mc_columns, compare_io_columns

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
path_out = '/usr/src/app/files-last/'   # Output path

if len(sys.argv) > 1:
    cmd  = sys.argv[1]

if len(sys.argv) > 2:
    mc_file = sys.argv[2]
    validate_file(mc_file, 2)

if len(sys.argv) > 3:
    io_file  = sys.argv[3] 
    validate_file(io_file, 3)

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

def column_stats(label, df):
    """
    Print statistics for column
    """
    print(" '{}' ".format(label).center(40,"-"))
    vc = df[label].value_counts()
    print(vc.to_string(index=True))

def compare_mc_and_io(mc_file_name, io_file_name):
    """
    Compare members from MC and IO
    """
    # Get "important" data from latest MC export
    # Note! Doesn't read all columns...
    mc_read_df = pd.read_excel(mc_file_name, 
        usecols = compare_mc_columns,
        dtype = {'Telefon mobil': 'string', 'Telefon bostad': 'string', 'Telefon arbete': 'string', 'Hemtelefon': 'string', 
            'MedlemsID': 'string', 'Mobiltelefon': 'string', 'Arbetstelefon': 'string', 'Övrig medlemsinfo': 'string'},
        converters = {'E-post kontakt':normalize_email, 'E-post privat':normalize_email,
            'Personnummer':convert_mc_personnummer_to_io, 
            'Kontakt 1 epost':normalize_email, 
            'Postnummer':convert_postnr, 'Postort':normalize_postort}) # MC Columns
    stats("Antal inlästa från MC: {:>4} ({})".format(str(len(mc_read_df)), Path(mc_file_name).name))

    #stats("# Information i My Club:")
    #stats("Friskportslöfte  = Ja: {:>4} st".format(len(mc_read_df.loc[mc_read_df['Frisksportlöfte'] == 'Ja' ])))
    #stats("Friskportslöfte != Ja: {:>4} st".format(len(mc_read_df.loc[mc_read_df['Frisksportlöfte'] != 'Ja' ])))
    #stats("Friskportslöfte = Nej: {:>4} st".format(len(mc_read_df.loc[mc_read_df['Frisksportlöfte'] == 'Nej' ])))
    #stats("Ingen tidning tack  = Ja: {:>7} st".format(len(mc_read_df.loc[mc_read_df['Ingen tidning tack'] == 'Ja' ])))
    #stats("Ingen tidning tack != Ja: {:>7} st".format(len(mc_read_df.loc[mc_read_df['Ingen tidning tack'] != 'Ja' ])))
    #stats("Ingen tidning tack = Nej: {:>7} st".format(len(mc_read_df.loc[mc_read_df['Ingen tidning tack'] == 'Nej' ])))
    #stats("Hedersmedlem = Ja: {:>8} st".format(len(mc_read_df.loc[mc_read_df['Hedersmedlem'] == 'Ja' ])))
    #stats("Frisksportutbildning (Basic): {:>8} st".format(len(mc_read_df.loc[mc_read_df['Frisksportutbildning'] == 'Frisksport Basic (grundledarutbildning)'])))
    #stats("Frisksportutbildning (Ledarutb.): {:>4} st".format(len(mc_read_df.loc[mc_read_df['Frisksportutbildning'] == 'Ledarutbildning steg 1'])))
    #stats("Trampolinutbildning: {:>6} st".format(len(mc_read_df.loc[mc_read_df['Trampolinutbildning'] == 'Ja' ])))
    #print(mc_read_df.keys())


    def print_mc_group_stats(label, extra = None):
        # Make label regexp safe
        slabel = label.replace("(", r"\(")
        slabel = slabel.replace(")", r"\)")
        if extra:
            print("{:<30} {:>3} st ({})".format(label, len(mc_read_df.loc[mc_read_df['Grupper'].str.contains(slabel) == True ]), extra))
        else:
            print("{:<30} {:>3} st".format(label, len(mc_read_df.loc[mc_read_df['Grupper'].str.contains(slabel) == True ])))

    print_mc_group_stats('Medlemmar')
    print_mc_group_stats('Senior')
    #print_mc_group_stats('Uppdatering till fullt personnummer')
    print_mc_group_stats('Orientering')
    #print_mc_group_stats('Remaining migration 3')
    print_mc_group_stats('Skidor')
    print_mc_group_stats('Huvudsektion')
    print_mc_group_stats('styrelsen')
    print_mc_group_stats('Fotboll')
    print_mc_group_stats('Trampolin (SACRO)')
    print_mc_group_stats('Volleyboll')
    #print_mc_group_stats('Remaining migration')
    print_mc_group_stats('MTB')
    print_mc_group_stats('Skateboard (Chillskate)')
    print_mc_group_stats('Innebandy')
    #print_mc_group_stats('Remaining migration 2')

    column_stats('Frisksportlöfte', mc_read_df)
    column_stats('Hedersmedlem', mc_read_df)
    column_stats('Ingen tidning tack', mc_read_df)
    column_stats('Trampolinutbildning', mc_read_df)
    column_stats('Frisksportutbildning', mc_read_df)

    stats(" Slut MC ".center(40,"-"))
    stats("")

    # Get data from latest IO export (and convert some cols to IO format)
    # Note! Doesn't read all columns...
    io_read_df = pd.read_excel(io_file_name, 
        usecols = compare_io_columns,
        dtype = {'Telefon mobil': 'string', 'Telefon bostad': 'string', 'Telefon arbete': 'string', 'Hemtelefon': 'string', 
            'Medlemsnr.': 'string', 'Mobiltelefon': 'string', 'Arbetstelefon': 'string', 'Övrig medlemsinfo': 'string'},
        converters = {'E-post kontakt':normalize_email, 'E-post privat':normalize_email,
            'Personnummer':convert_mc_personnummer_to_io, 
            'Kontakt 1 epost':normalize_email, 
            'Postnummer':convert_postnr, 
            'Kontaktadress - Postort':normalize_postort,
            'Postort':normalize_postort}) # IO Columns
    stats("Antal inlästa från IO: {:>4} ({})".format(str(len(io_read_df)), Path(io_file_name).name))

    def print_io_group_stats(label, extra = None):
        if extra:
            print("{:<30} {:>3} st ({})".format(label, len(io_read_df.loc[io_read_df['Grupp/Lag/Arbetsrum/Familj'].str.contains(label) == True ]), extra))
        else:
            print("{:<30} {:>3} st".format(label, len(io_read_df.loc[io_read_df['Grupp/Lag/Arbetsrum/Familj'].str.contains(label) == True ])))

    print_io_group_stats('Styrelse SFK')
    print_io_group_stats('Senior')
    print_io_group_stats('Sektion Innebandy')
    print_io_group_stats('Sektion MTB')
    print_io_group_stats('MC_Cirkusledarutbildning')
    print_io_group_stats('MC_Fotboll')
    print_io_group_stats('MC_FrisksportlöfteJa')
    print_io_group_stats('MC_FrisksportlöfteNej')
    print_io_group_stats('MC_FrisksportutbildningBasic')
    print_io_group_stats('MC_FrisksportutbildningSteg1')
    print_io_group_stats('MC_GruppViaMC', "Ignorera")
    print_io_group_stats('MC_Hedersmedlem')
    print_io_group_stats('MC_Huvudsektion')
    print_io_group_stats('MC_Import')
    print_io_group_stats('MC_IngenTidning')
    print_io_group_stats('MC_Innebandy')
    print_io_group_stats('MC_Medlemmar', "Ignorera. Tas bort?")
    print_io_group_stats('MC_Medlemsavgift_2020')
    print_io_group_stats('MC_MTB')
    print_io_group_stats('MC_OfullstPnr', "Ignorera")
    print_io_group_stats('MC_OL')
    print_io_group_stats('MC_SACRO')
    print_io_group_stats('MC_Skate')
    print_io_group_stats('MC_Skidor')
    print_io_group_stats('MC_TrampolinutbildningSteg1')
    print_io_group_stats('MC_TrampolinutbildningSteg2')
    print_io_group_stats('MC_Uppdaterad', "Ignorera")
    print_io_group_stats('MC_Volleyboll')

    #io_groups = io_read_df['Grupp/Lag/Arbetsrum/Familj']
    #io_each_group = io_groups.str.split(', ', expand=True)
    #print(io_each_group)

    # MC_FrisksportlöfteJa - 579061
    # merged_df = merged_df[merged_df['Grupp/Lag/Arbetsrum/Familj'].str.contains('MC_Import', na="") != True]
    #stats("Friskportslöfte =  Ja i IO: {:>8}".format(str(len(io_read_df.loc[io_read_df['Grupp/Lag/Arbetsrum/Familj'] == 'Ja' ]))))
    # MC_FrisksportlöfteNej - 579062
    #stats("Friskportslöfte = Nej i IO: {:>8}".format(str(len(io_read_df.loc[io_read_df['Grupp/Lag/Arbetsrum/Familj'] == 'Nej' ]))))



    # Merge on outer (means everyone)
    stats("MC " + "> Merge (outer: personnummer) <".center(40, "-") + " IO")
    merged_df = pd.merge(mc_read_df, io_read_df,
        left_on = 'Personnummer',
        right_on = 'Födelsedat./Personnr.',
        #left_on = ['Personnummer','Förnamn','Efternamn'],
        #right_on = ['Födelsedat./Personnr.','Förnamn','Efternamn'],
        how = 'outer',
        suffixes = ('_mc','_io'),
        indicator = True)
    stats("Antal efter merge: {:>8}".format(str(len(merged_df))))
    stats("Antal lika (på personnummer): {:>12} (fullst. + icke fullständiga)".format(str(len(merged_df))))

    stats("Antal endast i MC: {:>8}".format(str(len(merged_df.loc[merged_df['_merge'] == 'left_only' ]))))
    stats("Antal endast i IO: {:>8}".format(str(len(merged_df.loc[merged_df['_merge'] == 'right_only' ]))))
    stats("Antal i båda:      {:>8}".format(str(len(merged_df.loc[merged_df['_merge'] == 'both' ]))))

    # Find matching members (in both MC and IO)
    #in_both_df  

    # Find members only in MC
    #only_mc_df

    # Find members only in IO
    #only_io_df


    merged_filename = path_out + timestamp + '_comparison_merge_report.xlsx'
    save_file(merged_filename, merged_df)
    stats("Saving report: {}".format(merged_filename))


# Action 
print(" Start ".center(80, "-"))

if "compare" == cmd:
    compare_mc_and_io(mc_file, io_file)

print ("Tidsåtgång: " + str(round((time.time() - start_time),1)) + " s")
print((" Klart (" + strftime("%Y-%m-%d %H:%M") + ") ").center(80, "-"))
