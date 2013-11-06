'''

Cosmos 

An python message-oriented middleware


'''

from __future__ import with_statement

__author__ = 'Ramon M.'
__version__ = '2.0.0'
__license__ = 'GPL-3.0'

import json , sys , time , os , netifaces , importlib

from vysocket import TCPSocketClient , TCPSocketServer
from vylog    import VyLog
from multiprocessing  import Process , Queue , Pool
from traceback        import print_exc ,  format_exc

class util :
    
    @staticmethod
    def timestamp( ):
        
        return str( time.localtime()[:6] )
        
    @staticmethod
    def get_serial_code( class_instance ):
        
        return str(time.localtime(time.time())[:6])[1:-1].replace(', ','')+str(id( class_instance))

class Arguments :
    
    def __init__( self , argv ):
        
        if type( argv ) == str :
            
            self.__dict__.update( json.loads(argv) )
            
        else :
            
            self.__dict__.update( argv )
            

class Task :
    
    SUBJECT = 'task'
    
    def __init__( self , app="None" , argv={} , result="None" , error="None" , execution_time=-1 , json_str=None ):
        
        if json_str :
            
            json_str = json.loads( json_str )
            
            self.app    = json_str["app"]
            
            self.argv   = json_str["argv"]
            
            self.serial = json_str["serial"]
            
            self.result         = json_str["result"]
            
            self.error          = json_str["error"]
            
            self.execution_time = json_str["execution_time"]
            
        else :
            
            self.app = app
            
            self.argv = argv
            
            self.serial = util.get_serial_code( self )
            
            self.result         = result
            
            self.error          = error
            
            self.execution_time = execution_time
     
    def append_arg( self , arg_name , arg_value ):
        
        self.argv[ arg_name ] = arg_value
        
    def append_result( self , result_name , result_value ):
        
        self.result[ result_name ] = result_value
        
    def get_arguments( self ):
        
        return Arguments( self.argv )
        
    def __str__( self ):
        
        return json.dumps( self , default=lambda o: o.__dict__ )

class Orbit( dict ):
    
    def __init__( self , moons ):
        
        for moon_row in moons :
            
            self[ moon_row[0] ] = Moon( moon_row[0] , moon_row[1] )
            
    def get_moon( self , moon_name ):
        
        return Moon( moon_name , self.get( moon_name ) )
        
    def __str__( self ):
         
        return json.dumps( self , default=lambda o: o.__dict__  , indent=4 )

