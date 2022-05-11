import pandas as pd

import nltk
from nltk.corpus import wordnet
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import WordNetLemmatizer

import spacy
from spacy.matcher import Matcher

from thefuzz import fuzz, process

# set pandas to display all rows
pd.set_option('display.max_rows', None)

lemmatizer = WordNetLemmatizer()
stemmer = LancasterStemmer()

def root_words(string):
    wrds = nltk.word_tokenize(string)
    roots = [lemmatizer.lemmatize(word.lower()) for word in wrds]
    #roots = [stemmer.stem(word.lower()) for word in wrds]
    return roots

def get_synonyms(string):
    synonyms = []
    for syn in wordnet.synsets(string):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
    res = []
    for syn in synonyms:
        if '_' in syn:
            res.extend(syn.split('_'))
            #res.append(' '.join(syn.split('_')))
        else:
            res.append(syn)
    return res


def closest_matches(df1, df2):
    src1 = df1.name.to_list()
    src2 = df2.name.to_list()

    src1_dict = df1.name.to_dict()
    src2_dict = dict([(value, key) for key, value in src1_dict.items()])

    src2_dict = df2.name.to_dict()
    src2_dict = dict([(value, key) for key, value in src2_dict.items()])

    matched_ids = []
    matched_names_ids = []
    def get_match(src1, src2):
        for item in src1:
            best_match = process.extractOne(item, src2, scorer=fuzz.partial_token_sort_ratio)
            confidence = best_match[1]
            if confidence == 100:
                src1_item_id = src1_dict[item]

                src2_item = best_match[0]
                src2_item_id = src2_dict[src2_item]

                matched_ids.append(dict(source_1=src1_item_id, source_2=src2_item_id))
                df_ids = pd.DataFrame(matched_ids)
                df_ids.to_csv('matched_ids.csv')

                matched_names_ids.append(dict(id1=src1_item_id, source_1=item, id2=src2_item_id,source_2=src2_item))
                df_names_ids = pd.DataFrame(matched_names_ids)
                df_names_ids.to_csv('matched_names_ids.csv')

                src1.remove(item)
                src2.remove(src2_item)

                print(df_names_ids)
                return get_match(src1, src2)
            else:
                continue
    return matched_ids, matched_names_ids

#df_matched = pd.read_csv('matched_data.csv')
df_s1 = pd.read_csv('source_1.csv')
df_s2 = pd.read_csv('source_2.csv')

closest_matches(df_s1, df_s2)

