import discord, time, json
client = discord.Client()
f = open("infos.json", "r")
infos = json.load(f)
act = infos["status"]
owner = infos["owner"]
f = open("token.txt", "r")
TOKEN = f.read()
f = open("app.txt", "r")
application = f.read().split("|")

client = discord.Client()

#utility
def sortname(message, init=1):
    name = ""
    for i in range(init, len(message)):
        name += message[i] + " "
    return name


@client.event
async def on_ready():
    if act[0] == 0:
        await client.change_presence(activity=discord.Game(infos["status"][1]))
        print(f"{client.user} is connected as playing {infos['status'][1]}")
    elif act[0] == 1:
        act2 = ""
        for i in range(len(act) - 1):
            act2 = act2 + act[i] + " "
        await client.change_presence(activity=discord.Streaming(name=act2, url=act[-1]))
        print(f"{client.user} is connected as streaming {act2}")
    elif act[0] == 2:
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=infos["status"][1]))
        print(f"{client.user} is connected as listening to {infos['status'][1]}")
    elif act[0] == 3:
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=infos["status"][1]))
        print(f"{client.user} is connected as watching {infos['status'][1]}")
    else:
        await client.change_presence(activity=discord.Game('on TechTonic SMP'))
        print(f"{client.user} is connected as nope")

