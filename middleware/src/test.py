from network_messages import TaskRequest , TaskResponse

task_req = TaskRequest( 'ga_tsp' , { 'generation' : 1 , 'population_size' : 10 } )

print task_req 

task_res = TaskResponse( task_req.app , task_req.serial , { 'best_fitness' : 1000 }  )

print task_res
