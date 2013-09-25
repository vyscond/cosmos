'''
This code was writed by Ramon "Vyscond" and is distributed under the GNU General Public License

github : https://github.com/vyscond
email  : vyscond@gmail.com

'''

import socket as pysocket
from traceback import print_exc
from vylog     import VyLog

class VySocketServer :

    def __init__( self , server_address_to_bind , backlog=0 ):
    
        # The backlog argument specifies the maximum number of queued connections and should be at least 0; the maximum value is system-dependent (usually 5), the minimum value is forced to 0.
        
        self.log = VyLog( self )
        
        self.socket = pysocket.socket( pysocket.AF_INET , pysocket.SOCK_STREAM )
        
        # --- setting up ---
        
        self.socket.setblocking(1)
        
        self.socket.setsockopt(pysocket.SOL_SOCKET, pysocket.SO_REUSEADDR, 1)
        
        self.socket.bind( server_address_to_bind )
        
        self.socket.listen(backlog)
        
    def wait_for_a_connection(self):
        
        socket_client , hostname = self.socket.accept()
        
        socket_client.setblocking(1)
        
        return VySocketClient( socket=socket_client )
            
    def close( self ):

        # Shut down one or both halves of the connection.
        # 
        # If how is SHUT_RD, further receives are disallowed.
        # If how is SHUT_WR, further sends are disallowed.
        # If how is SHUT_RDWR, further sends and receives are disallowed.
        
        self.socket.shutdown( pysocket.SHUT_RDWR )
        
        self.socket.close()


class VySocketClient:

    def __init__( self , socket=None , server_address=None ):
        
        self.log = VyLog( self )
         
        self.server_address = server_address
         
        if not socket :
            
            self.socket = pysocket.socket( pysocket.AF_INET , pysocket.SOCK_STREAM )
            
            self.socket.setblocking(1)
            
        else :
            
            self.socket = socket
            
    def close( self ):
        
        # Shut down one or both halves of the connection.
        #  
        #  If how is SHUT_RD, further receives are disallowed.
        #  If how is SHUT_WR, further sends are disallowed.
        #  If how is SHUT_RDWR, further sends and receives are disallowed.
        
        self.socket.shutdown(pysocket.SHUT_RDWR)
        
        self.socket.close()

    def connect( self , server_address ):
            
        self.socket.connect( server_address )
            
    def send( self , msg ):
         
        self.socket.sendall( hex(len(msg))+'\n'+ msg )
         
    def read( self ):
        
        msg_size = []
        
        while True :
            
            tmp = self.socket.recv( 1 )
                
            if tmp != '\n':
                
                msg_size.append( tmp )
                
                continue
                
            break
            
        return self.socket.recv( int( ''.join( msg_size ) , 0 ) )

