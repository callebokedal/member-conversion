# pylint: disable=import-error
import pandas as pd 
import numpy as np
from utils import concat_special_cols, verify_special_cols


df = pd.DataFrame({'Grupper':['Trampolin (SACRO)', 'Medlemmar,Orientering', 'Fotboll', 'Medlemmar,Orientering', 'Medlemmar,Orientering', 'Medlemmar,Skateboard (Chillskate)', 'Medlemmar,Trampolin (SACRO)', 'Medlemmar,Orientering', 'Fotboll,Medlemmar', 'Fotboll,Medlemmar', 'Fotboll,Medlemmar', 'Medlemmar,Orientering', 'Fotboll', 'Volleyboll'], 
 #'Cirkusledarutbildning':['Nej','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej'], 
 'Frisksportlöfte':['Nej','Nej','Ja','Nej','Nej','Ja','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej'],
 'Hedersmedlem': ['Nej','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej','Nej','Ja','Ja','Nej','Nej'],
 'Ingen tidning tack': ['Nej','Nej','Nej','Nej', pd.NA,'Ja','','Nej','Nej','Nej','Ja','Nej','Nej','Nej'],
 #'Frisksportutbildning': ['Ja','Ja','Ja','Nej','Nej','Ja','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej'],
 #'Trampolinutbildning': ['Nej','Nej','Nej','Nej','','Ja','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej'],
 #'Avgift': ['Nej','Nej','Nej','Nej','','Ja','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej'],
 'Grupp': ['MC_FrisksportlöfteJa, MC_IngenTidning','MC_FrisksportlöfteJa','MC_FrisksportlöfteJa, MC_IngenTidning','MC_FrisksportlöfteNej','','MC_FrisksportlöfteJa','MC_FrisksportlöfteNej','MC_FrisksportlöfteJa','MC_FrisksportlöfteJa','MC_FrisksportlöfteJaJa, Nej','Ja','Nej','MC_FrisksportlöfteNej','Nej']})

print(" Start ".center(80, "-"))

# Verify special cols
df['Jmf FrisksportlöfteJa'] = [verify_special_cols(mc_value, io_value, "MC_FrisksportlöfteJa", "Ja")
    for mc_value, io_value
    in zip (df['Frisksportlöfte'], df['Grupp'])]

df['Jmf FrisksportlöfteNej'] = [verify_special_cols(mc_value, io_value, "MC_FrisksportlöfteNej", "Nej")
    for mc_value, io_value
    in zip (df['Frisksportlöfte'], df['Grupp'])]

df['Jmf Ingen tidning tack'] = [verify_special_cols(mc_value, io_value, "MC_IngenTidning", "Ja")
    for mc_value, io_value
    in zip (df['Ingen tidning tack'], df['Grupp'])]

print(df)

print("---")

#print(verify_special_cols("Nej", 
#    "MC_SACRO, MC_FrisksportlöfteNej, MC_TrampolinutbildningSteg1, MC_Medlemsavgift_2020, MC_Medlemmar, MC_Uppdaterad, EpostUppdaterad, MC_GruppViaMC, MC_Alla",
#    "MC_FrisksportlöfteNej",
#    "Nej"))


"""
    merged_df['Jmf FrisksportlöfteJa'] = [verify_special_cols(mc_value, io_value, "MC_FrisksportlöfteJa")
        for mc_value, io_value
        in zip (merged_df['Frisksportlöfte'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
    merged_df['Jmf FrisksportlöfteNej'] = [verify_special_cols(mc_value, io_value, "MC_FrisksportlöfteNej", "Nej")
        for mc_value, io_value
        in zip (merged_df['Frisksportlöfte'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
"""

assert (False == verify_special_cols("Ja", 
    "MC_SACRO, MC_FrisksportlöfteNej, MC_TrampolinutbildningSteg1, MC_Medlemsavgift_2020, MC_Medlemmar, MC_Uppdaterad, EpostUppdaterad, MC_GruppViaMC, MC_Alla",
    "MC_FrisksportlöfteNej",
    "Nej")), "Frisksportlöfte Ja i MC och MC_FrisksportlöfteNej i IO"

assert (True == verify_special_cols("Nej", 
    "MC_SACRO, MC_FrisksportlöfteNej, MC_TrampolinutbildningSteg1, MC_Medlemsavgift_2020, MC_Medlemmar, MC_Uppdaterad, EpostUppdaterad, MC_GruppViaMC, MC_Alla",
    "MC_FrisksportlöfteNej",
    "Nej")), "Frisksportlöfte Nej i MC och MC_FrisksportlöfteNej i IO"

