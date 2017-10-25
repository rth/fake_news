# -*- coding: utf-8 -*-

import numpy as np
import string, unicodedata

import pandas as pd
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.utils.validation import check_is_fitted
from sklearn.preprocessing import OneHotEncoder

from sklearn.preprocessing import MaxAbsScaler
        
MAX_SENT_LENGTH = 100
MAX_SENTS = 2

def clean_str(sentence, stem=True):
    english_stopwords = set([stopword for stopword in stopwords.words('english')])
    punctuation = set(string.punctuation)
    punctuation.update(["``", "`", "..."])
    if stem:
        stemmer = SnowballStemmer('english')
        return list((filter(lambda x: x.lower() not in english_stopwords and 
            x.lower() not in punctuation, 
            [stemmer.stem(t.lower()) for t in word_tokenize(sentence) if t.isalpha()])))
    print('>>', list((filter(lambda x: x.lower() not in english_stopwords and 
        x.lower() not in punctuation, 
        [t.lower() for t in word_tokenize(sentence) if t.isalpha()]))))
    return list((filter(lambda x: x.lower() not in english_stopwords and 
        x.lower() not in punctuation, 
        [t.lower() for t in word_tokenize(sentence) if t.isalpha()])))

        
def strip_accents_unicode(s):
    try:
        s = unicode(s, 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass
    s = unicodedata.normalize('NFD', s)
    s = s.encode('ascii', 'ignore')
    s = s.decode("utf-8")
    return str(s)


def _clean_statement_nan(statement):
    statement = statement.copy()
    mask = pd.isnull(statement)
    statement[mask] = ''
    return statement


class FeatureExtractor(TfidfVectorizer):
    """Convert a collection of raw documents to a matrix of TF-IDF features.

    Equivalent to CountVectorizer followed by TfidfTransformer.
    """
    
    def __init__(self):

        super(FeatureExtractor, self).__init__(
            input='content', encoding='utf-8',
                 decode_error='strict', strip_accents=None, lowercase=True,
                 preprocessor=None, tokenizer=None, analyzer='word',
                 stop_words=None, token_pattern=r"(?u)\b\w\w+\b",
                 ngram_range=(1, 1), max_df=1.0, min_df=1,
                 max_features=None, vocabulary=None, binary=False,
                 dtype=np.int64, norm='l2', use_idf=True, smooth_idf=True,
                 sublinear_tf=False)

        self._one_hot = OneHotEncoder()
        self._scaler = MaxAbsScaler()
        
    def fit(self, X_df, y=None):
        """Learn a vocabulary dictionary of all tokens in the raw documents.
        Parameters
        ----------
        raw_documents : iterable
            An iterable which yields either str, unicode or file objects.
        Returns
        -------
        self
        """
        #self._feat = np.array([' '.join(clean_str(text.strip_accents_unicode(dd)))
        #            for dd in X_df.statement])
        self._feat = True
        statement = _clean_statement_nan(X_df.statement)

        super(FeatureExtractor, self).fit(statement)

        return self
        
    def fit_transform(self, X_df, y=None):
        
        self.fit(X_df)
        statement = _clean_statement_nan(X_df.statement)

        return self.transform(statement)
        
    def transform(self, X_df):
        
        #X = np.array([' '.join(clean_str(text.strip_accents_unicode(dd))) 
        #            for dd in X_df.statement])

        check_is_fitted(self, '_feat', 'The tfidf vector is not fitted')
        statement = _clean_statement_nan(X_df.statement)

        X = super(FeatureExtractor, self).transform(statement)

        return X
