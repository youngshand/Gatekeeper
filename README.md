Gatekeeper
=========

HipChat Based Password Management System

## Disclaimer

**This system is not live on our servers**

This in an inhouse tool we use and security is not guaranteed.
Irresponsible use of this system will result in bad times.

## Setup

First, you'll need to create a database for the app using your favourite SQL
varient.

It would be a good idea to have this run through supervisor or some other
process management software.

The most basic way to run the bot is just `./hipchatbot.py`

I have included a fabfile for deployment utility, at the moment it works using
supervisor to manage the app but this can be adapted to use any system you like.