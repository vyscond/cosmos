from sys import argv
from traceback import print_exc
from cosmos import Moon
if __name__ == '__main__' :
    
    try :
        
        Moon( argv[1] , argv[2] ).start()
        
    except :
        
        print_exc()
        
        exit( 0 )
