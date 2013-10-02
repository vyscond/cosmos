import json
from sys import argv
from cosmos import Planet , recover_task
from vyscond.vylog import VyLog

class Manager :
    
    def __init__( self , orbit_file_path ): 
        
        self.log = VyLog( self ) 
        
        self.log.show( '[loading orbit]' + '['+orbit_file_path+']' )
        
        planet = Planet( orbit_file_path )     
        
        self.log.show( '[recovering tasks]' )
        
        task_list = [] 

        recover_task( 'tasks' , 'tsp_ulysses16_g1_p36.task' , 4  )
            
        result_queue = planet.launch_expeditions( task_list )
	
	for i in xrange( 4 ):
	
 	    print result_queue.get() 

if '__main__' == __name__ :
        
    m = Manager( argv[1] )
     
