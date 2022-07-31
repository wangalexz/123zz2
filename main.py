from discord_webhook import DiscordWebhook, DiscordEmbed
import discord, re, datetime, setup

account_token = setup.token

options = []

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged in as ', self.user)
        print('---')
        settings = open('settings.txt')
        for line in settings.readlines():
            options.append(line.replace('\n', ''))

    async def on_message(self, message):
        webhook = ''

        if options == []:
            settings = open('settings.txt')
            for line in settings.readlines():
                options.append(line.replace('\n', ''))

        for line in options:
            line = line.split(' ')
            if message.channel.id == int(line[0]):
                webhook = line[1]
                try:
                    if "t" in line[2].lower():
                        block_text = True
                    else:
                        block_text = False
                except:
                    block_text = False

        if webhook != '':

            # Splitting message is there are more then 2000 characters 
            big = False
            if len(message.content) > 1999:
                content = message.content[:len(message.content)//2]
                content2 = message.content[len(message.content)//2:]
                big = True
            else:
                content = message.content

            # Checking for attachments as links and dealing with them
            links = []
            regex = r"https://cdn.discordapp.com/attachments/.*/.*/.*"
            attachments = re.findall(regex, content)
            if len(attachments) == 0:
                pass
            else: 
                for a in attachments:
                    content = content.replace(a, '')
                    links.append(a)
            if big == True:
                attachments = re.findall(regex, content2)
                if len(attachments) == 0:
                    pass
                else: 
                    for a in attachments:
                        content2 = content2.replace(str(a), '')
                        links.append(a)

            # Setting up the basic webhook with the profile picture and name of the user
            if block_text:
                sendwebhook = DiscordWebhook(
                    url=webhook, 
                    rate_limit_retry=True
                )
            else:
                sendwebhook = DiscordWebhook(
                    url=webhook, 
                    content=f"\n{content}", 
                    rate_limit_retry=True
                )

            # Adding all embeds in the message to the new message
            for e in message.embeds:
                if e.type == "rich":

                    # Editing embed based off setup.py
                    if setup.embed_footer_enabled and setup.footer_image_enabled:
                        e.set_footer(text=setup.embed_footer, icon_url=setup.footer_image)
                    elif setup.embed_footer_enabled:
                        e.set_footer(text=setup.embed_footer)
                    elif setup.footer_image_enabled:
                        e.set_footer(text='​', icon_url=setup.footer_image)
                    if setup.author_name_enabled:
                        e.set_author(name=setup.author_name)
                    if setup.color_enabled:
                        e.color = setup.color_hex
                    embed_dict = e.to_dict()

                    # Fixing embed incase parts are broken
                    try:
                        i_t = 0
                        for field in embed_dict['fields']:
                            if field['name'] == '' and field['value'] == '' and field['inline' == False]:
                                del embed_dict['fields'][i_t]
                            i_t = i_t + 1
                        i_t = 0
                        for field in embed_dict['fields']:
                            if field['name'] == '':
                                embed_dict['fields'][i_t]['name'] = '​'
                            i_t = i_t + 1
                        i_t = 0
                        for field in embed_dict['fields']:
                            if field['value'] == '':
                                embed_dict['fields'][i_t]['value'] = '​'
                            i_t = i_t + 1
                    except:
                        pass
                    sendwebhook.add_embed(embed_dict)

            # Adding all attachments from the message to the new message
            for f in message.attachments:
                file = await f.read()
                sendwebhook.add_file(file=file, filename=f.filename)

            # Sending the message
            if big == True:
                sendwebhook.execute()
                if block_text:
                    sendwebhook = DiscordWebhook(
                        url=webhook, 
                        rate_limit_retry=True
                    )
                else:
                    sendwebhook = DiscordWebhook(
                        url=webhook, 
                        content=f"{content2}", 
                        rate_limit_retry=True
                    )
                sendwebhook.execute()
            else:
                sendwebhook.execute()
            if len(links) != 0:
                for a in links:
                    if not block_text:
                        sendwebhook = DiscordWebhook(
                            url=webhook, 
                            content=f"{a}", 
                            rate_limit_retry=True
                        )
                        sendwebhook.execute()

client = MyClient()
client.run(account_token)