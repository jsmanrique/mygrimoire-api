# What is this?

I am not a good programmer, but I like playing with Python code, so I decided
to create a simple REST API for [GrimoireLib](https://github.com/VizGrimoire/GrimoireLib)

# What do you need?

To use it, you need:
* [GrimoireLib](https://github.com/VizGrimoire/GrimoireLib)
* [Flask RESTful](https://flask-restful.readthedocs.org)

You would need MySQL databases produced by [Metrics Grimoire](http://metricsgrimoire.github.io/),

# How to use it?

Create a configuration file in the same folder than the '''api.py''' file:

'''
[database]
user = [MySQL database user]
password = [MySQL database password]
source_code_db = [MySQL database produced by cvsanaly]
identities_db = [MySQL database that hosts indetities]
'''

And lauch it with:

'''
$ python api.py
'''

# API definition

The API is quite simple
