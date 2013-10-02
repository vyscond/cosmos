

### Orbit Template

```json
{
    "name" : "planet_name",
    "ip"   : "planet_ip",
    "port" : planet_port,

    "moons" : 
    [
        { "name" : "moon_name" , "ip" : "moon_ip" , "port" : moon_host } 
    ]
}
```

#### Example

##### Apocalype Orbit

> Master : _Earth_

> Slaves
>> 1. _War_
>> 2. _Death_
>> 3. _Famine_
>> 4. _Pestilence_

```json
{
    "name" : "earth",
    "ip"   : "0.0.0.0",
    "port" : 666,

    "moons" : 
    [
        { "name" : "war"        , "ip" : "0.0.0.0" , "port" : 666 } ,
        { "name" : "death"      , "ip" : "0.0.0.0" , "port" : 668 } ,
        { "name" : "famine"     , "ip" : "0.0.0.0" , "port" : 669 } ,
        { "name" : "pestilence" , "ip" : "0.0.0.0" , "port" : 700 }
    ]
}
```

