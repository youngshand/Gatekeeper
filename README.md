Pass Word
=========

HipChat Based Password Management System

## Disclaimer

**This system is not live on our servers**

This in an inhouse tool we use and security is not guaranteed.
Irresponsible use of this system will result in bad times.

## Setup

First, you'll need to create a database for the app using your favourite SQL
varient.

I found to get this working without having to drop tables, its best to rename
the models.py before running `./manage.py syncdb`.

Revert the name of models.py and then run `./manage.py schemamigration pass --inital`
followed by `./manage.py migrate`

Now, you can set up gunicorn (or any other gateway server) or just run
`./manage.py runserver 0.0.0.0:8888` *shudder*