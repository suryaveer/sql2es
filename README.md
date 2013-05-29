sql2es
======

Python based REST service which converts SQL queries into ES format

#Python Server to run segmentation service from CMS REST endpoint.

The QueryService.py is a tornado Web service which converts SQL like queries into a corresponding ElasticSearch Format. It returns a dictionary of status and result.


##Dependent libs to be installed to set it up on a server

These steps are for deploying it with Python 2.7. 
The compatible version of pyparsing lib (the parser for SQL like queries) need pyparsing-1.5.5

easy_install http://cheeseshop.python.org/packages/source/p/pyparsing/pyparsing-1.5.5.tar.gz
easy_install rawes
easy_install cmd2
easy_install pip
pip install simplejson
pip install tornado

##Sample Run

    /usr/bin/python2.7 QueryService.py
    curl 127.0.0.1:9288 -d '{"query" : "SELECT cms.release,cms.module,cms.id  FROM dchung_crawler_demo WHERE bar BETWEEN 0 AND 39 OR content.foo = 32 AND content.growthAccelerationCashCost=10 OR content.levelUnlock BETWEEN 0 AND 20"}'
    {
    "status": "OK",
    "result": "{'query': {'query_string': {'query': 'bar:[0 TO 39] OR content.foo:32 AND content.growthAccelerationCashCost:10 OR content.levelUnlock:[0 TO 20]', 'default_operator': 'AND'}}, 'fields':['cms.release', 'cms.module', 'cms.id']}"
    }
