#!/usr/bin/env python

import json
import time
import os
import sys
import netifaces
import logging

from traceback        import print_exc
from multiprocessing  import Process , Queue
from vyscond.vylog    import VyLog
from vyscond.vysocket import VySocketServer , VySocketClient
from signal           import SIGTERM 

class PROTOCOL :
    
    # --- QUEUE BEHAVIOR
    QUEUE_REMOTE = '[queue_remote]'
    QUEUE_LOCAL  = '[queue_local]'
    
    # ---  CONNECTION CONTROL
    SESSION_END = '[end_session]'
    SESSION_UNEXPECTED_END = '[unexpected_session_end]'

    # --- APP CONTROL
    APP_EXECUTION_ERROR = '[execution_error]'
    
    APP_UNKNOW_APPLICATION = '[unknow_application]'

class MoonProfile :
    
    def __init__( self , name , ip , port ):
        
        self.log = VyLog( self )
        
        self.log.show('[building moon]['+name+']')
        
        self.name = name
        
        self.ip = ip.encode('ascii','ignore')
        
        self.port = int(port)
    
    def  get_connection_tuple( self ):
        
        return ( self.ip , self.port )

    def __str__( self ):
        
        tmp = '''
 Moon
---.---
   |
   |`- Name : %s
   |
   |`- IP   : %s
   |
    `- Port : %i
'''
         
        #return "[%s][%s][%i]" % ( self.name , self.ip , self.port )
        return tmp % ( self.name , self.ip , self.port )

class Planet :
     
    '''
         
        Config files need to be on JSON format like this
            
        {
            "planet":
            {
                "name" : "planetname"
            }
            
            "moons" :
            [
                "moon1",
                "moon2",
                "moonN"
            ]
                
            "moons_flight_route" :
            {
                "moon1" : { "ip" : "X.X.X.X" , "port" : "Y" } ,
                "moon2" : { "ip" : "X.X.X.X" , "port" : "Y" } ,
                "moonN" : { "ip" : "X.X.X.X" , "port" : "Y" } 
            }
        }
        
    '''

    def __init__( self , orbit_map_conf_path ):
        
        self.log = VyLog( self )
        
        self.log.show( '[loading orbit]['+orbit_map_conf_path+']')
         
        orbit_map_data = json.load( open( orbit_map_conf_path ) )
        
        self.name  = orbit_map_data["planet"]["name"]
        
        self.moon_profiles = {}
        
        # --- Registering Moons (Slave Hosts)
         
        for moon_name in orbit_map_data["moons"] :
            
            self.moon_profiles[ moon_name ] = MoonProfile(
                                            moon_name , 
                                            orbit_map_data["moons_flight_route"][ moon_name ]["ip"] , 
                                            orbit_map_data["moons_flight_route"][ moon_name ]["port"] 
                                          )
            
    def __getitem__( self , moon_name ):
        
        return self.moon_profiles[ moon_name ]
        
    def __str__( self ):
        
        tmp = []
        
        tmp.append( '[planet : ' )
        tmp.append( self.name )
        tmp.append( '][moons]' )
        
        for moon in self.moon_profiles.values():
            
            tmp.append('[')
            tmp.append(moon.name)
            tmp.append(']')
        
        return ''.join(tmp)
    
    def launch_expeditions( self , task_list ):
        
        # --- enqueue tasks on thread-safe struct
        
        self.log.show( '[building queues]' )

        task_queue   = Queue()
        
        result_queue = Queue()
        
        self.log.show( '[filling up task queue]' )
        
        for task in task_list :
            
            task_queue.put( task )
        
        expeditions = []
        
        # --- lauching expeditions
        
        for moon in self.moon_profiles.values():
            
            self.log.show( '[preparing expedition to]'+str(moon) )
            
            expeditions.append( Expedition( moon.get_connection_tuple() , task_queue , result_queue ) )
            
        for exp in expeditions:
            
            self.log.show( '[lauching expeditions]' )
            
            exp.start()
            
        # --- wait for finnish
        
        self.log.show( '[wait for expeditions ending]' )
        
        while True :
            
            if sum( [ exp.is_alive() for exp in expeditions ] ) == 0 :
                
                break
        
        # --- done
        
        self.log.show( '[all expeditions are done!]' )
          
        return result_queue

# ------------------------------------------------------------------------------------------------------------
#  ______                     _ _ _   _                   ________          _              _       _           
# |  ____|                   | (_) | (_)                 / /  ____|        | |            | |     | |          
# | |__  __  ___ __   ___  __| |_| |_ _  ___  _ __      / /| |__   ___  ___| |__   ___  __| |_   _| | ___ _ __ 
# |  __| \ \/ / '_ \ / _ \/ _` | | __| |/ _ \| '_ \    / / |  __| / __|/ __| '_ \ / _ \/ _` | | | | |/ _ \ '__|
# | |____ >  <| |_) |  __/ (_| | | |_| | (_) | | | |  / /  | |____\__ \ (__| | | |  __/ (_| | |_| | |  __/ |   
# |______/_/\_\ .__/ \___|\__,_|_|\__|_|\___/|_| |_| /_/   |______|___/\___|_| |_|\___|\__,_|\__,_|_|\___|_|   
#             | |                                                                                              
#             |_|                                                                                              
# ------------------------------------------------------------------------------------------------------------

