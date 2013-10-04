import logging , json , sys , time , os
from vysocket  import TCPSocketClient
from multiprocessing import Process , Queue
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
        
        self.log = logging.getLogger( self.__class__.__name__ )
        
        logging.info( 'creating new instance' )
        
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
    
    def __init__( self , app , request_serial , result , error='' ):
        
        self.app = app
        
        self.request_serial = request_serial
        
        self.result = result
        
        self.error = error
        
    def builds( self , network_message ):
        
        data = json.loads( network_message )["data"]
        
        self.request_serial = data["request_serial"]
        self.result         = data["result"]
        self.error          = data["error"]
        self.app            = data["app"]
        
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
class Moon :
    
    def __init__( self , moon_dict ):
        
        self.name = moon_dict["name"]
        self.ip   = moon_dict["ip"]
        self.port = int(  moon_dict["port"] )
        self.connection_tuple =  ( self.ip , self.port )
        

class Planet :
    
    # Master Host Abstraction
    
    '''
    Orbit File Template

    {
        "name" : "planet_name",
        "ip"   : "planet_ip",
        "port" : planet_port,

        "moons" : 
        [
            { "name" : "moon_name" , "ip" : "moon_ip" , "port" : moon_host } 
        ]
    }

    '''

    def __init__( self , orbit_file_path ): # orbit file is a JSON formatted file :)
        
        # --- loading orbit configs - [bgn]
        
        orbit_json = json.load( open( orbit_file_path ) )
        
        self.name = orbit_json["name"]
        
        self.ip   = orbit_json["ip"]
        
        self.port = int( orbit_json["port"] ) # just make sure, ok?
        
        self.orbit = {}
        
        for moon in orbit_json["moons"] :
            
            print 'indexing moon : ' + moon["name"]
            
            self.orbit[ moon["name"] ] = Moon( moon )
            
        # --- loading orbit configs - [end]
    
    def launch_expeditions( self , task_request_list , moon_name_list=None ):
        
        print '[launch_expeditions][begin]'
        
        # --- Walktrough ---
        # 
        # 1. Check if user want only few moons on the orbi to get the job done
        #
        #   1.1 - moon_name_list = None 
        #
        #        User want to use all available moons
        #
        #   1.2 - moon_name_list = []
        #        
        #        We Have to select specific moons
        #
        # 2. Converting the LIST of TaskRequests on a Thread/Process Safe QUEUE
        #
        # 3. Build a Thread/Process Safe QUEUE for the TaskResponses
        #
        # 4. Build the Expedition
        #
        # 5. Launch the Expedition
        #
        # 6. Loop on Checking if all Expeditions are done
        #
        # 7. Return TaskResponses QUEUE

        # ---[ 1 ]
        
        print '[launch_expeditions][checking workers list]'
        
        working_moons = []
        
        if not moon_name_list :
            
            print '[launch_expeditions][using all available workers]'
            
            working_moons = self.orbit.values()
            
        else :
            
            print '[launch_expeditions][using selective workers] -> ' + str( moon_name_list )
            
            working_moons = [ self.orbit[moon_name] for moon_name in moon_name_list ]
        
        print working_moons
            
        # ---[ 2 ]
        
        print '[launch_expeditions][building queues]'
        
        task_response_q = Queue()
        
        task_request_q  = Queue()
        
        print '[launch_expeditions][putting task requests on Queue]'
        
        for task_request in task_request_list : 
            
            print str(task_request)
            
            task_request_q.put( str(task_request) ) # "Normal" Objects are note thread safe!
            
        # ---[ 4 ]
        
        print '[launch_expeditions][Building and Indexing Process]'
        
        running_expeditions = []
        
        for moon in working_moons :
            
            running_expeditions.append( Expedition( moon.ip , moon.port , task_request_q , task_response_q ) )
        
        # ---[ 5 ]
        
        print '[launch_expeditions][Starting up Process]'
        
        for expedition in running_expeditions : 
            
            expedition.start()
        
        # ---[ 6 ]
        
        print '[launch_expeditions][waitting process termination]'
        
        while True:
            
            if sum( [ expedition.is_alive() for expedition in running_expeditions ] ) == 0 : 
                
                break
         
        # ---[ 7 ]
        
        print '[launch_expeditions][process is done]'
        
        return task_response_q

class Expedition( Process ) :
    
    def __init__( self , moon_ip , moon_port , task_request_queue , task_response_queue ):
        
        print '[Expedition][__init__][bgn]'
        
        super( Expedition , self ).__init__()
        
        self.moon_ip = moon_ip
        self.moon_port = moon_port
        self.task_request_queue  = task_request_queue
        self.task_response_queue = task_response_queue
        
        print '[Expedition][__init__][end]'
        
    def run( self ):
        
        print '[Expedition][run][bgn]'
        
        try :
            # ---[ 1 ]--- Creating a TCP Socket
            print '[Expedition][run][1]'
            moon_connection = TCPSocketClient()
            
            # ---[ 2 ]--- Recovering Connection Tuple From Moon Object (ip/port)
            print '[Expedition][run][2]'
            
            if moon_connection.connect( self.moon_ip , self.moon_port ) == 0:
                
                # ---[ 3 ]--- Setup Queue Mode
                print '[Expedition][run][3]' , SessionControl.BSRQ
                moon_connection.send( SessionControl.BSRQ )
                
                print '[Expedition][run][entering on loop]'
                while not self.task_request_queue.empty() :
                    
                    # ---[ 4 ]--- Get new task to send
                    print '[Expedition][run][4]'
                    task_request = self.task_request_queue.get()
                    
                    print '[Expedition][run][taks ['+task_request+'] send for moon]' 
                    
                    # ---[ 5 ]--- Sending Task
                    print '[Expedition][run][5]'
                    if moon_connection.send( task_request ) == 0:
                        
                        # ---[ 6 ]--- Wait result
                        print '[Expedition][run][6][waiting result]'
                        msg = moon_connection.read()
                        
                        if msg != None :
                            
                            # ---[ 7 ]--- parse data
                            print '[Expedition][run][7][extract data from network message]'
                            data = util.extract_message_data( msg )
                            
                            # ---[ 8 ]--- put request response on response queue
                            print '[Expedition][run][8][put response on queue result]' 
                            self.task_response_queue.put( data )
                            
                        else :
                        
                            print '[Expedition][run][6][error] cant read task response message! moon is probably out of orbit!'
                            
                            print '[Expedition][run][6][error] requeue task'
                            self.task_request_queue.put( task_request )
                            
                            print '[Expedition][run][6] shutting down connection'
                            moon_connection.close()
                        
                    else :
                        
                        print '[Expedition][run][5] cant send task request message! moon is probably out of orbit!'
                        
                        print '[Expedition][run][5] requeue task'
                        self.task_request_queue.put( task_request )
                        
                        print '[Expedition][run][5] shutting down connection'
                        moon_connection.close()
                        
                # ---[ 9 ]--- Quit connection
                if moon_connection.send( SessionControl.ESRQ ) == 0:
                    
                    print '[Expedition][run][9] no more tasks to solve! ending session'
                    moon_connection.close()
                    
                else :
                    
                    print '[Expedition][run][9] cant send end session message! moon is probably out of orbit!' 
                    print '[Expedition][run][9] shutting down connection' 
                    moon_connection.close()
        
        except :
            
            print_exc()


