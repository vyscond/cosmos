# Network Messages
## About

The composition of a network message is the following :

* Message Type

* Data

Every Message is builded on __JSON__ format for a more reliable and human readable levels. So every message has the scope

```json
{
    "message_type" : "message type" , 
    
    "data" :
    {
        
        "...espefic data type..."
        
    }
}
```
## Message Types

There are 3 types of message :

* Task __Request__

* Task __Response__

* Session Control

### Message Section

#### Task Request

> Task request especifications

* __APP__ : Application Name

* __ARGV__ : Execution Arguments

* __SERIAL__ : An unsigned integer generated on execution time.

```json
{
    "message_type" : "task_request" ,
        
    "data" : 
    {
        "app" : "sum" , 
    
        "serial" : 123456789 ,
        
        "argv" :
        {
            "first_operand" : "1" , 
            "second_operand" : "2" 
        }
    }
}

```

#### Task Response

> Task response especification

* __APP__ : The same  from related __Task__ sent.

    
* __REQUEST_SERIAL__ : An unsigned integer generated on execution time.
    
* __RESULT__ : Task's execution Result

* __ERROR__ : 

    * If something wrong happen at task execution this will hold the traceback message.
    
    * If everything goes fine this will be _empty_

```json
{
    "message_type" : "task_response" ,
        
    "data" : 
    {
        "app" : "sum" ,
        
        "request_serial" : 123456789 ,
        
        "result" :  
        {
            "total_sum" : "3"
        } ,
                
        "error" : ""
    }
}

```

#### Session Control

Most simple message for now

* __MESSAGE__ :
    
    * Remote _Queue (Queue is on Master Host)_
        
        * BSRQ : Begin Session

        * ESRQ : End Session
    
    * Local Queue (Queue is on Slave Host)
        
        * BSLQ : Begin Session

        * ESLQ : End Session
    
```json
{
    "message_type" : "session_control" ,
        
    "data" : 
    {
        "message" : "ESLQ"
    }
}

```