class Expedition( Process ):
    
    def __init__( self , moon_destination_profile , task_queue , result_queue ):
        
        # --- cool stuff setup

        super( Expedition , self ).__init__()
        
        self.log = VyLog( self )
        
        # --- We can user this serial codes to implement "recover session" schemes in the future!
        
        self.serial       = get_serial_code( self )
        
        self.destination  = moon_destination_profile # - I dont know why but this is a tuple only of (ip/port)
        
        self.task_queue   = task_queue
        
        self.result_queue = result_queue

    def run( self ):
        
        self.log.show( '[adjusting radio frequency]' )
        
        connection_to_moon = VySocketClient( )
        
        self.log.show('[bgn of expedition]['+self.serial+'][to]['+self.destination.name+']' )
        
        try :
                
            self.log.show( '[contacting control tower from '+ str( self.destination.get_connection_tuple() )+' for permission to flight]' )
            
            connection_to_moon.connect( self.destination.get_connection_tuple() )
            
            self.log.show( '[permission aquired! sending tasks to the moon]' )
            
            self.log.show( '[setting queue behavior]')
            
            connection_to_moon.send( PROTOCOL.QUEUE_REMOTE )
            
            # --- doing tasks - loop
            while not self.task_queue.empty() :
                
                self.log.show('[so we still have task to be solved]' )
                 
                try :
                    
                    self.log.show('[dequeue task]')
                    
                    tmp_task = self.task_queue.get() 
                    
                    self.log.show( '[sending task]['+tmp_task.serial+']' )
                    
                    connection_to_moon.send( str(tmp_task) )
                    
                    self.log.show( '[waiting for response from moon]['+self.destination.name+']' )
                    
                    result = connection_to_moon.read()

                    self.log.show( '[task]['+tmp_task.serial+'][is completed][enqueue on results]' )
                    
                    self.result_queue.put( result )
                    
                except :
                    
                    self.log.show( '[something goes wrong on send or receive state]' )
                    
                    self.log.show( '[re-enqueue task]['+tmp_task.serial+']' )
                    
                    self.task_queue.put( tmp_task )
                    
                    self.log.show( '[shutting down expedition]' )
                    
                    print_exc()
                    
                    connection_to_moon.close()
                    
                    break
                    
            self.log.show( '[expedition is done!]' )
            
            connection_to_moon.send( PROTOCOL.END_SESSION )    
            
            connection_to_moon.close()
                 
        except :
            
            self.log.show('[cant connect to moon]['+self.destination.name+']')
            
            print_exc()
        
        self.log.show('[end of expedition]['+self.serial+'][to]['+self.destination.name+']' )

# -------------------------------------------------------------------------------
#  _______        _               _         _                  _   _             
# |__   __|      | |        /\   | |       | |                | | (_)            
#    | | __ _ ___| | __    /  \  | |__  ___| |_ _ __ __ _  ___| |_ _  ___  _ __  
#    | |/ _` / __| |/ /   / /\ \ | '_ \/ __| __| '__/ _` |/ __| __| |/ _ \| '_ \ 
#    | | (_| \__ \   <   / ____ \| |_) \__ \ |_| | | (_| | (__| |_| | (_) | | | |
#    |_|\__,_|___/_|\_\ /_/    \_\_.__/|___/\__|_|  \__,_|\___|\__|_|\___/|_| |_|
#                                                                                
# -------------------------------------------------------------------------------

# this is a class for a user not for r

class Task :
    
    '''
        data argument need to be in json format
        as described above

        {
            
            "app" : "app_name"
             
            "argv" : 
            {
                "task_argv_1"     : "task_argv_value_1" ,
                "task_argv_2"     : "task_argv_value_2" ,
                "task_argv_N"     : "task_argv_value_N"
            }
        }
        
        for while this attributes are just enough

    '''

    def __init__( self , json_file_path ):
        
        self.serial = get_serial_code( self )
         
        if os.path.isfile( json_file_path ) : 
        
            self.json_data = json.load( open( json_file_path ) )
        
        else :
            
            self.json_data = json.loads( json_file_path )
         
        self.app  = self.json_data["app"] 
        self.argv = self.json_data["argv"]
        
    def __str__( self ):
        
        return json.dumps( { 'serial' : self.serial , 'app' : self.app , 'argv' : self.argv } , indent=4, separators=(',', ': ') )


def recover_task( folder , taskname , qtt ):
    
    if not os.path.exists( folder ):
        
        return None
        
    else :
        
        task = ''.join( open( os.path.abspath( folder ) + '/' + taskname ) )
        
        return [ task for i in xrange( qtt ) ]

def get_serial_code( class_instance ):
    
    return str(time.localtime(time.time())[0:6]).replace(', ','').replace('(','').replace(')','') + str( id( class_instance ) )


