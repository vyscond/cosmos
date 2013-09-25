from sys import argv

tsp_file = open( argv[1] , 'r' )

# --- reading head --- [bgn]

name      = tsp_file.readline( ).split(' ')[1].replace('\n','')
tsp_type  = tsp_file.readline( ).split(' ')[1].replace('\n','')
comment   = tsp_file.readline( ).split(' ')[1].replace('\n','')
dimension = tsp_file.readline( ).split(' ')[1].replace('\n','')
edge_weight_type  = tsp_file.readline( ).split(' ')[1].replace('\n','')
display_data_type = tsp_file.readline( ).split(' ')[1].replace('\n','')

tsp_file.readline( )

# --- readline head --- [end]

# --- filling up coordinates --- [bgn]

city_list = []

for i in xrange( int(dimension) ) :
                
    city_name , x , y = tsp_file.readline( ).replace('\n','').split(' ')[1::]
    
    city_list.append( ( city_name , x , y ) )

# --- filling up coordinates --- [end]

tsp_file.close()

# --- converting to json

import json
tsp_file_json_data = json.dumps(

{
    'name' : name ,

    'tsp_type' : tsp_type ,

    'comment' : comment ,

    'dimension' : dimension ,

    'edge_weight_type' : edge_weight_type ,

    'display_data_type' : display_data_type ,

    'node_coord_section' :  [ { "name" : city_name , "x" : x , "y" : y  }  for city_name , x , y in city_list ]
 
}
, indent=4, separators=(',', ': ')
)

tsp_json = open( argv[2] , 'w' )
tsp_json.write( tsp_file_json_data )
tsp_json.close()
