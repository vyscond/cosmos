import inspect , time

class VyLog :
    
    def __init__( self , class_name ):
        
        self.class_name = class_name
        
    def show( self , msg ):
        
        module , line , caller_function = inspect.getouterframes(inspect.currentframe(), 2)[1][1:4]        
        
        #from_class = inspect.getmembers( inspect.getouterframes(inspect.currentframe(), 2)[1][0] )[-6][1].keys()[-2]
        
        timestr =  '[%i/%i/%i - %i:%i:%i]' % time.localtime()[:6]
        
        print '%s[%s][%s][%s][%s] - %s' % ( timestr , module , line , self.class_name , caller_function , msg )
        
