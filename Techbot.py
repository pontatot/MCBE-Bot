import discord, json, time
f = open("infos.json", "r")
infos = json.load(f)
act = infos["status"]
owner = infos["owner"]
f = open("app.txt", "r")
application = f.read().split("|")
f = open("token.txt", "r")
TOKEN = f.read()

#utility
def sortname(message, init=1, end=None):
    if not end:
        end = len(message)
    name = ""
    for i in range(init, end):
        if i != end:
            name += message[i] + " "
    return name
def getid(message):
    try:
        id = ""
        for i in message:
            if i not in "<@&!#>":
                id += i
        return int(id)
    except:
        return None

class MyClient(discord.Client):
    async def on_ready(self):
        if act[0] == 0:
            await self.change_presence(activity=discord.Game(infos["status"][1]))
            print(f"{self.user} is connected as playing {infos['status'][1]}")
        elif act[0] == 1:
            act2 = ""
            for i in range(len(act) - 1):
                act2 = act2 + act[i] + " "
            await self.change_presence(activity=discord.Streaming(name=act2, url=act[-1]))
            print(f"{self.user} is connected as streaming {act2}")
        elif act[0] == 2:
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=infos["status"][1]))
            print(f"{self.user} is connected as listening to {infos['status'][1]}")
        elif act[0] == 3:
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=infos["status"][1]))
            print(f"{self.user} is connected as watching {infos['status'][1]}")
        else:
            await self.change_presence(activity=discord.Game('on TechTonic SMP'))
            print(f"{self.user} is connected as nope")

    async def on_member_join(self, member):
        guild = member.guild
        try:
            f = open(f"guilds/{guild.id}.json", "r")
            infoguild = json.load(f)
        except:
            #initialization
            f = open("guilds/default.json", "r")
            default = json.load(f)
            infoguild = default
            f.close()
            f = open(f"guilds/{guild.id}.json", "w")
            json.dump(default, f)
            f.close()
        if guild.system_channel is not None:
            if infoguild["welcome"][0]:
                to_send = infoguild["welcome"][0].replace("{ping}", member.mention).replace("{mention}", member.mention).replace("{name}", member.name).replace("{guild}", guild.name).replace("{number}", str(guild.member_count))
            else:
                to_send = 'Welcome {0.mention} to {1.name}!'.format(member, guild)
            await guild.system_channel.send(to_send)
        print(member.name, "joined", guild.name)
    
    async def on_member_remove(self, member):
        guild = member.guild
        try:
            f = open(f"guilds/{guild.id}.json", "r")
            infoguild = json.load(f)
        except:
            #initialization
            f = open("guilds/default.json", "r")
            default = json.load(f)
            infoguild = default
            f.close()
            f = open(f"guilds/{guild.id}.json", "w")
            json.dump(default, f)
            f.close()
        if guild.system_channel is not None:
            if infoguild["welcome"][1]:
                to_send = infoguild["welcome"][1].replace("{ping}", member.mention).replace("{mention}", member.mention).replace("{name}", member.name).replace("{guild}", guild.name).replace("{number}", str(guild.member_count))
                await guild.system_channel.send(to_send)
        print(member.name, "left", guild.name)

    async def on_message(self, message):
        #load config
        f = open("infos.json", "r", encoding = "utf-8")
        infos = json.load(f)
        f.close()
        f = open("help.json", "r")
        infos["help"] = json.load(f)
        if message.guild:
            try:
                f = open(f"guilds/{message.guild.id}.json", "r")
                infoguild = json.load(f)
            except:
                #initialization
                f = open("guilds/default.json", "r")
                default = json.load(f)
                infoguild = default
                f.close()
                f = open(f"guilds/{message.guild.id}.json", "w")
                json.dump(default, f)
                f.close()
        else:
            f = open("guilds/default.json", "r")
            infoguild = json.load(f)
        prefix = infoguild["prefix"]
        admin = infoguild["admins"]
        #cut message into list
        messlist = list(message.content.split(" "))
        #determine prefix
        for i in range(len(prefix)):
            if prefix[i] in messlist[0]:
                if messlist[0] == str(prefix[i] + messlist[0].split(prefix[i])[1]):
                    p = prefix[i]
                    break
                else:
                    p = "TT"
            else:
                p = "TT"
        #logs
        try:
            print(f"{message.guild.name} - {message.channel.name} - {message.author.name}: {message.content}")
        except:
            print(f"dm - {message.author.name}: {message.content}")
        #server message
        if message.guild:
            #message sent by muted?
            if infoguild["muted"]:
                if message.author.id in infoguild["muted"] and message.author.id not in owner and message.author.roles[-1].name not in admin and message.author != message.guild.owner:
                    await message.delete()
                    return
            #bot stuff
            elif message.author.bot:
                #techbot
                if message.author.id == 782922227397689345:
                    time.sleep(1)
                    #vote
                    if infoguild["vote"][2] == 1:
                        await message.add_reaction("👍")
                        await message.add_reaction("👎")
                        infoguild["vote"][2] = 0
                        f = open(f"guilds/{message.guild.id}.json", "w")
                        json.dump(infoguild, f)
                        f.close()
                return
            #commands
            if message.content.strip(" ") == "<@782922227397689345>" or message.content.strip(" ") == "<@!782922227397689345>":
                embed = discord.Embed(title="My prefix are", description=f"{infoguild['prefix']}", colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)
            if p in messlist[0]:
                #owner commands
                if message.author.id in owner:
                    #change status
                    if messlist[0] == p + "status":
                        await message.delete()
                        statuspron = ["p", "s", "l", "w"]
                        for i in range(4):
                            if messlist[1] == statuspron[i]:
                                messlist[1] = i
                        infos["status"][0] = messlist[1]
                        infos["status"][1] = sortname(messlist, 2)
                        f = open("infos.json", "w", encoding = "utf-8")
                        json.dump(infos, f)
                        f.close()
                        if messlist[1] == 0:
                            await self.change_presence(activity=discord.Game(sortname(messlist, 2)))
                        elif messlist[1] == 1:
                            act2 = ""
                            for i in range(2, len(messlist) - 1):
                                act2 = act2 + messlist[i] + " "
                            await self.change_presence(activity=discord.Streaming(name=act2, url=messlist[-1]))
                        elif messlist[1] == 2:
                            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=sortname(messlist, 2)))
                        elif messlist[1] == 3:
                            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=sortname(messlist, 2)))
                        else:
                            await self.change_presence(activity=discord.Game('on TechTonic SMP'))
                    #commands
                    elif messlist[0] == p + "clearcommand":
                        try:
                            await message.delete()
                            infoguild["command"] = [[], [], []]
                            f = open(f"guilds/{message.guild.id}.json", "w")
                            json.dump(infoguild, f)
                            embed = discord.Embed(title="Succesfully removed all commands", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        except:
                            embed = discord.Embed(title="Couldn't remove commands", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    #updates
                    elif messlist[0] == p + "update":
                        await message.delete()
                        welcome = infoguild["welcome"]
                        infoguild["welcome"] = [welcome, "{name} has left the server"]
                        f = open(f"guilds/{message.guild.id}.json", "w")
                        json.dump(infoguild, f)
                        f.close()
                        embed = discord.Embed(title="Server updated", description="", colour=infoguild["color"])
                        await message.channel.send(content=None, embed=embed)
                #number of users
                if messlist[0] == p + "users" or message.content == p + "members":
                    await message.delete()
                    embed = discord.Embed(title="Number of Members:", description=str(message.guild.member_count), colour=infoguild["color"])
                    await message.channel.send(content=None, embed=embed)
                #say something
                elif messlist[0] == p + "say":
                    await message.delete()
                    if message.author.roles[-1].id in admin or message.author.id in owner or message.author == message.guild.owner:
                        try:
                            channel = self.get_channel(getid(messlist[1]))
                            await channel.send(sortname(messlist, 2))
                        except:
                            await message.channel.send(sortname(messlist))
                    elif "@everyone" not in message.content and "@here" not in message.content and "<@&" not in message.content:
                        await message.channel.send(message.author.name + ": " + sortname(messlist))
                    else:
                        await message.channel.send(message.author.mention + " you tried")
                #nicks
                elif messlist[0] == p + "nick":
                    await message.delete()
                    try:
                        await message.author.edit(nick=sortname(messlist))
                    except:
                        embed = discord.Embed(title="Could not change nickname", description="Make sure that I have manage nickname permission and that my role is above yours", colour=infoguild["color"])
                        await message.channel.send(content=None, embed=embed)
                #custom commands
                for i in range(len(infoguild["command"][0])):
                    if messlist[0] == p + infoguild["command"][0][i]:
                        if infoguild["command"][2][i] == 0:
                            await message.channel.send(infoguild["command"][1][i])
                        else:
                            embed = discord.Embed(title="", description=infoguild["command"][1][i], colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                #admin commands
                if message.author.roles[-1].id in admin or message.author.id in owner or message.author == message.guild.owner:
                    #clear messages
                    if messlist[0] == p + "clear":
                        await message.delete()
                        await message.channel.purge(limit=(int(messlist[1])))
                    #vote
                    elif messlist[0] == p + "vote":
                        await message.delete()
                        if messlist[1] == "app" or messlist[1] == "application":
                            if infoguild["vote"][1] != 0:
                                infoguild["vote"][2] = 1
                                f = open(f"guilds/{message.guild.id}.json", "w")
                                json.dump(infoguild, f)
                                f.close()
                                channel = self.get_channel(infoguild["vote"][1])
                                await channel.send(sortname(messlist, 2))
                            else:
                                embed = discord.Embed(title="Application channel is missing", description="Do (TTsetvote #channel) to set it up", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                        else:
                            if infoguild["vote"][0] != 0:
                                infoguild["vote"][2] = 1
                                f = open(f"guilds/{message.guild.id}.json", "w")
                                json.dump(infoguild, f)
                                f.close()
                                channel = self.get_channel(infoguild["vote"][0])
                                await channel.send(sortname(messlist, 1))
                            else:
                                embed = discord.Embed(title="Voting channel is missing", description="Do (TTsetvote app #channel) to set it up", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                    #mute
                    elif messlist[0] == p + "mute":
                        if getid(messlist[1]) not in infoguild["muted"]:
                            infoguild["muted"].append(getid(messlist[1]))
                            f = open(f"guilds/{message.guild.id}.json", "w")
                            json.dump(infoguild, f)
                            f.close()
                            embed = discord.Embed(title="", description=f"<@{getid(messlist[1])}> has been stfu-ed", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    #unmute
                    elif messlist[0] == p + "unmute":
                        if messlist[1] == "all" or messlist[1] == "everyone":
                            infoguild["muted"] = []
                            f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                            json.dump(infoguild, f)
                            f.close()
                            embed = discord.Embed(title="", description="Everyone has been un-stfu-ed", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            if getid(messlist[1]) in infoguild["muted"]:
                                infoguild["muted"].remove(getid(messlist[1]))
                                f = open(f"guilds/{message.guild.id}.json", "w")
                                json.dump(infoguild, f)
                                f.close()
                                embed = discord.Embed(title="", description=f"<@{getid(messlist[1])}> has been un-stfu-ed", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                    #embeds
                    elif messlist[0] == p + "embed":
                        await message.delete()
                        try:
                            channel = self.get_channel(getid(messlist[1]))
                            embed = discord.Embed(title="", description=sortname(messlist, 2), colour=infoguild["color"])
                            await channel.send(content=None, embed=embed)
                        except:
                            embed = discord.Embed(title="", description=sortname(messlist), colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    #edit
                    elif messlist[0] == p + "edit":
                        await message.delete()
                        if messlist[1] != "embed":
                            if len(messlist[1].split("/")) == 7:
                                try:
                                    channel = self.get_channel(int(messlist[1].split("/")[5]))
                                    message2 = await channel.fetch_message(int(messlist[1].split("/")[6]))
                                    await message2.edit(content=sortname(messlist, 2))
                                except:
                                    embed = discord.Embed(title="Could not find message", description="Make sure to use the message link from a message I sent and that I have permission to see it", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                            else:
                                try:
                                    channel = self.get_channel(int(messlist[1]))
                                    message2 = await channel.fetch_message(int(messlist[2]))
                                    await message2.edit(content=sortname(messlist, 3))
                                except:
                                    embed = discord.Embed(title="Could not find message", description="make sure to use correct channel and message id or message link to a message I sent and have access to", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                        else:
                            if len(messlist[2].split("/")) == 7:
                                try:
                                    channel = self.get_channel(int(messlist[2].split("/")[5]))
                                    message2 = await channel.fetch_message(int(messlist[2].split("/")[6]))
                                    embed = discord.Embed(title="", description=sortname(messlist, 3), colour=infoguild["color"])
                                    await message2.edit(content=None, embed=embed)
                                except:
                                    embed = discord.Embed(title="Could not find message", description="Make sure to use the message link from a message I sent and that I have permission to see it", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                            else:
                                try:
                                    channel = self.get_channel(int(messlist[2]))
                                    message = await channel.fetch_message(int(messlist[3]))
                                    embed = discord.Embed(title="", description=sortname(messlist, 4), colour=infoguild["color"])
                                    await message.edit(content=None, embed=embed)
                                except:
                                    embed = discord.Embed(title="Could not find message", description="make sure to use correct channel and message id or message link to a message I sent and have access to", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                    #react
                    elif messlist[0] == p + "react":
                        await message.delete()
                        try:
                            channel = self.get_channel(int(messlist[1].split("/")[5]))
                            message2 = await channel.fetch_message(int(messlist[1].split("/")[6]))
                            try:
                                await message2.add_reaction(messlist[2])
                            except:
                                embed = discord.Embed(title="Could not find the emoji", description="Make sure the emoji is from a server I am in or that I have the Use External Emoji permission", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                        except:
                            embed = discord.Embed(title="Could not find the message", description="Make sure the second argument is a message link to a message that exists", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    #kick
                    elif messlist[0] == p + "kick":
                        user = self.get_user(getid(messlist[1]))
                        if user.id in owner:
                            embed = discord.Embed(title="Can't kick admins", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            try:
                                await message.guild.kick(user, reason=sortname(messlist, 2))
                                embed = discord.Embed(title="", description=f"<@{getid(messlist[1])}> has been kicked for: {sortname(messlist, 2)}", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                            except:
                                embed = discord.Embed(title="Can't kick admins", description="", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                    #ban
                    elif messlist[0] == p + "ban":
                        user = self.get_user(getid(messlist[1]))
                        if user.id in owner:
                            embed = discord.Embed(title="Can't ban admins", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            try:
                                await message.guild.ban(user, reason=sortname(messlist, 2))
                                embed = discord.Embed(title="", description=f"<@{getid(messlist[1])}> has been banned for: {sortname(messlist, 2)}", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                            except:
                                embed = discord.Embed(title="Can't ban admins", description="", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                    #unban
                    elif messlist[0] == p + "unban":
                        user = self.get_user(getid(messlist[1]))
                        try:
                            await message.guild.unban(user)
                            embed = discord.Embed(title="", description=f"<@{getid(messlist[1])}> has been unbanned", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        except:
                            embed = discord.Embed(title="Could not unban", description="make sure the user is banned and that I have permissions to unban", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    #join vc
                    elif messlist[0] == p + "join" or messlist[0] == p + "cum":
                        if message.guild.voice_client:
                            embed = discord.Embed(title="Already connected to a voice channel", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            if message.author.voice:
                                channel = message.author.voice.channel
                                await channel.connect()
                                embed = discord.Embed(title="Joined voice channel", description="", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                            else:
                                try:
                                    channel = self.get_channel(getid(messlist[1]))
                                    await channel.connect()
                                    embed = discord.Embed(title="Joined voice channel", description="", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                                except:
                                    embed = discord.Embed(title="Couldn't join a voice channel", description="Join a voice channel or give a channel to join", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                    #leave vc
                    elif messlist[0] == p + "leave" or messlist[0] == p + "yeet" or messlist[0] == p + "fuckoff" or messlist[0] == p + "dc":
                        if message.guild.voice_client:
                            await message.guild.voice_client.disconnect()
                            embed = discord.Embed(title="Left voice channel", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            embed = discord.Embed(title="Currently not in a voice channel", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    #play
                    elif messlist[0] == p + "play":
                        if not message.guild.voice_client or not message.author.voice:
                            if message.guild.voice_client:
                                embed = discord.Embed(title="Joined voice channel", description="", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                            elif message.author.voice:
                                channel = message.author.voice.channel
                                await channel.connect()
                            else:
                                embed = discord.Embed(title="Couldn't join a voice channel", description="Join a voice channel", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                        if message.guild.voice_client and message.author.voice:
                            embed = discord.Embed(title="Playing", description="...", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    #spam
                    elif messlist[0] == p + "spam":
                        await message.delete()
                        for i in range(int(messlist[1])):
                            await message.channel.send(sortname(messlist, 2))
                    #ghost ping
                    elif messlist[0] == p + "ghost":
                        await message.channel.send(f"<@{int(messlist[1])}><@&{int(messlist[1])}>")
                        await message.channel.purge(limit=1)
                        await message.delete()
                    #botnick
                    elif messlist[0] == p + "botnick":
                        await message.delete()
                        user = message.guild.get_member(self.user.id)
                        await user.edit(nick=sortname(messlist, 1))
                    #custom commands
                    elif messlist[0] == p + "command":
                        if messlist[1] not in infoguild["command"][0]:
                            infoguild["command"][0].append(messlist[1])
                            if messlist[2] != "embed":
                                infoguild["command"][1].append(sortname(messlist, 2))
                                infoguild["command"][2].append(0)
                                embed = discord.Embed(title="successfully added", description=f"**{p}{messlist[1]}**\n{sortname(messlist, 2)}", colour=infoguild["color"])
                            else:
                                infoguild["command"][1].append(sortname(messlist, 3))
                                infoguild["command"][2].append(1)
                                embed = discord.Embed(title="successfully added", description=f"**{p}{messlist[1]}**\n{sortname(messlist, 3)}\n as embed", colour=infoguild["color"])
                            f = open(f"guilds/{message.guild.id}.json", "w")
                            json.dump(infoguild, f)
                            f.close()
                            await message.channel.send(content=None, embed=embed)
                    elif messlist[0] == p + "removecommand":
                        if messlist[1] in infoguild["command"][0]:
                            for i in range(len(infoguild["command"][0])):
                                if messlist[1] == infoguild["command"][0][i]:
                                    infoguild["command"][0].pop(i)
                                    infoguild["command"][1].pop(i)
                                    infoguild["command"][2].pop(i)
                                    f = open(f"guilds/{message.guild.id}.json", "w")
                                    json.dump(infoguild, f)
                                    f.close()
                                    embed = discord.Embed(title="successfully removed", description=f"**{p}{messlist[1]}**", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                                    break
                    #setup
                    elif messlist[0] == p + "setup":
                        embed = discord.Embed(title="SETUP help page", description=f"prefix: {infoguild['prefix']}", colour=infoguild["color"])
                        for i in range(len(infos["help"][2])):
                            embed.add_field(name=p + infos["help"][2][i].split("|")[0], value=infos["help"][2][i].split("|")[1])
                        adminlist = ""
                        for i in range(len(infoguild["admins"])):
                            adminlist = adminlist + f'<@&{int(infoguild["admins"][i])}>'
                        embed.add_field(name="current configuration", value=f'color: {infoguild["color"]}\nprefix: {infoguild["prefix"]}\nadmins: {adminlist}\nvote: <#{int(infoguild["vote"][0])}>\napp vote: <#{int(infoguild["vote"][1])}>\nwelcome message: {infoguild["welcome"]}')
                        await message.channel.send(content=None, embed=embed)
                    elif messlist[0] == p + "color":
                        try:
                            if int(messlist[1]) >= 0 and int(messlist[1]) <= 16777215:
                                infoguild["color"] = int(messlist[1])
                                f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                                json.dump(infoguild, f)
                                f.close()
                                embed = discord.Embed(title="Color has been changed to", description=infoguild['color'], colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                            else:
                                embed = discord.Embed(title="Invalid color number", description="Make sure to preovide an integer from 0 to 16777215", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                        except:
                            embed = discord.Embed(title="Invalid color number", description="Make sure to preovide an integer from 0 to 16777215", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    elif messlist[0] == p + "prefixadd":
                        if messlist[0] not in infoguild["prefix"]:
                            infoguild["prefix"].append(messlist[1])
                            f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                            json.dump(infoguild, f)
                            f.close()
                            embed = discord.Embed(title="Added to prefix list", description=messlist[1], colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    elif messlist[0] == p + "prefixremove":
                        if messlist[1] in infoguild["prefix"] and len(infoguild["prefix"]) > 1:
                            infoguild["prefix"].remove(messlist[1])
                            f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                            json.dump(infoguild, f)
                            f.close()
                            embed = discord.Embed(title="Removed from prefix list", description=messlist[1], colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    #op
                    elif messlist[0] == p + "op":
                        infoguild["admins"].append(int(getid(messlist[1])))
                        f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                        json.dump(infoguild, f)
                        f.close()
                        embed = discord.Embed(title="Added to admin list", description=f"<@&{getid(messlist[1])}>", colour=infoguild["color"])
                        await message.channel.send(content=None, embed=embed)
                    #unop
                    elif messlist[0] == p + "unop":
                        if getid(messlist[1]) in infoguild["admins"]:
                            infoguild["admins"].remove(getid(messlist[1]))
                            f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                            json.dump(infoguild, f)
                            f.close()
                            embed = discord.Embed(title="Removed from admin list", description=f"<@&{getid(messlist[1])}>", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            embed = discord.Embed(title="Invalid admin role", description="Make sure the role is already in the admin list", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    #setup vote
                    elif messlist[0] == p + "setvote":
                        if messlist[1] == "app" or messlist[1] == "application":
                            infoguild["vote"][1] = getid(messlist[2])
                            embed = discord.Embed(title="Set application voting channel", description=f"<#{getid(messlist[2])}>", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            infoguild["vote"][0] = getid(messlist[1])
                            embed = discord.Embed(title="Set voting channel", description=f"<#{getid(messlist[1])}>", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                        json.dump(infoguild, f)
                        f.close()
                    #welcome
                    elif messlist[0] == p + "welcome":
                        if messlist[1] != "leave":
                            infoguild["welcome"][0] = sortname(messlist)
                            embed = discord.Embed(title="Set welcome message", description=sortname(messlist), colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                            f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                            json.dump(infoguild, f)
                            f.close()
                        else:
                            infoguild["welcome"][1] = sortname(messlist, 2)
                            embed = discord.Embed(title="Set leave message", description=sortname(messlist, 2), colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                            f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                            json.dump(infoguild, f)
                            f.close()
        #dms
        else:
            #say
            if messlist[0] == p + "say":
                await message.channel.send(sortname(messlist))
            #embed
            elif messlist[0] == p + "embed":
                try:
                    color = int(messlist[1])
                    embed = discord.Embed(title="", description=sortname(messlist, 2), colour=color)
                except:
                    embed = discord.Embed(title="", description=sortname(messlist), colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)
        #fun
        if "782922227397689345" in message.content:
            await message.channel.send("https://tenor.com/view/discord-ping-discord-ping-i-got-pinged-reeee-gif-17313380")
        #everywhere commands
        if p in messlist[0]:
            #ping
            if message.content == p + "ping":
                embed = discord.Embed(title="", description=f"{round(self.latency * 1000)} ms", colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)
            #help page
            if message.content == p + "help":
                embed = discord.Embed(title="Help page", description=f"prefix: {infoguild['prefix']}", colour=infoguild["color"])
                for i in range(len(infos["help"][0])):
                    embed.add_field(name=p + infos["help"][0][i].split("|")[0], value=infos["help"][0][i].split("|")[1])
                await message.channel.send(content=None, embed=embed)
            elif message.content == p + "dm":
                embed = discord.Embed(title="DM Help page", description=f"prefix: {infoguild['prefix']}", colour=infoguild["color"])
                for i in range(len(infos["help"][1])):
                    embed.add_field(name=p + infos["help"][1][i].split("|")[0], value=infos["help"][1][i].split("|")[1])
                await message.channel.send(content=None, embed=embed)
            #application helps
            elif message.content == p + "application" or message.content == p + "app" or message.content == p + "a":
                embed = discord.Embed(title="Application help", description=application[0], colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)
            elif message.content == p + "layout" or message.content == p + "l":
                embed = discord.Embed(title="Application layout", description=application[1], colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)
            #logo
            elif messlist[0] == p + "logo":
                embed = discord.Embed(title="Logo", description="", colour=infoguild["color"])
                embed.set_image(url="https://cdn.discordapp.com/attachments/786325403651276800/843598660935090206/techlogo.png")
                await message.channel.send(content=None, embed=embed)
            #trailer
            elif messlist[0] == p + "trailer":
                await message.channel.send("https://youtu.be/dNfiFiI6yI0")
            #pack
            elif messlist[0] == p + "pack":
                await message.channel.send(file=discord.File("TTpack.mcpack"))


intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run(TOKEN)