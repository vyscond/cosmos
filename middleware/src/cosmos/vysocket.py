
# owner   : Ramon Moraes "Vyscond" 
# github  : https://github.com/vyscond
# email   : vyscond@gmail.com
# license : GNU General Public License v3

import socket as pysocket
import logging
from traceback import print_exc , format_exc

logging.basicConfig(filename='/tmp/vysocket.log',level=logging.DEBUG)

class TCPSocketServer :

    def __init__( self ):
    
        # The backlog argument specifies the maximum number of queued connections and should be at least 0; the maximum value is system-dependent (usually 5), the minimum value is forced to 0.
        
        self.socket = pysocket.socket( pysocket.AF_INET , pysocket.SOCK_STREAM )
        
    def bind( self , ip , port ):
        
        try :
            
            # --- setting up ---
            
            self.socket.setblocking(1)
            
            self.socket.setsockopt(pysocket.SOL_SOCKET, pysocket.SO_REUSEADDR, 1)
            
            self.socket.bind( ( ip , port ) )
            
            self.socket.listen( 0 )
            
            return 0
            
        except :
            
            logging.debug( format_exc() ) 
            
            return 1
         
    def wait( self ):
        
        try :
            
            return TCPSocketClient( socket= self.socket.accept()[0] )
            
        except : 
            
            logging.debug( format_exc() )
            
            return None

    def close( self ):
        
        try : 
            
            self.socket.shutdown( pysocket.SHUT_RDWR )
            
            self.socket.close()
            
            return 0
            
        except :
            
            logging.debug( format_exc() )
            
            return 1
         

class TCPSocketClient:

    def __init__( self , socket=None ):
         
        if not socket :
            
            self.socket = pysocket.socket( pysocket.AF_INET , pysocket.SOCK_STREAM )
            
            self.socket.setblocking(1)
            
        else :
            
            self.socket = socket
            
    def close( self ):
        
        try : 
            
            self.socket.shutdown( pysocket.SHUT_RDWR )
            
            self.socket.close()
            
            return 0
            
        except :
            
            logging.debug( format_exc() )
            
            return 1
            
    def connect( self , ip , port ):
        
        try :
            
            self.socket.connect( ( ip , port ) )
            
            return 0
            
        except :
            
            logging.debug( format_exc() )
            
            return 1
            
    def send( self , msg ):
        
        try : 
            
            self.socket.sendall( hex(len(msg))+'\n'+ msg )
            
            return 0
            
        except:
            
            logging.debug( format_exc() )
            
            return 1
         
    def read( self ):
        
        try :
            
            msg_size = []
            
            while True :
                
                msg_size.append( self.socket.recv( 1 ) )
                
                if msg_size[-1] == '\n':
                    
                    return self.socket.recv( int( ''.join(msg_size[:-1]) , 0 ) )
                    
        except :
            
            logging.debug( format_exc() )
            
            return None
