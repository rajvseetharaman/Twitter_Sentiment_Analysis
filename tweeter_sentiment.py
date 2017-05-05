#importing the required data variables
from data.uw_ischool_sample import SAMPLE_TWEETS
from data.sentiments_nrc import EMOTIONS
from data.sentiments_nrc import SENTIMENTS
#importing needed modules
import re
from functools import reduce
import json
import requests

def text_split(text_string):
    """This function takes as input a string and return as output the list of words in the string in lower case having length greater than 1"""
    #getting all the words in the string
    words=re.compile('\w+').findall(text_string)
    #converting all words to lowercase and filtering out words smaller in length than 2 characters
    wd=[word.lower() for word in words if len(word)>1]
    return wd

def has_emotion(wordlist,emotion):
    """This function takes as input a list of words and an emotion and returns as output a list of words which have that emotion"""
    #for each word in the list of words, check the sentiments dictionary for emotions corresponding to each word
    #If the given emotion is in the list of emotions for a word, add it to the list of words to be returned
    newlist=[word for word in wordlist if SENTIMENTS.get(word,None)!=None if emotion in SENTIMENTS.get(word,None)]
    return newlist

def word_emotion_map(wordlist):
    """This function takes as input a list of words and returns a dictionary which maps each emotion to the list of words in the wordlist which contain that emotion"""
    #iterate through the EMOTIONS list and for each emotion, use the has_emotion function defined to determine which words have the specified emotion 
    emotion_dict=dict((emotion,has_emotion(wordlist,emotion)) for emotion in EMOTIONS)
    return emotion_dict

def most_common(wordlist):
    """This function takes as input a list of words and returns a list of most common words in the list"""
    #dictionary which counts frequency of each word in the input list
    wordfreq=dict()
    #populate the word frequency dictionary
    for word in wordlist:
        if word not in wordfreq.keys():
            wordfreq[word]=1
        else:
            wordfreq[word]+=1
    #create a list of tuples of each word and its corresponding frequency in the wordlist
    wordcount=[(k,v) for k,v in wordfreq.items()]
    #sort the list in descending order based on the frequency of each word in the wordlist
    wordcount_sorted=[values[0] for values in sorted(wordcount ,key= lambda x:x[1],reverse=True)]
    return wordcount_sorted        

def analyze_tweets(tweetslist):
    """This function takes as input the list of tweets and returns as output a list of dictionaries with the following information for each emotion- The percentage of words across all tweets that have that emotion, The most common words across all tweets that have that emotion, and The most common hashtags across all tweets associated with that emotion"""
    #add the wordslist and the dictionary which maps each emotion to words having that emotion, to the tweetslist dictionary
    for val in tweetslist:
        val['words']=text_split(val['text'])
        val['emo-words']=word_emotion_map(text_split(val['text']))
    tweetstats=[]
    #find all the hashtags in the tweets
    hashtags=[x['text'] for y in [c['hashtags'] for c in [tweet['entities'] for tweet in SAMPLE_TWEETS] if c['hashtags']!=[]] for x in y]
    #create a dictionary in the tweetstats list for each emotion which stores percent words, common example words, and common hashtags
    for emotion in EMOTIONS:
        #compute the percent of words which have a certain emotion 
        dict_percent_words=round((100*reduce(lambda x,y:x+y,[len(val['emo-words'][emotion]) for val in tweetslist]))/reduce(lambda x,y:x+y,[len(val['words']) for val in tweetslist]),2)
        #find the most common words which have the emotion
        dict_example_words=most_common(reduce(lambda x,y:x+y,[has_emotion(val['words'],emotion) for val in tweetslist]))
        #find the most common hashtags across tweets associated with the emotion
        dict_hashtags=most_common([x['text'] for y in [c['hashtags'] for c in [tweet['entities'] for tweet in tweetslist if has_emotion(text_split(tweet['text']),emotion)] if c['hashtags']!=[]] for x in y])
        #append the dictionary to the list to be returned
        tweetstats.append({'EMOTION':emotion,'% of WORDS':dict_percent_words,'EXAMPLE WORDS':dict_example_words,'HASHTAGS':dict_hashtags})
    return tweetstats

def print_stats(tweetslist):
    """This function takes as input the list of dictionaries corresponding to the tweets analyzed and prints it in a tabular format"""
    print("{0:14} {1:11} {2:35} {3}".format('EMOTION','% of WORDS','EXAMPLE WORDS','HASHTAGS'))
    #iterate through each emotion and print the statistics associated with it
    for v in tweetslist:
        row=[val for key,val in v.items()]
        print("{0:14} {1:11} {2:35} {3}".format(row[0],str(row[1])+'%',','.join(row[2][:3]),','.join(['#'+x for x in row[3][:3] ])))
    
def download(scrname):
    """This function takes as input the twitter username for a user and returns as output the list of dictionaries corresponding to the tweets of the user"""
    #set the screen name and tweet count parameters to be passed to the requests.get method
    parameters={'screen_name':scrname,'count':200}
    #send the get request and load the returned json data to dictionary
    r=requests.get(url='https://faculty.washington.edu/joelross/proxy/twitter/timeline/',params=parameters)
    twitterdata=json.loads(r.text)
    #return the list of dictionaries corresponding to the tweets
    return twitterdata

def main():
    #Take as input the user name
    scrname=input("Enter the Twitter Screen Name-")
    #if user enters SAMPLE analyze SAMPLE_TWEETS else analyze data corresponding to the user name
    if scrname=='SAMPLE':
        print_stats(analyze_tweets(SAMPLE_TWEETS))
    else:
        twitterdata=download(scrname)
        print_stats(analyze_tweets(twitterdata))

if __name__ == "__main__":
    main()
