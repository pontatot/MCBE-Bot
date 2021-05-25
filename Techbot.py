import discord, json, time, datetime
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
            if i not in "<@&!#> ":
                id += i
        return int(id)
    except:
        return None
def openconfig(id="default"):
    try:
        f = open(f"guilds/{id}.json", "r", encoding = "utf-8")
        infoguild = json.load(f)
    except:
        #initialization
        f = open("guilds/default.json", "r", encoding = "utf-8")
        default = json.load(f)
        infoguild = default
        f.close()
        f = open(f"guilds/{id}.json", "w", encoding = "utf-8")
        json.dump(default, f)
        f.close()
    return infoguild
def saveconfig(infoguild, id):
    f = open(f"guilds/{id}.json", "w", encoding = "utf-8")
    json.dump(infoguild, f)
    f.close()

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
        elif act[0] == 4:
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers"))
            print(f"{self.user} is connected as watching {len(self.guilds)} servers")
        else:
            await self.change_presence(activity=discord.Game('on TechTonic SMP'))
            print(f"{self.user} is connected as nope")

    async def on_member_join(self, member):
        guild = member.guild
        infoguild = openconfig(guild.id)
        if guild.system_channel is not None:
            if infoguild["welcome"][0]:
                to_send = infoguild["welcome"][0].replace("{ping}", member.mention).replace("{mention}", member.mention).replace("{name}", member.name).replace("{guild}", guild.name).replace("{number}", str(guild.member_count))
            else:
                to_send = 'Welcome {0.mention} to {1.name}!'.format(member, guild)
            await guild.system_channel.send(to_send)
        print(member.name, "joined", guild.name)
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["joins"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Member joined", description=f"Target: {member.mention}\n\n{member}", colour=infoguild["color"])
            embed.set_thumbnail(url=member.avatar_url)
            await channel.send(content=None, embed=embed)
        if infoguild["welcome"][2]:
            await member.add_roles(member.guild.get_role(infoguild["welcome"][2]))
    
    async def on_member_remove(self, member):
        guild = member.guild
        infoguild = openconfig(guild.id)
        if guild.system_channel is not None:
            if infoguild["welcome"][1]:
                to_send = infoguild["welcome"][1].replace("{ping}", member.mention).replace("{mention}", member.mention).replace("{name}", member.name).replace("{guild}", guild.name).replace("{number}", str(guild.member_count))
                await guild.system_channel.send(to_send)
        print(member.name, "left", guild.name)
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["joins"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Member Left", description=f"Target: {member.mention}\n\n{member}", colour=infoguild["color"])
            embed.set_thumbnail(url=member.avatar_url)
            await channel.send(content=None, embed=embed)

    async def on_member_update(self, before, after):
        guild = before.guild
        infoguild = openconfig(guild.id)
        if infoguild["logs"][0] != 0:
            channel = self.get_channel(infoguild["logs"][0])
            if infoguild["logs"][1]["nick"] == 1 and before.nick != after.nick:
                embed = discord.Embed(title="Nickname update", description=f"Target: {before.mention}\n\n{before.nick} -> {after.nick}".replace("None", before.name), colour=infoguild["color"])
                embed.set_thumbnail(url=before.avatar_url)
                await channel.send(content=None, embed=embed)
            if infoguild["logs"][1]["member_role"] == 1 and len(after.roles) != len(before.roles):
                if len(before.roles) > len(after.roles):
                    role = None
                    for i in before.roles:
                        if i not in after.roles:
                            role = i
                    embed = discord.Embed(title="Role removed", description=f"Target: {before.mention}\n\n<@&{role.id}>", colour=infoguild["color"])
                    embed.set_thumbnail(url=before.avatar_url)
                    await channel.send(content=None, embed=embed)
                else:
                    role = None
                    for i in after.roles:
                        if i not in before.roles:
                            role = i
                    embed = discord.Embed(title="Role added", description=f"Target: {before.mention}\n\n<@&{role.id}>", colour=infoguild["color"])
                    embed.set_thumbnail(url=before.avatar_url)
                    await channel.send(content=None, embed=embed)
    
    async def on_user_update(self, before, after):
        for i in self.guilds:
            guild = i
            infoguild = openconfig(guild.id)
            if guild.get_member(before.id) != None and infoguild["logs"][0] != 0:
                channel = self.get_channel(infoguild["logs"][0])
                if infoguild["logs"][1]["user"] == 1 and after.avatar and before.avatar != after.avatar:
                    embed = discord.Embed(title="Avatar update", description=f"Target: {before.mention}\n\n", colour=infoguild["color"])
                    embed.set_thumbnail(url=before.avatar_url)
                    embed.set_image(url=after.avatar_url)
                    await channel.send(content=None, embed=embed)
                if infoguild["logs"][1]["user"] == 1 and before.name != after.name:
                    embed = discord.Embed(title="Username changed", description=f"Target: {before.mention}\n\n{before.name} -> {after.name}", colour=infoguild["color"])
                    embed.set_thumbnail(url=before.avatar_url)
                    await channel.send(content=None, embed=embed)
                if infoguild["logs"][1]["user"] == 1 and before.discriminator != after.discriminator:
                    embed = discord.Embed(title="Discriminator changed", description=f"Target: {before.mention}\n\n{before.discriminator} -> {after.discriminator}", colour=infoguild["color"])
                    embed.set_thumbnail(url=before.avatar_url)
                    await channel.send(content=None, embed=embed)

    async def on_guild_update(self, before, after):
        infoguild = openconfig(before.id)
        if infoguild["logs"][0] != 0:
            channel = self.get_channel(infoguild["logs"][0])
            if infoguild["logs"][1]["guild"] == 1 and after.name and before.name != after.name:
                embed = discord.Embed(title="Server name change", description=f"Target: {before.name}\n\n{before.name} -> {after.name}", colour=infoguild["color"])
                embed.set_thumbnail(url=before.icon_url)
                await channel.send(content=None, embed=embed)

    async def on_guild_role_create(self, role):
        guild = role.guild
        infoguild = openconfig(guild.id)
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["guild_role"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Role created", description=f"Target: {guild.name}\n\n<@&{role.id}>", colour=infoguild["color"])
            embed.set_thumbnail(url=guild.icon_url)
            await channel.send(content=None, embed=embed)

    async def on_guild_role_delete(self, role):
        guild = role.guild
        infoguild = openconfig(guild.id)
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["guild_role"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Role deleted", description=f"Target: {guild.name}\n\n{role.name}", colour=infoguild["color"])
            embed.set_thumbnail(url=guild.icon_url)
            await channel.send(content=None, embed=embed)
    
    async def on_guild_role_update(self, before, after):
        guild = before.guild
        infoguild = openconfig(guild.id)
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["guild_role"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            if before.name != after.name:
                embed = discord.Embed(title="Role edited", description=f"Target: <@&{before.id}>\nname:\n\n{before.name} -> {after.name}", colour=infoguild["color"])
                embed.set_thumbnail(url=guild.icon_url)
                await channel.send(content=None, embed=embed)
            if before.permissions != after.permissions:
                embed = discord.Embed(title="Role edited", description=f"Target: <@&{before.id}>\npermissions:\n\n{before.permissions} -> {after.permissions}", colour=infoguild["color"])
                embed.set_thumbnail(url=guild.icon_url)
                await channel.send(content=None, embed=embed)
            if before.position != after.position:
                embed = discord.Embed(title="Role edited", description=f"Target: <@&{before.id}>\nposition:\n\n{before.position} -> {after.position}", colour=infoguild["color"])
                embed.set_thumbnail(url=guild.icon_url)
                await channel.send(content=None, embed=embed)

    async def on_guild_emojis_update(self, guild, before, after):
        infoguild = openconfig(guild.id)
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["emojis"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            if len(before) > len(after):
                for i in before:
                    if i not in after:
                        embed = discord.Embed(title="Emoji deleted", description=f"Target: :{i.name}:", colour=infoguild["color"])
                        embed.set_thumbnail(url=i.url)
                        await channel.send(content=None, embed=embed)
            elif len(before) < len(after):
                for i in after:
                    if i not in before:
                        embed = discord.Embed(title="Emoji added", description=f"Target: :{i.name}:", colour=infoguild["color"])
                        embed.set_thumbnail(url=i.url)
                        await channel.send(content=None, embed=embed)
            else:
                for i in range(len(after)):
                    if i not in before[i] and before[i].name != after[i].name:
                        embed = discord.Embed(title="Emoji edited", description=f"Target: :{before[i].name}:\n\n{before[i].name} -> {after[i].name}", colour=infoguild["color"])
                        embed.set_thumbnail(url=before[i].url)
                        await channel.send(content=None, embed=embed)

    async def on_member_ban(self, guild, user):
        infoguild = openconfig(guild.id)
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["bans"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Member banned", description=f"Target: {user.mention}\n\n{user}", colour=infoguild["color"])
            embed.set_thumbnail(url=user.avatar_url)
            await channel.send(content=None, embed=embed)

    async def on_member_unban(self, guild, user):
        infoguild = openconfig(guild.id)
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["bans"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Member unbanned", description=f"Target: {user.mention}\n\n{user}", colour=infoguild["color"])
            embed.set_thumbnail(url=user.avatar_url)
            await channel.send(content=None, embed=embed)

    async def on_message_edit(self, before, after):
        guild = before.guild
        infoguild = openconfig(guild.id)
        #ignore channel
        if before.channel.id in infoguild["blackchannels"]:
            return
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["messages"] == 1 and not before.author.bot:
            channel = self.get_channel(infoguild["logs"][0])
            if before.content != after.content:
                embed = discord.Embed(title="Message edited", description=f"Target: {before.author.mention}\n\n{before.channel.mention} - {before.content} -> [{after.content}]({after.jump_url})", colour=infoguild["color"])
                embed.set_thumbnail(url=before.author.avatar_url)
                await channel.send(content=None, embed=embed)

    async def on_message_delete(self, message):
        guild = message.guild
        infoguild = openconfig(guild.id)
        #ignore channel
        if message.channel.id in infoguild["blackchannels"]:
            return
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["messages"] == 1 and not message.author.bot:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Message deleted", description=f"Target: {message.author.mention}\n\n{message.channel.mention} - ~~{message.content}~~", colour=infoguild["color"])
            embed.set_thumbnail(url=message.author.avatar_url)
            await channel.send(content=None, embed=embed)

    async def on_raw_reaction_add(self, payload):
        guild = self.get_guild(payload.guild_id)
        infoguild = openconfig(guild.id)
        if len(infoguild["reactrole"]) >= 1:
            for i in infoguild["reactrole"]:
                if i[0] == payload.channel_id and i[1] == payload.message_id and str(payload.emoji.id) in i[2]:
                    await payload.member.add_roles(guild.get_role(i[3]))
    
    async def on_raw_reaction_remove(self, payload):
        guild = self.get_guild(payload.guild_id)
        infoguild = openconfig(guild.id)
        if len(infoguild["reactrole"]) >= 1:
            for i in infoguild["reactrole"]:
                if i[0] == payload.channel_id and i[1] == payload.message_id and str(payload.emoji.id) in i[2]:
                    member = guild.get_member(payload.user_id)
                    await member.remove_roles(guild.get_role(i[3]))


    async def on_message(self, message):
        #load config
        f = open("infos.json", "r", encoding = "utf-8")
        infos = json.load(f)
        f.close()
        f = open("help.json", "r")
        infos["help"] = json.load(f)
        infoguild = openconfig(message.guild.id)
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
        #ignore channel
        if message.channel.id in infoguild["blackchannels"]:
            return
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
                        saveconfig(infoguild, message.guild.id)
                return
            #commands
            if message.content.strip(" ") == "<@782922227397689345>" or message.content.strip(" ") == "<@!782922227397689345>":
                embed = discord.Embed(title="My prefix are", description=f"{infoguild['prefix']}", colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)
            if p in messlist[0]:
                messlist[0] = p + messlist[0].replace(p, "").lower()
                print(messlist[0])
                #owner commands
                if message.author.id in owner:
                    #change status
                    if messlist[0] == p + "status":
                        await message.delete()
                        if messlist[1] == "default":
                            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers"))
                            print(f"{self.user} is connected as watching {len(self.guilds)} servers")
                            infos["status"][0] = 4
                            infos["status"][1] = ""
                            f = open("infos.json", "w", encoding = "utf-8")
                            json.dump(infos, f)
                            f.close()
                        else:
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
                            saveconfig(infoguild, message.guild.id)
                            embed = discord.Embed(title="Succesfully removed all commands", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        except:
                            embed = discord.Embed(title="Couldn't remove commands", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    #updates
                    elif messlist[0] == p + "update":
                        await message.delete()
                        for a in self.guilds:
                            print(a.name, a.owner)
                            try:
                                f = open(f"guilds/{a.id}.json", "r")
                                infoguild = json.load(f)
                            except:
                                #initialization
                                f = open("guilds/default.json", "r")
                                default = json.load(f)
                                infoguild = default
                                f.close()
                                f = open(f"guilds/{a.id}.json", "w")
                                json.dump(default, f)
                                f.close()
                            #f = open("guilds/default.json", "r")
                            #infos2 = json.load(f)
                            #for i in infoguild:
                            #    infos2[i] = infoguild[i]
                            infoguild["blackchannels"] = []
                            saveconfig(infoguild, a.id)
                            #f = open(f"guilds/{a.id}.json", "w")
                            #json.dump(infos2, f)
                            #json.dump(infoguild, f)
                            #f.close()
                            embed = discord.Embed(title="Updated", description=a.name, colour=infoguild["color"])
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
                #whois/info page
                elif messlist[0] == p + "whois":
                    if len(messlist) > 1:
                        try:
                            member = message.guild.get_member(getid(messlist[1]))
                        except:
                            member = message.author
                    else:
                        member = message.author
                    roles = ""
                    rolelist = member.roles
                    rolelist.pop(0)
                    rolelist.reverse()
                    for i in range(len(rolelist)):
                        roles += f"{rolelist[i].mention}"
                    embed = discord.Embed(title="", description=f"**{member.mention} / {member.name}#{member.discriminator}**\n\ncreation: {member.created_at.strftime('%m/%d/%Y')}\njoined: {member.joined_at.strftime('%m/%d/%Y')}\nroles: {roles}", colour=infoguild["color"])
                    embed.set_thumbnail(url=member.avatar_url)
                    await message.channel.send(content=None, embed=embed)
                #nicks
                elif messlist[0] == p + "nick":
                    if message.author.roles[-1].id in admin and getid(messlist[1]) or message.author.id in owner and getid(messlist[1]) or message.author == message.guild.owner and getid(messlist[1]):
                        try:
                            member = message.guild.get_member(getid(messlist[1]))
                            nick = sortname(messlist, 2)
                            if nick.replace(" ", "") == "" or nick.replace(" ", "") == "reset":
                                nick = member.name
                            await member.edit(nick=nick)
                            embed = discord.Embed(title="Successfully changed nickname", description=f"{member.mention} to {nick}", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        except:
                            embed = discord.Embed(title="Could not change nickname", description="Make sure that I have manage nickname permission and that my role is above the target's", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    else:
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
                                saveconfig(infoguild, message.guild.id)
                                channel = self.get_channel(infoguild["vote"][1])
                                await channel.send(sortname(messlist, 2))
                            else:
                                embed = discord.Embed(title="Application channel is missing", description="Do (TTsetvote #channel) to set it up", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                        else:
                            if infoguild["vote"][0] != 0:
                                infoguild["vote"][2] = 1
                                saveconfig(infoguild, message.guild.id)
                                channel = self.get_channel(infoguild["vote"][0])
                                await channel.send(sortname(messlist, 1))
                            else:
                                embed = discord.Embed(title="Voting channel is missing", description="Do (TTsetvote app #channel) to set it up", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                    #mute
                    elif messlist[0] == p + "mute":
                        if getid(messlist[1]) not in infoguild["muted"]:
                            infoguild["muted"].append(getid(messlist[1]))
                            saveconfig(infoguild, message.guild.id)
                            embed = discord.Embed(title="", description=f"<@{getid(messlist[1])}> has been stfu-ed", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    #unmute
                    elif messlist[0] == p + "unmute":
                        if messlist[1] == "all" or messlist[1] == "everyone":
                            infoguild["muted"] = []
                            saveconfig(infoguild, message.guild.id)
                            embed = discord.Embed(title="", description="Everyone has been un-stfu-ed", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            if getid(messlist[1]) in infoguild["muted"]:
                                infoguild["muted"].remove(getid(messlist[1]))
                                saveconfig(infoguild, message.guild.id)
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
                    #delete:
                    elif messlist[0] == p + "delete":
                        await message.delete()
                        try:
                            channel = self.get_channel(int(messlist[1].split("/")[5]))
                            message2 = await channel.fetch_message(int(messlist[1].split("/")[6]))
                            await message2.delete()
                        except:
                            embed = discord.Embed(title="Could not find the message", description="Make sure the second argument is a message link to a message that exists", colour=infoguild["color"])
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
                    #role
                    elif messlist[0] == p + "role":
                        if messlist[1] == "add":
                            try:
                                member = message.guild.get_member(getid(messlist[2]))
                                role = message.guild.get_role(getid(messlist[3]))
                                await member.add_roles(role)
                                embed = discord.Embed(title="Successfully added", description=f"{role.mention} to {member.mention}", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                            except:
                                embed = discord.Embed(title="Could not add role", description="Make sure the command syntax is correct and that my role is above the role to give", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                        elif messlist[1] == "remove":
                            try:
                                member = message.guild.get_member(getid(messlist[2]))
                                role = message.guild.get_role(getid(messlist[3]))
                                await member.remove_roles(role)
                                embed = discord.Embed(title="Successfully removed", description=f"{role.mention} from {member.mention}", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                            except:
                                embed = discord.Embed(title="Could not remove role", description="Make sure the command syntax is correct and that my role is above the role to remove", colour=infoguild["color"])
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
                            saveconfig(infoguild, message.guild.id)
                            await message.channel.send(content=None, embed=embed)
                    elif messlist[0] == p + "removecommand":
                        if messlist[1] in infoguild["command"][0]:
                            for i in range(len(infoguild["command"][0])):
                                if messlist[1] == infoguild["command"][0][i]:
                                    infoguild["command"][0].pop(i)
                                    infoguild["command"][1].pop(i)
                                    infoguild["command"][2].pop(i)
                                    saveconfig(infoguild, message.guild.id)
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
                        blackchannels = ""
                        for i in range(len(infoguild["blackchannels"])):
                            blackchannels = blackchannels + f'<#{int(infoguild["blackchannels"][i])}>'
                        embed.add_field(name="current configuration", value=f'color: {infoguild["color"]}\nprefix: {infoguild["prefix"]}\nadmins: {adminlist}\nvote: <#{int(infoguild["vote"][0])}>\napp vote: <#{int(infoguild["vote"][1])}>\nwelcome message: {infoguild["welcome"][0]}\nyeet message: {infoguild["welcome"][1]}\nblacklisted channels: {blackchannels}')
                        await message.channel.send(content=None, embed=embed)
                    elif messlist[0] == p + "reset":
                        if len(messlist) > 1:
                            f = open("guilds/default.json", "r")
                            default = json.load(f)
                            infoguild[messlist[1]] = default[messlist[1]]
                            saveconfig(infoguild, message.guild.id)
                        else:
                            f = open("guilds/default.json", "r")
                            default = json.load(f)
                            saveconfig(infoguild, message.guild.id)
                    elif messlist[0] == p + "color":
                        try:
                            if int(messlist[1]) >= 0 and int(messlist[1]) <= 16777215:
                                infoguild["color"] = int(messlist[1])
                                saveconfig(infoguild, message.guild.id)
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
                            saveconfig(infoguild, message.guild.id)
                            embed = discord.Embed(title="Added to prefix list", description=messlist[1], colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    elif messlist[0] == p + "prefixremove":
                        if messlist[1] in infoguild["prefix"] and len(infoguild["prefix"]) > 1:
                            infoguild["prefix"].remove(messlist[1])
                            saveconfig(infoguild, message.guild.id)
                            embed = discord.Embed(title="Removed from prefix list", description=messlist[1], colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    #op
                    elif messlist[0] == p + "op":
                        infoguild["admins"].append(int(getid(messlist[1])))
                        saveconfig(infoguild, message.guild.id)
                        embed = discord.Embed(title="Added to admin list", description=f"<@&{getid(messlist[1])}>", colour=infoguild["color"])
                        await message.channel.send(content=None, embed=embed)
                    #unop
                    elif messlist[0] == p + "unop":
                        if getid(messlist[1]) in infoguild["admins"]:
                            infoguild["admins"].remove(getid(messlist[1]))
                            saveconfig(infoguild, message.guild.id)
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
                        saveconfig(infoguild, message.guild.id)
                    #welcome
                    elif messlist[0] == p + "welcome":
                        if messlist[1] == "leave":
                            infoguild["welcome"][1] = sortname(messlist, 2)
                            embed = discord.Embed(title="Set leave message", description=sortname(messlist, 2), colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                            saveconfig(infoguild, message.guild.id)
                        elif messlist[1] == "role":
                            infoguild["welcome"][2] = getid(messlist[2])
                            embed = discord.Embed(title="Set welcome role", description=f"<@&{getid(messlist[2])}>", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                            saveconfig(infoguild, message.guild.id)
                        else:
                            infoguild["welcome"][0] = sortname(messlist)
                            embed = discord.Embed(title="Set welcome message", description=sortname(messlist), colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                            saveconfig(infoguild, message.guild.id)
                    #blacklist
                    elif messlist[0] == p + "blacklist":
                        channel = getid(messlist[1])
                        infoguild["blackchannels"].append(channel)
                        embed = discord.Embed(title="Blacklisted channel", description=f"<#{channel}>", colour=infoguild["color"])
                        await message.channel.send(content=None, embed=embed)
                        saveconfig(infoguild, message.guild.id)
                    #logs
                    elif messlist[0] == p + "logs" or messlist[0] == p + "log":
                        try:
                            if messlist[1] == "channel":
                                try:
                                    infoguild["logs"][0] = getid(messlist[2])
                                    saveconfig(infoguild, message.guild.id)
                                    embed = discord.Embed(title="Set log channel", description=f"<#{getid(messlist[2])}>", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                                except:
                                    embed = discord.Embed(title="Could not set log channel", description="Make sure to have input a correct channel or channel id as the second argument", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                            elif messlist[1] == "add" or messlist[1] == "enable":
                                if messlist[2] == "all" or messlist[2] == "everything":
                                    for i in infoguild["logs"][1]:
                                        infoguild["logs"][1][i] = 1
                                    saveconfig(infoguild, message.guild.id)
                                    embed = discord.Embed(title="Enabled all log types", description="", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                                else:
                                    for i in infoguild["logs"][1]:
                                        if messlist[2] == i:
                                            infoguild["logs"][1][i] = 1
                                            saveconfig(infoguild, message.guild.id)
                                            embed = discord.Embed(title="Enabled", description=i, colour=infoguild["color"])
                                            await message.channel.send(content=None, embed=embed)
                            elif messlist[1] == "remove" or messlist[1] == "disable":
                                if messlist[2] == "all" or messlist[2] == "everything":
                                    for i in infoguild["logs"][1]:
                                        infoguild["logs"][1][i] = 0
                                    saveconfig(infoguild, message.guild.id)
                                    embed = discord.Embed(title="Disabled all log types", description="", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                                else:
                                    for i in infoguild["logs"][1]:
                                        if messlist[2] == i:
                                            infoguild["logs"][1][i] = 0
                                            saveconfig(infoguild, message.guild.id)
                                            embed = discord.Embed(title="Disabled", description=i, colour=infoguild["color"])
                                            await message.channel.send(content=None, embed=embed)
                            else:
                                embed = discord.Embed(title="Logs help page", description=f"prefix: {infoguild['prefix']}", colour=infoguild["color"])
                                for i in range(len(infos["help"][3])):
                                    embed.add_field(name=p + infos["help"][3][i].split("|")[0], value=infos["help"][3][i].split("|")[1])
                                log = ""
                                for i in infoguild["logs"][1]:
                                    log += f'{i}: {infoguild["logs"][1][i]}\n'
                                embed.add_field(name="current config", value=f"channel: <#{infoguild['logs'][0]}>\n" + log.replace("0", "<:cross:845741065306112040>").replace("1", "<:check:845741031344963605>"))
                                await message.channel.send(content=None, embed=embed)
                        except:
                            embed = discord.Embed(title="Logs help page", description=f"prefix: {infoguild['prefix']}", colour=infoguild["color"])
                            for i in range(len(infos["help"][3])):
                                embed.add_field(name=p + infos["help"][3][i].split("|")[0], value=infos["help"][3][i].split("|")[1])
                            log = ""
                            for i in infoguild["logs"][1]:
                                log += f'{i}: {infoguild["logs"][1][i]}\n'
                            embed.add_field(name="current config", value=f"channel: <#{infoguild['logs'][0]}>\n" + log.replace("0", "<:cross:845741065306112040>").replace("1", "<:check:845741031344963605>"))
                            await message.channel.send(content=None, embed=embed)
                    #reaction role
                    elif messlist[0] == p + "reactionrole" or messlist[0] == p + "reaction_role":
                        try:
                            infoguild["reactrole"].append([int(messlist[1].split("/")[5]), int(messlist[1].split("/")[6]), messlist[2], getid(messlist[3])])
                            saveconfig(infoguild, message.guild.id)
                            channel = self.get_channel(int(messlist[1].split("/")[5]))
                            message2 = await channel.fetch_message(int(messlist[1].split("/")[6]))
                            embed = discord.Embed(title="Reaction role", description=f"channel: <#{int(messlist[1].split('/')[5])}>\nmessage: {message2.content}\nemoji: {messlist[2]}\nrole: <@&{getid(messlist[3])}>", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        except:
                            embed = discord.Embed(title="Couldn't setup reaction role", description=f"Make sure everything is correct, doublecheck {p}setup and that i have perms", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
        #dms
        else:
            if p in messlist[0]:
                messlist[0] = p + messlist[0].replace(p, "").lower()
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
        if "832240193020624896" in message.content:
            await message.channel.send("https://cdn.discordapp.com/attachments/761594268405989399/845705313885880391/ezgif.com-gif-maker_28.gif")
        if "782922227397689345" in message.content:
            await message.channel.send("https://cdn.discordapp.com/emojis/823170480143204383.gif?v=1")
        #everywhere commands
        if p in messlist[0]:
            messlist[0] = p + messlist[0].replace(p, "").lower()
            #ping
            if messlist[0] == p + "ping":
                embed = discord.Embed(title="", description=f"{round(self.latency * 1000)} ms", colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)
            #help page
            if messlist[0] == p + "help":
                embed = discord.Embed(title="Help page", description=f"prefix: {infoguild['prefix']}", colour=infoguild["color"])
                for i in range(len(infos["help"][0])):
                    embed.add_field(name=p + infos["help"][0][i].split("|")[0], value=infos["help"][0][i].split("|")[1])
                await message.channel.send(content=None, embed=embed)
            elif messlist[0] == p + "dm":
                embed = discord.Embed(title="DM Help page", description=f"prefix: {infoguild['prefix']}", colour=infoguild["color"])
                for i in range(len(infos["help"][1])):
                    embed.add_field(name=p + infos["help"][1][i].split("|")[0], value=infos["help"][1][i].split("|")[1])
                await message.channel.send(content=None, embed=embed)
            #application helps
            elif messlist[0] == p + "application" or messlist[0] == p + "app" or message.content == p + "a":
                embed = discord.Embed(title="Application help", description=application[0], colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)
            elif messlist[0] == p + "layout" or messlist[0] == p + "l":
                embed = discord.Embed(title="Application layout", description=application[1], colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)
            #logo
            elif messlist[0] == p + "logo":
                embed = discord.Embed(title="Logo", description="", colour=infoguild["color"])
                embed.set_image(url="https://cdn.discordapp.com/attachments/786325403651276800/843598660935090206/techlogo.png")
                await message.channel.send(content=None, embed=embed)
            #av
            elif messlist[0] == p + "av" or messlist[0] == p + "avatar":
                if len(messlist) >= 2:
                    user = self.get_user(getid(messlist[1]))
                    embed = discord.Embed(title="Avatar", description=user.mention, colour=infoguild["color"])
                    embed.set_image(url=user.avatar_url)
                    await message.channel.send(content=None, embed=embed)
                else:
                    embed = discord.Embed(title="Avatar", description=message.author.mention, colour=infoguild["color"])
                    embed.set_image(url=message.author.avatar_url)
                    await message.channel.send(content=None, embed=embed)
            #invite
            elif messlist[0] == p + "invite":
                embed = discord.Embed(title="Invite link", description="invite link: [click here](https://discordapp.com/oauth2/authorize?client_id=782922227397689345&scope=bot&permissions=1073217110)\njoin this server to get help: [click here](https://discord.gg/q6HFJwv7gA)\nDM bot owner: <@630919091015909386>", colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)

intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run(TOKEN)