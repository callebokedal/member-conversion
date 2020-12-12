# pylint: disable=import-error
import pandas as pd
import numpy as np
import os, sys
from pathlib import Path
from datetime import date
import time 
from time import strftime

from xlsxwriter.utility import xl_rowcol_to_cell

from utils import convert_countrycode, convert_mc_personnummer_to_io, convert_postnr, \
    clean_pii_comments, convert_mc_groups_to_io_groups, normalize_email, concat_special_cols, \
    normalize_postort, mc_family_to_id, concat_group_id, add_comment_info, \
    compare_mc_columns, compare_io_columns, convert_io_comment_to_mc_member_id, extract_mc_medlemsid, \
    _read_mc_file, _read_io_file, search_medlemsid_from_io, verify_special_cols, verify_group

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

if len(sys.argv) > 1:
    cmd  = sys.argv[1]

if len(sys.argv) > 2:
    mc_file = sys.argv[2]
    validate_file(mc_file, 2)

if len(sys.argv) > 3:
    io_file  = sys.argv[3] 
    validate_file(io_file, 3)

def save_file(file_name, df, color = False):
    """
    Save to Excel file
    """
    # To get colors to work
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    df.to_excel(writer, index=False)

    if color:
        # Get access to the workbook and sheet
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Add a format. Light red fill with dark red text.
        format1 = workbook.add_format({'bg_color': '#FFC7CE',
                                    'font_color': '#9C0006'})

        # Define our range for the color formatting
        color_range = "DO2:EF900"

        # Highlight the bottom 5 values in Red
        worksheet.conditional_format(color_range, {
            #'type': 'bottom',
            #                                    'value': '5',
            #                                    'format': format1})

                                            'type': 'cell',
                                            'criteria': '=',
                                            'value': 'FALSE',
                                            'format': format1})

    writer.save()
    # df.to_excel(file_name, index=False)
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
    mc_read_df = _read_mc_file(mc_file_name)
    stats("Antal inlästa från MC: {:>4} ({})".format(str(len(mc_read_df)), Path(mc_file_name).name))

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
    io_read_df = _read_io_file(io_file_name, compare_io_columns)
    stats("Antal inlästa från IO: {:>4} ({})".format(len(io_read_df), Path(io_file_name).name))

    # Filter only with MC_Alla
    #io_read_df = io_read_df[io_read_df['Grupp/Lag/Arbetsrum/Familj'].str.contains("MC_Alla", na=False)]
    #stats("Antal medlemmar med MC_Alla i IO: {}".format(len(io_read_df)))

    # Extract MC MedlemsID for all IO members
    io_read_df['MC_MedlemsID'] = [search_medlemsid_from_io(comment, medlemsnr)
        for comment, medlemsnr 
        in zip (io_read_df['Övrig medlemsinfo'], io_read_df['Medlemsnr.'])]
    # Set correct dtype
    io_read_df['MC_MedlemsID'] = io_read_df['MC_MedlemsID'].astype('string')

    def print_io_group_stats(label, extra = None):
        if extra:
            print("{:<30} {:>3} st ({})".format(label, len(io_read_df.loc[io_read_df['Grupp/Lag/Arbetsrum/Familj'].str.contains(label) == True ]), extra))
        else:
            print("{:<30} {:>3} st".format(label, len(io_read_df.loc[io_read_df['Grupp/Lag/Arbetsrum/Familj'].str.contains(label) == True ])))

    print_io_group_stats('Styrelse SFK')
    print_io_group_stats('Senior')
    print_io_group_stats('Sektion Innebandy')
    print_io_group_stats('Sektion MTB')
    print_io_group_stats('MC_Alla')
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

    stats("MC " + "> Merge (outer: personnummer) <".center(40, "-") + " IO")
    merged_df = pd.merge(mc_read_df, io_read_df,
        left_on = 'MedlemsID',
        right_on = 'MC_MedlemsID',
        how = 'outer',
        suffixes = ('_mc','_io'),
        indicator = True)
    stats("Antal efter merge: {:>8}".format(str(len(merged_df))))
    stats("Antal lika (på personnummer): {:>12} (fullst. + icke fullständiga)".format(str(len(merged_df))))

    stats("Antal endast i MC: {:>8}".format(str(len(merged_df.loc[merged_df['_merge'] == 'left_only' ]))))
    stats("Antal endast i IO: {:>8}".format(str(len(merged_df.loc[merged_df['_merge'] == 'right_only' ]))))
    stats("Antal i båda:      {:>8}".format(str(len(merged_df.loc[merged_df['_merge'] == 'both' ]))))

    merged_filename = path_out + timestamp + '_comparison_merge_report.xlsx'
    save_file(merged_filename, merged_df)
    stats("Saving report: {}".format(merged_filename))

    return

    # Add group MC_Alla to everyone in MC and now also IO
    for_mc_alla_df = pd.merge(mc_read_df, io_read_df,
        left_on = 'Personnummer',
        right_on = 'Födelsedat./Personnr.',
        #left_on = ['Personnummer','Förnamn','Efternamn'],
        #right_on = ['Födelsedat./Personnr.','Förnamn','Efternamn'],
        how = 'inner',
        suffixes = ('_mc','_io'))

    mc_alla_filename = path_out + timestamp + '_mc_alla_report.xlsx'
    #save_file(mc_alla_filename, merged_df)
    #stats("Saving MC_Alla report: {}".format(mc_alla_filename))

