import network_messages as netm
import logging
import json

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
        
        logging.info( "loading orbit from : " + orbit_file_path )
        
        orbit_json = json.load( open( orbit_file_path ) )
        
        self.name = orbit_json["name"]
        
        self.ip   = orbit_json["ip"]
        
        self.port = int( orbit_json["port"] ) # just make sure, ok?
        
        self.orbit = {}
        
        for moon in orbit_json["moons"] :
            
            self.orbit[ moon_spec["name"] ] = Moon( moon )
            
        # --- loading orbit configs - [end]
    
    def launch_expeditions( self , task_request_list , moon_name_list=None ):
        
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
        
        logging.info( "launching expeditions" )
        
        logging.debug( "checking moon list" )
        
        # ---[ 1 ]
         
        working_moons = []
        
        if not moon_list :
            
            logging.debug( "using all available moons on the orbit" )
            
            self.working_moons = self.orbit.values()
            
        else :
            
            logging.debug( "using selection from user" )
            
            self.working_moons = [ self.orbit[moon_name] for moon_name in moon_name_list ]
            
        loggin.info( "enqueue tasks" )
        
        # ---[ 2 ]
        
        task_request_q  = Queue()
        
        for task_request in task_request_list : task_request_q.put( task_request ) 
        
        # ---[ 3 ]
        
        task_response_q = Queue()
        
        logging.info( "building expedition process" )
        
        # ---[ 4 ]
        
        running_expeditions = [ Expedition( task_request_q , task_response_q , moon ) for moon in working_moons ]
        
        logging.info( "starting up expeditions processes" )
        
        # ---[ 5 ]
        
        for expedition in running_expeditions : expedition.start()
        
        # ---[ 6 ]
        
        while True:
            
            if sum( [ expedition.is_alive() for expedition in running_expeditions ] ) == 0 : break
         
        # ---[ 7 ]
         
        return task_response_q

class Moon :
    
    def __init__( self , moon_spec ):
        
        moon_json = json.loads( moon )
        
        self.name = moon_json["name"]
        self.ip   = moon_json["ip"]
        self.port = int(  moon_json["port"] )
        self.connection_tuple =  ( self.ip , self.port )
        

class MoonServer :
    
    def __init__( self , ip , port , application_index ):
        
        self.ip   = ip
        
        self.port = port
