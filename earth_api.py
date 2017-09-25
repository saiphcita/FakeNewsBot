from flask import Flask, render_template
import tweepy, time, sys
from time import sleep
from random import randint
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream 
from flask import jsonify
import flask
import time
import datetime
import re
from flask import request
import os
import io

import urllib3
import urllib 

BITLYTOK='9d91f449c96e4acc64ff6cef202071e75b1123f8'

###
### Se definen las siguientes tres funciones para mandar mensajes a usuarios.
### Para DM se requiere que sean seguidores del bot, asi que se revisa si existen en la lista
### de seguidores.
### 

#La siguiente es una lista de influencers, es decir
#gente a la que se le enviaran las notificaciones.
influencers = ["jrmm22" ]
#influencers = ["saiphcita", "jrmm22", "chidalavida" ]
influencers_onlyurgent = [ "gabilooo", "BuzzFeedMexico", "IntiLeonardo", "LaMalaSuarez", "LuisMiSalgado", "lopezdoriga" ]

#La siguiente es una lista de los usuarios que nos siguen
# Se usa para saber si podemos mandar mensajes privados o no.
followed_by = [""]
followed_by.append( "@saiphcita" )
followed_by.append( "@jrmm22" )
followed_by.append( "@chidalavida" )

#Estas son las tablas que vamos a leer de la tabla
tabs=[ "centros", "urgencias", "albergues", "otros", "ofrecimientos" ]
#Y estos son los ultimos IDs que leimos en cada tabla.
proc_ids=[ 0, 0, 0, 0, 0 ]

def load_last_ids():
    idfiles = open( "tabs_ids.txt", "rt" )
    if idfiles:
        
        idfiles_data  = flask.json.loads( idfiles.readline() )

        proc_ids[ 0 ] = idfiles_data[ "centros" ]
        proc_ids[ 1 ] = idfiles_data[ "urgencias" ]
        proc_ids[ 2 ] = idfiles_data[ "albergues" ]
        proc_ids[ 3 ] = idfiles_data[ "otros" ]
        proc_ids[ 4 ] = idfiles_data[ "ofrecimientos" ]

        print( "Detected {} {} {} {} {}".format( proc_ids[0], proc_ids[1], proc_ids[2], proc_ids[3], proc_ids[4] ) );
        idfiles.close()

def store_last_ids( ):
    idfiles = open( "tabs_ids.txt", "wt" )
    if idfiles:
#        idfiles_data=[ "centros", "urgencias", "albergues", "otros", "ofrecimientos" ]
#        idfiles_data[ "centros" ] = proc_ids[ 0 ]
#        idfiles_data[ "urgencias" ] = proc_ids[ 1 ]
#        idfiles_data[ "albergues" ] = proc_ids[ 2 ]
#        idfiles_data[ "otros" ] = proc_ids[ 3 ]
#        idfiles_data[ "ofrecimientos" ] = proc_ids[ 4 ]
        asstring = "{{ \"centros\":{}, \"urgencias\":{}, \"albergues\":{}, \"otros\":{}, \"ofrecimientos\":{} }}".format( proc_ids[0], proc_ids[1], proc_ids[2], proc_ids[3], proc_ids[4] )
        print( "Stored {} ".format( asstring ) );
        idfiles.write( asstring )
        idfiles.close
    
def check_if_str_valid( var ):
    result = False
    if var:
        if len( var ) > 2:
            result = True
    return result

def bitly_my_url( url ):
    bitly_address = "https://api-ssl.bitly.com"
    bitly_address += "/v3/shorten?access_token="+ BITLYTOK + "&longUrl=" + urllib.parse.quote_plus( url ) + "&format=txt"
    req = http.request( 'GET', bitly_address )
    
    result = req.data.decode( )
    print( "My long address {} is now {}".format( url, result ) );
    print( "Queried {}".format( bitly_address ) )
    return result

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

