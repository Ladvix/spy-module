from pyrogram import Client, filters, enums
from string import Template
from utils import dirs, json_helper

def launch(bot, module_name):
    config = json_helper.read(dirs.MODULES_PATH + module_name + '/config.json')

    @bot.app.on_message(group=1)
    def message_handler(client, message):
        try:
            for i in config['chats']:
                if str(message.chat.id) == str(i):
                    message.forward(config['chats'][i]['group_id'])
        except:
            pass

    @bot.app.on_message(filters.command('spy_mode', prefixes='.') & filters.me)
    def message_handler(client, message):
        data = message.text.split(' ', maxsplit=1)
        mode = data[1]

        if mode == 'on':
            if message.chat.title != None:
                name = message.chat.title
            elif message.chat.last_name != None:
                name = message.chat.first_name + ' ' + message.chat.last_name
            else:
                name = message.chat.first_name

            chat = bot.app.create_supergroup(str(message.chat.id) + ' / ' + name, '')

            config['chats'][str(message.chat.id)] = {'group_id': chat.id}
            json_helper.write(dirs.MODULES_PATH + module_name + '/config.json', config)

            message.delete()
        elif mode == 'off':
            bot.app.delete_supergroup(config['chats'][str(message.chat.id)]['group_id'])
            
            config['chats'].pop(str(message.chat.id))
            json_helper.write(dirs.MODULES_PATH + module_name + '/config.json', config)

            message.delete()

    @bot.app.on_message(filters.command('search_messages', prefixes='.') & filters.me)
    def message_handler(client, message):
        data = message.text.split(' ', maxsplit=1)
        username = data[1].replace('@', '')

        chat = bot.app.create_supergroup(f'Сообщения от @{username} в чате ' + message.chat.title, '')

        with open(dirs.MODULES_PATH + module_name + '/templates/loading.html', encoding='utf-8') as f:
            message.edit(f.read())

        messages = []

        try:
            for msg in bot.app.get_chat_history(message.chat.id):
                if username == msg.from_user.username:
                    messages.append(msg.id)

            bot.app.forward_messages(chat.id, message.chat.id, messages)
        except:
            pass

        with open(dirs.MODULES_PATH + module_name + '/templates/success.html', encoding='utf-8') as f:
            message.edit(f.read())