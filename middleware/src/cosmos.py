import network_messages as netm
import logging
import json

class Planet :
    
    # Master Host Abstraction

    def __init__( self , orbit_file ): # orbit file is a JSON formatted file :)
        
        # loading orbit configs
        orbit_json = json.load( open( orbit_file ) )
        

