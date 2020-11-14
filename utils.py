# Utility functions
import re
import pandas as pd
import numpy as np

def convert_personnummer(mc_pnr):
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
    Convert Groups in MC to group to use in IO - always with prefix "MC_"
    """
    # Split on ,
    result = ""
    for grp in groups_str.split(','):
        result += ", " + one_mc_groupto_io(grp)
    if result.startswith(", "):
        result = result[2:]
    return result

def one_mc_groupto_io(single_group):
    """
    Convert one singel group from MC to IO
    """
    prefix = "MC_"
    g = str(single_group).strip()
    if g == "Trampolin (SACRO)":
        return prefix + "SACRO"
    elif g == "Orientering":
        return prefix + "OL"
    elif g == "Fotboll":
        return prefix + "Fotboll"
    elif g == "Volleyboll":
        return prefix + "Volleyboll"
    elif g == "Skateboard (Chillskate)":
        return prefix + "Skate"
    elif g == "Medlemmar":
        return prefix + "Medlemmar"
    elif g == "MTB":
        return prefix + "MTB"
    elif g.lower() == "styrelsen":
        return "Styrelse SFK"
    elif g == "Huvudsektion":
        return prefix + "Huvudsektion"
    elif g == "Senior":
        return "Senior"
    elif g == "Innebandy":
        return prefix + "Innebandy"
    elif g == "Skidor":
        return prefix + "Skidor"
    else:
        return prefix + g

def simple_lower(x):
    """
    Convert to lower, if string
    """
    return x if type(x)!=str else x.lower()

def concat_special_cols(groups, cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb):
    """
    Concatinate special columns into one, comma-separated list of strings
    """
    result = [ str.strip(grp) for grp in groups.split(",") ]
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
    result.sort()
    if len(result) > 0:
        return ", ".join(result)
    else:
        return ""