import tweepy

CONSUMER_KEY = 'csh4Fe6ERZXxxmwuWPItc2qf5'
CONSUMER_SECRET = '39xMxRVjpirLgXwUCawKjf9H3AyIL0RxtwrpikHh70cafPCREH'
ACCESS_TOKEN = '1386831684121866242-WvFuYtg5Cg9FO2vL9fkV6WzldDGpmK'
ACCESS_TOKEN_SECRET = '3q6YBwpDGRcYDB0gVHLpzYUae0SQQy7FBdu7S9yTUeo3A'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

with open('/Users/aidanslovinski/Desktop/HERALD/Tweet_Output.txt','r') as file:
   status = file.read()

#with open('Tweet_Output.txt','r') as file:
 #  status = file.read()
#status = "this is a test"
#status = directmessage
api.update_status(status=status)
