import numpy as np
import pandas as pd
import re
import tweepy 
from nltk import word_tokenize
from nltk.corpus import stopwords
import string
stop = stopwords.words('english') + list(string.punctuation)
import html,nltk
from nltk.corpus import wordnet 
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from collections import Counter 
from string import digits

from textblob import TextBlob 

API_KEY = consumer_key = "LrJEUbLJ8j4xg3Kd2mLk5959J"
API_SECRET = consumer_secret = "zdnkWwMuP3ke7G3g9MtWsWuGFigik0NIWqDLhyq9OFP1QmmsGX"
ACCESS_TOKEN = access_token = "1279223548482117633-nqJKgr6sF2nkDVh3guPxC4nUzzE4p2"
ACCESS_TOKEN_SECRET = access_token_secret = "Ox15BhZy8jxPjhbZOVFVtgzVI5oqDOevFToP11BzsWy3q"


def flatten(input_dict, separator='_', prefix=''):
    output_dict = {}
    for key, value in input_dict.items():
        if isinstance(value, dict) and value:
            deeper = flatten(value, separator, prefix+key+separator)
            output_dict.update({key2: val2 for key2, val2 in deeper.items()})
        elif isinstance(value, list) and value:
            for index, sublist in enumerate(value, start=1):
                if isinstance(sublist, dict) and sublist:
                    deeper = flatten(sublist, separator, prefix+key+separator+str(index)+separator)
                    output_dict.update({key2: val2 for key2, val2 in deeper.items()})
                else:
                    output_dict[prefix+key+separator+str(index)] = value
        else:
            output_dict[prefix+key] = value
    return output_dict

def clean_tweet(tweet): 
    ''' 
    Utility function to clean tweet text by removing links, special characters 
    using simple regex statements. 
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 

def get_tweet_sentiment(tweet): 
    ''' 
    Utility function to classify sentiment of passed tweet 
    using textblob's sentiment method 
    '''
    # create TextBlob object of passed tweet text 
    analysis = TextBlob(clean_tweet(tweet))
    return analysis.sentiment.polarity
def get_into_df_profile(di):
    jj = list()
    abc= flatten(di)#searched_tweets[2]._json)
    for i in abc.keys():
        if i.find('indices')==-1: jj.append(i)
    our_dic = {x:abc[x] for x in jj}
    twitter_username_re = re.compile(r'@([A-Za-z0-9_]+)')
    twitter_hashtag_re = re.compile(r'#([A-Za-z0-9_]+)')
    df =  pd.DataFrame(list(our_dic.values()),index=our_dic.keys(),columns=[0]).T
    df['clean_text'] = clean_tweet(df.full_text.values[0]).replace('RT','')
    df['usernames'] = ','.join(twitter_username_re.findall(df.full_text.values[0]))
    df['hashtags'] = ','.join(twitter_hashtag_re.findall(df.full_text.values[0]))
    df['links'] =  ','.join(re.findall(r'(https?://[^\s]+)', df.full_text.values[0]))
    df['sentiment'] = get_tweet_sentiment(df['clean_text'].values[0])
    return df



def get_pos( word ):
    w_synsets = wordnet.synsets(word)

    pos_counts = Counter()
    pos_counts["n"] = len(  [ item for item in w_synsets if item.pos()=="n"]  )
    pos_counts["v"] = len(  [ item for item in w_synsets if item.pos()=="v"]  )
    pos_counts["a"] = len(  [ item for item in w_synsets if item.pos()=="a"]  )
    pos_counts["r"] = len(  [ item for item in w_synsets if item.pos()=="r"]  )
    
    most_common_pos_list = pos_counts.most_common(3)
    return most_common_pos_list[0][0]
def text_cleaning(text, escape_list=[], stop=['could','would']):
    l=[]
    """
    Text cleaning function:
        Input: 
            -text: a string variable, the text to be cleaned
            -escape_list : words not to transform by the cleaning process (only lowcase transformation is needed)  
            -stop : custom stopwords
        Output:
            -text cleaned and stemmed           
    """
    
    """ Get stop word list from package"""
    text=text.lower()
    StopWords = list(set(stopwords.words('english')))
    custom_stop = StopWords + stop
    
    """ Step 1: Parse html entities"""
    text = html.unescape(text)
    text=text.replace('/',' ').replace('?',' ').replace(',',' ').replace('\'',' ')
    
    tokenz=nltk.word_tokenize(text)
    #Tense Removal
    tokenz=([ WordNetLemmatizer().lemmatize( token.lower(), get_pos(token) ) for token in tokenz ]) 
    """ Step 2: Remove stop words """
    tokenz=([token for token in tokenz if token not in custom_stop]) 
    
    """ Step 4: Remove digits from tokens"""
    remove_digits = str.maketrans('', '', digits)
    tokenz=[token.translate(remove_digits)  if token not in  escape_list else token for token in tokenz   ]
    
    """ Step 5: Lowcase the text"""
    tokenz=([token.lower() for token in tokenz])
    """ Step 6: Stemming the text"""
    tokenz=[SnowballStemmer("english").stem(token) if token not in escape_list else token for token in tokenz ]
    
    return ' '.join(tokenz)