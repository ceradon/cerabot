Documentation
-------------

[Cerabot](http://en.wikipedia.org/wiki/User:Cerabot) is a [Python](http://python.org) robot that allows for the editing
and perfoming of bot tasks on [Wikipedia](http://en.wikipedia.org), and the interaction of users and command execution
in an IRC network. The bot is currently in alpha development stage, and not completely suited for operation. Use this 
code at your own risk.

Authors
-------

* [ceradon](http://en.wikipedia.org/wiki/User:Ceradon)
* [Earwig](http://en.wikipedia.org/wiki/User:Earwig) (I used some bits and peices of his code)

Operation
---------

Cerabot operates with two components (an IRC component (```cerabot/irc/```); and a Wiki component (```cerabot/wiki```).
Both are able to run independantly of each other. The IRC component connects to an IRC server (i.e. ```chat.freenode.net``` or 
```irc.efnet.net```) and are able to interact with other users connected to the server and are in a channel they are in.
Cerabot can also run commands from the IRC server. The default command triggers for IRC commands are ```!``` and ```.```,
 however, this can be changed by editing self._triggers in the Parser class (```cerabot/irc/parser.py```, line 19). Custom IRC
 commands can be added to the ```irc/commands/``` directory. Here is a simple template for commands:

    #!/usr/bin/python
    # -*- coding: utf-8 -*-

    # In order for the command to work you must 
    # import the Command class and make your 
    # command derive from this class.
    from cerabot.irc.commands import Command

    class MyCommand(Command):
        # This is the name of the command itself:
        name = "mycommand"

        # These are the hook that can be used from
        # IRC to call the command (i.e. if there is a 
        # hook named `foobar`, then a user on IRC may
        # call `!foobar` or `.foobar` (if you are using
        # the default command triggers):
        hooks = ["mycommand", "mycomm", "my_command"]

        # This is the help documentation for the command
        help_docs = "This is my command. Bazingaa!"

        def setup(self):
            """This is called immediately after the command
            class is instantiated. This is great for doing 
            tasks that the command will need. NOTE: setup()
            will only be called once on instantiation."""
            pass

        def call(self):
            """This is the main entry point for your command.
            Whenever an IRC user calls one of your hooks, this
            is what the command manager calls."""
            pass

Wiki
====

The ```wiki``` component is designed for editing Wikipedia pages (I use it to edit Wikipedia, it can be used for just about
any site with [MediaWiki](http://mediawiki.org) installed). There are several useful classes here: ```Page``` 
([```cerabot/wiki/page.py```](https://github.com/ceradon/cerabot/blob/master/cerabot/wiki/page.py)), which compiles some helpful
details about an undividual page from a wiki. ```Category``` ([```cerabot/wiki/category.py```]
(https://github.com/ceradon/cerabot/blob/master/cerabot/wiki/category.py)) and ```File``` ([```cerabot/wiki/file.py```]
(https://github.com/ceradon/cerabot/blob/master/cerabot/wiki/file.py)) are classes derived from ```Page```, but include
some extra information specific to categories and files, respectively. ```User``` ([```cerabot/wiki/user.py```]
(https://github.com/ceradon/cerabot/blob/master/cerabot/wiki/user.py)) represents a particular user on the wiki. ```Site``` 
([```cerabot/wiki/api.py```](https://github.com/ceradon/cerabot/blob/master/cerabot/wiki/api.py)) represents the wiki itself. 
You can use ```Site.iterator``` for the site object to iterate over an API query result and return a Python [generator]
(http://wiki.python.org/moin/Generators) with the results of the query; ```Site.tokener``` to return tokens for various
wiki API actions (i.e. Changing user preferences, etc.); ```Site.name_to_id``` and ```Site.id_to_name``` to change a wiki namespace's
name to it's id and vice versa; and ```Site.login``` and ```Site.logout``` to login and out of a wiki account. Use ```Site.query``` to
get a raw API data back from a query. ```Site.page```, ```Site.category```, ```Site.file``` and ```Site.user``` can be used to return an
object of ```Page```, ```Category```, ```File``` and ```User```, respectively.
