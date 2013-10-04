
import netifaces , time , os , sys , json 
from vysocket import TCPSocketServer , TCPSocketClient
from daemon import Daemon
from traceback import print_exc

'''
+----------+---------------------------------------------------------------------------
| DEBUG    | Detailed information, typically of interest only when diagnosing problems.
+----------+---------------------------------------------------------------------------
| INFO     | Confirmation that things are working as expected.
+----------+---------------------------------------------------------------------------
| WARNING  | An indication that something unexpected happened, or indicative of some problem in the near future.
+----------+---------------------------------------------------------------------------
| ERROR    | Due to a more serious problem, the software has not been able to perform some function.
+----------+---------------------------------------------------------------------------
| CRITICAL | A serious error, indicating that the program itself may be unable to continue running.
+----------+---------------------------------------------------------------------------
'''

# logging.basicConfig(filename='example.log',level=logging.DEBUG)

class util :
    
    @staticmethod
    def timestamp( ):
        
        return str( time.localtime()[:6] )
        
    @staticmethod
    def get_serial_code( class_instance ):
        
        return str(time.localtime(time.time())[:6])[1:-1].replace(', ','')+str(id( class_instance))
    
    @staticmethod 
    def extract_message_type( msg ):
    
        if type(msg) == dict :
            
            return msg["message_type"]
            
        elif type(msg) == str :
            
            return json.loads( msg )["message_type"]
        
    @staticmethod
    def extract_message_data( msg ):
        
        if type(msg) == dict :
            
            return msg["data"]
            
        elif type(msg) == str :
            
            return json.loads( msg )["data"]
     

class TaskRequest :
    
    def __init__( self , app=None , argv={} ):
        
        self.app = app
        
        self.argv = argv
        
        self.serial = util.get_serial_code( self )
        
    def builds( self , network_message ):
        
        data = json.loads( network_message )["data"]
        
        self.app = data["app"]
        self.argv = data["argv"]
        self.serial = data["serial"]

    def __str__( self ):
        
        return json.dumps( { 'message_type' : 'task_request' , 'data' : { 'app' : self.app , 'serial' : self.serial , 'argv' : self.argv } } , indent=4, separators=(',', ': ') )

class TaskResponse :
    
    def __init__( self , app , request_serial , result={} , error='' ):
        
        self.app = app
        
        self.request_serial = request_serial
        
        self.result = result
        
        self.error = error
        
    def __str__( self ):
         
        return json.dumps( { 'message_type' : 'task_response' , 'data' : { 'app' : self.app , 'request_serial' : self.request_serial , 'result' : self.result , 'error' : self.error } } , indent=4 , separators=(',', ': ') )

class SessionControl :
    
    BSRQ = '''
    {
        "message_type" : "session_control" ,

        "data" : 
        {
            "message" : "BSRQ"
        }
    }
    '''
    
    ESRQ = '''
    {
        "message_type" : "session_control" ,

        "data" : 
        {
            "message" : "ESRQ"
        }
    }
    '''

    BSLQ = '''
    {
        "message_type" : "session_control" ,

        "data" : 
        {
            "message" : "BSLQ"
        }
    }
    '''
    
    ESLQ = '''
    {
        "message_type" : "session_control" ,

        "data" : 
        {
            "message" : "ESLQ"
        }
    }
    ''' 
# +-----------------------------------------------------+
#                  NETWORK MESSAGE END
# +-----------------------------------------------------+

# +-----------------------------------------------------+
#                  Moon Server BGN
# +-----------------------------------------------------+

'''
Build MoonServer

    1 - Build MoonServer Instance
    2 - Change base dir to "/home/moonserver"
    3 - Load string constants from "moon.config"
    4 - Setup values for Daemon Super Class
    5 - Loading Application Map
    6 - Get ip on ethernet device set device
    7 - From here we jump to Run

Run MoonServer

    1 - Build TCP Socket Server
    2 - Bind for selected ip
        Error : Cant bind. Kill Daemon
    3 - Wait for connection
        Error : Kill Daemon
    4 - Connection Received. Select which type of session
    5 - Call A function to handle the session type
    6 - Wait function return and go to 3

Solving Tasks # anyerror on socket connection make it return function
    
    1 - Wait client to send a message
        1.1 - TaskRequest goto 2
        1.2 - End Session : Close client connection : Return function
    2 - Recover Application Name
    3 - Try to open Application based on actual Application Map
        Error : Application Not defined : Return An Error message on TaskResponse
    4 - Run Application
        Error : Run time execution on application : Return An Error message on TaskResponse
    5 - Send to client TaskResponse, and goto 1

'''

