'''
This code was writed by Ramon "Vyscond" and is distributed under the GNU General Public License

github : https://github.com/vyscond
email  : vyscond@gmail.com

'''

import time

class VyLog :

    APPEND = 'a'

    WRITE  = 'w'

    def __init__( self , class_reference ):

        if class_reference == str :
            
            self.header = self.generate_timestamp() + '['+ class_reference +']'
            self.log_filename = '/tmp/'+class_reference + '.log'
        else :
            
            self.header = self.generate_timestamp() + '['+ str( class_reference.__class__.__name__ ) +']'
            self.log_filename = '/tmp/'+class_reference.__class__.__name__ + '.log'
            
        self.log_lines = []

    def dump_log_to( self , path , mode ):
        
        try :
            
            file_log_dump = open( path , mode )
            
            log_lines_tmp = self.header + '[log dump][BGN]\n' + (''.join(self.log_lines)) + self.header + '[log dump][END]\n'
            
            file_log_dump.write( log_lines_tmp )
            
            file_log_dump.close()
            
        except :
            
            print 'cant dump log to ['+path+']'
    
    def dump( self , msg ):
         
        msg = self.header + msg + '\n'
        
        try :
            
            file_log_dump = open( self.log_filename , 'a' )
            
            file_log_dump.write( msg )
            
            file_log_dump.close()
            
        except :
            
            print 'cant dump log to ['+path+']'
    def append( self , msg ):
        
        msg = self.header + msg + '\n'
        
        self.log_lines.append( msg )

    def show( self , msg ):
        
        msg = self.header + msg
        
        self.log_lines.append( msg )
        
        print msg
 
    def generate_timestamp( self ):
        
        year , day , month , hour , minute , second = time.localtime(time.time())[0:6]
        
        return '['+str(year)+'/'+str(month)+'/'+str(day)+' - '+str(hour)+':'+str(minute)+':'+str(second)+']'

