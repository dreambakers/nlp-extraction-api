from utils import *
import re
import spacy
import sys
nlp = spacy.load("en_core_web_sm")
from spacy import displacy
import pandas as pd


auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)


def fetch_tweets_from_handles(top_covid_handles,cols,savepath = 'Covid_handle_tweets.csv'):
    '''
    Input:
    top_covid_handles : Handles that you want to scrape.
    cols: columns that you want to save from twitter's response
    savepath : path where you want to save the fetched data.
    '''

    limit = 10
    index = 0

    for handle in top_covid_handles:
        try:
            for status in tweepy.Cursor(api.user_timeline, screen_name=handle, tweet_mode="extended").items():
                if (index == limit):
                    break
                get_into_df_profile(status._json)[cols].to_csv(savepath, mode='a',index=False,header=False)
                index +=1
        except:
            pass
    print('Fetching Tweets Completed.')
    return True

def more_text_cleaning(text,stop=['covid-19','count','#covid19','2020']):
    text=text.lower()
    StopWords = list(set(stopwords.words('english')))
    custom_stop = StopWords + stop
    tokenz=nltk.word_tokenize(text)
    tokenz=([token for token in tokenz if token not in custom_stop])
    return ' '.join(tokenz)

def get_regex(line, text_to_find,how_many_chars_inbetween):
    match = re.search(fr'{text_to_find}[a-z\D]{{0,{how_many_chars_inbetween}}}(\d+)', line.lower().replace(',',''))
    if match: return match.group(1)
    return None
def get_regex_front(line, text_to_find,how_many_chars_inbetween):
    match = re.search(fr'(\d+) {text_to_find}', line.lower().replace(',',''))
    if match: return match.group(1)
    return None

def extract_all_info(line_sent_str,infos_for_extraction = ['case','death','hospital','negative',]):
    info_to_extract = infos_for_extraction.copy()
    line_sent = line_sent_str.lower()
    stop_words = ['#covid19','2020','covid-19','2019']
    for stop in stop_words:
        line_sent = line_sent.replace(stop,'')
    line = line_sent
    info_dict = {}
    try:
        for line in line_sent.split('/n'):
            doc = nlp(line)
            for token in doc:
                loop_line = token.head.text +' '+ token.text
                for z in info_to_extract:
                    loop_extract = get_regex(loop_line,z,10)
                    if pd.notna(loop_extract):
                        info_dict[z] = loop_extract
                        info_to_extract.remove(z)

            line = more_text_cleaning(line)

            for i in info_to_extract:
                loop_extract = get_regex(line,i,20)
                if pd.notna(loop_extract):
                    info_dict[i] = loop_extract
                    info_to_extract.remove(z)
            for i in info_to_extract:
                loop_extract = get_regex_front(line,i,20)
                if pd.notna(loop_extract):
                    info_dict[i] = loop_extract
                    info_to_extract.remove(z)
    except:
        pass
    finally:
#         if len(info_dict)>0:
#             print(line_sent_str)
#             print('--'*50)
#             print(info_dict)
#             print('--'*50)
        return info_dict

def get_covid_or_not(data):
    '''
    This function takes the entire dataframe and returns only the covid related rows.
    '''
    df = data.copy()
    df['is_covid'] = df.full_text.apply(lambda x:True if x.lower().find('covid')!=-1 else False).dropna()
    df1 = df[df.is_covid==True].reset_index(drop=True)
    return df1

def extract_possible_features(df1,infos_for_extraction=['case','death','hospital','negative',], savepath='Information_extracted_tweets2.csv'):
    '''
    Input:
    dataframe
    informations to extract
    Path to save the file.

    output:
    Returns the dataframe with extracted informations
    '''
    info_to_extract = infos_for_extraction.copy()
    infos = df1['full_text'].apply(lambda x: extract_all_info(x,info_to_extract))

    for i in info_to_extract:
        df1[i] = infos.apply(lambda x: x[i] if i in x.keys() else None)
    not_na_index = df1[info_to_extract].dropna(how='all').index
    df1[['full_text']+info_to_extract].iloc[not_na_index,:].to_csv(savepath,index=False)
    return df1[['full_text']+info_to_extract].iloc[not_na_index,:]


def part_1(df,info_to_extract, savepath):
    df1 = get_covid_or_not(df)
    extracted_df = extract_possible_features(df1,info_to_extract, savepath)
    return extracted_df


def clean_updates(text):
    text = clean_tweet(text)
    text = text_cleaning(text)
    text = text.lower()
    text = text.replace('covid19','').replace('rt ','')
    return text

def search_updates(line):
    line = line.lower()
    stops = ['closest']
    for i in stops:
        line = line.replace(i,'')
    if (
        ((line.find('school')!=-1) or (line.find('bar')!=-1) or (line.find('resturant')!=-1) or (line.find('college')!=-1))
        and ((line.find('restrict')!=-1) or (line.find('clos')!=-1) or (line.find('shut')!=-1))
       ):
        return True

def part_2(data):
    '''
    Returns a dataframe filtered by only the updates.
    '''
    df_func = data.copy()
    df = get_covid_or_not(df_func)
    search_updt = df.full_text.apply(search_updates).dropna().index
    return df.iloc[search_updt,:]

if __name__ == '__main__':

    job_id = sys.argv[1]
    handles = sys.argv[2].split(',')
    toInvoke = sys.argv[3]

    cols = ['created_at','id','full_text','user_name', 'user_screen_name', 'user_location', 'user_description','lang', 'clean_text', 'usernames', 'hashtags', 'links', 'sentiment',]
    # IF you want to fetch more tweets you can un-comment below line
    fetch_tweets_from_handles(handles,cols)

    # Loading the fetched data
    df = pd.read_csv('Covid_handle_tweets.csv')
    #Information that you want to extract
    info_to_extract=['case','death','hospital','negative',]

    if toInvoke == '1' or toInvoke == '3':
        print('Invoking function 1 against job id', job_id)
        part_1_output = part_1(df,info_to_extract, f'./output/{job_id}-stats.csv')
        print(part_1_output)

    if toInvoke == '2' or toInvoke == '3':
        print('Invoking function 2 against job id', job_id)
        part_2_output = part_2(df)
        with open(f'./output/{job_id}-guidance.txt', "a") as myfile:
            myfile.write(str(part_2_output))