class Moon :
    
    def __init__( self , name , moon_dict ):
        
        self.name = name
        
        self.ip   = moon_dict["ip"]
        
        self.port = int(  moon_dict["port"] )
        
    def __str__( self ):
        
        return json.dumps( self , default=lambda o: o.__dict__  , indent=4 )

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
            [ "moon_name" , { "ip" : "moon_ip" , "port" : moon_host } ]
        ]
    }
    '''

    def __init__( self , orbit_file_path ): # orbit file is a JSON formatted file :)
        
        self.log = VyLog( self.__class__.__name__ ) 
        
        # --- loading orbit configs - [bgn]
        
        self.log.show('loading orbit configs [bgn]')
        
        orbit_json = json.load( open( orbit_file_path ) )
        
        self.name = orbit_json["name"]
        
        self.ip   = orbit_json["ip"]
        
        self.port = int( orbit_json["port"] ) # just make sure, ok?
        
        self.orbit = Orbit(orbit_json["moons"])
        
        self.log.show('loading orbit configs [end]')
            
        # --- loading orbit configs - [end]
    
    def launch_expeditions( self , task_request_list , moon_name_list=None ):
        
        self.log.show('[bgn]')
        
        # ---[ 1 ]------------------------------------------------------
        self.log.show( 'Checking Moon list sent by user' )
        
        working_moons = []
        
        if not moon_name_list :
            
            self.log.show( 'Using all available Moons on Orbit' )
            
            working_moons = self.orbit.values()
            
        else :
            
            self.log.show( 'Using selective workers -> ' + str( moon_name_list ) )
            
            working_moons = [ self.orbit.get_moon( moon_name ) for moon_name in moon_name_list ]
            
        # ---[ 2 ]------------------------------------------------------
        self.log.show( 'Build Thread-safe Queues' )
        
        taskresponse_queue = Queue()
        
        taskrequest_queue  = Queue()
        
        # ---[ 3 ]------------------------------------------------------
        self.log.show( 'Enqueue tasks on Thread-safe Queue object' )
        
        for taskrequest_obj in task_request_list : 
            
            print '[Planet][launch_expeditions][3.1][enqueue task]' + str(taskrequest_obj)
            
            taskrequest_queue.put( str(taskrequest_obj) ) # "Normal" Objects are note thread safe!
            
        # ---[ 4 ]------------------------------------------------------
        
        self.log.show( 'Building and Indexing Process Objects' )
        
        running_expeditions = []
        
        for moon in working_moons :
            
            running_expeditions.append( Expedition( self.name , moon.name , moon.ip , moon.port , taskrequest_queue , taskresponse_queue ) )
            
        # ---[ 5 ]------------------------------------------------------
        
        self.log.show( 'Starting up Process' ) 
        
        for expedition in running_expeditions : 
            
            expedition.start()
            
        # ---[ 6 ]------------------------------------------------------
        
        self.log.show( 'waitting process join]' )
        
        while True:
            
            if sum( [ expedition.is_alive() for expedition in running_expeditions ] ) == 0 : 
                
                break
         
        # ---[ 7 ]
        
        self.log.show('[end]')
        
        return taskresponse_queue

class Expedition( Process ) :
    
    def __init__( self , planet_name , moon_name , moon_ip , moon_port , task_request_queue , task_response_queue ):
        
        self.log = VyLog( self.__class__.__name__ )
        
        self.log.show('Creating Instance of Super Class "Process"')
        
        super( Expedition , self ).__init__()
        
        self.planet_name = planet_name
        
        self.moon_name = moon_name
        
        self.moon_ip   = moon_ip
        
        self.moon_port = moon_port
        
        self.task_request_queue = task_request_queue
        
        self.task_response_queue = task_response_queue
        
    def run( self ):
        
        self.log.show('[bgn]')
        
        try :
            
            self.log.show('Entering on main loop')
            
            while not self.task_request_queue.empty() :
                
                self.log.show( 'Task Queue is not empty' )
                
                moon_connection = TCPSocketClient()
                
                self.log.show( 'Contacting Base at Moon@'+self.moon_name )
                
                moon_connection.connect( self.moon_ip , self.moon_port ) # Moon(Slave Host) is down.
                
                self.log.show( 'We have permission to flight' )
                
                task_json_str = self.task_request_queue.get()
                
                self.log.show( 'Flying to Moon@'+self.moon_name )
                
                moon_connection.send( task_json_str )
                
                self.log.show( 'Expedition has landing! Waiting to get back to home.' )
                
                task_json_str = moon_connection.read()
                
                self.log.show( 'Comming back to home with result' )
                
                self.log.show( 'Response : ' + task_json_str )
                
                self.log.show( 'Enqueue response to TaskResponse Queue' )
                
                self.task_response_queue.put( task_json_str )
                
                self.log.show( 'Shuttingdown Connection' )
                
                moon_connection.close()
                
        except :
            
            print_exc()
            
        self.log.show('[end]')

# +--------------------------------------------------------------------+
#
#    *                            (                                       
#  (  `                           )\ )                                    
#  )\))(                         (()/(     (    (       )       (    (    
# ((_)()\    (     (     (        /(_))   ))\   )(     /((     ))\   )(   
# (_()((_)   )\    )\    )\ )    (_))    /((_) (()\   (_))\   /((_) (()\  
# |  \/  |  ((_)  ((_)  _(_/(    / __|  (_))    ((_)  _)((_) (_))    ((_) 
# | |\/| | / _ \ / _ \ | ' \))   \__ \  / -_)  | '_|  \ V /  / -_)  | '_| 
# |_|  |_| \___/ \___/ |_||_|    |___/  \___|  |_|     \_/   \___|  |_| 
#  
# +--------------------------------------------------------------------+

class Application :
    
    def __init__( self ):
        
        self.log = VyLog( self.__class__.__name__ )
        self.name        = None
        self.alias       = None
        self.boot_module = None
    
    def load_profile( self , application_profile_dict ):
        
        try :
            
            self.name        = application_profile_dict["name"]
            self.alias       = application_profile_dict["alias"]
            self.boot_module = application_profile_dict["boot_module"]
            
            return 0
            
        except :
            
            self.log.show( '[error][wrong json format]' )
            
            print_exc()
            
            return 1
            
    def __str__( self ):
         
        return json.dumps( self , default=lambda o: o.__dict__  , indent=4 )
        
    def run( self , task_obj ):
        
        self.log.show( '['+str(os.getcwd())+']' )
        
        try :
            
            self.log.show( '[importing module]['+self.boot_module+']' )
            
            self.log.show( self.boot_module )
            self.log.show( self.boot_module.split('.')[-1] )
            
            app = __import__( self.boot_module , globals() , locals() , [ self.boot_module.split('.')[-1] ] , -1 )
             
            os.chdir(  os.path.dirname( app.__file__ ) )
            
            #app = importlib.import_module( self.boot_module )
            
            result_queue = Queue()
            
            error_queue = Queue()
            
            self.log.show( '[executing app]' )
            
            task_obj.result , task_obj.error = app.run( task_obj.get_arguments() , result_queue , error_queue )
            
            self.log.show( '[done execution]' )
            
        except:
            
            self.log.show('[error][cant import application]' )
            print_exc()
            task_obj.error = format_exc()
            
        
        return task_obj
    

class MoonServer :
    
    def __init__( self , moon_cfg ):
        
        self.log = VyLog( self.__class__.__name__ )
            
        try :
            
            moon_cfg = json.load( open( moon_cfg ) )
            
            self.log.show( "[filling up ip, port and name]" )
            
            self.ip = moon_cfg["ip"]
            self.port = int( moon_cfg["port"] )
            self.name = moon_cfg["name"]
            
            self.log.show( "[filling up std(in|out|err) for daemon class]" )
            
            # ---
            
            self.log.show( "[filling up directorys" )
            
            self.application_dir = moon_cfg["directorys"]["applications"]
            self.application_profile_dir = moon_cfg["directorys"]["application_profiles"]
            
        except :
            
            print_exc()
            
            self.log.show( '[wrong json format :/]' )
            
            self.log.show( '[bye bye]' )
            
            exit( 0 )
        
        self.log.show("[loading application index]")
        
        self.library = {}
        
        self.log.show( '[acessing]['+self.application_profile_dir+']' )
        
        os.chdir( os.path.expanduser( self.application_profile_dir ) )
        
        for app_profile_filename in os.listdir('.'):
            
            app_tmp = Application()
            
            try :
            
                app_profile_dict = json.load( open( app_profile_filename ) )
                
                if 0 == app_tmp.load_profile( app_profile_dict ) :
                    
                    self.library[app_tmp.alias] = app_tmp
                    
                    self.log.show( '[application]['+app_tmp.alias+'][indexed]' )
                    
            except :
                
                print_exc()
                
                self.log.show( '[error][wrong json formating on profile][application will not be indexed]' )
                
        self.log.show( '[appending application dir to path]['+self.application_dir+']' )
        
        sys.path.append( os.path.expanduser( self.application_dir ) )
        
    def start( self ):
        
        self.run()
        
    def stop( self ):
        
        pass
        
    def run( self ):
        
        server = None
        
        client = None
        
        try :
            
            #self.ip = netifaces.ifaddresses(self.network_device)[netifaces.AF_INET][0]['addr']
            
            self.log.show( '[setting up bind]['+self.ip+'/'+str(self.port)+']' )
            
            server = TCPSocketServer()
            
            server.bind( self.ip , self.port )
                
            while True :
                
                self.log.show( '[wait for an expedition]' )
                
                client = server.wait()
                
                self.log.show( '[solving task mode]' )
                
                self.solving_tasks( client )
                
                self.log.show( '[closing connectio]' )
                
                client.close()
                
        except :
            
            print_exc() 
            
            if server : server.close()
            
            if client : client.close()
            
            exit(0)
    
    def solving_tasks( self , client ):
        
        try :
            
            self.log.show( '[wait for a task request]' )
            
            task_json_str = client.read()
            
            task_obj = Task( json_str = task_json_str )
            
            self.log.show( '[checking if the app is intalled]['+task_obj.app+']' )
            
            app = self.library[ task_obj.app ]
            
            self.log.show( '[executing]['+task_obj.app+']' )
            
            task_obj = app.run( task_obj )
            
            self.log.show( '[sending result to planet]' )
            
            client.send( str( task_obj ) )
                
        except :
            
            print_exc()
            
#if __name__ == '__main__':
#    
#    if len(sys.argv) == 2 :
#        
#        print 'running cosmos as a moon slave host'
#        MoonServer( sys.argv[1] ).run()
