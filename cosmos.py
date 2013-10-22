'''

Cosmos 

An python message-oriented middleware


'''

from __future__ import with_statement

__author__ = 'Ramon M.'
__version__ = '0.1.0'
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

class NetworkMessage : 
    
    # Deprecated for now.
    
    # addresser - remetente
    # addressee - destinatario
    
    def __init__( self ,  addresser=None , addressee=None , subject=None , body=None , message=None ):
        
        if message : # is a string on JSON format

            message_dict = json.loads( message )
            
            self.addresser = message_dict["addresser"]
            self.addressee = message_dict["addressee"]
            
            self.subject   = message_dict["subject"]
            self.body      = message_dict["body"]
        
        else :
            
            self.addresser = addresser
            self.addressee = addressee
            
            self.subject   = subject
            
            if type( body ) == str :
            
                self.body      = json.loads(body)
                
            else : 
            
                self.body      = body
    
    def __str__( self ):
        
        return json.dumps( self , default=lambda o: o.__dict__ )

class Arguments :
    
    def __init__( self , argv ):
        
        self.__dict__.update( json.loads(argv) )

class TaskRequest :
    
    SUBJECT = 'task_request'
    
    def __init__( self , app="" , argv={} , network_message_str=None ):
        
        if network_message_str :
            
            network_message_str = json.loads( network_message_str )
            
            self.app    = network_message_str["app"]
            
            self.argv   = network_message_str["argv"]
            
            self.serial = network_message_str["serial"]
            
        else :
            
            self.app = app
            
            self.argv = argv
            
            self.serial = util.get_serial_code( self )
            
    def append_arg( self , arg_name , arg_value ):
        
        self.argv[ arg_name ] = arg_value
        
    def to_object( self ):   
        
        return Arguments( self.argv )
        
    def get_TaskResponse( self ):
        
        return TaskResponse( self.app , self.serial )
        
    def __str__( self ):
        
        return json.dumps( self , default=lambda o: o.__dict__  , indent=4 )

class TaskResponse : 
    
    SUBJECT = 'task_response'
    
    def __init__( self , app="" , request_serial=-1 , result={} , error="no errors" , network_message_str=None ):
        
        if network_message_str :
            
            network_message_str = json.loads( network_message_str )
            
            self.app            = network_message_str["app"]
            self.request_serial = network_message_str["resquest_serial"]
            self.result         = network_message_str["result"]
            self.error          = network_message_str["error"]
            
        else :
            
            self.app            = app
            self.request_serial = request_serial
            self.result         = result
            self.error          = error
        
    def __str__( self ):
         
        return json.dumps( self , default=lambda o: o.__dict__  , indent=4 )

class SessionControl :
    
    SUBJECT = "session_control"
    
    MESSAGE_BSRQ = { "message" : "BSRQ" } # BEGIN SESSION REMOTE QUEUE
    
    MESSAGE_ESRQ = { "message" : "ESRQ" } # END SESSION REMOTE QUEUE

    MESSAGE_BSLQ = { "message" : "BSLQ" } # BEGIN SESSION LOCAL QUEUE
    
    MESSAGE_ESLQ = { "message" : "ESLQ" } # END SESSION LOCAL QUEUE
    
    @staticmethod
    def to_dict( session_control_str_json ):
        
        try :
            
            return json.loads( session_control_str_json )
            
        except :
            
            return None

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
                
                task_request_json_str = self.task_request_queue.get()
                
                self.log.show( 'Flying to Moon@'+self.moon_name )
                
                moon_connection.send( task_request_json_str )
                
                self.log.show( 'Expedition has landing! Waiting to get back to home.' )
                
                task_response_json_str = moon_connection.read()
                
                self.log.show( 'Comming back to home with result' )
                
                self.log.show( 'Response : ' + task_response_json_str )
                
                self.log.show( 'Enqueue response to TaskResponse Queue' )
                
                self.task_response_queue.put( task_response_json_str )
                
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
            
            print '[Application][__init__][error][wrong json format]'
            
            print_exc()
            
            return 1
            
    def __str__( self ):
         
        return json.dumps( self , default=lambda o: o.__dict__  , indent=4 )
        
    def run( self , taskrequest_obj ):
        
        #taskresponse_obj = TaskResponse( taskrequest_obj.app , taskrequest_obj.serial )
        
        taskresponse_obj = taskrequest_obj.get_TaskResponse()
        
        print '[Application][run][current dir]['+str(os.getcwd())+']'
        
        try :
            
            print '[Application][run][current dir][importing module]['+self.boot_module+']'
            
            print self.boot_module
            print self.boot_module.split('.')[-1]
            
            app = __import__( self.boot_module , globals() , locals() , [ self.boot_module.split('.')[-1] ] , -1 )
            print ' >>> app >>> ' , app.__file__
            
            os.chdir(  os.path.dirname( app.__file__ ) )
            
            #app = importlib.import_module( self.boot_module )
            
            result_queue = Queue()
            
            error_queue = Queue()
            
            print '[Application][run][executing app]'
            
            taskresponse_obj.result , taskresponse_obj.error = app.run( taskrequest_obj.to_object() , result_queue , error_queue )
            
            print '[Application][run][done execution]'
            
            return taskresponse_obj
            
        except:
            
            print '[Application][run][error][cant import application]'
            
            taskresponse_obj.error = "[cant import application]" + format_exc()
            
            return taskresponse_obj
    
class Directory :
    
    APPLICATIONS     = '~/.cosmos/moonserver/applications'
    APPLICATION_PROFILES = '~/.cosmos/moonserver/applications_map'

