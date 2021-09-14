#VERSION 1.3 (new section)
import re
import sys
import praw
import time
import json
import pprint
import operator
import datetime
from praw.models import MoreComments
#from iexfinance import Stock as IEXStock
from iexfinance.stocks import Stock as IEXStock
import os
# to add the path for Python to search for files to use my edited version of vaderSentiment
sys.path.insert(0, 'vaderSentiment/vaderSentiment')
#!pip install vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#analyzer = SentimentIntensityAnalyzer()
import time
  
  
timenow = time.localtime()
timenow_display = time.strftime("%H:%M:%S", timenow)

from datetime import date

today = date.today()

file_path = 'HistoricalHERALD.txt'

def extract_ticker(body, start_index):

   count  = 0
   ticker = ""

   for char in body[start_index:]:
      if not char.isalpha():
         # if there aren't any letters following the $
         if (count == 0):
            return None

         return ticker.upper()
      else:
         ticker += char
         count += 1

   return ticker.upper()

def parse_section(ticker_dict, body):
   blacklist_words = [
      "YOLO", "TOS", "CEO", "CFO", "CTO", "DD", "BTFD", "WSB", "OK", "RH",
      "KYS", "FD", "TYS", "US", "USA", "IT", "ATH", "RIP", "BMW", "GDP",
      "OTM", "ATM", "ITM", "IMO", "LOL", "DOJ", "BE", "PR", "PC", "ICE",
      "TYS", "ISIS", "PRAY", "PT", "FBI", "SEC", "GOD", "NOT", "POS", "COD",
      "AYYMD", "FOMO", "TL;DR", "EDIT", "STILL", "LGMA", "WTF", "RAW", "PM",
      "LMAO", "LMFAO", "ROFL", "EZ", "RED", "BEZOS", "TICK", "IS", "DOW"
      "AM", "PM", "LPT", "GOAT", "FL", "CA", "IL", "PDFUA", "MACD", "HQ",
      "OP", "DJIA", "PS", "AH", "TL", "DR", "JAN", "FEB", "JUL", "AUG",
      "SEP", "SEPT", "OCT", "NOV", "DEC", "FDA", "IV", "ER", "IPO", "RISE"
      "IPA", "URL", "MILF", "BUT", "SSN", "FIFA", "USD", "CPU", "AT",
      "GG", "ELON", "CUM", "ROPE", "BBAGHOLDERS", "MILK","ASS", "DILDO",
   ]

   if '$' in body:
      index = body.find('$') + 1
      word = extract_ticker(body, index)
      
      if word and word not in blacklist_words:
         try:
             #special case for $TEST
            if word != "TEST":
               price = IEXStock(word).get_price()
               if word in ticker_dict:
                  ticker_dict[word].count += 1
                  ticker_dict[word].bodies.append(body)
                  price = IEXStock(word).get_price()
               else:
                  ticker_dict[word] = Ticker(word)
                  ticker_dict[word].count = 1
                  ticker_dict[word].bodies.append(body)
         except:
            pass
   
   # checks for non-$ formatted comments, splits every body into list of words
   word_list = re.sub("[^\w]", " ",  body).split()
   for count, word in enumerate(word_list):
      # initial screening of words
      if word.isupper() and len(word) != 1 and (word.upper() not in blacklist_words) and len(word) <= 5 and word.isalpha():
         # sends request to IEX API to determine whether the current word is a valid ticker
         try:
            # special case for $TEST
            if word != "TEST":
               price = IEXStock(word).get_price()
         except:
            continue
      
         # add/adjust value of dictionary
         if word in ticker_dict:
            ticker_dict[word].count += 1
            ticker_dict[word].bodies.append(body)
         else:
            ticker_dict[word] = Ticker(word)
            ticker_dict[word].count = 1
            ticker_dict[word].bodies.append(body)

   return ticker_dict

def get_url(key, value, total_count):
   # determine whether to use plural or singular
   mention = ("mentions", "mention") [value == 1]
   if int(value / total_count * 100) == 0:
         perc_mentions = "<1"
   else:
         perc_mentions = int(value / total_count * 100)
   # special case for $TEST
   if key == "TEST":
      return "${0} | [{1} {2} ({3}% of all mentions)]".format(key, value, mention, perc_mentions)
   else:
      return "${0} | [{1} {2} ({3}% of all mentions)]".format(key, value, mention, perc_mentions)

