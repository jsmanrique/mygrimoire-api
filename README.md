# What is this?

I am not a good programmer, but I like playing with Python code, so I decided
to create a simple REST API for [GrimoireLib](https://github.com/VizGrimoire/GrimoireLib)

# What do you need?

To use it, you need:
* [GrimoireLib](https://github.com/VizGrimoire/GrimoireLib)
* [Flask RESTful](https://flask-restful.readthedocs.org)

You would need MySQL databases produced by [Metrics Grimoire](http://metricsgrimoire.github.io/),

# How to use it?

Create a configuration file in the same folder than the api.py file:

```
[database]
user = [MySQL database user]
password = [MySQL database password]
source_code_db = [MySQL database produced by cvsanaly]
identities_db = [MySQL database that hosts indetities]
```

And lauch it with:

```
$ python api.py
```

# API definition

The API is quite simple. We have different data sources types:
* scm: source code
* its: issues
* crs: code reviews
* ...

For each one we have different metrics:
* activity
* repositories
* contributors

For each one, we should get a count (aggregated data) and a list.
For each item in the list, we could get specific information

So requests would be as simple as:

```
GET /scm/activity
GET /scm/repositories
GET /scm/repositories/<string:repo>
GET /scm/contributors
GET /scm/contributors/<string:contrbutor>
```

Added to this, GrimoireLib let's you to apply different filters to the data:
* startdate
* enddate
* period
* repository
* author
* domain

So, for example, to get activity by weeks for John Doe, it would be something like:

```
GET /scm/activity&period=week&author="John Doe"
```

# What is next?

A lot of work is still pending, so any collaboratio is more than welcome ;-)

As, I've said, I am not a good programmer!
