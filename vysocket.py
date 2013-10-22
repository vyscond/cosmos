#
# Owner
#   Ramon M. "Vyscond"
#
# email
#   vyscond@gmail.com
#
# github
#   vyscond
#
# twitter
#   @vyscond
#
#
# License 
#   This software is licensed under GNU General Public License, version 3 (GPL-3.0)


import socket as pysocket
import logging
from traceback import print_exc , format_exc

class TCPSocketServer :

    def __init__( self ):
    
        # The backlog argument specifies the maximum number of queued connections and should be at least 0; the maximum value is system-dependent (usually 5), the minimum value is forced to 0.
        
        self.socket = pysocket.socket( pysocket.AF_INET , pysocket.SOCK_STREAM )
        
    def bind( self , ip , port ):
            
        # --- setting up ---
        
        self.socket.setblocking(1)
        
        self.socket.setsockopt(pysocket.SOL_SOCKET, pysocket.SO_REUSEADDR, 1)
        
        self.socket.bind( ( ip , port ) )
        
        self.socket.listen( 0 )
        
        return 0
         
    def wait( self ):
            
        return TCPSocketClient( socket= self.socket.accept()[0] )
            
    def close( self ):
        
        self.socket.shutdown( pysocket.SHUT_RDWR )
        
        self.socket.close()
        

class TCPSocketClient:

    def __init__( self , socket=None ):
         
        if not socket :
            
            self.socket = pysocket.socket( pysocket.AF_INET , pysocket.SOCK_STREAM )
            
        else :
            
            self.socket = socket
            
    def close( self ):
        
        self.socket.shutdown( pysocket.SHUT_RDWR )
        
        self.socket.close()
        
    def connect( self , ip , port , timeout=2 ):
        
        #self.socket.settimeout( 2 )
        
        self.socket.connect( ( ip , port ) )
        
    def send( self , msg , tries=1 , timeout=1 ):
        
        msg = hex(len(msg))+'\n'+ msg
        
        #self.socket.settimeout(timeout)
        
        self.socket.sendall( msg )
        
    def read( self , timeout=0 ):
        
        msg_size = []
        
        while True :
            
            msg_size.append( self.socket.recv( 1 ) )
            
            if msg_size[-1] == '\n':
                
                return self.socket.recv( int( ''.join(msg_size[:-1]) , 0 ) )
                
