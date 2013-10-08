import json
from cosmos import TaskRequest , Planet

p = Planet( 'tanis.orbit' )

t = TaskRequest( app='helloworld' , argv='{ "name" : "josephin" }' )

print '[My Sides][task request]' , t

qr = p.launch_expeditions( [ t ] )

r = qr.get()

print r
