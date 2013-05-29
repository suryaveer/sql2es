sql2es
======

Python based REST service which converts SQL queries into ES format.
The QueryService.py is a tornado Web service which converts SQL like queries into a corresponding ElasticSearch Format. It returns a dictionary of status and result.

##Dependent libs to be installed to set it up on a server

These steps are for deploying it with Python 2.7. 
The compatible version of pyparsing lib (the parser for SQL like queries) need pyparsing-1.5.5.
The steps:

    easy_install http://cheeseshop.python.org/packages/source/p/pyparsing/pyparsing-1.5.5.tar.gz
    easy_install rawes
    easy_install cmd2
    easy_install pip
    pip install simplejson
    pip install tornado


##Sample Run

    /usr/bin/python2.7 QueryService.py -port=9288

    curl 127.0.0.1:9288 -d '{"query" : "SELECT * FROM dchung_crawler_demo WHERE content.growthAccelerationCashCost=10 OR content.levelUnlock BETWEEN 0 AND 20"}'
    {
    "status": "OK", 
    "result": "{'query': {'query_string': {'query': 'content.growthAccelerationCashCost:10 OR content.levelUnlock:[0 TO 20]', 'default_operator': 'AND'}}}"
    }

    curl 127.0.0.1:9288 -d '{"query" : "SELECT * FROM dchung_crawler_demo WHERE content.growthAccelerationCashCost=10 AND content.levelUnlock BETWEEN 0 AND 20"}'
    {
    "status": "OK", 
    "result": "{'query': {'query_string': {'query': 'content.growthAccelerationCashCost:10 AND content.levelUnlock:[0 TO 20]', 'default_operator': 'AND'}}}"
    }

    curl 127.0.0.1:9288 -d '{"query" : "SELECT * FROM dchung_crawler_demo WHERE content.growthAccelerationCashCost=10 AND content.llUnlock > 0"}'
    {
    "status": "OK", 
    "result": "{'query': {'query_string': {'query': 'content.growthAccelerationCashCost:10 AND content.levelUnlock:{0 TO *}', 'default_operator': 'AND'}}}"
    }

    curl 127.0.0.1:9288 -d '{"query" : "SELECT * FROM dchung_crawler_demo WHERE NOT content.itemCap=5 AND content.growthAccelerationshCost=3 AND content.levelUnlock BETWEEN 0 AND 200"}'
    {
    "status": "OK", 
    "result": "{'query': {'query_string': {'query': 'NOT content.itemCap:5 AND content.growthAccelerationCashCost:3 AND content.levelUnlock:[0 TO 200]', 'default_operator': 'AND'}}}"
    }

    //Invalid SQL Syntax - an orphan 'AND' at the end of query
    curl 127.0.0.1:9288 -d '{"query" : "SELECT * FROM dchung_crawler_demo WHERE NOT content.itemCap=5 AND content.growthAccelerationCashCost=3 AND content.levelUnlock BETWEEN 0 AND 200 AND"}'
    {
    "status": "FAILED", 
    "reason": "Invalid Syntax (at char 148), (line:1, col:149)"}

    //Invalid JSON passed - Missing '"' after 200
    curl 127.0.0.1:9288 -d '{"query" : "SELECT * FROM dchung_crawler_demo WHERE NOT content.itemCap=5 AND content.growthAccelerationCashCost=3 AND content.levelUnlock BETWEEN 0 AND 200}'
    {
    "status": "FAILED", 
    "reason": "Decoding input JSON has failed"
    }

//Will be adding more