import pandas as pd

#import nltk
#from nltk.corpus import wordnet
#from nltk.stem.lancaster import LancasterStemmer
#from nltk.stem import WordNetLemmatizer

#import spacy
#from spacy.matcher import Matcher

from thefuzz import fuzz, process
import sys
sys.setrecursionlimit(10**6)

# lists to create pandas dataframes
matched_ids = []
matched_names_ids = []
def closest_matches(src1:list, src2:list, names_id_src1:dict, names_id_src2:dict):
    s1_df = pd.DataFrame(src1)
    s1_df.to_csv('remaininder_s1.csv')

    s2_df = pd.DataFrame(src2)
    s2_df.to_csv('remaininder_s2.csv')

    if len(src1) == 0:
        return matched_ids, matched_names_ids
    for item in src1:
        best_match = process.extractOne(item, src2, scorer=fuzz.partial_token_sort_ratio)
        confidence = best_match[1]
        if confidence == 100:
            src1_item_id = names_id_src1[item]

            src2_item = best_match[0]
            src2_item_id = names_id_src2[src2_item]

            matched_ids.append(dict(source_1=src1_item_id, source_2=src2_item_id))
            df_ids = pd.DataFrame(matched_ids)
            df_ids.to_csv('matched_ids.csv')

            matched_names_ids.append(dict(id1=src1_item_id, source_1=item, id2=src2_item_id,source_2=src2_item))
            df_names_ids = pd.DataFrame(matched_names_ids)
            df_names_ids.to_csv('matched_names_ids.csv')

            src1.remove(item)
            src2.remove(src2_item)

            print(df_names_ids)
            print()
            return closest_matches(src1, src2, names_id_src1, names_id_src2)
        else:
            src1.remove(item)
            return closest_matches(src1, src2, names_id_src1, names_id_src2)

#df_matched = pd.read_csv('matched_data.csv')
df1 = pd.read_csv('source_1.csv')
df2 = pd.read_csv('source_2.csv')

df1 = df1[['id', 'name']].set_index('name')
df1.index.name = None
s1_dict = df1.to_dict()['id']

df2 = df2[['id', 'name']].set_index('name')
df2.index.name = None
s2_dict = df2.to_dict()['id']

df_old_matches = pd.read_csv('matched_names_ids.csv')

df1_old = df_old_matches[['id1', 'source_1']].set_index('source_1')
df1_old_dict = df1_old.to_dict()['id1']

df2_old = df_old_matches[['id2', 'source_2']].set_index('source_2')
df2_old_dict = df2_old.to_dict()['id2']

s1 = []
for entry in df1.index.to_list():
    try:
        df1_old_dict[entry]
    except KeyError:
        s1.append(entry)

s2 = []
for entry in df2.index.to_list():
    try:
        df2_old_dict[entry]
    except KeyError:
        s2.append(entry)

ids_matched, names_ids_matched = closest_matches(s1, s2, s1_dict, s2_dict)