assert (False == verify_special_cols("Nej",
    "MC_SACRO, MC_FrisksportlöfteJa, MC_TrampolinutbildningSteg1, MC_Medlemsavgift_2020, MC_Medlemmar, MC_Uppdaterad, EpostUppdaterad, MC_GruppViaMC, MC_Alla",
    "MC_FrisksportlöfteJa",
    "Ja")), "Frisksportlöfte Nej i MC och MC_FrisksportlöfteJa i IO"

assert (True == verify_special_cols("Ja", 
    "MC_SACRO, MC_FrisksportlöfteJa, MC_TrampolinutbildningSteg1, MC_Medlemsavgift_2020, MC_Medlemmar, MC_Uppdaterad, EpostUppdaterad, MC_GruppViaMC, MC_Alla",
    "MC_FrisksportlöfteJa",
    "Ja")), "Frisksportlöfte Ja i MC och MC_FrisksportlöfteJa i IO"

assert (verify_special_cols("Ja", 
    "MC_SACRO, MC_FrisksportlöfteJa, MC_TrampolinutbildningSteg1, MC_Medlemsavgift_2020, MC_Medlemmar, MC_Uppdaterad, EpostUppdaterad, MC_GruppViaMC, MC_Alla",
    "MC_FrisksportlöfteJa",
    "Ja")), "Frisksportlöfte Ja i MC och MC_FrisksportlöfteJa i IO"

assert (False == verify_special_cols("Ja", 
    "MC_SACRO, MC_FrisksportlöfteNej, MC_TrampolinutbildningSteg1, MC_Medlemsavgift_2020, MC_Medlemmar, MC_Uppdaterad, EpostUppdaterad, MC_GruppViaMC, MC_Alla",
    "MC_FrisksportlöfteJa",
    "Ja")), "Frisksportlöfte Ja i MC och MC_FrisksportlöfteNej i IO"

assert (True == verify_special_cols("Steg 1", 
    "MC_SACRO, MC_FrisksportlöfteNej, MC_FrisksportutbildningSteg1, MC_Medlemsavgift_2020, MC_Medlemmar, MC_Uppdaterad, EpostUppdaterad, MC_GruppViaMC, MC_Alla",
    "MC_FrisksportutbildningSteg1",
    "Steg 1")), "Frisksportutbildning 'Steg 1' i MC och 'MC_FrisksportutbildningSteg1' i IO"

assert (False == verify_special_cols("Steg 1", 
    "MC_SACRO, MC_FrisksportlöfteNej, MC_Medlemsavgift_2020, MC_Medlemmar, MC_Uppdaterad, EpostUppdaterad, MC_GruppViaMC, MC_Alla",
    "MC_FrisksportutbildningSteg1",
    "Steg 1")), "Frisksportutbildning 'Steg 1' i MC och 'MC_FrisksportutbildningSteg1' saknas i IO"

assert (False == verify_special_cols("Steg 2", 
    "MC_SACRO, MC_FrisksportlöfteNej, MC_FrisksportutbildningSteg2, MC_Medlemsavgift_2020, MC_Medlemmar, MC_Uppdaterad, EpostUppdaterad, MC_GruppViaMC, MC_Alla",
    "MC_FrisksportutbildningSteg1",
    "Steg 2")), "Frisksportutbildning 'Steg 2' i MC men 'MC_FrisksportutbildningSteg1' i IO"

assert (False == verify_special_cols("Steg 1", 
    "MC_SACRO, MC_FrisksportlöfteNej, MC_Medlemsavgift_2020, MC_Medlemmar, MC_Uppdaterad, EpostUppdaterad, MC_GruppViaMC, MC_Alla",
    "MC_FrisksportutbildningSteg1",
    "Steg 1")), "Frisksportutbildning 'Steg 1' i MC och 'MC_FrisksportutbildningSteg1' saknas i IO"

assert (verify_special_cols("Ledarutbildning steg 1", 
    "MC_Cirkusledarutbildning, MC_FrisksportlöfteJa, MC_FrisksportutbildningSteg1",
    "MC_FrisksportutbildningSteg1",
    "Ledarutbildning steg 1")), "Frisksportutbildning 'Steg 1' i MC och 'MC_FrisksportutbildningSteg1' i IO"

assert (False == verify_special_cols("Ledarutbildning bla", 
    "MC_Cirkusledarutbildning, MC_FrisksportlöfteJa, MC_FrisksportutbildningSteg1",
    "MC_FrisksportutbildningSteg1",
    "Ledarutbildning steg 1")), "Frisksportutbildning 'Steg 1' i MC och 'MC_FrisksportutbildningSteg1' i IO"


"""
    merged_df['Jmf Frisksportutbildning Steg 1'] = [verify_special_cols(mc_value, io_value, "MC_FrisksportutbildningSteg1", "Ledarutbildning steg 1")
        for mc_value, io_value
        in zip (merged_df['Frisksportutbildning'], merged_df['Grupp/Lag/Arbetsrum/Familj'])]
"""

print(" Done ".center(80, "-"))