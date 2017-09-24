from flask import Flask, render_template
import tweepy, time, sys
from time import sleep
from random import randint
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream 
from flask import jsonify
from flask import request
import os
import io

app = Flask(__name__, template_folder="mytemplate")
list_names = ["@fakeNewsBots"]
# Authentication
try:
	t_consumerkey=''
	t_secretkey=''
	access_tokenkey=''
	access_tokensecret=''
except KeyError: 
	print("You need to set the environment variables: TW_CONSUMERKEY, TW_SECRETKEY, TW_ACCESS_TOKENKEY, TW_TOKENSECRET")
	sys.exit(1)
# list of name to handle duplicates


try:
    auth = tweepy.OAuthHandler(t_consumerkey, t_secretkey)
    auth.set_access_token(access_tokenkey, access_tokensecret)

    api = tweepy.API(auth)

    handle = '@saiphcita'
    m = "Hola. esto es una prueba - de @jrmm22."
    s = api.send_direct_message( handle, text=m )
except:
    print( "Usuario {} no nos esta siguiendo".format( handle ) )
#open file to read hashtags
#ifdef'd out, or whatever
if 0:
    with open('hashtags.txt') as f:
       for line in f:
            auth = tweepy.OAuthHandler(t_consumerkey, t_secretkey)
            auth.set_access_token(access_tokenkey, access_tokensecret)

            api = tweepy.API(auth)

            search_text = line
            search_number = 2
            search_result = api.search(search_text, rpp=search_number)

            # with io.open('output_tweets.txt', 'a', encoding='utf8') as w:
            #     for tweet in search_result:
            #         w.write('Username:  ' + tweet.author.screen_name + '\n')
            #         w.write("Tweet:  " + tweet.text + "\n")
            # w.close()
    #tweet in the usernames
            for tweet in search_result:
                handle = "@" + tweet.user.screen_name
                print( "Encontre tweet {} de {}".format( tweet.text, handle ) )
                print(handle)
                if handle not in list_names:
                    m = handle + " " + "hola! Soy un bot verificando info del sismo. Me puedes confirmar si estos recursos aun se requieren? Grax! #19SRecursos"
                    list_names.append(handle)

       nap = randint(1, 60)
       time.sleep(nap)

    f.close()
if(__name__) == '__main__':
    app.run(debug=True)