def get_date():
   now = datetime.datetime.now()
   return now.strftime("%b %d, %Y")

def setup(sub):
   if sub == "":
      sub = "wallstreetbets"

   # create a reddit instance
   reddit = praw.Reddit(client_id = "cENOq22q9m2j0Q",
  client_secret = "in-o3pyDTFONNqAXYPQjPd7en13zcQ",
  user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15")
   # create an instance of the subreddit
   subreddit = reddit.subreddit(sub)
   return subreddit


def run(mode, sub, num_submissions):
   ticker_dict = {}
   text = ""
   total_count = 0
   within24_hrs = False

   subreddit = setup(sub)
   new_posts = subreddit.new(limit=num_submissions)

   for count, post in enumerate(new_posts):
      # if not already viewed this post thread
      if not post.clicked:
         # parse the post's title's text
         ticker_dict = parse_section(ticker_dict, post.title)

         # to determine whether it has gone through all posts in the past 24 hours
         if "Daily Discussion Thread - " in post.title:
            if not within24_hrs:
               within24_hrs = True
            else:
               print("\nTotal posts searched: " + str(count) + "\nTotal ticker mentions: " + str(total_count))
               break
         
         # search through all comments and replies to comments
         comments = post.comments
         for comment in comments:
            # without this, issues b/c of "load more comments"
            if isinstance(comment, MoreComments):
               continue
            ticker_dict = parse_section(ticker_dict, comment.body)

            # now through comment's replies
            replies = comment.replies
            for rep in replies:
               if isinstance(rep, MoreComments):
                  continue
               ticker_dict = parse_section(ticker_dict, rep.body)
         
         # update the progress count
         sys.stdout.write("\rProgress: {0} / {1} posts".format(count + 1, num_submissions))
         sys.stdout.flush()

   text = "A BEQUANT.ORG Model: The top ten stocks discussed on /r/wallstreetbets along with NLP analysis:"
   text += "\n\nTicker | Mentions | Bullish (%) | Neutral (%) | Bearish (%)\n:- | :- | :- | :- | :-"

   total_mentions = 0
   ticker_list = []
   for key in ticker_dict:
      # print(key, ticker_dict[key].count)
      total_mentions += ticker_dict[key].count
      ticker_list.append(ticker_dict[key])

   ticker_list = sorted(ticker_list, key=operator.attrgetter("count"), reverse=True)

   for ticker in ticker_list:
      Ticker.analyze_sentiment(ticker)

   # will break as soon as it hits a ticker with fewer than 5 mentions
   for count, ticker in enumerate(ticker_list):
      if count == 40:
         break
      
      url = get_url(ticker.ticker, ticker.count, total_mentions)
      # setting up formatting for table
      text += "\n{} | {} | {} | {}".format(url, ticker.bullish, ticker.neutral, ticker.bearish)
      sys.stdout = open("HistoricalHERALD.txt", 'a')
   text += "\n\nVersion Alpha - Developed April 2021, Updated May 2021 - Aidan Slovinski."

   if not mode:
      print(" ")
   # testing
   else:
      print("*****************************************************************")
      print("Date: ", today, timenow_display)
      print(text)

class Ticker:
   def __init__(self, ticker):
      self.ticker = ticker
      self.count = 0
      self.bodies = []
      self.pos_count = 0
      self.neg_count = 0
      self.bullish = 0
      self.bearish = 0
      self.neutral = 0
      self.sentiment = 0 # 0 is neutral

   def analyze_sentiment(self):
      analyzer = SentimentIntensityAnalyzer()
      neutral_count = 0
      for text in self.bodies:
         sentiment = analyzer.polarity_scores(text)
         if (sentiment["compound"] > .005) or (sentiment["pos"] > abs(sentiment["neg"])):
            self.pos_count += 1
         elif (sentiment["compound"] < -.005) or (abs(sentiment["neg"]) > sentiment["pos"]):
            self.neg_count += 1
         else:
            neutral_count += 1

      self.bullish = int(self.pos_count / len(self.bodies) * 100)
      self.bearish = int(self.neg_count / len(self.bodies) * 100)
      self.neutral = int(neutral_count / len(self.bodies) * 100)

if __name__ == "__main__":
   mode = 1
   num_submissions = 295
   sub = "wallstreetbets"

   run(mode, sub, num_submissions)
    #new post analysis



