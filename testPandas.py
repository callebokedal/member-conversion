import pandas as pd 
import numpy as np
from utils import concat_special_cols

df = pd.DataFrame({'A': ['A0', 'A1', 'A2'],
    'B': ['B0', 'B1', 'B2'],
    'C': ['C0', 'C1', 'C2']},
    index=pd.Index(['K0', 'K1', 'K2'], name='key'))

df2 = df.copy()

#     io_current_df['E-post arbete'] = io_current_df['E-post arbete'].map(lambda x: x if type(x)!=str else x.lower())
def to_lower(val,d):
    """
    Test of lowercase
    """
    return val + "-" + str(d)

df['A'] = df['A'].apply(to_lower, args=(4,))
df['B'] = df['A'].apply(to_lower, args=("A",))
print(df)


#     io_current_df['E-post arbete'] = io_current_df['E-post arbete'].map(lambda x: x if type(x)!=str else x.lower())
def test2(val,d):
    """
    Test of lowercase
    """
    #print(d)
    #print(type(d))
    return val + "-" + str(d)

df2['A'] = df2['A'].apply(test2, args=("",))
#df2['B'] = df2['A'].apply(test2, args=("A",))
df2['B'] = df2['A'].apply(test2, args=(df2['B'],))
print(df2)


# creating a DataFrame 
df = pd.DataFrame({'Integers' :[1, 2, 3, 4, 5], 
				'Float' :[1.1, 2.2, 3.3, 4.4 ,5.5]}) 

# displaying the DataFrame 
print(df) 

# function for prepending 'Geek' 
def multiply_by_2(number): 
	return 2 * number 

# executing the function 
df[["Integers", "Float"]] = df[["Integers", "Float"]].apply(multiply_by_2) 

# displaying the DataFrame 
print(df) 

df = pd.DataFrame({'species': ['bear', 'bear', 'marsupial'],
    'something': ['a','b','c'],
    'population': [1864, 22000, 80000]},
    index=['panda', 'polar', 'koala'])

print(df)
print(df[['population','species']])

print("===")
for a, b in df[['population','species']].items():
    print(f'label: {a}')
    print(f'content: {b}')


print("===")

one = ['a','b','d','e','f']
two = [1,2,3,4,5]
three = [2,0,3,3,2]
tuples = list(zip(one,two,three))
#df = pd.DataFrame(tuples, names=['A','B','C','D','E','F']).T
df = pd.DataFrame(tuples, columns=['A','B','C']).T
print(df)

print("===")

def try_concat(x, y, z):
    try:
        return str(x) + ' is ' + y
    except (ValueError, TypeError):
        return np.nan

df = pd.DataFrame({'foo':['a','b','c'], 'bar':[1, 2, 3], 'hoho':[1, 2, 3]})
df['foo'] = [try_concat(x, y, z) for x, y, z in zip(df['bar'], df['foo'], df['hoho'])]

print(df)

print("===")

def concat_special_cols_old(groups, cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb):
    """
    Concatinate special columns into one, comma-separated list of strings
    """
    result = [ str.strip(grp) for grp in groups.split(",") ]
    if cirkusutb == "Ja":
        result.append("MC_Cirkusledarutbildning")
    if frisksportlofte == "Ja":
        result.append("MC_FrisksportlöfteJa")
    if frisksportlofte == "Nej":
        result.append("MC_FrisksportlöfteNej")
    if hedersmedlem == "Ja":
        result.append("MC_Hedersmedlem")
    if ingen_tidning == "Ja":
        result.append("MC_IngenTidning")
    if frisksportutb == "Frisksport Basic (grundledarutbildning)":
        result.append("MC_FrisksportutbildningBasic")
    if frisksportutb == "Ledarutbildning steg 1":
        result.append("MC_FrisksportutbildningSteg1")
    if trampolinutb == "Steg 1":
        result.append("MC_TrampolinutbildningSteg1")
    if trampolinutb == "Steg 2":
        result.append("MC_TrampolinutbildningSteg2")
    if len(result) > 0:
        return ", ".join(result)
    else:
        return ""

df = pd.DataFrame({'Grupper':['Trampolin (SACRO)', 'Medlemmar,Orientering', 'Fotboll', 'Medlemmar,Orientering', 'Medlemmar,Orientering', 'Medlemmar,Skateboard (Chillskate)', 'Medlemmar,Trampolin (SACRO)', 'Medlemmar,Orientering', 'Fotboll,Medlemmar', 'Fotboll,Medlemmar', 'Fotboll,Medlemmar', 'Medlemmar,Orientering', 'Fotboll', 'Volleyboll'], 
 'Cirkusledarutbildning':['Nej','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej'], 
 'Frisksportlöfte':['Nej','Nej','Ja','Nej','Nej','Ja','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej'],
 'Hedersmedlem': ['Nej','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej','Nej','Ja','Ja','Nej','Nej'],
 'Ingen tidning tack': ['Nej','Nej','Nej','Nej','Nej','Ja','','Nej','Nej','Nej','Ja','Nej','Nej','Nej'],
 'Frisksportutbildning': ['Ja','Ja','Ja','Nej','Nej','Ja','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej'],
 'Trampolinutbildning': ['Nej','Nej','Nej','Nej','','Ja','Nej','Nej','Nej','Nej','Ja','Nej','Nej','Nej']})
print(df)
df['Grupper'] = [concat_special_cols(groups, cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb) 
    for groups, cirkusutb, frisksportlofte, hedersmedlem, ingen_tidning, frisksportutb, trampolinutb 
    in zip(df['Grupper'], df['Cirkusledarutbildning'], df['Frisksportlöfte'], df['Hedersmedlem'], df['Ingen tidning tack'], df['Frisksportutbildning'], df['Trampolinutbildning'])]


print(df)


