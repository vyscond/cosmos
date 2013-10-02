import logging
import time
import json
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
def timestamp( ):
    
    return str( time.localtime()[:6] )
 
def get_serial_code( class_instance ):
    
    return str(time.localtime(time.time())[:6])[1:-1].replace(', ','')+str(id( class_instance))

class TaskRequest :
    
    def __init__( self , app=None , argv={} ):
        
        self.log = logging.getLogger( self.__class__.__name__ )
        
        logging.info( 'creating new instance' )
        
        self.app = app
        
        self.argv = argv
        
        self.serial = get_serial_code( self )
        
    def __str__( self ):
        
        return json.dumps( { 'message_type' : 'task_request' , 'data' : { 'app' : self.app , 'serial' : self.serial , 'argv' : self.argv } } , indent=4, separators=(',', ': ') )

class TaskResponse :
    
    def __init__( self , app , request_serial , result , error='' ):
        
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
