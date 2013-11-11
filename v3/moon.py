from sys import argv
from traceback import print_exc

try :
    
    from cosmos import MoonServer

    if argv[ 2 ] == 'start' :
        
        MoonServer( argv[ 1 ] ).start()
        
    elif argv[ 2 ] == 'stop' :
        
        MoonServer( argv[ 1 ] ).stop()
        
    #~ elif argv[ 2 ] == 'restart' :
        #~ 
        #~ MoonServer( argv[ 1 ] ).stop()
        #~ 
        #~ MoonServer( argv[ 1 ] ).start()
        
except :

    print_exc()
    