class Stream :
    
    STDIN = '/dev/null'
    STDOUT = '/dev/null'
    STDERR = '/dev/null'

class MoonServer :
    
    def log( self , msg ):
        
        print '[MoonServer]' + msg
    
    def __init__( self , moonserver_config_file ):
        
        # ---[ 1 ]--- config file located!
        self.log('[__init__][checking if the config file exits]')
        
        if os.path.isfile( moonserver_config_file ) :
            
            try :
                
                # ---[ 2 ]--- extract data from config file as JSON-----
                self.log('[__init__][config file exist! extracting info]')
                
                moonserver_config_dict = json.load( open( moonserver_config_file ) )
                
                # ---[ 2.1 ]--- network message info
                self.log('[__init__][config file][extrac info][name]')
                
                self.name = moonserver_config_dict["name"]
                
                # ---[ 2.2 ]--- network info
                self.log('[__init__][config file][extrac info][network info]')
                
                self.port = int( moonserver_config_dict["port"] )
                self.network_device = moonserver_config_dict["network_device"]
                self.ip = None # we will get this little one on run method
                
                # ---[ 2.3 ]--- stream pipes info ----------------------
                self.log('[__init__][config file][stream pipes]')
                
                if moonserver_config_dict["stream"]["stdin"] != Stream.STDIN :
                    
                    Stream.STDIN = moonserver_config_dict["stream"]["stdin"]
                    
                if moonserver_config_dict["stream"]["stdout"] != Stream.STDOUT :
                    
                    Stream.STDOUT = moonserver_config_dict["stream"]["stdout"]
                    
                if moonserver_config_dict["stream"]["stderr"] != Stream.STDERR :
                    
                    Stream.STDERR = moonserver_config_dict["stream"]["stderr"]
                    
                # ---[ 2.4 ]--- directorys -----------------------------
                self.log('[__init__][config file][extrac info][directorys]')
                    
                if moonserver_config_dict["directorys"]["applications"] != Directory.APPLICATIONS :
                    
                    Directory.APPLICATIONS = moonserver_config_dict["directorys"]["applications"]
                    
                if moonserver_config_dict["directorys"]["application_profiles"] != Directory.APPLICATION_PROFILES :
                    
                    Directory.APPLICATION_PROFILES = moonserver_config_dict["directorys"]["application_profiles"]
                
                self.log('[__init__][config file][extrac info][done]')
                
                # ---[ 3 ]--- Build up Daemon Super Class --------------
                self.log('[__init__][instancing daemon super class]')
                
            except :
                
                print_exc()
                self.log( '[__init__][wrong json format :/]' )
                self.log( '[__init__][bye bye]' )
                exit( 0 )
                
        else :
            
            self.log( '[__init__][error][cant load config file at given path]' )
            self.log( '[__init__][error][bye bye]' )
            exit( 0 )
        
        # --[ 4 ]--- Indexing Application Maps
        self.log( '[__init__][indexing application on RAM memory]' )
        
        self.library = {}
        
        self.log( '[__init__][change to application profiles directory]['+Directory.APPLICATION_PROFILES+']' )
        os.chdir( os.path.expanduser( Directory.APPLICATION_PROFILES ) )
        
        for app_profile_filename in os.listdir('.'):
            
            app_tmp = Application()
            
            try :
            
                app_profile_dict = json.load( open( app_profile_filename ) )
                
                if 0 == app_tmp.load_profile( app_profile_dict ) :
                    
                    self.library[app_tmp.alias] = app_tmp
                    
                    self.log( '[__init__][application]['+app_tmp.alias+'][indexed]' )
                    
            except :
                
                print_exc()
                
                self.log( '[__init__][error][wrong json formating on profile][application will not be indexed]' )
                
                
                
        sys.path.append( os.path.expanduser( Directory.APPLICATIONS ) )
        
    def start( self ):
        
        self.run()
        
    def stop( self ):
        
        pass
        
    def run( self ):
        
        server = None
        
        client = None
        
        try :
            
            self.ip = netifaces.ifaddresses(self.network_device)[netifaces.AF_INET][0]['addr']
            
            self.log( '[Moonserver][run][setting up to bind]['+self.ip+'/'+str(self.port)+']' )
            
            server = TCPSocketServer()
            
            server.bind( self.ip , self.port )
                
            while True :
                
                self.log( '[Moonserver][run][wait for an expedition]' )
                
                client = server.wait()
                
                self.log( '[Moonserver][run][solving task mode]' )
                
                self.solving_tasks( client )
                
                self.log( '[Moonserver][run][closing connectio]' )
                
                client.close()
                
        except :
            
            print_exc() 
            
            server.close()
            
            client.close()
            
            
            
            exit(0)
    
    def solving_tasks( self , client ):
        
        try :
            
            self.log( '[Moonserver][solving_tasks][wait for a task request]' )
            
            task_request_str = client.read()
            
            task_request_obj = TaskRequest( network_message_str = task_request_str )
            
            self.log( '[Moonserver][solving_tasks][checking if the app is intalled]['+task_request_obj.app+']' )
            
            app = self.library[ task_request_obj.app ]
            
            self.log( '[Moonserver][solving_tasks][executing]['+task_request_obj.app+']' )
            
            task_response_json_obj = app.run( task_request_obj )
            
            self.log( '[Moonserver][solving_tasks][sending result to planet]' )
            
            client.send( str( task_response_json_obj ) )
                
        except :
            
            print_exc()
            
            return 0
            
        return 0
        
#if __name__ == '__main__':
#    
#    if len(sys.argv) == 2 :
#        
#        print 'running cosmos as a moon slave host'
#        MoonServer( sys.argv[1] ).run()