def send_image( api, imgurl, message ):
    result = False
    filename = 'temp.png'
    req = http.request( 'GET', imgurl )
    if req:
        msg = message
        msglen = len( msg )

        if msglen >= 140 :
            msg = msg[0:135] + "..."
        
        with open( filename, "wb" ) as im:
            im.write( req.data )
            im.flush( )


        print( "sending msg {} with len {}".format( msg, len( msg )  ) )
        print( "original msg {} with image {}".format( message, imgurl  ) )
        try:
            api.update_with_media( filename, status=msg )
            result = True
        except:
            result = False
        #os.remove( filename )
        im.close()
    return result

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
        else:
            print( "User {} is not following us".format( user ) );
    if as_public:
        if len( user ) > 1:
            msg = user + " " + msg
        msglen = len( msg )
        if msglen >= 140 :
            msg = msg[0:135] + "..."
        try:
            rate_limit( api.update_status( user + " " + msg ) )
            result = True
        except:
            result = False
    return result

## A continuacion se muestra un ejemplo de como usar las funciones.

load_last_ids( )

# Se hace Auth
if 0: 
    #Credenciales de ErFonseca
    auth = tweepy.OAuthHandler( 'sNrcmb8HtJAsykme4T0f17CdV', 'qvVu7yLNxZMqjBsra5W88LtdHz5BfemEa52lXEAXEAuHsS9143' )
    auth.set_access_token( '802949-p44eiRkrq19TimFzNmpACiJkN5yrxq65grO4r2WE9Lw' , 'XAUlDllO39beVzYBIe8dO0TjART8NILY4dZoPoOSseNUg' )

else:
    #Credenciales de FakeSismo
    auth = tweepy.OAuthHandler( 'Z2KNcJ51ORt6rLjvXlGi1y9mY', 'Vt8T1a2BhWc8PxnSlvxe3d8HULDGPkLLmqRxXRoEHaHljBeQnl' )
    auth.set_access_token( '911231467870670848-qhpup7gmr5EuLncJB4A7NMsWixHTS8P' , '8RnGqdoHJjV6j7IKyb7aTSgFc8VPwCau2hloPR3wJyRfq' )


# Se obtiene el objeto API
api = tweepy.API( auth )

# Se compila la lista de seguidores
#populate_my_follower_list()

http = urllib3.PoolManager( )


LASTTIMESTAMP= datetime.datetime.strptime( "01/01/2017-00:00", "%d/%m/%Y-%H:%M"  ).timestamp()
while True:
#if 1:
    # Se obtiene la lista de noticias.
    NEWSFEEDIMG="http://aquinecesitamos.paw.mx/latest.json"
    NEWSFEED="http://ec2-34-223-244-147.us-west-2.compute.amazonaws.com/api/data/news"
    req = http.request( 'GET', NEWSFEED )
    # Data is now at req.data
    #print( req.data )
    procdatatab = flask.json.loads( req.data )

    #tabs = ["urgencias", "albergues", "otros"] 
    #tab = "urgencias"
    tab_n = 0
    #if 1:

    for tab in tabs:
        procdata = procdatatab[ tab ]
        #print( procdata )
        ENTRY=0
        entries = len(procdata)
        while ENTRY < entries:
        #ENTRY = len( procdata ) - 1
        #while ENTRY >= 0: 


            print( "Trabajando ahora con {}".format( tab ) );
