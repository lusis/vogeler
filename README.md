Vogeler
=======

This somewhat pisspoor codebase in front of you is the beginings of something I've come to call Vogeler. 
It is essentially a python-based CMDB insipired by [mcollective](http://github.com/mcollective/marionette-collective).

It's very basic right now. Python is NOT my first language. I'm a Rubyist at heart but the company I work for uses Python for all the system-side stuff so I've had to learn it. Vogeler is part of that process.

Getting started
---------------
So Vogeler has a real working setup.py now. Got some advice from a trusted Python guy. I've also uploaded it to PyPi so you can install from there if you like.

Here's what you'll need:

* RabbitMQ (2.0 is what I'm using)
* CouchDB (1.0.1 is what I'm using)
* Python 2.6/2.7 (2.6 tested on Ubuntu 10.04/2.7 tested on CentOS 5.5 with ActivePython 2.7 and Python 2.7)
* Modules: couchdbkit, amqplib, ConfigParser (this should be defined properly in setup.py)

The rest of the modules appear to be standard in 2.7 (json and such). In cases where 2.6 doesn't natively support a module, I've required it in setup (anyjson, pyyaml)

Setup
-----

So I don't have a full setup script yet. There are some things you'll need to do for rabbitmq:

	rabbitmqctl add_vhost /vogeler
	rabbitmqctl set_permissions -p /vogeler guest ".*" ".*" ".*"

Now you'll need to fire up the server first. He creates all the main configuration with the broker and optionally loads some basic views in CouchDB:

	vogeler-server

	Vogeler(Server) is starting up

If you want to load the design docs:

	vogeler-server -l /path/to/design/docs
	vogeler-server

Some key options:

* _--dbname_: The name of the database to created in CouchDB
* _-l_: Load design docs. Requires a path to the design docs root. This is a one-shot operation. The process exits afterwards.
* _--dbhost_ - a RestKit formatted URI
* _--qhost_ - The hostname/ip address of the rabbitmq instance
* _--quser_ - Username for rabbitmq
* _--qpass_ - Password for rabbitmq


By default, loading of design docs does not happen. This will probably kept this way but for now I'm trying to determine the best way to handle install of design docs/plugins during setup.py (if root - use /etc/vogeler, otherwise install in another location possibly relative to virtualenv?)

Should you choose to load design docs, the output is similar to this:

	vogeler-server -l $VIRTUAL_ENV/etc/vogeler/_design --dbname=sysrecs2

	Loading design docs from /home/jvincent/.python-envs/vogeler-dev/etc/vogeler/_design
	Design docs loaded

You should see the design docs in the database 'sysrecs2' under Futon.

Now you can start the client:

	vogeler-client -p ../etc/plugins/ run

	Vogeler is parsing plugins
	Found plugins: ['facter', 'rpm']
	Registering plugin: {'command_alias': 'get_facts', 'command': 'facter -y', 'result_format': 'yaml', 'description': 'Uses facter to return facts'}
	Registering plugin: {'command_alias': 'get_rpms', 'command': 'rpm -qa', 'result_format': 'list', 'description': 'Grabs packages installed on a system using rpm'}
	Authorizing registered plugins
	Vogeler(Client) is starting up

For now you'll have to pass the location to plugins, otherwise they won't work. I'm working in a virtualenv for all testing so plugins are install in "$VIRTUAL\_ENV/etc/vogeler". Same goes for design docs, by the way.

If this node is a remote node (i.e. not the same place rabbitmq is running), you can pass _--qhost <rabbitmq host/ipaddr>_ to the script like so:

	vogeler-client -p etc/vogeler/plugins/ run --qhost 10.10.10.2

So you now have Vogeler running. Right now, all interaction with Vogeler is done through a runner script:

	vogeler-runner -c facter -n all

	Vogeler(Runner) is sending a message
	Sending facter to all

As with server and client, runner also takes an argument to specify the rabbitmq properties:

	vogeler-runner -c facter -n all --qhost 10.10.10.2

To target a specific node:

	vogeler-runner -c facter -n <node fqdn> [--qhost 10.10.10.2]

_See the running vogeler-client window for the named host vice the other running nodes_

In the client window:

	Vogeler(Client) is sending a message

In the server window:

	Incoming message from: <hostname>
	Got response for: facter

Now check couchdb and you should have, under the system\_records (or dbname if specified) database a new document under your hostname. In that document is a record for the output of 'facter -y'.

How it works
------------
As I said, this is inspired by mcollective. Interestingly enough, at a previous company I used the same queue server design to move information between network partitions. In that case, it was a combination of ActiveMQ,Camel, and Sinatra (a ruby project) so the concept is nothing new to me.

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
	result_format = list
	command_alias = get_rpms

When the client starts up, it checks the plugin directory and "compiles" all the .cfg files into one big file. This is similar to what Nagios started doing in v3. This way you can modify, create, delete plugins without affecting the running client instance.

Any valid plugin configs found are then "registered" in a tuple. When the client gets a command, he validates that the command is allowed and runs it or ignores it. The output is put into a dictionary along with some other information, JSON encoded and dumped on the wire for the server to pick up. Based on some basic internal logic, the server creates or updates the document for that client and adds the command name as a key and the results (formatted based on format) as the value.

That's it. You could then go behind and write a CouchApp, a [Padrino app](http://github.com/padrino/padrino-framework) (yah Padrino!) or even a Django app to put a front end on it for end-users. Use the information how you will.

What's missing
--------------
A whole heck of a lot.

* Logging: I haven't implemented logging yet so everything is stdout. I've got a good handle on Python logging already so that's just laziness on my part.
* Unit Tests: Nose makes testing easy but actually writing unit tests in Python is still painful coming from the world of RSpec, Cucumber, Shoulda and the like.
* Support for anything OTHER than RabbitMQ and CouchDB: Those are the technologies we use internally and my first target. I want to abstract out but Stomp support under RabbitMQ is still third-class citizen. Abstracting the datastore will probably come pretty quick. I'll probably NOT use a traditional RDBMS for this because things are SO dynamic. I don't even know what the names of your plugins are going to be. I would have to denormalize everything anyway so why use an RDBMS?
* Better exception handling: I've got a VogelerException class that I want to wrap everything in. Right now it's only being used in a few spots.
* A setup mode for the server invocation: Partial support is there now. Most options are simple stubs that do nothing.
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
