Vogeler
=======

This somewhat pisspoor codebase in front of you is the beginings of something I've come to call Vogeler. 
It is essentially a python-based CMDB framework insipired by [mcollective's](http://github.com/mcollective/marionette-collective) architecture (message queue-based communication) as well as similar professional implementations I've done.

It's very basic right now. Python is NOT my first language. I'm a Rubyist at heart but the company I work for uses Python for all the system-side stuff so I've had to learn it. Vogeler is part of that process.

Getting started
---------------
Here's what you'll need:

* RabbitMQ (2.0 is what I'm using)
* CouchDB (1.0.1 is what I'm using)
* Python 2.6/2.7 (2.6 tested on Ubuntu 10.04/2.7 tested on CentOS 5.5 with ActivePython 2.7 and Python 2.7)
* Modules: couchdbkit, amqplib, ConfigParser (this should be defined properly in setup.py)

The rest of the modules appear to be standard in 2.7 (json and such). In cases where 2.6 doesn't natively support a module, I've required it in setup (anyjson, pyyaml)

Now just do a:
	
	pip install vogeler

And you should have it installed.

The design docs, plugins and master configuration file will be installed to /tmp/vogeler/. Move those to a permanent location somewhere you feel comfortable.

Setup
-----

So I don't have a full setup script yet. There are some things you'll need to do for rabbitmq:

	rabbitmqctl add_vhost /vogeler
	rabbitmqctl set_permissions -p /vogeler guest ".*" ".*" ".*"

### Starting the server

Now you'll need to fire up the server first. He creates all the main configuration with the broker:

	vogeler-server -c /tmp/vogeler/vogeler.conf

_The default configuration file is set to output only warnings_

or to bypass configuration file settings:

	vogeler-server --dbhost couch://127.0.0.1:5984/system_records --qhost amqp://guest:guest@127.0.0.1:5672/vogeler --loglevel INFO

	[2010-09-26 02:16:29,609: INFO] vogeler-server (vogeler-server) - Using qhost from command-line options
	[2010-09-26 02:16:29,609: INFO] vogeler-server (vogeler-server) - Using dbhost from command-line options
	[2010-09-26 02:16:29,648: INFO] vogeler-server (vogeler-server) - Skipping design document load
	[2010-09-26 02:16:29,648: INFO] vogeler-server (vogeler-server) - Skipping design document load
	[2010-09-26 02:16:29,648: INFO] vogeler-server (server) - Vogler(Server) has started
	[2010-09-26 02:16:29,648: INFO] vogeler-server (server) - Vogler(Server) has started
	[2010-09-26 02:16:29,649: INFO] vogeler-server (server) - Waiting for more messages
	[2010-09-26 02:16:29,649: INFO] vogeler-server (server) - Waiting for more messages


By default, vogeler-server will attempt to use the couchdb persistence backend (couch://localhost:5984). You can change that with --dbhost. Current, only couch persistence is supported so all you're buying yourself is being able to run couchdb on another server.

*If no config file option is passed, then dbhost and qhost must be provided on the command line. Optionally you can change the logging level*

Some key options:

* _-c_: the path to the global config file
* _--dbhost_: the persistence uri to use (i.e. couch://localhost:5984/system\_records)
* _--qhost_: - the messaging uri to use (i.e. amqp://guest:guest@127.0.0.1:5672/vogeler)
* _--loglevel_: One of DEBUG, INFO, WARN, ERROR, CRITICAL
* _-l_: Load design docs. Requires a path to the design docs root. This is a one-shot operation. The process exits afterwards.


Should you choose to load design docs, the output is similar to this:

	vogeler-server -l /tmp/vogeler/_design --dbhost couch://localhost:5984/sysrecs3 --qhost amqp://guest:guest@127.0.0.1:5672/vogeler

	Loading design docs from /tmp/vogeler/_design
	Design docs loaded

You should see the design docs in the database 'sysrecs3' under Futon.

### Starting the client

Now you can start the client:

	vogeler-client -c /tmp/vogeler/vogeler.conf run

_As with server, only warnings or higher are output_

or to bypass configuration file settings:
	
	vogeler-client -p etc/vogeler/plugins/ --qhost amqp://guest:guest@localhost:5672/vogeler --loglevel INFO run

	[2010-09-26 02:26:09,780: INFO] vogeler-client (vogeler-client) - Using qhost from command-line options
	[2010-09-26 02:26:09,780: INFO] vogeler-plugins (plugins) - Vogeler is parsing plugins
	[2010-09-26 02:26:09,781: INFO] vogeler-plugins (plugins) - Found plugins: ['facter', 'ps', 'ohai', 'rpm']
	[2010-09-26 02:26:09,781: INFO] vogeler-plugins (plugins) - Registering plugin: {'command_alias': 'get_facts', 'command': 'facter -y', 'result_format': 'yaml', 'description': 'Uses facter to return facts'}
	[2010-09-26 02:26:09,781: INFO] vogeler-plugins (plugins) - Registering plugin: {'command_alias': 'get_procs', 'command': 'ps -ef', 'result_format': 'output', 'description': 'Grabs currently running processes'}
	[2010-09-26 02:26:09,781: INFO] vogeler-plugins (plugins) - Registering plugin: {'command_alias': 'ohai', 'command': 'ohai', 'result_format': 'json', 'description': 'Uses ohai to return system information'}
	[2010-09-26 02:26:09,782: INFO] vogeler-plugins (plugins) - Registering plugin: {'command_alias': 'get_rpms', 'command': 'rpm -qa', 'result_format': 'output', 'description': 'Grabs packages installed on a system using rpm'}
	[2010-09-26 02:26:09,782: INFO] vogeler-plugins (plugins) - Authorizing registered plugins
	[2010-09-26 02:26:09,826: INFO] vogeler-client (client) - Vogeler(Client) is starting up
	[2010-09-26 02:26:09,826: INFO] vogeler-client (client) - Vogeler(Client) is starting up
	[2010-09-26 02:26:09,827: INFO] vogeler-client (client) - Vogeler(Client) has started
	[2010-09-26 02:26:09,827: INFO] vogeler-client (client) - Vogeler(Client) has started

_see 'vogeler-client -h' for a full list of options_

### Issuing commands

So you now have Vogeler running. Right now, all interaction with Vogeler is done through a runner script:

	vogeler-runner -c etc/vogeler/vogeler.conf -n all -x facter

	[2010-09-26 14:19:58,325: INFO] vogeler-runner (vogeler-runner) - Using qhost from configuration file
	[2010-09-26 14:19:58,367: INFO] vogeler-runner (runner) - Vogeler(Runner) is starting up
	[2010-09-26 14:19:58,367: INFO] vogeler-runner (runner) - Vogeler(Runner) is starting up
	[2010-09-26 14:19:58,367: INFO] vogeler-runner (runner) - Vogeler(Runner) is sending a message
	[2010-09-26 14:19:58,367: INFO] vogeler-runner (runner) - Vogeler(Runner) is sending a message
	[2010-09-26 14:19:58,367: INFO] vogeler-runner (vogeler-runner) - Sending facter to all
	[2010-09-26 14:19:58,367: INFO] vogeler-runner (vogeler-runner) - Sending facter to all


_as with server and client, only warning and higher messages are displayed_

To target a specific node:

	vogeler-runner -c etc/vogeler/vogeler.conf -x facter -n <node name> [--qhost 10.10.10.2]

_See the running vogeler-client window for the named host vice the other running nodes_

In the client window:

	[2010-09-26 14:19:58,380: INFO] vogeler-client (client) - Message recieved
	[2010-09-26 14:19:58,380: INFO] vogeler-client (client) - Message recieved
	[2010-09-26 14:19:58,380: INFO] vogeler-client (client) - Message decoded
	[2010-09-26 14:19:58,380: INFO] vogeler-client (client) - Message decoded

In the server window:

	[2010-09-26 14:19:59,078: INFO] vogeler-server (vogeler-server) - Incoming message from: jvx64
	[2010-09-26 14:19:59,078: INFO] vogeler-server (vogeler-server) - Incoming message from: jvx64
	[2010-09-26 14:19:59,082: INFO] vogeler-server (vogeler-server) - Got response for: facter
	[2010-09-26 14:19:59,082: INFO] vogeler-server (vogeler-server) - Got response for: facter
	[2010-09-26 14:19:59,110: INFO] vogeler-server (server) - Waiting for more messages
	[2010-09-26 14:19:59,110: INFO] vogeler-server (server) - Waiting for more messages


Now check couchdb and you should have, under the system\_records (or dbname if specified) database a new document under your hostname. In that document is a record for the output of 'facter -y'.

How it works
------------
As I said, this is somewhat inspired by the mcollective architecture. Interestingly enough, at a previous company I used the same queue server design to move information between network partitions. In that case, it was a combination of ActiveMQ, Camel and Sinatra (a ruby project) so the concept is nothing new to me.

Essentially the broker has 2 exchanges - a topic exchange and a direct exchange.

* The clients bind queues under two routing keys "broadcast.\*" and one under thier hostname.
* The server binds to the direct exchange under its own queue.

Messages are dropped onto the topic exchange with a routing key by the _vogeler-runner_ script. Clients read the queue and respond to anything routed with 'broadcast.\*' or with thier hostname. This is a single channel to the RabbitMQ server with multiple bindings. By simply changing the routing key (specifying a node name when calling vogeler-runner), you can hit everyone or one box.

Clients drop responses back on the direct exchange that the server has bound. From there, the server updates CouchDB. Pretty basic right now.

Plugins and Authorized Commands
-------------------------------
Pretty much from the begining I wanted this to be "simple". By simple, I mean "I'm going to take whatever I get back from the client and dump it in the data store. It will be up to the end user to decide what to do with it"
I didn't want to do any metaprogramming (especially not in Python) and I sure as shit didn't want to write another DSL. I didn't want to decide for anyone what information they even needed. Yeah, there's basic information - hostname, installed software, running processes but for the most part, I wanted people to write plugins in whatever language they were comfortable in. The only thing I wanted to know was what to run and what format it was coming back in. The main reason for even knowing the format is so I could try and use native CouchDB types. I *COULD* just convert everything I get back to JSON and dump it but I really wanted to make it easily viewable in Futon.

To that end, plugins are nothing more that standard INI format files using ConfigParser to do the dirty work.

Sample Plugin File:
	[facter]
	name = facter
	description = Uses facter to return facts
	command = facter -y
	result_format = yaml
	command_alias = get_facts

Another One:
	[rpm]
	name = rpm
	description = Grabs packages installed on a system using rpm
	command = rpm -qa
	result_format = output
	command_alias = get_rpms

Currently, result\_formats are listed in _vogeler/db/couch.py_. I plan on moving those out to a more global area that each persistence engine can import.

When the client starts up, it checks the plugin directory and "compiles" all the .cfg files into one big file. This is similar to what Nagios started doing in v3. This way you can modify, create, delete plugins without affecting the running client instance.

Any valid plugin configs found are then "registered" in a tuple. When the client gets a command, he validates that the command is allowed and runs it or ignores it. The output is put into a dictionary along with some other information, JSON encoded and dumped on the wire for the server to pick up. Based on some basic internal logic, the server creates or updates the document for that client and adds the command name as a key and the results (formatted based on format) as the value.

That's it. You could then go behind and write a CouchApp, a [Padrino app](http://github.com/padrino/padrino-framework) (yah Padrino!) or even a Django app to put a front end on it for end-users. Use the information how you will.

What's missing
--------------
A whole heck of a lot.

* Support for anything OTHER than RabbitMQ and CouchDB: Those are the technologies we use internally and my first target. I want to abstract out but Stomp support under RabbitMQ is still third-class citizen. Abstracting the datastore will probably come pretty quick. I'll probably NOT use a traditional RDBMS for this because things are SO dynamic. I don't even know what the names of your plugins are going to be. I would have to denormalize everything anyway so why use an RDBMS? Swapable persistence is already in place but only the couchdb backend has been defined.
* Better exception handling: I'm still catching and raising almost all Exceptions in an attempt to determine what I should trap and pass versus halting execution
* A setup mode for the messaging backend.
* Some reporting capability
* Durability tuning for queues and messages

Is it usable?
-------------
Actually, yes. All hostnames, usernames and passwords are configurable options now. I haven't tested it daemonized or anything but at this point, I'm ready to instantiate a few hundred EC2 instances myself and test it out. Global configuration file and plugin placement is still wonky though.

One big security gotcha is that passwords are currently visible in the process list. Gotta figure out how to hide those in python.
Also, you'll need to ensure that any node you want to specifically target with _vogeler-runner_ has been started at least once. Once registered, offline clients will get messages when they come back online but they need to be started at least once to create the durable queues.

Likewise, even if _vogeler-server_ is offline, any client messages will be parsed when it comes back online.

How you can help
----------------
I'd love for some Pythonistas to take a look and make harsh recommendations on where I'm doing stupid stuff in Python. I've tried to be very Pythonic (even to the point of realtime pylint in vim while I'm working). I'm not going to stress over 'line too long' messages right now though.
I'd also like to see what people think. Shoot me a message on twitter or github. Tell me I suck. Tell me I rock. Tell me that you're thinking of me...