class Application :
    
    def __init__( self , alias , boot ):
        
        self.alias = alias
        
        self.boot = boot

class MoonServer( Daemon ) :
    
    def log( self , msg ):
        
        print str( time.localtime()[:6] ) +'[MoonServer]'+ msg

    def __init__( self , config_file ):
        
        # --- The "moon.config" file is storef at default working directory "/home/moonserver"
        self.log( '[__init__][openning moon.config file]' )
        
        config_file = json.load( open( config_file ) )
        
        # --- Setup values to Fork/Daemon Process 
        
        # - The default working directory set on .service (systemd) file
        self.working_dir = config_file["base"]
        
        # - Where the Application Codes are Stored 
        self.app_working_dir = self.working_dir+'/'+config_file["applications"]
        
        # - Where the Application Info Map are Stored
        self.app_map_working_dir = self.working_dir+'/'+ config_file["applications_map"]
        
        pid    = config_file["pid"]
        stdin  = config_file["stdin"]
        stdout = config_file["stdout"]
        stderr = config_file["stderr"]
        
        network_interface = config_file["network_interface"] 
        
        self.log( '[__init__][all config string are loaded]' )
        
        # ---[  ] - indexing all application maps
        
        self.log( '[__init__][changing from directorys][from]['+os.path.abspath('.')+'][to][' + self.app_map_working_dir +']')
        
        os.chdir( self.app_map_working_dir )
        
        self.log( '[__init__][recovering/indexing applications][bgn]' )
        
        self.applications = {}
        
        try :
            
            for map_file in os.listdir( '.' ) :
                
                map_file = json.load( open( map_file ) )
                
                self.log( '[__init__][indexing][app]['+map_file["alias"]+']' )
                
                self.applications[ map_file["alias"] ] = Application( map_file["alias"] , config_file["applications"]+'.'+map_file["boot"] )
                
                self.log( '[__init__][recovering/indexing applications][end]' ) 
                
        except :
            
            print_exc()
            
            self.log( '[__init__][warning][no applications available][]' )
         
        # ---[ ] - collecting network info
        self.log( '[__init__][collecting network info][bgn]' ) 
        
        # --- Network ---[bgn]
        network_interface = config_file["network_interface"]
        
        self.log( '[__init__][collecting network info][getting ip from]['+network_interface+']' ) 
        
        self.ip            = netifaces.ifaddresses(network_interface)[netifaces.AF_INET][0]['addr']
        self.port          = 666
        
        self.log( '[__init__][collecting network info][end]' ) 
        # --- Network ---[end] 
        
        self.log( '[__init__][building daemon class]' ) 
        super( MoonServer , self ).__init__( pid , stdin , stdout , stderr )
        
    def run( self ):
        
        self.log( '[run][entering on main loop]' ) 
        
        while True :
            
            # ---[ 1 ]
            self.log( '[run][main loop][build socket server]' ) 
            socket_server = TCPSocketServer()
            
            # ---[ 2 ]
            self.log( '[run][main loop][binding]' ) 
            if socket_server.bind( self.ip , self.port ) == 0 : # bind success
                
                # ---[ 3 ]
                self.log( '[run][main loop][wait master]' ) 
                socket_client = socket_server.wait()
                
                if socket_client != None : # connection stablhisment sucess
                    
                    # ---[ 4 ]
                    self.log( '[run][main loop][waiting for message]' ) 
                    msg = socket_client.read()
                    
                    self.log( '[run][main loop][message received][extracting message type]' ) 
                    msg_type = util.extract_message_type( msg )
                    
                    if msg_type == 'session_control' :
                        
                        self.log( '[run][main loop][session control message type]' ) 
                        
                        self.log( '[run][main loop][extracting data from message][queue behavior]' ) 
                        msg_data = util.extract_message_data( msg )
                        
                        queue_mode = msg_data["message"]
                        
                        # ---[ 5 ]
                        if queue_mode == 'BSRQ' :
                            
                            self.log( '[run][main loop][set remote queue session]' ) 
                            
                            self.begin_session_remote_queue( socket_client )
                            
                            self.log( '[run][main loop][getting back from remote queue session]' ) 
                            
                        elif queue_mode == 'BSLQ' :
                            
                            self.log( '[run][main loop][local queue not implemented... yet!]' )
                            pass
            else :
                
                self.log( '[run][main loop][cant binding]' ) 
                self.log( '[run][main loop][shutting down daemon]' ) 
                self.stop()
        
        self.log( '[run][main loop][end]' ) 
        
    '''

    Solving Tasks # anyerror on socket connection make it return function
    
    1 - Wait client to send a message
        1.1 - TaskRequest goto 2
        1.2 - End Session : Close client connection : Return function
    2 - Recover Application Name
    3 - Try to open Application based on actual Application Map
        Error : Application Not defined : Return An Error message on TaskResponse
    4 - Run Application
        Error : Run time execution on application : Return An Error message on TaskResponse
    5 - Send to client TaskResponse, and goto 1
    ''' 
    def begin_session_remote_queue( self , client ):
        
        self.log( '[run][begin_session_remote_queue][main loop][bgn]' )
        
        while True :
            
            # ---[ 1 ]
            self.log( '[run][begin_session_remote_queue][main loop][wait for message]' )
            msg = client.read()
            
            if util.extract_message_type( msg ) == 'session_control' :
                
                self.log( '[run][begin_session_remote_queue][main loop][session control message to shutdown session]' )
                client.close()
                
                return 0 # normal termination
                
            else : # it must to be taskrequest message, if not discard connection
                
                self.log( '[run][begin_session_remote_queue][main loop][task request message type]' )
                
                # ---[ 2 ]
                task_request = TaskRequest( )
                
                self.log( '[run][begin_session_remote_queue][main loop][building a TaskRequest Object from the message]' )
                task_request.builds( msg )
                 
                # ---[ 3 ]
                self.log( '[run][begin_session_remote_queue][main loop][extracting application name]' )
                app_info = self.applications[ task_request.app ]
                
                if app_info :
                    
                    # ---[ 4 ]
                    self.log( '[run][begin_session_remote_queue][main loop][application exist]' )
                    
                    os.chdir( self.working_dir )
                    
                    self.log( '[run][begin_session_remote_queue][main loop][preparing TaskResponse]' )
                    
                    task_response = TaskResponse( task_request.app , task_request.serial , {} )
                    
                    self.log( '[run][begin_session_remote_queue][main loop][executing application]' )
                    
                    try :
                        
                        
                        app = __import__( app_info.boot , globals() , locals() , ['applications'], -1 )
                        
                        app.Boot(task_request , task_response)
                        
                        self.log( '[run][begin_session_remote_queue][main loop][application execution is done][send back response]' )
                        
                        client.send( str(task_response) )
                    
                    except :
                        
                        self.log( '[run][begin_session_remote_queue][main loop][error][something wrong on execution try]' )
                        
                        print_exc()
                        
                        client.close()
                    
                else :
                    
                    self.log( '[run][begin_session_remote_queue][main loop][application not installed][send back a TaskResponse with error reporting]' )
                    
                    if client.send( TaskResponse( task_request.app , task_request.serial , {} , error="Application Not Installed" ) ) == 1:
                        
                        self.log( '[run][begin_session_remote_queue][main loop][error][cant send error reporting]' )
                        
                        client.close()
                        

if __name__ == "__main__":
    
    # ---[ Rising MoonServer ]---
    
    daemon = MoonServer( '/home/moonserver/moon.config' )

    if len(sys.argv) == 2:
        
        if 'start' == sys.argv[1]:
            
            daemon.start()
            
        elif 'stop' == sys.argv[1]:
            
            daemon.stop()
            
        elif 'restart' == sys.argv[1]:
            
            daemon.restart()
            
        else:
            
            print "Unknown command"
            
            sys.exit(2)
            
        sys.exit(0)
        
    else:
        
        print "usage: %s start|stop|restart" % sys.argv[0]
        
        sys.exit(2)
