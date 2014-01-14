#!/usr/bin/env python2.7

import logging
from sleekxmpp import ClientXMPP
import psycopg2

class Gatekeeper(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, msg):

        # You can of course use other SQL database flavours.
        db = psycopg2.connect(
            host="<host_name/id_address>",
            port=<port_number>,
            user="u<username>",
            password="<password>",
            dbname="<database_name>")

        cursor = db.cursor()

        if msg['type'] in ('chat', 'normal'):

            from_addr = repr(msg['from']).split("/")[0]

            args = msg['body'].split()
            messages = []

            if str.lower(args[0]) in ['search', 's']:

                terms = ['%%%s%%' % str.lower(x) for x in args[1:]]

                query_base = "SELECT * FROM pass_accounts WHERE (%s) OR (%s) OR (%s) OR (%s);"

                query_column_base = "(LOWER({column}) LIKE %s)"
                query_column = query_column_base + (" OR " + query_column_base) * (len(terms) - 1)

                query_column_name = query_column.format(column = 'name')
                query_column_username = query_column.format(column = 'username')
                query_column_url = query_column.format(column = 'url')
                query_column_metadata = query_column.format(column = 'metadata')

                query = query_base % (query_column_name, query_column_username, query_column_url, query_column_metadata)

                cursor.execute(query, terms * 4)

                results = cursor.fetchall()

                for account in results:
                    messages.append('Name: %s\nURL: %s' % (account[1], account[4]))


            elif str.lower(args[0]) in ['find', 'f']:

                name = " ".join(args[1:])

                # The name=%s AND name=%s is there due to a bug in the psycopg2 module
                query = "SELECT * FROM pass_accounts WHERE name=%s AND name=%s;"

                cursor.execute(query, (name, name))

                results = cursor.fetchall()

                for account in results:
                    messages.append('Username: %s\nPassword: %s\nURL: %s' % (account[2], account[3], account[4]))

            elif str.lower(args[0]) in ['delete', 'd']:
                name = " ".join(args[1:])

                if from_addr in ['<list of jids for authorized accounts to use this feature, e.g.: 12345_678910@chat.hipchat.com']:

                    # The name=%s AND name=%s is there due to a bug in the psycopg2 module
                    cursor.execute("DELETE FROM pass_accounts WHERE name=%s AND name=%s;", (name, name))
                    db.commit()

                    messages.append('Deleted %s from database.' % name)

            elif str.lower(args[0]) in ['create', 'c']:
                details = msg['body'].split('\n')[1:]

                account = {
                    'name': '-',
                    'username': '-',
                    'password': '-',
                    'url': '-',
                    'metadata': '-'
                    }

                for detail in details:
                    detail, data = detail.split(':', 1)

                    if detail in account.keys():
                        account[detail] = data.strip()

                # The name=%s AND name=%s is there due to a bug in the psycopg2 module
                query = "SELECT 1 FROM pass_accounts WHERE name=%s AND name=%s;"

                cursor.execute(query, (account['name'], account['name']))

                results = cursor.fetchall()

                # If the fetched list is empty, there are no duplicates in the system.
                duplicate = results != []

                if duplicate:
                    messages.append("There is already an entry in the database with that name. Please choose another.")

                if "-" in [account['name'], account['username'], account['password']]:
                    messages.append("An entry must contain a Name, Username and Password.")

                elif not duplicate:
                    cursor.execute("INSERT INTO pass_accounts(name, username, password, url, metadata) VALUES (%s, %s, %s, %s, %s);",
                        (account['name'], account['username'], account['password'], account['url'], account['metadata']))
                    db.commit()

                    messages.append('Added %s into database.' % account['name'])

            else:
                messages.append('Unknown command.\nAvaliable commands: Search (s), Find (f), Create (c).')

            if messages == []:
                msg.reply('I got nothing.').send()
            else:
                for message in messages:
                    self.send_message(
                        mto = from_addr,
                        mbody = message,
                        mtype = 'chat'
                        )




if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    gatekeeper = Gatekeeper('<bot_jid>', '<bot_password>')
    gatekeeper.connect(('chat.hipchat.com', 5222)) # This can be any xmpp service.
    gatekeeper.process(block=True)