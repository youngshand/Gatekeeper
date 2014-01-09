import logging
from sleekxmpp import ClientXMPP
import psycopg2

class HipChatBot(ClientXMPP):

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

        cursor.execute("SELECT * FROM <table_name>")

        database_accounts = cursor.fetchall()

        accounts = []

        for account in database_accounts:
            accounts.append({
                'name': account[1],
                'username': account[2],
                'password': account[3],
                'url': account[4],
                'metadata': account[5],
                })


        if msg['type'] in ('chat', 'normal'):

            from_addr = repr(msg['from']).split("/")[0]

            args = msg['body'].split()
            messages = []

            if str.lower(args[0]) in ['search', 's']:
                for account in accounts:
                    found = True
                    for term in args[1:]:
                        term = str.lower(term)
                        if not (term in account['name'].lower() or term in account['url'].lower() or term in account['metadata'].lower() or term in account['username'].lower()):
                            found = False
                    if found:
                        messages.append('Name: %s\nURL: %s' % (account['name'], account['url']))

                

            elif str.lower(args[0]) in ['find', 'f']:
                
                for account in accounts:
                    if account['name'].lower() == str.lower(msg['body'][5:]):
                        # If you encrypted the password, you'll need to decrypt it here.
                        messages.append('Username: %s\nPassword: %s\nURL: %s' % (account['username'], account['password'], account['url']))

            elif str.lower(args[0]) in ['delete', 'd']:
                name = " ".join(args[1:])

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

                cursor.execute("INSERT INTO pass_accounts(name, username, password, url, metadata) VALUES (%s, %s, %s, %s, %s);",
                    # It would probably be a good idea to encrypt your password.
                    (account['name'], account['username'], account['password'], account['url'], account['metadata']))
                db.commit()

                messages.append('Added %s into database.' % account['name'])
            else:
                messages.append('Unknown command.\nAvaliable commands: Search (s), Find (f), Delete (d), Create (c).')

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

    xmpp = HipChatBot('<bot_jid>', '<bot_password>')
    xmpp.connect(('chat.hipchat.com', 5222))
    xmpp.process(block=True)