import json
from cosmos import TaskRequest , Planet

hello_task_request = TaskRequest( "sayhelloworldto" , { "name" : "cosmos" } )

r = Planet( 'tanis.orbit' ).launch_expeditions( [ hello_task_request ] )

print r.get()["result"]["say_hello_tp"]
print type( r.get() )
