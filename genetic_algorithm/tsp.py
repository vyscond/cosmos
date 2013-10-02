from math import sqrt , pow
from traceback import print_exc
from random import randint , shuffle
from vyscond.vylog import VyLog
import json

class GeneticAlgorithm :
    
    def __init__( self , generations , population_length , base_city_list ):
        
        self.log = VyLog( self )
        
        self.generations = generations
        
        self.population_length = population_length
        
        self.population = []
        
        self.base_city_list = base_city_list
    
    def generate_population( self ):
        
        self.log.show('[generating first instance of population]')
        
        for i in xrange( self.population_length ):
            
            shuffle( self.base_city_list )
                        
            self.population.append( Tour( list( self.base_city_list ) ) )

    def run( self ):
        
        self.log.show( '[running]' )
        
        self.generate_population( )
        
        self.log.show( '[entering on evolution loop]' )
        
        for i in xrange( self.generations ):
            
            self.log.show( '[generation]['+str(i)+']' )
            
            # --- fitness
            
            #for tour in self.population :
              
            #    print '[tour][', self.population.index( tour ) ,'][cost][', tour.cost()  ,']'
            
            self.log.show( '[calculating fitness]')
            
            for tour in sorted( self.population , key = lambda tour : tour.cost() ):
                
                self.log.show( '[tour][' + str( self.population.index( tour ) ) + '][cost][' + str( tour.cost() ) + ']' )
                
            # --- crossover
                
            self.log.show( '[crossover]' )
                
            for i in xrange( self.population_length ) :
                 
                try :
                    
                    self.log.show( '[father]' + str( self.population[i] ) )
                    self.log.show( '[mother]' + str( self.population[i+1] ) )
                    
                    # --------------------------------------------------------
                    
                    self.log.show( str( self.population[ i ]     + self.population[ i + 1 ] ) )
                    self.log.show( str( self.population[ i + 1 ] + self.population[ i ] )     )
                    
                except :
                    
                    print_exc()
                    
                    pass

            break

class Tour :

    def __init__( self , path=None ):
        
        self.path = path
        
        self.path_length = len( self.path )
        
    def cost( self ): # fitness
        
        tmp_sum = 0
        
        for i in xrange( self.path_length ):
            
            try :
                
                tmp_sum += self.path[ i ] + self.path[i+1]
                
            except IndexError :
                
                pass
                
        return tmp_sum
        
    def __add__( self , other_tour ): # crossover
        
        try : 
            
            # 1 - self tour dna
            
            # 0 - other tour dna
            
            bitmask = [ randint(0,1) for x in xrange( self.path_length ) ]
            
            new_path = []
            
            for i in xrange( self.path_length ) :
                
                if bitmask[i] == 1:
                    
                    new_path.append( self[i] )
                    
                else :
                    
                    new_path.append( other_tour[i] )
                    
            # ---
             
        except :
            
            self.log.show('[error at crossover]')
            
            print_exc()

        return Tour( new_path )

    def __getitem__( self , index ):
        
        return self.path[ index ]

    def __str__( self ):
         
        tmp = '[tour]['
        
        for city in self.path : 
            
            tmp += ' '+str(city.name)
            
        tmp +=']'
        return tmp
        
class City :

    def __init__( self , name , x , y ):
 
        self.name = name
        self.x = x
        self.y = y
    
    def __add__( self , other_city ):
        
        return  sqrt( pow( self.x - other_city.x , 2 ) + pow(self.y - other_city.y , 2 )) 
   
    # this is the operator to use this object on "sum" function.
    # but this is not gonna work out because we need 2 citys to make the calc.
    #
    # def __radd__( self , sum_buffer ):
    #    
    #    return  sqrt( pow( self.x - other_city.x , 2 ) + pow(self.y - other_city.y , 2 )) 
    
    def __str__( self ):
        
        return '[city]['+str(self.name)+'][x]['+str(self.x)+'][y]['+str(self.y)+']'

    def __eq__( self , other_city ):
        
        return self.name == other_city.name
        
    def coordinates_as_tuple( self ):
         
        return ( self.x , self.y )
         
    def as_tuple( self ):
        
        return ( self.name , self.x , self.y )

class Instance :

    def __init__( self , tsp_conf_json_file_path  ):
        
        tsp_json_data = json.load( open( tsp_conf_json_file_path ) )
         
        self.name               = tsp_json_data["name"]
        self.tsp_type           = tsp_json_data["tsp_type"]
        self.comment            = tsp_json_data["comment"]
        self.dimension          = tsp_json_data["dimension"]
        self.edge_weight_type   = tsp_json_data["edge_weight_type"]
        self.display_data_type  = tsp_json_data["display_data_type"]
        
        self.city_list = []

        # --- filling up coordinates --- [bgn]
        
        for node in tsp_json_data["node_coord_section"] :
            
            self.city_list.append( City( node["name"] , float( node["x"] ) , float( node["y"] ) ) )
            
        # --- filling up coordinates --- [end]


if __name__ == '__main__' :
    
    uly = Instance( 'instances/ulysses16.jtsp' )

    GeneticAlgorithm( 1 , 4 ,  uly.city_list ).run()
