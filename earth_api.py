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


###
### Se definen las siguientes tres funciones para mandar mensajes a usuarios.
### Para DM se requiere que sean seguidores del bot, asi que se revisa si existen en la lista
### de seguidores.
### 

#La siguiente es una lista de los usuarios que nos siguen
# Se usa para saber si podemos mandar mensajes privados o no.
followed_by = [""]
# La siguiente funcion permite limitar el trafico, para no exceder el limite
def rate_limit( cursor ):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            print( "ZZZzzz" );
            time.sleep( 30 )

def populate_my_follower_list():
    # Usamos nuestra rate_limit para revisar los seguidores q tenemos.
    for f in rate_limit( tweepy.Cursor(api.followers).items() ):
        print( "Found follower {}".format( f.screen_name ) )
        followed_by.append( '@' + f.screen_name )

def send_private_or_public( tweepy_api, user, msg, as_private, as_public ):
    result = False
    # Checamos que el usuario al que queremos mandar mensaje privado en efecto 
    # pueda recibirlos
    if as_private:
        if user in followed_by:
            try:
                rate_limit( tweepy_api.send_direct_message( user, text=msg ) )
                result = True
            except:
                result = False
    if as_public:
        try:
            rate_limit( api.update_status( user + " " + msg ) )
            result = True
        except:
            result = False
    return result

## A continuacion se muestra un ejemplo de como usar las funciones.

# Se hace Auth
auth = tweepy.OAuthHandler(t_consumerkey, t_secretkey)
auth.set_access_token(access_tokenkey, access_tokensecret)

# Se obtiene el objeto API
api = tweepy.API( auth )

# Se compila la lista de seguidores
populate_my_follower_list()

# Mandamos un mensaje privado
send_private_or_public( api, "@jrmm22", "Este es un texto de prueba PM 2!", True, False )
# Mandamos un tweet publico
send_private_or_public( api, "@jrmm22", "Este es un tweet de prueba Public 2!", False, True )
# Mandamos uno combinado
send_private_or_public( api, "@jrmm22", "Este es un tweet de prueba doble 2!", True, True )

exit(1)

app = Flask(__name__, template_folder="mytemplate")
list_names = ["@fakeNewsBots"]
# Authentication
try:
	t_consumerkey='TW_CONSUMERKEY'
	t_secretkey='TW_SECRETKEY'
	access_tokenkey='TW_ACCESS_TOKENKEY'
	access_tokensecret='TW_TOKENSECRET'
except KeyError: 
	print("You need to set the environment variables: TW_CONSUMERKEY, TW_SECRETKEY, TW_ACCESS_TOKENKEY, TW_TOKENSECRET")
	sys.exit(1)
# list of name to handle duplicates


#open file to read hashtags
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
            print(handle)
            if handle not in list_names:
                m = handle + " " + "hola! Soy un bot verificando info del sismo. Me puedes confirmar si estos recursos aun se requieren? Grax! #19SRecursos"
                s = api.update_status(m)
                nap = randint(1, 60)
                time.sleep(nap)
                list_names.append(handle)


f.close()
if(__name__) == '__main__':
    app.run(debug=True)