#            if ENTRY > 1:
#                ENTRY = entries - 1
            valid_data = False
            entry_id = procdata[ENTRY]['id']
            print( "{} is id {}".format( ENTRY, entry_id ) )
            TSTAMP = None
            #print( "Data is now of form {}".format( procdata[ ENTRY ]['requeridos'] ) )
            #Get the date from the last entry we processed.
            CTDTIMESTAMP=procdata[ENTRY]['created_at']
            UPDTIMESTAMP=procdata[ENTRY]['updated_at']

            #print( "{} is timestamp ".format( UPDTIMESTAMP ) )
            #print( "entry is {} ".format( procdata[ ENTRY ] ) )
            if UPDTIMESTAMP :
                TSTAMP = UPDTIMESTAMP
            else:
                TSTAMP = CTDTIMESTAMP

            if tab.find( "urgencias" ) > -1 :
                if check_if_str_valid( procdata[ ENTRY ][ 'most_important_required' ] ) :
                    valid_data = True
                if TSTAMP == None:
                    valid_data = False
            elif tab.find( "albergues" ) > -1 :
                if check_if_str_valid( procdata[ ENTRY ][ 'receiving' ] ):
                    valid_data = True
            elif tab.find( "otros" ) > -1 :
                if check_if_str_valid( procdata[ ENTRY ][ 'description' ] ):
                    valid_data = True
            elif tab.find( "ofrecimientos" ) > -1 :
                if check_if_str_valid( procdata[ ENTRY ][ 'offering_details' ] ):
                    valid_data = True
            else:
                if check_if_str_valid( procdata[ ENTRY ][ 'requirements_details' ] ):
                    valid_data = True
                

            if valid_data:
        #        CURTIMESTAMP=CURTIMESTAM
                YEAR=TSTAMP[0:4]
                MONTH=TSTAMP[5:7]
                DAY=TSTAMP[8:10]
                HOUR=TSTAMP[11:13]
                MIN=TSTAMP[14:16]
                if int(MONTH) > 12:
                    MONTHtmp = DAY
                    DAY = MONTH
                    MONTH = MONTHtmp

                time_str="{}/{}/{}-{}:{}".format( DAY,MONTH,YEAR,HOUR,MIN )
                #print( "{}/{}/{}-{}:{}".format( DAY,MONTH,YEAR,HOUR,MIN ) )
                cur_timestamp = datetime.datetime.strptime( time_str, "%d/%m/%Y-%H:%M"  ).timestamp()

                print( "{} against {} ".format( entry_id, proc_ids[ tab_n ] ) )
                
                if entry_id > proc_ids[ tab_n ]:

                    #Used only for 'urgencias'
                    filename=""

                    proc_ids[ tab_n ] = entry_id 
                    
                    msg = ""


                    if tab.find( "centros" ) > -1 or tab.find( "albergues" ) > -1:
                        msg += " " + tab[:-1].upper() + ": "
                        # Poner el mapa al principio
                        if check_if_str_valid( procdata[ ENTRY ][ 'map' ] ):
                            newurl = bitly_my_url( procdata[ ENTRY ][ 'map' ].replace( "\\", "" ) )
                            if newurl.find( "http" ) > -1 :
                                msg += newurl + " "
                    elif tab.find( "otros" ) > -1:
                        if check_if_str_valid( procdata[ ENTRY ][ 'description' ] ):
                            msg += " LINK:"
                            newurl = bitly_my_url( procdata[ ENTRY ][ 'description' ].replace( "\\", "" ) )
                            if newurl.find( "http" ) > -1 :
                                msg += newurl + " "
                        
                        msg += procdata[ ENTRY ]['url']

                    elif tab.find( "urgencias" ) > -1:
                        if procdata[ ENTRY ][ 'urgency_level' ].find( "alto" ) > -1:
                            msg += "URGENTE: "
                        else:
                            msg += "NECESITAMOS: "

                        msg += procdata[ ENTRY ]['most_important_required'].replace( "URGE", "" ).replace( ":", "" )
                        if len( procdata[ ENTRY ][ 'not_required' ] ) > 2 :
                            msg += " Abstenerse: " + procdata[ ENTRY ][ 'not_required' ]
                    
                        if len( procdata[ ENTRY ][ 'source' ] ) > 2 :
                            msg += ". FUENTE: " + procdata[ ENTRY ][ 'source' ].replace( "\\", "" ) 
                        msg += " en " + procdata[ ENTRY ][ 'address' ]
                        msg += " Zona " + procdata[ ENTRY ][ 'zone' ]

                    elif tab.find( "ofrecimientos" ) > -1:
                        msg += procdata[ ENTRY ][ 'offering_from' ] 
                        msg += " OFRECE: " 
                        msg += procdata[ ENTRY ][ 'notes' ] 
                        msg += " Contacto: "
                        msg += procdata[ ENTRY ][ 'contact' ] 
                        msg += " Mas informacion: "
                        msg += procdata[ ENTRY ][ 'offering_details' ] 


                    if tab.find( "albergues" ) > -1 :
                        msg += procdata[ ENTRY ]['location']
                        msg += " en " + procdata[ ENTRY ][ 'address' ]
                        msg += " Zona " + procdata[ ENTRY ][ 'zone' ]

                    #else: #
                    if tab.find( "centros" ) > -1 :
                        msg += procdata[ ENTRY ]['requirements_details']
                        msg += " en " + procdata[ ENTRY ][ 'address' ]
                        msg += " Zona " + procdata[ ENTRY ][ 'zone' ]

                    #Calcular filename en servidor
                    if tab.find( "urgencias" ) > -1 :
                        fnametstamp = "{}{}{}{}{}".format( YEAR, MONTH, DAY, HOUR, MIN )
                        filename = re.sub( " ", "", procdata[ ENTRY ][ 'zone' ].lower() )
                        filename+= "-" + procdata[ ENTRY ][ 'urgency_level' ].lower() + "-" + fnametstamp + ".png"

                    
                    for user in influencers:
                        result = False
                        dm_msg = time_str + " " + msg
                        if tab.find( "urgencias" ) > -1 :
                            dm_msg += ". http://aquinecesitamos.paw.mx/" + filename #procdata[ ENTRY ][ 'file_name' ]

                        result = send_private_or_public( api, "@"+user, dm_msg, True, False )
                    
                        if result:
                            print( "Enviando dm a {} : '{}'".format( user, msg ) )
                        else:
                            print( "Fallo enviando dm a {} ".format( user, msg ) )
                        
                        time.sleep( 5 )
                    
                    if 0:
                        if tab.find( "urgencias" ) > -1 :
                            imgurl = "http://aquinecesitamos.paw.mx/" +  urllib.parse.quote_plus( filename )
                            print( "Mandando imagen {}".format( imgurl) );
                            result = send_image( api, imgurl, msg )
                        else:
                            result = send_private_or_public( api, "", msg, False, True )

                    if result:
                        print( "Enviando public a '{}'".format( msg ) )
                    else:
                        print( "Fallo enviando public {} ".format( msg ) )
                    time.sleep( 15 )
                    print( "Filename {} has timestamp {} into {}".format( filename, time_str, cur_timestamp) )

                
                else:
                    print( "Already processed ID!" );

        
            ENTRY += 1
            
            time.sleep( 10 )
            #ENTRY -= 1

        tab_n += 1
        store_last_ids()

    time.sleep( 60 * 5 )


