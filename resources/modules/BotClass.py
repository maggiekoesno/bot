import os
import telepot
from telepot.loop import MessageLoop
import sys
import GoogleapiClass as gc
import HelperClass as hc


class API(object):
    """API Basic initialisation"""
    def __init__(self):
        # Deploy Bot
        self.cwd = os.path.dirname(sys.argv[0])
        self.api_key = self.cwd + '/a.txt'
        f = open(self.api_key, 'r')
        self.token = f.read()
        f.close()
        self.bot = telepot.Bot(self.token)

        # Important storage information
        self.db_chat = {}
        self.list_update_message = []

    def handleAPI(self, msg):
        content_type, self.chat_type, chat_id = telepot.glance(msg)
        print(content_type, self.chat_type, chat_id)  # debug msg received
        response = self.bot.getUpdates()
        self.StoreChat(response)

        if content_type == 'text':

            # Convert the message to lower case
            msg_received = msg['text'].lower()
            print(msg_received)

            # If the message is a valid command
            if BotCommand().isValidCommand(msg_received):
                
                if msg_received == '/start':
                    msg_reply = "Beep. You can start chatting with me now, or ask me to do stuff. :)"
                    self.bot.sendMessage(chat_id, msg_reply)

                elif msg_received == '/createevent':
                    msg_reply = "Okay send me the details in following format: \n"
                    str_format = "Event Name;location;yyyy-mm-ddThh:mm;yyyy-mm-ddThh:mm"
                    self.bot.sendMessage(chat_id, msg_reply)
                    self.bot.sendMessage(chat_id, str_format)
                    print(response)

                elif msg_received == '/quit':
                    self.bot.sendMessage(chat_id, "Bye :(")
    
                else:
                    self.bot.sendMessage(chat_id, "Command not updated!")

            else:
                
                # Execute the command further

                if '/createevent' in self.list_update_message:
                    
                    try:
                        BotCommand().CreateEventCommand(msg['text'])
                    
                    except:
                        self.bot.sendMessage(chat_id, 'Cannot create event! Make sure to enter the correct format!')
                    
                    else:
                        self.bot.sendMessage(chat_id, 'Successful!')
                            
                # If the bot knows reply the message
                elif BotReply().isValidtoReply(msg_received):
                    print(BotReply().reply_dict[msg_received])

                    # With name?
                    if BotReply().isWithName(msg_received):
                        self.bot.sendMessage(chat_id, BotReply().reply_dict[msg_received]+', ' + msg['chat']['first_name']+' !')

                    else:
                        self.bot.sendMessage(chat_id, BotReply().reply_dict[msg_received])
              
                else:
                    self.bot.sendMessage(chat_id, "Sorry, I don't know what to reply such conversation yet. :'(")

    def StoreChat(self, update_object):
        update_id = update_object[0]['update_id']
        text = update_object[0]['message']['text']
        
        # A simple dictionary {update_id: 'text'}
        self.db_chat[update_id] = text

        # only the text
        self.list_update_message = list(self.db_chat.values())


class BotReply(API):
    """This is a class for Replies"""
    def __init__(self):
        super().__init__()
        self.reply_dict = {
            'hi': 'Hi',
            'hello': 'Hello',
            'good morning': 'Good morning',
            'good afternoon': 'Good afternoon',
            'good evening': 'Good evening',
            'good night': 'Good night',
            'good day': 'Good day',
        }

        self.reply_with_name = {
            'hi': 1,
            'hello': 1,
            'good morning': 1,
            'good afternoon': 1,
            'good evening': 1,
            'good night': 1,
            'good day': 1,
        }

    def isValidtoReply(self, msg):
        return msg in self.reply_dict

    def isWithName(self, msg):
        return self.reply_with_name[msg] == 1


class BotCommand(API):
    """This is a class for Commands"""

    def __init__(self):
        super().__init__()
        self.command_list = [
            '/start',
            '/createevent',
            '/mergeevent',
            '/quit'
        ]

    def isValidCommand(self, command):
        return command in self.command_list

    def CreateEventCommand(self, str_text):
        str_input = hc.StringParse(str_text)
        str_input.Parse()
        event_name = str_input.event_name
        location = str_input.location
        start_date = str_input.start_date
        end_date = str_input.end_date

        # Call the GoogleAPI class and create event
        gc.GoogleAPI().createEvent(event_name, location, start_date, end_date)