@client.event
async def on_message(message):
    #load config
    f = open("infos.json", "r", encoding = "utf-8")
    infos = json.load(f)
    f.close()
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
            if message.author.id in infoguild["muted"] and message.author.id not in owner and message.author.roles[-1].name not in admin:
                await message.channel.purge(limit=1)
                return
        #bot stuff
        elif message.author.bot:
            #welcome
            if infoguild["welcome"][0] and infoguild["welcome"][1] and infoguild["welcome"][2]:
                if message.author.id == infoguild["welcome"][0] and infoguild["welcome"][1] in message.content:
                    await message.channel.send(infoguild["welcome"][2])
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
                #bot nick
                elif message.content == "editing nick":
                    await message.channel.purge(limit=1)
                    time.sleep(1)
                    name = infoguild["nick"]
                    await message.author.edit(nick=name)
                    infoguild["nick"] = ""
                    f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                    json.dump(infoguild, f)
                    f.close()
            return
        #commands
        if message.content.strip(" ") == "<@782922227397689345>" or message.content.strip(" ") == "<@!782922227397689345>":
            await message.channel.send(f"my prefix are {infoguild['prefix']}")
        if p in messlist[0]:
            #owner commands
            if message.author.id in owner:
                #change status
                if messlist[0] == p + "status":
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
                        await client.change_presence(activity=discord.Game(sortname(messlist, 2)))
                    elif messlist[1] == 1:
                        act2 = ""
                        for i in range(2, len(messlist) - 1):
                            act2 = act2 + messlist[i] + " "
                        await client.change_presence(activity=discord.Streaming(name=act2, url=messlist[-1]))
                    elif messlist[1] == 2:
                        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=sortname(messlist, 2)))
                    elif messlist[1] == 3:
                        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=sortname(messlist, 2)))
                    else:
                        await client.change_presence(activity=discord.Game('on TechTonic SMP'))
                #commands
                elif messlist[0] == p + "clearcommand":
                    try:
                        await message.channel.purge(limit=1)
                        infoguild["command"] = [[], [], []]
                        f = open(f"guilds/{message.guild.id}.json", "w")
                        json.dump(infoguild, f)
                        embed = discord.Embed(title="succesfully removed all commands", description="", colour=infoguild["color"])
                        await message.channel.send(content=None, embed=embed)
                    except:
                        await message.channel.send("uhh")
                #updates
                elif messlist[0] == p + "update":
                    f = open("guilds/default.json", "r")
                    infos2 = json.load(f)
                    for i in infoguild:
                        infos2[i] = infoguild[i]
                    f = open(f"guilds/{message.guild.id}.json", "w")
                    json.dump(infos2, f)
                    f.close()
                    await message.channel.send("server updated")
            #number of users
            if message.content == p + "users" or message.content == p + "members":
                await message.channel.purge(limit=1)    
                embed = discord.Embed(title="Number of Members:", description=str(client.get_guild(message.guild.id).member_count), colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)
            #say something
            elif messlist[0] == p + "say":
                await message.channel.purge(limit=1)
                if message.author.roles[-1].id in admin or message.author.id in owner:
                    await message.channel.send(sortname(messlist))
                elif "@everyone" not in message.content and "@here" not in message.content and "<@&" not in message.content:
                    await message.channel.send(message.author.name + ": " + sortname(messlist))
                else:
                    await message.channel.send(message.author.mention + " you tried")
            #nicks
            elif messlist[0] == p + "nick":
                await message.channel.purge(limit=1)
                await message.author.edit(nick=sortname(messlist))
            #custom commands
            for i in range(len(infoguild["command"][0])):
                if messlist[0] == p + infoguild["command"][0][i]:
                    if infoguild["command"][2][i] == 0:
                        await message.channel.send(infoguild["command"][1][i])
                    else:
                        embed = discord.Embed(title="", description=infoguild["command"][1][i], colour=infoguild["color"])
                        await message.channel.send(content=None, embed=embed)
            #admin commands
            if message.author.roles[-1].id in admin or message.author.id in owner:
                #clear messages
                if messlist[0] == p + "clear":
                    await message.channel.purge(limit=1)
                    await message.channel.purge(limit=(int(messlist[1])))
                #vote
                elif messlist[0] == p + "vote":
                    await message.channel.purge(limit=1)
                    if messlist[1] == "app" or messlist[1] == "application":
                        if infoguild["vote"][1] != 0:
                            infoguild["vote"][2] = 1
                            f = open(f"guilds/{message.guild.id}.json", "w")
                            json.dump(infoguild, f)
                            f.close()
                            channel = client.get_channel(infoguild["vote"][1])
                            await channel.send(sortname(messlist, 2))
                        else:
                            await message.channel.send("application channel is missing")
                    else:
                        if infoguild["vote"][0] != 0:
                            infoguild["vote"][2] = 1
                            f = open(f"guilds/{message.guild.id}.json", "w")
                            json.dump(infoguild, f)
                            f.close()
                            channel = client.get_channel(infoguild["vote"][0])
                            await channel.send(sortname(messlist, 1))
                        else:
                            await message.channel.send("voting channel missing")
                #mute
                elif messlist[0] == p + "mute":
                    try:
                        mute = int(messlist[1])
                        if mute not in infoguild["muted"]:
                            infoguild["muted"].append(mute)
                            f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                            json.dump(infoguild, f)
                            f.close()
                            embed = discord.Embed(title="", description=f"<@{int(mute)}> has been stfu-ed", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    except:
                        name = ""
                        for i in messlist[1]:
                            if i not in "<@!>":
                                name += i
                        if int(name) not in infoguild["muted"]:
                            infoguild["muted"].append(int(name))
                            f = open(f"guilds/{message.guild.id}.json", "w")
                            json.dump(infoguild, f)
                            f.close()
                            embed = discord.Embed(title="", description=f"<@{int(name)}> has been stfu-ed", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                #unmute
                elif messlist[0] == p + "unmute":
                    try:
                        mute = int(messlist[1])
                        if mute in infoguild["muted"]:
                            for i in range(len(infoguild["muted"])):
                                if mute == infoguild["muted"][i]:
                                    infoguild["muted"].pop(i)
                                    break
                            f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                            json.dump(infoguild, f)
                            f.close()
                            embed = discord.Embed(title="", description=f"<@{int(mute)}> has been un-stfu-ed", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                    except:
                        if message.content == "TTunmute all":
                            infoguild["muted"] = []
                            f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                            json.dump(infoguild, f)
                            f.close()
                            embed = discord.Embed(title="", description=f"<@{int(mute)}> has been un-stfu-ed", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            name = ""
                            for i in messlist[1]:
                                if i not in "<@!>":
                                    name += i
                            mute = int(name)
                            if mute in infoguild["muted"]:
                                for i in range(len(infoguild["muted"])):
                                    if mute == infoguild["muted"][i]:
                                        infoguild["muted"].pop(i)
                                        break
                                f = open(f"guilds/{message.guild.id}.json", "w")
                                json.dump(infoguild, f)
                                f.close()
                                embed = discord.Embed(title="", description=f"<@{int(mute)}> has been un-stfu-ed", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                #embeds
                elif messlist[0] == p + "embed":
                    await message.channel.purge(limit=1)
                    try:
                        color = int(messlist[1])
                        for i in range(2, len(messlist)):
                            name += messlist[i] + " "
                        embed = discord.Embed(title="", description=sortname(messlist, 2), colour=color)
                    except:
                        embed = discord.Embed(title="", description=sortname(messlist), colour=infoguild["color"])
                    await message.channel.send(content=None, embed=embed)
                #spam
                elif messlist[0] == p + "spam":
                    await message.channel.purge(limit=1)
                    for i in range(int(messlist[1])):
                        await message.channel.send(sortname(messlist, 2))
                #ghost ping
                elif messlist[0] == p + "ghost":
                    await message.channel.send(f"<@{int(messlist[1])}><@&{int(messlist[1])}>")
                    await message.channel.purge(limit=2)
                #botnick
                elif messlist[0] == p + "botnick":
                    await message.channel.purge(limit=1)
                    infoguild["nick"] = sortname(messlist, 1)
                    f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                    json.dump(infoguild, f)
                    f.close()
                    await message.channel.send("editing nick")
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
                        await message.channel.send(content=None, embed=embed)
                elif messlist[0] == p + "removecommand":
                    if messlist[1] in infoguild["command"][0]:
                        for i in range(len(infoguild["command"][0])):
                            if messlist[1] == infoguild["command"][0][i]:
                                infoguild["command"][0].pop(i)
                                infoguild["command"][1].pop(i)
                                infoguild["command"][2].pop(i)
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
                    embed.add_field(name="current configuration", value=f'color: {infoguild["color"]}\nprefix: {infoguild["prefix"]}\nadmins: {adminlist}\nvote: <#{int(infoguild["vote"][0])}>\napp vote: <#{int(infoguild["vote"][1])}>\nwelcome bot: <@{int(infoguild["welcome"][0])}>\nwelcome detection: {infoguild["welcome"][1]}\nwelcome message: {infoguild["welcome"][2]}')
                    await message.channel.send(content=None, embed=embed)
                elif messlist[0] == p + "color":
                    infoguild["color"] = int(messlist[1])
                    f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                    json.dump(infoguild, f)
                    f.close()
                    embed = discord.Embed(title="", description=infoguild['color'], colour=infoguild["color"])
                    await message.channel.send(content=f"color has been changed to:", embed=embed)
                elif messlist[0] == p + "prefixadd":
                    if messlist[0] not in infoguild["prefix"]:
                        infoguild["prefix"].append(messlist[1])
                        f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                        json.dump(infoguild, f)
                        f.close()
                        await message.channel.send(f'added {messlist[1]} to prefixes')
                elif messlist[0] == p + "prefixremove":
                    if messlist[1] in infoguild["prefix"] and len(infoguild["prefix"]) > 1:
                        for i in range(len(infoguild["prefix"])):
                            if messlist[0] == infoguild["prefix"][i]:
                                infoguild["prefix"].pop(i)
                                break
                        f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                        json.dump(infoguild, f)
                        f.close()
                        await message.channel.send(f'removed {messlist[1]} to prefixes')
                elif messlist[0] == p + "op":
                    infoguild["admins"].append(int(messlist[1]))
                    f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                    json.dump(infoguild, f)
                    f.close()
                    embed = discord.Embed(title="", description=f"<@&{int(messlist[1])}>", colour=infoguild["color"])
                    await message.channel.send(content=f"made admin", embed=embed)
                elif messlist[0] == p + "unop":
                    for i in range(len(infoguild["admins"])):
                        if int(infoguild["admins"][i]) == int(messlist[1]):
                            infoguild["admins"].pop(i)
                    f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                    json.dump(infoguild, f)
                    f.close()
                    embed = discord.Embed(title="", description=f"<@&{int(messlist[1])}>", colour=infoguild["color"])
                    await message.channel.send(content=f"removed admin", embed=embed)
                elif messlist[0] == p + "setvote":
                    if messlist[1] == "app" or messlist[1] == "application":
                        infoguild["vote"][1] = int(messlist[2])
                        await message.channel.send(f"set application voting channel to <#{int(infoguild['vote'][1])}>")
                    else:
                        infoguild["vote"][0] = int(messlist[1])
                        await message.channel.send(f"set voting channel to <#{int(infoguild['vote'][0])}>")
                    f = open(f"guilds/{message.guild.id}.json", "w", encoding = "utf-8")
                    json.dump(infoguild, f)
                    f.close()
                elif messlist[0] == p + "welcome":
                    if messlist[1] == "message":
                        infoguild["welcome"][2] = sortname(messlist, 2)
                        await message.channel.send(f"set welcome message to {infoguild['welcome'][2]}")
                    else:
                        infoguild["welcome"][0] = int(messlist[1])
                        infoguild["welcome"][1] = sortname(messlist, 2)
                        await message.channel.send(f"set welcoming from <@{int(infoguild['welcome'][0])}> with {infoguild['welcome'][1]}")
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
                for i in range(2, len(messlist)):
                    name += messlist[i] + " "
                embed = discord.Embed(title="", description=sortname(messlist, 2), colour=color)
            except:
                embed = discord.Embed(title="", description=sortname(messlist), colour=infoguild["color"])
            await message.channel.send(content=None, embed=embed)
        #spam
        elif messlist[0] == p + "spam":
            for i in range(int(messlist[1])):
                await message.channel.send(sortname(messlist, 2))

    #fun
    if "782922227397689345" in message.content:
        await message.add_reaction("<:pepogun:819303119489597470>")
    #everywhere commands
    if p in messlist[0]:
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
            await message.channel.send(application[0])
        elif message.content == p + "layout" or message.content == p + "l":
            await message.channel.send(application[1])
        #logo
        elif messlist[0] == p + "logo":
            await message.channel.send(file=discord.File('techlogo.png'))
        #trailer
        elif messlist[0] == p + "trailer":
            await message.channel.send("https://youtu.be/dNfiFiI6yI0")

client.run(TOKEN)