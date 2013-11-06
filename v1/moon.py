from sys import argv
from traceback import print_exc

try :
    
    from cosmos import MoonServer

    if argv[ 2 ] == 'start' :
        
        MoonServer( argv[ 1 ] ).start()
        

except :

    print_exc()
    print 'cosmos [config_file] (start|stop|restart)'
