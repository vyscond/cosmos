from cosmos import TaskResponse

class Boot :
    
    def __init__( self , task_request , task_response ):
        
        ret = HelloWorld().say_hello_to( task_request.argv["name"] )
        
        print ret
        print type(ret)
        
        task_response.result = ret
        

class HelloWorld :
    
    def say_hello_to( self , name ):
        
        return { "say_hello_tp" : "Hello World, " +name+"!"   }
