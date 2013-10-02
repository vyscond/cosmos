#!/usr/bin/env python

import sys, os, time, atexit , json , netifaces , time
from signal           import SIGTERM 
from traceback        import format_exc
from vyscond.vylog    import VyLog
from vyscond.vysocket import VySocketServer , VySocketClient


# To use the daemon method you class need 2 specs:
# 
#    1 - put a constructor like this in your daemon class
#
#       def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
#           self.stdin = stdin
#           self.stdout = stdout
#           self.stderr = stderr
#           self.pidfile = pidfile
#
#    2 - Have a run method
#
#       def run( self ):

def daemon_daemonize( daemon_class ):
    """
    do the UNIX double-fork magic, see Stevens' "Advanced 
    Programming in the UNIX Environment" for details (ISBN 0201563177)
    http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
    """
    try: 
        pid = os.fork() 
        if pid > 0:
            
            # exit first parent
            sys.exit(0)

    except OSError, e: 
        
        sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1)

    # decouple from parent environment
    #os.chdir("/") 
    os.setsid() 
    os.umask(0) 

    # do second fork
    try: 
        
        pid = os.fork() 
        
        if pid > 0:
            
            # exit from second parent
            sys.exit(0) 

    except OSError, e: 
        sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
        sys.exit(1) 

    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = file(daemon_class.stdin, 'r')
    so = file(daemon_class.stdout, 'a+')
    se = file(daemon_class.stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    # write pidfile
    atexit.register( os.remove , path=daemon_class.pidfile )
    pid = str(os.getpid())
    file(daemon_class.pidfile,'w+').write("%s\n" % pid)
    

def daemon_start( daemon_class ):
    """
    Start the daemon
    """
    # Check for a pidfile to see if the daemon already runs
    try:

        pf = file(daemon_class.pidfile,'r')

        pid = int(pf.read().strip())

        pf.close()

    except IOError:

        pid = None

    if pid:

        message = "pidfile %s already exist. Daemon already running?\n"

        sys.stderr.write(message % daemon_class.pidfile)

        sys.exit(1)
    
    # Start the daemon

    daemon_daemonize( daemon_class )
    daemon_class.run()

def daemon_stop( daemon_class ):
    """
    Stop the daemon
    """
    # Get the pid from the pidfile
    daemon_class.close_connections()
    try:

        pf = file(daemon_class.pidfile,'r')

        pid = int(pf.read().strip())

        pf.close()

    except IOError:

        pid = None

    if not pid:

        message = "pidfile %s does not exist. Daemon not running?\n"

        sys.stderr.write(message % daemon_class.pidfile)

        return # not an error in a restart

    # Try killing the daemon process    
    try:
        
        while 1:

            os.kill(pid, SIGTERM)

            time.sleep(0.1)

    except OSError, err:

        err = str(err)

        if err.find("No such process") > 0:

            if os.path.exists(daemon_class.pidfile):

                os.remove(daemon_class.pidfile)

        else:

            print str(err)

            sys.exit(1)

def daemon_restart( daemon_class ):
    """
    Restart the daemon
    """
    self.stop( daemon_class )
    self.start( daemon_class )

# -------------------------------------------------------------------------------------------------------------



class Moon :
    
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        
        self.log = VyLog( self )
        
        # --- Network ---[bgn]
        self.socket_server = None
        self.socket_client = None
        self.ip            = netifaces.ifaddresses('enp2s0')[netifaces.AF_INET][0]['addr']
        self.port          = 666
        # --- Network ---[end]
    
    def end_session( self ):
        
        try : # trying to close connection with master
            
            self.socket_client.close()
            
        except :
            
            return 1 # cant close connection
            
        return 0
     
    def remote_queue( self  ):
        
        # --- Connection with master is already up
        
        try : # --- Waiting for Tasks to solve or Control Message
            
            message = self.socket_client.read()
            
        except :
            
            self.log.dump( '[problem on reading data from master]' )
            
            return PROTOCOL.END_SESSION
            
        try : # --- Ok we got a new message from master! Let's check the type of message
            
            message_as_json = json.dumps( message )
            
            if message_as_json["message_type"] == MessageType.CONTROL_MESSAGE :
                
                # Closing Session and getting back to wait another session
                if message_as_json["control_message"] == ControlMessages.END_SESSION : 
                    
                    self.socket_client.close() 
                    
                    break
                    
            elif message_as_json["message_type"] == MessageType.TASK :
                
                application_name = message_as_json["app"]
                
                application_argv = message_as_json["argv"]
                
                try : # --- Executing Task with Respective Application
                    
                    self.log.dump( '[importing and executiong app]['+application_name+']' )
                    
                    result = getattr( __import__( application_name ) , 'App' )().run( application_argv )
                    
                    self.log.dump( '[execution done!]' )
                    
                    self.log.dump( '[appending result]' )
                    
                except :
                    
                    # --- Something goes worng on the task execution!
                    
                    self.log.dump( '[an error has ocurried on execution of app]' )
                    
                    self.log.dump( '[appending error msg on task]' )
                    
                    result = format_exc().replace('\n', '\\n')
                
                # --- Appending Result
                 
                message_as_json["result"] = result
                
                self.log.dump( '[read to another task]' )
                
        except :
            
            self.log.dump( '[bad formmating message]' )
            
            self.socket_client.send( ControlMessages.JSON_UNKNOW_MESSAGE_FORMAT )
            
            self.log.dump( '[control message sent]' )
            
            
    def run(self):
        
        self.log.dump( '[building the socket_server]' )
        
        try :
            
            self.socket_server = VySocketServer( ( self.ip , self.port ) )
            
        except :
            
            # - something weird will happen
            # we are trying an "suicide" here.
            
            self.log.dump( '[socket_server has failed to bind/listen]' )
            
            daemon_stop( self )
        
        # --- socket server is binded! we are ready to receive connection from planet
        
        self.log.dump( '[socket_server is binded and listening! moon is ready to receive expeditions]' )
        
        # --- main loop to received the expedition's tasks

        while True:
            
            try:

                self.log.dump('[waiting for a connection/expedition]')
                
                self.socket_client = self.socket_server.wait_for_a_connection()
                
                self.log.dump( '[we gotta a new connection/expedition]' )
                
                self.log.dump( '[reading the tasks from the current connection/expedition]' )

            except : # another suicide
                
                self.log.dump( '[something goes wrong while waitting for a client connection]' )
                
                self.log.dump( format_exc() )
                
                daemon_stop( self )
                
            # +------------------------------+
            #
            #          READING TASKS
            #
            # +------------------------------+
            
            try :
                
                queue_type = self.socket_client.read()
                
                if queue_type = PROTOCOL.QUEUE_REMOTE :
                    
                    try :
                     
                        while True:
                            
                            # reading incomming packets
                            
                            self.log.dump( '[reading data from client]' )
                            
                            data_from_client = self.socket_client.read()
                            
                            if data_from_client == PROTOCOL.END_SESSION :
                                
                                self.log.dump( '[there is no more tasks for me. byebye!]' )
                                self.socket_client.close()
                                
                                break
                                
                            else :
                                
                                self.log.dump( '[we have got a new task! casting to object]' )
                                
                                json_task = Task( data_from_client ) 
                                
                                self.log.dump( '[invoking '+json_task.app+' to solve task]' )
                                
                                result = getattr( __import__( json_task.app ) , 'App' )().run( json_task.argv )
                                
                                self.log.dump( '[task was solved. returning result]' )
                                
                                self.socket_client.send( result )
                                
                                self.log.dump( '[taks result was delivered]' )
                        
                    except :
                        
                        self.log.dump( '[something goes wrong while reading tasks from client]' ) 
                        
                        self.log.dump( format_exc() )
                        
                        self.socket_client.close()
                        
                        break
            
            except :
                
                self.log.dump( '[there is no such time of queue]' )
                
                break



class Task :
    
    '''
        data argument need to be in json format
        as described above

        {
            
            "app" : "app_name"
             
            ,
            
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

def get_serial_code( class_instance ):
    
    return str(time.localtime(time.time())[0:6]).replace(', ','').replace('(','').replace(')','') + str( id( class_instance ) )


class ControlMessages : 
    
    END_SESSION = 'end_session'

    JSON_END_SESSION = '''
    {
        type : control_message
        
            ,

        control_message : end_session 
    }
    '''
    
    # -------------------------------
    
    UNKNOW_MESSAGE_FORMAT = 'unknow_message_format'
     
    JSON_UNKNOW_MESSAGE_FORMAT = '''
    {
        type : control_message
            
            ,
            
        control_message : unknow_message_format

    }
    '''
    
    # ------------------------------

class MessageType :
    
    CONTROL_MESSAGE = 'control_message'

    TASK            = 'task'

if __name__ == "__main__":

    moon = Moon('/tmp/moon.pid' , stdout='/tmp/moon.stdout' , stderr='/tmp/moon.stderr' )
    
    if len(sys.argv) == 2:

        if 'start' == sys.argv[1]:
            
            daemon_start( moon )
            
        elif 'stop' == sys.argv[1]:
            
            daemon_stop( moon )
            
        elif 'restart' == sys.argv[1]:
            
            daemon_restart( moon )
            
        else:
            
            print "Unknown command"
            
            sys.exit(2)
            
        sys.exit(0)
    else:
        
        print "usage: %s start|stop|restart" % sys.argv[0]
        
        sys.exit(2)

