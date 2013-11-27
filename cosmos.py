'''

Cosmos 

An python message-oriented middleware


'''

from __future__ import with_statement

__author__ = 'Ramon M.'
__version__ = '0.1.0'
__license__ = 'GPL-3.0'

import sys , os , signal , time , json 
# , netifaces , importlib

from vysocket import TCPSocketClient , TCPSocketServer
from vylog    import VyLog
from multiprocessing  import Process , Queue , Pool , Manager
from traceback        import print_exc ,  format_exc
import socket as pysocket

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
            
            self.moon_name = json_str["moon_name"]
        else :
            
            self.app = app
            
            self.argv = argv
            
            self.serial = str(time.localtime(time.time())[:6])[1:-1].replace(', ','')+str(id(self))
            
            self.result         = result
            
            self.error          = error
            
            self.execution_time = execution_time
            
            self.moon_name = ''
        
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
        
        return self[ moon_name ]
        
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
        
        global expedition
        
        # ---[ 1 ]------------------------------------------------------
        
        self.log.show( 'Checking Moon list sent by user' )
        
        working_moons = []
        
        if not moon_name_list :
            
            self.log.show( 'Traveling to available Moons on Orbit' )
            
            working_moons = self.orbit.values()
            
        else :
            
            self.log.show( 'Traveling to ' + str( moon_name_list ) )
            
            working_moons = [ self.orbit.get_moon( moon_name ) for moon_name in moon_name_list ]
            
        # ---[ 2 ]------------------------------------------------------
        
        self.log.show( 'Build Thread-safe Queues with no maximum size' )
        
        recv_queue = Manager().Queue( )#len(task_request_list) )
        
        send_queue  = Manager().Queue( )#len(task_request_list) )

        # ---[ 3 ]------------------------------------------------------
        
        self.log.show( 'Enqueue tasks on "send_queue" object' )
        
        for task_obj in task_request_list : 
            
            send_queue.put_nowait( str(task_obj) ) # "Normal" Objects are note thread safe!
            
        self.log.show( 'send_queue = ' + str(send_queue.qsize())+'/'+str(len(task_request_list)) + 'tasks')
        
        # ---[ 4 ]------------------------------------------------------
        
        self.log.show( 'Starting up Process Pool' )
                
        pool = Pool(processes=len(working_moons))

        

        for moon in working_moons :
            
            #running_expeditions.append( Process( target=expedition , args=(self.name , moon.name , moon.ip , moon.port , taskrequest_queue , taskresponse_queue, ) ) ) # Process Object
            pool.apply_async( func=expedition , args=(self.name , moon.name , moon.ip , moon.port , send_queue , recv_queue , ) )

        # ---[ 5 ]------------------------------------------------------
        
        pool.close()
        pool.join()
        
        self.log.show( 'recv_queue = '+ str(recv_queue.qsize())+'/'+str(len(task_request_list)) + 'tasks' )
        
        tmp = []
        while not recv_queue.empty() :
            
            tmp.append( recv_queue.get() )
            
        self.log.show( 'closing queue' )
        
        self.log.show( 'return results' )
        
        return tmp

def expedition( planet_name , moon_name , moon_ip , moon_port , send_q , recv_q ):
    
    log = VyLog( 'Expedition' )
          
    log.show('Expedition to '+moon_name+' is launched')
    
    try :
        
        #log.show('Entering on main loop')
        
        while not send_q.empty() :
            log.show('get task to send')
            task_json_str = send_q.get()
            
            try :
                
                moon_connection = TCPSocketClient()
            
                log.show( 'connecting to '+moon_name )
            
                moon_connection.connect( moon_ip , moon_port ) # Moon(Slave Host) is down.
                
                log.show( 'sending task to '+moon_name )
                
                moon_connection.send( task_json_str )
                
                log.show( 'reading a response from '+moon_name )
                
                task_json_str = moon_connection.read()
                
                log.show( 'closing connection' )
                
                moon_connection.close()
                
                log.show( 'enqueue on recv_queue' )
                
                recv_q.put_nowait( task_json_str )
                
            except :
                
                send_q.put( task_json_str )
                
                log.show( 'Expedition on '+moon_name+' is aborted!' )
                
                log.show(format_exc())
                
                break
                
            
    except :
        
        log.show( 'Expedition on '+moon_name+' is aborted!' )
        
        log.show(format_exc())
        
    log.show( 'Expedition on '+moon_name+' was a sucess! returning to home!' )

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
            
            self.log.show( '[executing app]' )
            
            s = time.time()
            
            task_obj.result , task_obj.error = app.run( task_obj.get_arguments() )
            
            e = time.time()
            
            task_obj.execution_time = e - s
            
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
            
            self.log.show( "[filling up std ( in |out | err ) for daemon class]" )
            
            # ---
            
            self.log.show( "[filling up directorys" )
            
            self.application_dir = moon_cfg["directorys"]["applications"]
            self.application_profile_dir = moon_cfg["directorys"]["application_profiles"]
            
            self.pidfile = moon_cfg["pid"]
            
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
        
        self.log.show('persisting pid -> ' + moon_cfg["pid"] )
        
        if not os.path.isfile(moon_cfg["pid"]):
            
            pid = open( self.pidfile , 'w' )
            
            pid.write(str( os.getpid() ))
            
            pid.close()
        
    def start( self ):
        
        self.run()
        
    def stop( self ):
        
        if os.path.isfile(self.pidfile):
            
            pid = ''.join( open( self.pidfile , 'r' ) )
            
            try :

                self.log.show('Kill moon server at PID '+pid)
                
                os.kill( int(pid) , 9 )
                
            except :
                
                self.log.show('pid file exist but process is already dead!')
                
            os.remove( self.pidfile )
            
        else :
            
            self.log.show('there is nothing to stop! .-.')
        
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
                
                self.log.show( '[closing connection]' )
                
                client.close()
                
        except :
            
            print_exc() 
            
            if server : server.close()
            
            if client : client.close()
            
            self.stop()
            
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
            
            task_obj.moon_name = self.name
            
            self.log.show( '[sending result to planet]' )
            
            client.send( str( task_obj ) )
            
        except :
            
            print_exc()
            
