import tweepy

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

with open('/Users/aidanslovinski/Downloads/BEQUANT/Tweet_Output.txt','r') as file:
   status = file.read()

#with open('Tweet_Output.txt','r') as file:
 #  status = file.read()
#status = "this is a test"
#status = directmessage
api.update_status(status=status)