def compare_persons(mc_file_name, io_file_name):
    """
    Compare persons by personnummer, firstname and lastname
    """
    mc_read_df = pd.read_excel(mc_file_name, 
        #usecols = ['Förnamn','Efternamn','Personnummer','MedlemsID'],
        dtype = {'Förnamn': 'string','Efternamn': 'string','MedlemsID': 'string'},
        converters = {'Personnummer':convert_mc_personnummer_to_io})
    mc_read_df['Personnummer'] = mc_read_df['Personnummer'].astype('string')
    stats("Antal inlästa från MC: {:>4} ({})".format(str(len(mc_read_df)), Path(mc_file_name).name))

    io_read_df = pd.read_excel(io_file_name, 
        #usecols = ['Förnamn','Efternamn','Födelsedat./Personnr.','Övrig medlemsinfo', 'Medlemsnr.', 'Grupp/Lag/Arbetsrum/Familj'],
        dtype = {'Förnamn': 'string','Efternamn': 'string','Födelsedat./Personnr.': 'string', 'Medlemsnr.': 'string',
        'Telefon mobil': 'string', 'Telefon bostad': 'string', 'Telefon arbete': 'string', 'Hemtelefon': 'string', 
        'Medlemsnr.': 'string', 'Mobiltelefon': 'string', 'Arbetstelefon': 'string', 'Övrig medlemsinfo': 'string'}) 
    stats("Antal inlästa från IO: {:>4} ({})".format(str(len(io_read_df)), Path(io_file_name).name))

    # Extract MC MedlemsID for all IO members
    io_read_df['MC_MedlemsID'] = [search_medlemsid_from_io(comment, medlemsnr)
        for comment, medlemsnr 
        in zip (io_read_df['Övrig medlemsinfo'], io_read_df['Medlemsnr.'])]
    # Set correct dtype
    io_read_df['MC_MedlemsID'] = io_read_df['MC_MedlemsID'].astype('string')

    # Merge on matching MedlemsID
    merged_df = pd.merge(mc_read_df, io_read_df,
        left_on = 'MedlemsID',
        right_on = 'MC_MedlemsID',
        how = 'inner',
        suffixes = ('_mc','_io'),
        indicator = True)
    #merged_df['Kopior'] = merged_df.duplicated(keep=False) 
    stats("Antal mergade: {:>8}".format(len(merged_df)))

    stats("Antal endast i MC: {:>8}".format(str(len(merged_df.loc[merged_df['_merge'] == 'left_only' ]))))
    stats("Antal endast i IO: {:>8}".format(str(len(merged_df.loc[merged_df['_merge'] == 'right_only' ]))))
    stats("Antal i båda:      {:>8}".format(str(len(merged_df.loc[merged_df['_merge'] == 'both' ]))))

    # Add comparison columns
    merged_df['Jmf Förnamn'] = np.where(merged_df['Förnamn_mc'] == merged_df['Förnamn_io'], True, False)
    merged_df['Jmf Efternamn'] = np.where(merged_df['Efternamn_mc'] == merged_df['Efternamn_io'], True, False)
    merged_df['Jmf Personnummer'] = np.where(merged_df['Personnummer'] == merged_df['Födelsedat./Personnr.'], True, False)
    
    merged_df['Jmf Volleyboll'] = [verify_group(mc_value, io_value, "MC_Volleyboll", "Volleyboll")
        for mc_value, io_value in zip (merged_df['Alla grupper'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]

    merged_df['Jmf Orientering'] = [verify_group(mc_value, io_value, "MC_OL", "Orientering")
        for mc_value, io_value in zip (merged_df['Alla grupper'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf Skateboard'] = [verify_group(mc_value, io_value, "MC_Skate", "Skateboard (Chillskate)")
        for mc_value, io_value in zip (merged_df['Alla grupper'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf Fotboll'] = [verify_group(mc_value, io_value, "MC_Fotboll", "Fotboll")
        for mc_value, io_value in zip (merged_df['Alla grupper'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf SACRO'] = [verify_group(mc_value, io_value, "MC_SACRO", "Trampolin (SACRO)")
        for mc_value, io_value in zip (merged_df['Alla grupper'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf Skidor'] = [verify_group(mc_value, io_value, "MC_Skidor", "Skidor")
        for mc_value, io_value in zip (merged_df['Alla grupper'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf Skidor'] = [verify_group(mc_value, io_value, "MC_MTB", "MTB")
        for mc_value, io_value in zip (merged_df['Alla grupper'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]

    merged_df['Jmf Skidor'] = [verify_group(mc_value, io_value, "MC_Huvudsektion", "Huvudsektion")
        for mc_value, io_value in zip (merged_df['Alla grupper'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]

    merged_df['Jmf Cirkusledarutbildning'] = [verify_special_cols(mc_value, io_value, "MC_Cirkusledarutbildning", "Ja")
        for mc_value, io_value in zip (merged_df['Cirkusledarutbildning'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf FrisksportlöfteJa'] = [verify_special_cols(mc_value, io_value, "MC_FrisksportlöfteJa", "Ja")
        for mc_value, io_value in zip (merged_df['Frisksportlöfte'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf FrisksportlöfteNej'] = [verify_special_cols(mc_value, io_value, "MC_FrisksportlöfteNej", "Nej")
        for mc_value, io_value in zip (merged_df['Frisksportlöfte'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf Hedersmedlem'] = [verify_special_cols(mc_value, io_value, "MC_Hedersmedlem", "Ja")
        for mc_value, io_value in zip (merged_df['Hedersmedlem'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf Ingen tidning tack'] = [verify_special_cols(mc_value, io_value, "MC_IngenTidning", "Ja")
        for mc_value, io_value in zip (merged_df['Ingen tidning tack'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf Frisksportutbildning Basic'] = [verify_special_cols(mc_value, io_value, "MC_FrisksportutbildningBasic", "Frisksport Basic (grundledarutbildning)")
        for mc_value, io_value in zip (merged_df['Frisksportutbildning'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf Frisksportutbildning Steg 1'] = [verify_special_cols(mc_value, io_value, "MC_FrisksportutbildningSteg1", "Ledarutbildning steg 1")
        for mc_value, io_value in zip (merged_df['Frisksportutbildning'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf Trampolinutbildning Steg 1'] = [verify_special_cols(mc_value, io_value, "MC_TrampolinutbildningSteg1", "Steg 1")
        for mc_value, io_value in zip (merged_df['Trampolinutbildning'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    
    merged_df['Jmf Trampolinutbildning Steg 2'] = [verify_special_cols(mc_value, io_value, "MC_TrampolinutbildningSteg2", "Steg 2")
        for mc_value, io_value in zip (merged_df['Trampolinutbildning'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]

    if False:
        # Colorise mismatches
        def mark_mismatches(x):
            return ['background-color: red']
            #return ['background-color: red' if x == 'FALSE' else '']
        merged_df.style.apply(mark_mismatches, subset=['Jmf Cirkusledarutbildning','Jmf Efternamn','Jmf FrisksportlöfteJa',
            'Jmf FrisksportlöfteNej','Jmf Frisksportutbildning Basic','Jmf Frisksportutbildning Steg 1',
            'Jmf Förnamn','Jmf Hedersmedlem','Jmf Ingen tidning tack','Jmf Personnummer',
            'Jmf Trampolinutbildning Steg 1','Jmf Trampolinutbildning Steg 2'])

    compare_persons_file = path_out + timestamp + '_compare_matching_persons.xlsx'
    save_file(compare_persons_file, merged_df, True)
    stats("Saved compare persons report: {}".format(compare_persons_file))

    if False:
        def get_different_rows(source_df, new_df):
            """Returns just the rows from the new dataframe that differ from the source dataframe"""
            merged_df = source_df.merge(new_df, indicator=True, how='outer')
            changed_rows_df = merged_df[merged_df['_merge'] == 'right_only']
            return changed_rows_df.drop('_merge', axis=1)

        # Compare
        mc_partial_df = merged_df[['Förnamn_mc','Efternamn_mc','Personnummer','MedlemsID']].copy()
        mc_partial_df.rename(columns = {'Förnamn_mc':'Förnamn', 'Efternamn_mc':'Efternamn'}, inplace=True)
        io_partial_df = merged_df[['Förnamn_io','Efternamn_io','Födelsedat./Personnr.','MC_MedlemsID']].copy()
        io_partial_df.rename(columns = {'Förnamn_io':'Förnamn', 'Efternamn_io':'Efternamn', 'Födelsedat./Personnr.':'Personnummer','MC_MedlemsID':'MedlemsID'}, inplace=True)
        #print(mc_partial_df.columns)
        #print(io_partial_df.columns)
        print(mc_partial_df.info())
        print(io_partial_df.info())
        #print(mc_partial_df.dtypes)
        #print(io_partial_df.dtypes)
        #df = mc_partial_df.compare(io_partial_df, align_axis=0)
        #print(df)

        diff_df = get_different_rows(mc_partial_df, io_partial_df)
        print(diff_df)


# Action 
print(" Start ".center(80, "-"))

if "compare" == cmd:
    compare_mc_and_io(mc_file, io_file)
elif "compare_persons" == cmd:
    compare_persons(mc_file, io_file)

print ("Tidsåtgång: " + str(round((time.time() - start_time),1)) + " s")
print((" Klart (" + strftime("%Y-%m-%d %H:%M") + ") ").center(80, "-"))
