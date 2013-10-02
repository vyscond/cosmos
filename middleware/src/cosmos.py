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

    def __init__( self , orbit_file ): # orbit file is a JSON formatted file :)
        
        # loading orbit configs
        orbit_json = json.load( open( orbit_file ) )
        
        self.name = orbit_file["name"]
        self.ip   = orbit_file["ip"]
        self.port = int( orbit_file["port"] ) # just make sure, ok?
        
        for moon_spec in orbit_file["moons"] :

class Moon :
    
    def __init__( self , name , ip , port ):
        
        self.name = name 
        self.ip   = ip
        self.port = port
        
    def connection_tuple( self ):
        
        return ( self.ip , self.port )
        
