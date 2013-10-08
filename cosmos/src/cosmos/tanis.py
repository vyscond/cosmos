#
# Owner
#    Ramon M. "Vyscond"
#
# email
#   vyscond@gmail.com
#
# github
#   vyscond
#
# twitter
#   @vyscond
#
#
# License 
#   This software is licensed under GNU General Public License, version 3 (GPL-3.0)

import json
from cosmos import TaskRequest , Planet

p = Planet( 'tanis.orbit' )

t = TaskRequest( app='helloworld' , argv='{ "name" : "josephin" }' )

print '[My Sides][task request]' , t

qr = p.launch_expeditions( [ t ] )

r = qr.get()

print r
