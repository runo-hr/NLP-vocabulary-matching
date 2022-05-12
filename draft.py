import pandas as pd

import nltk
from nltk.corpus import wordnet
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import WordNetLemmatizer

import spacy
from spacy.matcher import Matcher

from thefuzz import fuzz, process


# lists to create pandas dataframes
matched_ids = []
matched_names_ids = []
def closest_matches(src1:list, src2:list, names_id_src1:dict, names_id_src2:dict):
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

#print(f'Shape of source_1 : {df1.shape}')
#print(f'Shape of source_2 : {df2.shape}')

# list of items to iterate over.
# Will be modified in every iteration where a match is found
src1 = df1.name.to_list()
src2 = df2.name.to_list()

# name(key), id(value) dictionaries
src1_dict = df1.name.to_dict()
src1_dict = dict([(value, key) for key, value in src1_dict.items()])

src2_dict = df2.name.to_dict()
src2_dict = dict([(value, key) for key, value in src2_dict.items()])

ids_matched, names_ids_matched = closest_matches(src1, src2, src1_dict, src2_dict)