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

matched_data = []
def get_match(source_1, source_2):
    def get_ratios(i, j):
        #print(f"'{i}' vs '{j}'")

        ratio = fuzz.ratio(i, j)
        #print(f"Ratio : {ratio}")

        partial_ratio = fuzz.partial_ratio(root_words(i)[0], j)
        #print(f"Partial Ratio : {partial_ratio}")

        token_sort_ratio = fuzz.token_sort_ratio(i, j)
        #print(f"Token sort Ratio : {token_sort_ratio}")

        token_set_ratio = fuzz.token_set_ratio(i, j)
        #print(f"Token set Ratio : {token_set_ratio}")
        #print()

        return partial_ratio, token_set_ratio

    for i in source_2:
        i = i.strip()
        synonyms = get_synonyms(i) if ' ' not in i else None
        all_synonyms = ''
        if synonyms:
            synonym_str = ' '.join(synonyms)
            all_synonyms = i + ' ' + synonym_str

        for j in source_1:
            partial_ratio, token_set_ratio = get_ratios(i, j)
            if token_set_ratio == 100 or partial_ratio > 80:
                matched_data.append(dict(s1=j, s2=i))
                source_2.remove(i)
                source_1.remove(j)
                return get_match(source_1, source_2)
            if len(all_synonyms) > 0:
                partial_ratio = get_ratios(all_synonyms, j)[0]
                if partial_ratio > 80:
                    matched_data.append(dict(s1=j, s2=i))
                    source_2.remove(i)
                    source_1.remove(j)
                    return get_match(source_1, source_2)
            else:
                continue
    return matched_data

# Matched examples
df_matched = pd.read_csv('matched_data.csv')
df_s1 = pd.read_csv('source_1.csv')
df_s2 = pd.read_csv('source_2.csv')

src_1 = df_matched.source_1.to_list()
src_2 = df_matched.source_2.to_list()
#src_1 = df_s1.name.to_list()
#src_2 = df_s2.name.to_list()

df_data = get_match(src_1, src_2)
df = pd.DataFrame(df_data)
print(df)
df.to_csv('matched_try.csv')