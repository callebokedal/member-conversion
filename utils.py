# Utility functions
import re
import pandas as pd
import numpy as np

from families import families

def convert_mc_personnummer_to_io(mc_pnr):
    """
    Convert Personnummer of format "yyyymmddnnnn" to "yyyymmdd-nnnn". Also handle case "yyyymmdd".
    IO use this format
    """
    if len(mc_pnr) == 12:
        return "{}-{}".format(mc_pnr[0:8],mc_pnr[-4:])
    else:
        # Assume as-is ok
        return mc_pnr
    
def convert_postnr(mc_nr):
    """
    Convert Postnummer of format "nnnnn" to "nnn nn"
    IO use this format
    """
    nr = str(mc_nr)
    if nr and len(nr) == 5:
        return "{} {}".format(nr[0:3],nr[-2:])
    else:
        return nr

def normalize_postort(x):
    """
    Normalize Postort, "city somewhere" -> "City Somewhere"
    """
    return x if type(x)!=str else x.title()

def convert_countrycode(country):
    """
    Convert Country code of format "SE" to "Sverige"
    """
    c = str(country)
    if c == "SE":
        return "Sverige"
    elif c == "NO":
        return "Norge"
    elif c == "DE":
        return "Tyskland"
    else:
        return c # As is

def clean_pii_comments(text):
    """
    Clean out Personal Identifiable Information (PII) from text
    """
    starting_pii_1 = r"^\d{4} " # Case: "nnnn other text"
    starting_pii_2 = r"^-\d{4}" # Case: "-nnnn other text"

    if type(text) == type(pd.NA):
        return text

    if text.startswith("20"):
        # Ok - validated manually
        return text
    elif re.match(starting_pii_1, text):
        # Case "nnnn ". Remove first 5 chars
        return text[5:].lstrip()
    elif re.match(starting_pii_2, text):
        # Case "-nnnn". Remove first 5 chars
        return text[5:].lstrip()
    else:
        return text

def convert_mc_groups_to_io_groups(groups_str):
    """
    Convert Groups in MC to group to use in IO 
    """
    # Split on ,
    result = []
    for grp in groups_str.split(','):
        group_id = one_mc_groupto_io(grp)
        if group_id:
            result.append(group_id)
    #if result.startswith(", "):
    #    result = result[2:]
    if len(result) > 0:
        return ", ".join(result)
    else:
        return ""

def one_mc_groupto_io(single_group):
    """
    Convert one single group from MC to IO GroupID
    """
    g = str(single_group).strip()    
    if g == "Trampolin (SACRO)":
        return "579036" # MC_SACRO
    elif g == "Orientering":
        return "579037" # MC_OL
    elif g == "Fotboll":
        return "579038" # MC_Fotboll
    elif g == "Volleyboll":
        return "579040" # MC_Volleyboll
    elif g == "Skateboard (Chillskate)":
        return "579039" # MC_Skate
    elif g == "Medlemmar":
        return "579396" # MC_Medlemmar TODO: Behövs denna?
    elif g == "MTB":
        return "579397" # MC_MTB
    elif g.lower() == "styrelsen":
        return "578806" # Styrelse SFK
    elif g == "Huvudsektion":
        return "579041" # MC_Huvudsektion
    elif g == "Senior":
        return "579045" # Senior
    elif g == "Innebandy":
        return "579399" # MC_Innebandy
    elif g == "Skidor":
        return "579398" # MC_Skidor
    else:
        #print("Warning - unhandled group: " + g)
        return None

def simply_lower(x):
    """
    Convert to lower, if string
    """
    return x if type(x)!=str else x.lower()

def concat_group_id(groups, group_id):
    """
    Concatinate group_id to already existing groups
    """
    #print(groups)
    #print(group_id)
    result = [ str.strip(grp) for grp in groups.split(",") ]
    #if len(str(group_id)) > 0:
    if not pd.isna(group_id):
        result.append(str(group_id))
    result.sort()
    if len(result) > 0:
        return ", ".join(result)
    else:
        return ""

def concat_special_cols(groups, cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb, avgift):
    """
    Concatinate special columns into one, comma-separated list of strings
    """
    result = [ str.strip(grp) for grp in groups.split(",") ]
    result.append("579010") # Always append MC_Import
    if cirkusutb == "Ja":
        result.append("579058") # MC_Cirkusledarutbildning
    if frisksportlofte == "Ja":
        result.append("579061") # MC_FrisksportlöfteJa
    if frisksportlofte == "Nej":
        result.append("579062") # MC_FrisksportlöfteNej
    if hedersmedlem == "Ja":
        result.append("579065") #M C_Hedersmedlem
    if ingen_tidning == "Ja":
        result.append("579035") # MC_IngenTidning
    if frisksportutb == "Frisksport Basic (grundledarutbildning)":
        result.append("579069") # MC_FrisksportutbildningBasic
    if frisksportutb == "Ledarutbildning steg 1":
        result.append("579068") # MC_FrisksportutbildningSteg1
    if trampolinutb == "Steg 1":
        result.append("579071") # MC_TrampolinutbildningSteg1
    if trampolinutb == "Steg 2":
        result.append("579072") # MC_TrampolinutbildningSteg2
    if avgift == "Medlemsavgift 2020":
        result.append("579384") # MC_Medlemsavgift_2020

    result.sort()
    if len(result) > 0:
        return ", ".join(result)
    else:
        return ""

def add_import_group(p):
    """
    Add additional groups for person
    MC_Import: 579010
    """
    pass

_MC_GROUPS = [(26905, 31, 'Fotboll'),
(26914, 40, 'Huvudsektion'),
(28612, 192, 'Innebandy'),
(26875, 1, 'Medlemmar'),
(31196, 197, 'MIS'),
(35906, 253, 'MTB'),
(26883, 9, 'Orientering'),
(26916, 42, 'Senior'),
(26937, 63, 'Skateboard (Chillskate)'),
(26876, 2, 'Skidor'),
(26938, 64, 'styrelsen'),
(26949, 75, 'Trampolin (SACRO)'),
(26913, 39, 'Volleyboll')]

def mc_family_to_id(name):
    """
    Convert My Club family name to IO Group id

    Real names hidden from github
    families = [('Lastname [123]','123456'),
        ('Ohter name [456]','123457'),
        ...
    """
    #print(name)
    if not pd.isna(name):
        name = re.sub(r'.*\[', '[', name) # Name skipped due to encoding issue risk
        if name in families:
            return families[name]
    return None


#print(mc_family_to_id("Andersson [24151]"))
#print(mc_family_to_id("Whatever [24151]"))
#print(mc_family_to_id("Foo [14202]"))
#print(mc_family_to_id("Not there [1234567]"))