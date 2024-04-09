# Summary: Replaced all the NaN with "Others". However, might not be the best solution - why is it 
# evaluating to NaN? seems to be most gxs reviews evaluating to NaN.
# 

import csv
import pandas as pd
import gensim
from gensim import corpora
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from pprint import pprint
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from collections import Counter
from collections import defaultdict
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')

#csv_file = r'./all_app_reviews.csv'
csv_file = r'./My_Bank_Data.csv'

df = pd.read_csv(csv_file)

text_data = df['review'].astype(str)  # Replace 'column_name' with the name of the column containing text data

#######
df.dropna(subset=['review'], inplace=True)
tokenized_review = [word_tokenize(review.lower()) for review in df['review']]
dictionary = Dictionary(tokenized_review)
dictionary.filter_extremes(no_below=10, no_above=0.5)
corpus = [dictionary.doc2bow(tokens) for tokens in tokenized_review]
associated_words = ['application', 'login', 'interface', 'update', 'bug']
lda_model = LdaModel(corpus, num_topics=len(associated_words), passes=10, id2word=dictionary, eta='auto', eval_every=None, iterations=500, alpha='auto', random_state=42)
similarity_df = pd.DataFrame(index=df.index, columns=associated_words)

threshold = 0.1  # Set your threshold value here

for i, review in enumerate(tokenized_review):
    bow = dictionary.doc2bow(review)
    topics = lda_model.get_document_topics(bow)
    for j, word in enumerate(associated_words):
        max_score = 0.0  # Initialize with default probability score
        for topic_id, score in topics:
            if topic_id == j:
                max_score = score
                break  # Exit loop once topic is found
        if max_score < threshold:
            max_score = 0.0  # Assign a default probability score if below threshold
        similarity_df.at[i, word] = max_score


'''
for i, review in enumerate(tokenized_review):
    bow = dictionary.doc2bow(review)
    topics = lda_model.get_document_topics(bow)
    for j, word in enumerate(associated_words):
        similarity_df.at[i, word] = max(score for topic_id, score in topics if topic_id == j)
'''
similarity_df = similarity_df.apply(pd.to_numeric)

df['associated_word'] = similarity_df.idxmax(axis=1)

df = df.drop(df.columns[[1, 2, 3, 4]], axis=1)

df['associated_word'] = df['associated_word'].fillna("others")

print(df)

full_associated_words_list = df['associated_word'].tolist()
#print(full_associated_words_list)

#######