exit(1)
#push an image to imgur:
#imgur.push


data = None
with open('home-bg.png', 'rb') as im:
    data = im.read()

    if data != None:

        req = http.request( 'POST', 
                            'https://api.imgur.com/3/image',
                            body=data,
                            headers={'Content-type' : 'media/png',
                            'authorization' : 'Client-ID 846a1d86c2629d2'} )
        #req.add_header( 'Content-type' , 'media/jpeg' )

        #print( req.data )
        response = req.data.decode( ).split( "," )

#b'{"data":{"id":"Poj28rh","title":null,"description":null,"datetime":1506237092,"type":"image\\/jpeg","animated":false,"width":600,"height":66,"views":0,"bandwidth":0,"vote":null,"favorite":false,"nsfw":null,"section":null,"account_url":null,"account_id":0,"is_ad":false,"in_most_has_sound":false,"tags":[],"ad_type":0,"ad_url":"","in_gallery":false,"deletehash":"aWwHrY0WpJtxtIo","name":"","link":"https:\\/\\/i.imgur.cpg"},"success":true,"status":200}'
        for r in response:
            if r.find( "\"link\":" ) > -1 :
                user = "@saiphcita"
                #imglink.replace( )
                link_data = r.split( ":", 1 )
                link = link_data[1].replace( "\\", "" ).replace( "}", "" ).replace( "\"", "" )
                print( "Got link @ {} -> {}".format( r, link ) )
                result = send_private_or_public( api, user, "Este es un texto de prueba! " + link, True, False )

                if result == False:
                    print( "Failed sending message to {}".format( user ) )
            else:
                print( "Didnt find link here! {}".format( r ) )

    else:
        print( "Failed getting data from file!" )

    im.close()
# Mandamos un mensaje privado



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
