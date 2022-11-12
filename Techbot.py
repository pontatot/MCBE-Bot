import discord
import json
import os
from keep_alive import keep_alive
import youtube_dl
import time
import random
import urllib.request, urllib.parse

#load infos
with open("app.txt") as app_file:
    application = app_file.read().split("|")

with open("infos.json", "r") as help_file:
    infos = json.load(help_file)
act = infos["status"]
owner = infos["owner"]
with open("help.json", "r") as help_file:
    help = json.load(help_file)


#utility
#get a string from the message list
sortname = lambda message, init=1, end=None : " ".join(list(message[init:end]))

#extract id from discord mentions
def getid(message):
    try:
        return int(message.replace("<", "").replace("#", "").replace("@", "").replace("!", "").replace("&", "").replace(">", ""))
    except:
        return None

# open the guild config
def openconfig(id="default"):
    try:
        with open(f"guilds/{id}.json", encoding="utf-8") as help_file:
            infoguild = json.load(help_file)
    except FileNotFoundError:
        # initialization
        with open("guilds/default.json", encoding="utf-8") as help_file:
            default = json.load(help_file)
        infoguild = default
        with open(f"guilds/{id}.json", "w", encoding="utf-8") as help_file:
            json.dump(default, help_file)
    return infoguild

# save the guild config
def saveconfig(infoguild, id):
    with open(f"guilds/{id}.json", "w", encoding="utf-8") as f:
        json.dump(infoguild, f)

class MyClient(discord.Client):
    async def on_ready(self):

        #select the bot activity
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
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers"))
            print(f"{self.user} is connected as watching {len(self.guilds)} servers")

    async def on_member_join(self, member):
        guild = member.guild
        infoguild = openconfig(guild.id)

        #welcome message
        if infoguild["welcome"][2] != 0:
            if infoguild["welcome"][0]:
                to_send = infoguild["welcome"][0].replace("{ping}", member.mention).replace("{mention}", member.mention).replace("{name}", member.name).replace("{guild}", guild.name).replace("{number}", str(guild.member_count))
            else:
                to_send = f'Welcome {member.mention} to {guild.name}!'
            await guild.get_channel(infoguild["welcome"][2]).send(to_send)
        elif guild.system_channel is not None and infoguild["welcome"][0] and infoguild["welcome"][0] != "disabled":
            await guild.system_channel.send(infoguild["welcome"][0].replace("{ping}", member.mention).replace("{mention}", member.mention).replace("{name}", member.name).replace("{guild}", guild.name).replace("{number}", str(guild.member_count)))
        print(member.name, "joined", guild.name)

        #welcome role
        if infoguild["welcome"][2]:
            await member.add_roles(member.guild.get_role(infoguild["welcome"][2]))

        #logging
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["joins"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Member joined", description=f"Target: {member.mention}\n\n{member}", colour=infoguild["color"])
            embed.set_thumbnail(url=member.avatar_url)
            await channel.send(content=None, embed=embed)
    
    async def on_member_remove(self, member):
        guild = member.guild
        infoguild = openconfig(guild.id)

        #leave message
        if infoguild["welcome"][2]:
            if infoguild["welcome"][0]:
                to_send = infoguild["welcome"][1].replace("{ping}", member.mention).replace("{mention}", member.mention).replace("{name}", member.name).replace("{guild}", guild.name).replace("{number}", str(guild.member_count))
            else:
                to_send = 'Welcome {0.mention} to {1.name}!'.format(member, guild)
            await guild.get_channel(infoguild["welcome"][2]).send(to_send)
        elif guild.system_channel is not None and infoguild["welcome"][1] and infoguild["welcome"][1] != "disabled":
            await guild.system_channel.send(infoguild["welcome"][1].replace("{ping}", member.mention).replace("{mention}", member.mention).replace("{name}", member.name).replace("{guild}", guild.name).replace("{number}", str(guild.member_count)))
  
        #logs
        print(member.name, "left", guild.name)
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["joins"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Member Left", description=f"Target: {member.mention}\n\n{member}", colour=infoguild["color"])
            embed.set_thumbnail(url=member.avatar_url)
            await channel.send(content=None, embed=embed)

    async def on_member_update(self, before, after):
        guild = before.guild
        infoguild = openconfig(guild.id)

        #logs
        if infoguild["logs"][0] != 0:
            channel = self.get_channel(infoguild["logs"][0])

            #nickname change
            if infoguild["logs"][1]["nick"] == 1 and before.nick != after.nick:
                embed = discord.Embed(title="Nickname update", description=f"Target: {before.mention}\n\n{before.nick} -> {after.nick}".replace("None", before.name), colour=infoguild["color"])
                embed.set_thumbnail(url=before.avatar_url)
                await channel.send(content=None, embed=embed)

            #role change
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

            #logs
            if guild.get_member(before.id) != None and infoguild["logs"][0] != 0:
                channel = self.get_channel(infoguild["logs"][0])

                #avatar change
                if infoguild["logs"][1]["user"] == 1 and after.avatar and before.avatar != after.avatar:
                    embed = discord.Embed(title="Avatar update", description=f"Target: {before.mention}\n\n", colour=infoguild["color"])
                    embed.set_thumbnail(url=before.avatar_url)
                    embed.set_image(url=after.avatar_url)
                    await channel.send(content=None, embed=embed)

                #username change
                if infoguild["logs"][1]["user"] == 1 and before.name != after.name:
                    embed = discord.Embed(title="Username changed", description=f"Target: {before.mention}\n\n{before.name} -> {after.name}", colour=infoguild["color"])
                    embed.set_thumbnail(url=before.avatar_url)
                    await channel.send(content=None, embed=embed)

                #discriminator change
                if infoguild["logs"][1]["user"] == 1 and before.discriminator != after.discriminator:
                    embed = discord.Embed(title="Discriminator changed", description=f"Target: {before.mention}\n\n{before.discriminator} -> {after.discriminator}", colour=infoguild["color"])
                    embed.set_thumbnail(url=before.avatar_url)
                    await channel.send(content=None, embed=embed)

    async def on_guild_update(self, before, after):
        infoguild = openconfig(before.id)

        #logs
        if infoguild["logs"][0] != 0:
            channel = self.get_channel(infoguild["logs"][0])

            #server name change
            if infoguild["logs"][1]["guild"] == 1 and after.name and before.name != after.name:
                embed = discord.Embed(title="Server name change", description=f"Target: {before.name}\n\n{before.name} -> {after.name}", colour=infoguild["color"])
                embed.set_thumbnail(url=before.icon_url)
                await channel.send(content=None, embed=embed)

            #server name change
            if infoguild["logs"][1]["guild"] == 1 and after.icon and before.icon != after.icon:
                embed = discord.Embed(title="Server icon change", description=f"Target: {before.name}", colour=infoguild["color"])
                embed.set_thumbnail(url=before.icon_url)
                embed.set_image(url=after.icon_url)
                await channel.send(content=None, embed=embed)

            #server owner change
            if infoguild["logs"][1]["guild"] == 1 and after.owner_id and before.owner_id != after.owner_id:
                embed = discord.Embed(title="Server owner change", description=f"Target: {before.name}\n\n<@{before.owner_id}> -> <@{after.owner_id}>", colour=infoguild["color"])
                embed.set_thumbnail(url=before.icon_url)
                await channel.send(content=None, embed=embed)

    async def on_guild_channel_create(self, channel):
        guild = channel.guild
        infoguild = openconfig(guild.id)

        #logs channel creation
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["channels"] == 1:
            channel2 = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Channel created", description=f"Target: {guild.name}\n\n{channel.mention} in {channel.category.mention}", colour=infoguild["color"])
            embed.set_thumbnail(url=guild.icon_url)
            await channel2.send(content=None, embed=embed)

    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        infoguild = openconfig(guild.id)

        #logs channel deletion
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["channels"] == 1:
            channel2 = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Role deleted", description=f"Target: {guild.name}\n\n#{channel.name} from {channel.category.mention}", colour=infoguild["color"])
            embed.set_thumbnail(url=guild.icon_url)
            await channel2.send(content=None, embed=embed)

    async def on_guild_channel_update(self, before, after):
        guild = before.guild
        infoguild = openconfig(guild.id)

        #logs channel creation
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["channels"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            #category change
            if before.category != after.category:
                embed = discord.Embed(title="Channel moved", description=f"Target: {before.mention}\n\n{before.category.mention} -> {after.category.mention}", colour=infoguild["color"])
                embed.set_thumbnail(url=guild.icon_url)
                await channel.send(content=None, embed=embed)

            #name
            if before.name != after.name:
                embed = discord.Embed(title="Channel renamed", description=f"Target: {before.mention}\n\n{before.name} -> {after.name}", colour=infoguild["color"])
                embed.set_thumbnail(url=guild.icon_url)
                await channel.send(content=None, embed=embed)

    async def on_guild_role_create(self, role):
        guild = role.guild
        infoguild = openconfig(guild.id)

        #logs role creation
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["guild_role"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Role created", description=f"Target: {guild.name}\n\n<@&{role.id}>", colour=infoguild["color"])
            embed.set_thumbnail(url=guild.icon_url)
            await channel.send(content=None, embed=embed)

    async def on_guild_role_delete(self, role):
        guild = role.guild
        infoguild = openconfig(guild.id)

        #logs role deletion
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["guild_role"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Role deleted", description=f"Target: {guild.name}\n\n@{role.name}", colour=infoguild["color"])
            embed.set_thumbnail(url=guild.icon_url)
            await channel.send(content=None, embed=embed)
    
    async def on_guild_role_update(self, before, after):
        guild = before.guild
        infoguild = openconfig(guild.id)

        #logs
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["guild_role"] == 1:
            channel = self.get_channel(infoguild["logs"][0])

            #role name change
            if before.name != after.name:
                embed = discord.Embed(title="Role edited", description=f"Target: <@&{before.id}>\nname:\n\n{before.name} -> {after.name}", colour=infoguild["color"])
                embed.set_thumbnail(url=guild.icon_url)
                await channel.send(content=None, embed=embed)

            #role permission change
            if before.permissions != after.permissions:
                embed = discord.Embed(title="Role edited", description=f"Target: <@&{before.id}>\npermissions:\n\n{before.permissions} -> {after.permissions}", colour=infoguild["color"])
                embed.set_thumbnail(url=guild.icon_url)
                await channel.send(content=None, embed=embed)

            #role position change
            if before.position != after.position:
                embed = discord.Embed(title="Role edited", description=f"Target: <@&{before.id}>\nposition:\n\n{before.position} -> {after.position}", colour=infoguild["color"])
                embed.set_thumbnail(url=guild.icon_url)
                await channel.send(content=None, embed=embed)

            #role color change
            if before.color != after.color:
                embed = discord.Embed(title="Role edited", description=f"Target: <@&{before.id}>\ncolor:\n\n{before.color.value} -> {after.color.value}", colour=infoguild["color"])
                embed.set_thumbnail(url=guild.icon_url)
                await channel.send(content=None, embed=embed)

    async def on_guild_emojis_update(self, guild, before, after):
        infoguild = openconfig(guild.id)

        #logs
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["emojis"] == 1:
            channel = self.get_channel(infoguild["logs"][0])

            #emoji deleted
            if len(before) > len(after):
                for i in before:
                    if i not in after:
                        embed = discord.Embed(title="Emoji deleted", description=f"Target: :{i.name}:", colour=infoguild["color"])
                        embed.set_thumbnail(url=i.url)
                        await channel.send(content=None, embed=embed)

            #emoji added
            elif len(before) < len(after):
                for i in after:
                    if i not in before:
                        embed = discord.Embed(title="Emoji added", description=f"Target: :{i.name}:", colour=infoguild["color"])
                        embed.set_thumbnail(url=i.url)
                        await channel.send(content=None, embed=embed)
            
            #emoji name change
            else:
                for i in range(len(after)):
                    if i not in before[i] and before[i].name != after[i].name:
                        embed = discord.Embed(title="Emoji edited", description=f"Target: :{before[i].name}:\n\n{before[i].name} -> {after[i].name}", colour=infoguild["color"])
                        embed.set_thumbnail(url=before[i].url)
                        await channel.send(content=None, embed=embed)

    async def on_member_ban(self, guild, user):
        infoguild = openconfig(guild.id)

        #logs ban
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["bans"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Member banned", description=f"Target: {user.mention}\n\n{user}", colour=infoguild["color"])
            embed.set_thumbnail(url=user.avatar_url)
            await channel.send(content=None, embed=embed)

    async def on_member_unban(self, guild, user):
        infoguild = openconfig(guild.id)

        #logs unban
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["bans"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            embed = discord.Embed(title="Member unbanned", description=f"Target: {user.mention}\n\n{user}", colour=infoguild["color"])
            embed.set_thumbnail(url=user.avatar_url)
            await channel.send(content=None, embed=embed)

    async def on_raw_message_edit(self, payload):
        channel = self.get_channel(payload.channel_id)
        guild = channel.guild
        infoguild = openconfig(guild.id)
        mess = await channel.fetch_message(payload.message_id)

        #ignore
        if payload.channel_id in infoguild["blackchannels"] or mess.author.bot:
            return
        
        #logs message edited
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["messages"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
            if payload.cached_message:
                if payload.cached_message.content != message.content:
                    embed = discord.Embed(title="Message edited", description=f"Target: {message.author.mention}\n\n<#{payload.channel_id}> [click to jump]({message.jump_url}):\n{payload.cached_message.content} -> {message.content}", colour=infoguild["color"])
                    embed.set_thumbnail(url=message.author.avatar_url)
                    if len(message.attachments) >= 1:
                        for i in message.attachments:
                            if list(i.filename.split("."))[-1].lower() in "pngsvgjpgjpegif":
                                embed.set_image(url=i.url)
                    await channel.send(content=None, embed=embed)
            else:
                embed = discord.Embed(title="Message edited", description=f"Target: {message.author.mention}\n\n<#{payload.channel_id}> [click to jump]({message.jump_url}):\nNot cached -> {message.content}", colour=infoguild["color"])
                embed.set_thumbnail(url=message.author.avatar_url)
                if len(message.attachments) >= 1:
                    for i in message.attachments:
                        if list(i.filename.split("."))[-1].lower() in "pngsvgjpgjpegif":
                            embed.set_image(url=i.url)
                await channel.send(content=None, embed=embed)

    async def on_raw_message_delete(self, payload):
        guild = self.get_guild(payload.guild_id)
        infoguild = openconfig(guild.id)

        #ignore
        if payload.channel_id in infoguild["blackchannels"]:
            return

        #logs message deleted
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["messages"] == 1:
            channel = self.get_channel(infoguild["logs"][0])
            if payload.cached_message:
                embed = discord.Embed(title="Message deleted", description=f"Target: {payload.cached_message.author.mention}\n\n{payload.cached_message.channel.mention} - {payload.cached_message.content}", colour=infoguild["color"])
                embed.set_thumbnail(url=payload.cached_message.author.avatar_url)
                if len(payload.cached_message.attachments) >= 1:
                    for i in payload.cached_message.attachments:
                        if list(i.filename.split("."))[-1].lower() in "pngsvgjpgjpegif":
                            embed.set_image(url=i.url)
            else:
                embed = discord.Embed(title="Message deleted", description=f"Target: <#{payload.channel_id}>\n\nNot cached", colour=infoguild["color"])
                embed.set_thumbnail(url=guild.icon_url)
            await channel.send(content=None, embed=embed)

    async def on_raw_bulk_message_delete(self, payload):
        guild = self.get_guild(payload.guild_id)
        infoguild = openconfig(guild.id)

        #ignore channel
        if payload.channel_id in infoguild["blackchannels"]:
            return

        #logs message deleted
        channel2 = self.get_channel(infoguild["logs"][0])
        if infoguild["logs"][0] != 0 and infoguild["logs"][1]["messages"] == 1:
            if payload.cached_messages:
                messages = ""
                for i in payload.cached_messages:
                    messages = messages + "\n>" + i.author.mention + ": " + i.content 
                embed = discord.Embed(title="Bulk message delete", description=f"Target: {payload.cached_messages[0].channel.mention}\n\n{len(payload.cached_messages)} messages deleted\n{messages}", colour=infoguild["color"])
            else:
                embed = discord.Embed(title="Bulk message delete", description=f"Target: <#{payload.channel_id}>\n\n{len(payload.message_ids)} messages deleted\nNo cache", colour=infoguild["color"])
            embed.set_thumbnail(url=guild.icon_url)
            await channel2.send(content=None, embed=embed)

    async def on_raw_reaction_add(self, payload):
        guild = self.get_guild(payload.guild_id)
        infoguild = openconfig(guild.id)
        mess = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)

        #reaction role
        if len(infoguild["reactrole"]) >= 1:
            for i in infoguild["reactrole"]:
                if i[0] == payload.channel_id and i[1] == payload.message_id and str(payload.emoji) in i[2]:
                    await payload.member.add_roles(guild.get_role(i[3]))

        #enlarge
        if mess.content == "react with the emoji you want to get":
            emote=payload.emoji.url
            if not emote:
                emote = str(payload.emoji)
            await mess.edit(content=emote)

        #help
        if "Help page: " in mess.content and mess.author.id == self.user.id and payload.user_id != self.user.id:
            number = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣"]
            for b in range(len(number)):
                if str(payload.emoji) == number[b]:
                    try:
                        await mess.reactions[b].remove(self.get_user(payload.user_id))
                    except:
                        print()
                    embed = discord.Embed(title=help[b][0], description=f"prefix: {infoguild['prefix']}", colour=infoguild["color"])
                    for i in range(1, len(help[b])):
                        embed.add_field(name="TT" + help[b][i].split("|")[0], value=help[b][i].split("|")[1])
                    await mess.edit(content=f"Help page: {number[b]}", embed=embed)

        #starboard
        if infoguild["star"][1] and str(payload.emoji) in infoguild["star"][2]:
            try:
                f = open(f"star/{payload.guild_id}.json", "r", encoding = "utf-8")
                star = json.load(f)
            except:
                #initialization
                star = {}
                f = open(f"star/{payload.guild_id}.json", "w", encoding = "utf-8")
                json.dump(star, f)
                f.close()
                return
            userid = {}
            for i in mess.reactions:
                if str(i) in infoguild["star"][2]:
                    users = await i.users().flatten()
                    for i in users:
                        userid[str(i.id)] = 1
            channel = guild.get_channel(infoguild["star"][0])

            #send to starboard
            if str(payload.message_id) not in star and len(userid) >= infoguild["star"][1] and channel != mess.channel:
                embed = discord.Embed(title="", description=f"Author: {mess.author.mention} {mess.author.name}#{mess.author.discriminator}\n\n{mess.content}\n\n[Jump to Message]({mess.jump_url})", colour=infoguild["color"])
                embed.set_thumbnail(url=mess.author.avatar_url)
                if len(mess.attachments) >= 1:
                    for i in mess.attachments:
                        embed.set_image(url=i.url)
                message = await channel.send(content=f"**{len(userid)} | {mess.channel.mention}**", embed=embed)
                star[str(payload.message_id)] = [message.id, userid]
                f = open(f"star/{guild.id}.json", "w", encoding = "utf-8")
                json.dump(star, f)
                f.close()

            #edit starboard message
            elif str(payload.message_id) in star and len(userid) >= infoguild["star"][1] and channel != mess.channel:
                message = await guild.get_channel(infoguild["star"][0]).fetch_message(star[str(payload.message_id)][0])
                for i in message.reactions:
                    if str(i) in infoguild["star"][2]:
                        users = await i.users().flatten()
                        for i in users:
                            userid[str(i.id)] = 1
                star[str(payload.message_id)] = [message.id, userid]
                f = open(f"star/{guild.id}.json", "w", encoding = "utf-8")
                json.dump(star, f)
                await message.edit(content=f"**{len(userid)} | {mess.channel.mention}**")

            #starring starboard
            elif channel == mess.channel:
                messageid = 0
                for i in star:
                    if star[i][0] == payload.message_id:
                        messageid = i
                message = await mess.channel_mentions[0].fetch_message(int(messageid))
                userid = star[str(messageid)][1]
                for i in mess.reactions:
                    if str(i) in infoguild["star"][2]:
                        users = await i.users().flatten()
                        for i in users:
                            userid[str(i.id)] = 1
                star[messageid][1] = userid
                f = open(f"star/{guild.id}.json", "w", encoding = "utf-8")
                json.dump(star, f)
                await mess.edit(content=f"**{len(userid)} | {message.channel.mention}**")

    async def on_raw_reaction_remove(self, payload):
        guild = self.get_guild(payload.guild_id)
        infoguild = openconfig(guild.id)
        mess = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)

        #reaction role
        if len(infoguild["reactrole"]) >= 1:
            for i in infoguild["reactrole"]:
                if i[0] == payload.channel_id and i[1] == payload.message_id and str(payload.emoji) in i[2]:
                    member = guild.get_member(payload.user_id)
                    await member.remove_roles(guild.get_role(i[3]))

        #starboard
        if infoguild["star"][1] and str(payload.emoji) == infoguild["star"][2]:
            try:
                f = open(f"star/{guild.id}.json", "r", encoding = "utf-8")
                star = json.load(f)
            except:
                #initialization
                star = {}
                f = open(f"star/{guild.id}.json", "w", encoding = "utf-8")
                json.dump(star, f)
                f.close()
            mess = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
            userid = {}
            for i in mess.reactions:
                if str(i) in infoguild["star"][2]:
                    users = await i.users().flatten()
                    for i in users:
                        userid[str(i.id)] = 1
            channel = guild.get_channel(infoguild["star"][0])

            #edit starboard message
            if str(payload.message_id) in star and len(userid) >= infoguild["star"][1] and channel != mess.channel:
                message = await channel.fetch_message(star[str(payload.message_id)][0])
                for i in message.reactions:
                    if str(i) in infoguild["star"][2]:
                        users = await i.users().flatten()
                        for i in users:
                            userid[str(i.id)] = 1
                star[str(payload.message_id)] = [message.id, userid]
                f = open(f"star/{guild.id}.json", "w", encoding = "utf-8")
                json.dump(star, f)
                await message.edit(content=f"**{len(userid)} | {mess.channel.mention}**")

            #starring starboard
            elif channel == mess.channel:
                message = mess
                messageid = 0
                for i in star:
                    if star[i][0] == payload.message_id:
                        messageid = i
                userid = star[str(messageid)][1]
                for i in message.reactions:
                    if str(i) in infoguild["star"][2]:
                        users = await i.users().flatten()
                        for i in users:
                            userid[str(i.id)] = 1
                star[messageid][1] = userid
                f = open(f"star/{guild.id}.json", "w", encoding = "utf-8")
                json.dump(star, f)
                await message.edit(content=f"**{len(userid)} | {mess.channel.mention}**")


    async def on_message(self, message):
        #load config
        try:
            infoguild = openconfig(message.guild.id)
        except:
            infoguild = openconfig()
        prefix = infoguild["prefix"]
        admin = infoguild["admins"]

        # ignore channel
        if message.channel.id in infoguild["blackchannels"]:
            return

        # cut message into list
        messlist = message.content.split()

        # determine prefix
        if messlist[0].startswith(prefix):
            p = prefix
        else:
            p = "TT"

        # logs
        try:
            print(f"{message.guild.name} - {message.channel.name} - {message.author.name}: {message.content}")
        except AttributeError:
            print(f"dm - {message.author.name}: {message.content}")

        if ":ccc" in message.content:
            await message.delete()
            return

        #server message
        if message.guild:
            #message sent by muted?
            if infoguild["muted"]:
                if message.author.id in infoguild["muted"] and message.author.id not in owner and message.author.roles[-1].id not in admin and message.author != message.guild.owner:
                    await message.delete()
                    return

            #bot stuff
            elif message.author.bot:
                return

            #commands
            if message.content.strip(" ") == "<@782922227397689345>" or message.content.strip(" ") == "<@!782922227397689345>":
                embed = discord.Embed(title="My prefix are", description=f"{infoguild['prefix']}", colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)
                return
            if p in messlist[0]:
                messlist[0] = p + messlist[0].replace(p, "").lower()
                print(messlist[0])

                #owner commands
                if message.author.id in owner:
                    if message.author.id in owner and messlist[0] == "TTleaveserver": 
                        guild = self.get_guild(getid(messlist[1]))
                        await guild.leave()
                        print(f"left {guild.name}")
                    if messlist[0] == p + "givechannel":
                        channel = self.get_channel(getid(messlist[1]))
                        await channel.set_permissions(message.author, overwrite=discord.PermissionOverwrite(view_channel=True))
                        await message.channel.send("successfully gave access")
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
                                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.guilds)} servers"))
                    
                    #custom commands
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

                    #update server configs
                    elif messlist[0] == p + "update":
                        async with message.channel.typing():
                            updated = 0
                            embed = discord.Embed(title=f"Updating 0 / {len(self.guilds)}", description="", colour=infoguild["color"])
                            mess = await message.channel.send(content=None, embed=embed)
                            for a in self.guilds:
                                infoguild = openconfig(a.id)
                                default = openconfig()
                                try:
                                    #update here
                                    
                                    #end of update
                                    saveconfig(infoguild, a.id)
                                    updated += 1
                                    embed = discord.Embed(title=f"Updating {updated} / {len(self.guilds)}", description=f"guild: {a.name}\nowner: {a.owner.mention}\nid: {a.id}", colour=infoguild["color"])
                                    await mess.channel.send(content=None, embed=embed)
                                except:
                                    embed = discord.Embed(title="Could not update", description=f"guild: {a.name}\nowner: {a.owner}", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                            embed = discord.Embed(title="Successfully updated", description=f"{updated} / {len(self.guilds)} guilds", colour=infoguild["color"])
                            await mess.edit(content=None, embed=embed)

                #everyone commands
                #number of users
                if messlist[0] == p + "users" or messlist[0] == p + "members":
                    await message.delete()
                    embed = discord.Embed(title="Number of Members:", description=str(message.guild.member_count), colour=infoguild["color"])
                    await message.channel.send(content=None, embed=embed)

                #say something
                elif messlist[0] == p + "say":
                    await message.delete()
                    if message.author.roles[-1].id in admin or message.author.id in owner or message.author == message.guild.owner:
                        if "<#" in messlist[1]:
                            channel = message.guild.get_channel(getid(messlist[1]))
                            if len(messlist) >= 3:
                                await channel.send(sortname(messlist, 2))
                            if len(message.attachments) >= 1:
                                for i in message.attachments:
                                    if list(i.filename.split("."))[-1].lower() in "pngsvgjpgjpegif":
                                        await i.save(f'cache/attachment.{list(i.filename.split("."))[-1].lower()}', use_cached=True)
                                        await channel.send(file=discord.File(f'cache/attachment.{list(i.filename.split("."))[-1].lower()}'))
                        else:
                            if len(message.attachments) >= 1:
                                for i in message.attachments:
                                    if list(i.filename.split("."))[-1].lower() in "pngsvgjpgjpegif":
                                        await i.save(f'cache/attachment.{list(i.filename.split("."))[-1].lower()}', use_cached=True)
                                        await message.channel.send(content=sortname(messlist), file=discord.File(f'cache/attachment.{list(i.filename.split("."))[-1].lower()}'))
                            else:
                                await message.channel.send(sortname(messlist))
                    elif "@everyone" not in message.content and "@here" not in message.content and "<@&" not in message.content:
                        await message.channel.send(message.author.name + ": " + sortname(messlist))
                    else:
                        await message.channel.send(message.author.mention + " you tried")

                #whois/info page
                elif messlist[0] == p + "whois" or messlist[0] == p + "userinfo":
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
                    if member == message.guild.owner:
                        type = "owner"
                    elif member.bot:
                        type = "bot"
                    elif member.guild_permissions.administrator:
                        type = "admin"
                    else:
                        type = "member"
                    embed = discord.Embed(title="", description=f"**{member.mention} / {member.name}#{member.discriminator}**\n\n**creation:** {member.created_at.strftime('%m/%d/%Y')}\n**joined:** {member.joined_at.strftime('%m/%d/%Y')}\n**id:** {member.id}\n**roles:** {roles}\n**type:** {type}", colour=infoguild["color"])
                    embed.set_thumbnail(url=member.avatar_url)
                    await message.channel.send(content=None, embed=embed)

                #help
                if messlist[0] == p + "help":
                    embed = discord.Embed(title=help[0][0], description=f"prefix: {infoguild['prefix']}", colour=infoguild["color"])
                    for i in range(1, len(help[0])):
                        embed.add_field(name=p + help[0][i].split("|")[0], value=help[0][i].split("|")[1])
                    mess = await message.channel.send(content="Help page: 1️⃣", embed=embed)
                    await mess.add_reaction("1️⃣")
                    await mess.add_reaction("2️⃣")
                    await mess.add_reaction("3️⃣")
                    await mess.add_reaction("4️⃣")
                    await mess.add_reaction("5️⃣")

                #server info
                if messlist[0] == p + "serverinfo" or messlist[0] == p + "server":
                    embed = discord.Embed(title=f"{message.guild.name}'s info page", description=f'prefix: {infoguild["prefix"]}', colour=infoguild["color"])
                    embed.add_field(name="General infos", value=f'\n**Owner:** {message.guild.owner.mention}\n**Created:** {message.guild.created_at.strftime("%m/%d/%Y")}\n\n{message.guild.member_count} members\n{len(message.guild.roles)} roles\n{len(message.guild.categories)} categories\n{len(message.guild.text_channels)} channels\n{len(message.guild.voice_channels)} voice channels')
                    embed.set_thumbnail(url=message.guild.icon_url)
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
                                channel = self.get_channel(infoguild["vote"][1])
                                if len(message.attachments) >= 1:
                                    for i in message.attachments:
                                        if list(i.filename.split("."))[-1].lower() in "pngsvgjpgjpegif":
                                            await i.save(f'cache/attachment.{list(i.filename.split("."))[-1].lower()}', use_cached=True)
                                            message = await channel.send(content=sortname(messlist, 2), file=discord.File(f'cache/attachment.{list(i.filename.split("."))[-1].lower()}'))
                                            await message.add_reaction("👍")
                                            await message.add_reaction("👎")
                                else:
                                    message = await channel.send(sortname(messlist, 2))
                                    await message.add_reaction("👍")
                                    await message.add_reaction("👎")
                            else:
                                embed = discord.Embed(title="Application channel is missing", description="Do (TTsetvote #channel) to set it up", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                        else:
                            if infoguild["vote"][0] != 0:
                                infoguild["vote"][2] = 1
                                saveconfig(infoguild, message.guild.id)
                                channel = self.get_channel(infoguild["vote"][0])
                                if len(message.attachments) >= 1:
                                    for i in message.attachments:
                                        if list(i.filename.split("."))[-1].lower() in "pngsvgjpgjpegif":
                                            await i.save(f'cache/attachment.{list(i.filename.split("."))[-1].lower()}', use_cached=True)
                                            message = await channel.send(content=sortname(messlist, 1), file=discord.File(f'cache/attachment.{list(i.filename.split("."))[-1].lower()}'))
                                            await message.add_reaction("👍")
                                            await message.add_reaction("👎")
                                else:
                                    message = await channel.send(sortname(messlist, 1))
                                    await message.add_reaction("👍")
                                    await message.add_reaction("👎")
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
                        member = message.guild.get_member(getid(messlist[1]))
                        role = message.guild.get_role(getid(messlist[2]))
                        if role not in member.roles:
                            try:
                                await member.add_roles(role)
                                embed = discord.Embed(title="Successfully added", description=f"{role.mention} to {member.mention}", colour=infoguild["color"])
                            except:
                                embed = discord.Embed(title="Could not add role", description="Make sure the command syntax is correct and that my role is above the role to give", colour=infoguild["color"])
                        else:
                            try:
                                await member.remove_roles(role)
                                embed = discord.Embed(title="Successfully removed", description=f"{role.mention} from {member.mention}", colour=infoguild["color"])
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
                        voice = discord.utils.get(self.voice_clients, guild=message.channel.guild)
                        if message.author.voice:
                            channel = message.author.voice.channel
                            await channel.connect()
                            embed = discord.Embed(title="Joined voice channel", description=message.author.voice.channel.mention, colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            embed = discord.Embed(title="Could not join voice channel", description="Make sure you are connected to a voice channel that I have access of", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)

                    #leave vc
                    elif messlist[0] == p + "leave" or messlist[0] == p + "yeet" or messlist[0] == p + "fuckoff" or messlist[0] == p + "dc":
                        voice = discord.utils.get(self.voice_clients, guild=message.channel.guild)
                        if message.guild.voice_client:
                            await message.guild.voice_client.disconnect()
                            embed = discord.Embed(title="Left voice channel", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            embed = discord.Embed(title="Currently not in a voice channel", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)

                    #play
                    elif messlist[0] == p + "play" and str(message.guild.id) in "819121115971977276847183491468492902795187736322506782761594268405989396823362441362538507":
                        async with message.channel.typing():
                            voice = discord.utils.get(self.voice_clients, guild=message.channel.guild)
                            if message.guild.voice_client:
                                await message.guild.voice_client.disconnect()
                                embed = discord.Embed(title="Left voice channel", description="", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                            else:
                                embed = discord.Embed(title="Currently not in a voice channel", description="", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                            if len(messlist) >= 2:
                                song_there = os.path.isfile("song.mp3")
                                try:
                                    if song_there:
                                        os.remove("song.mp3")
                                except PermissionError:
                                    embed = discord.Embed(title="Can't change song", description=f"wait the end or use {p}stop", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                                    return
                                except:
                                    embed = discord.Embed(title="uhh idk tbh", description="", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                                    return
                                embed = discord.Embed(title="Downloading video", description="", colour=infoguild["color"])
                                mess = await message.channel.send(content=None, embed=embed)
                                ydl_opts = {
                                    'format': 'bestaudio/best',
                                    'postprocessors': [{
                                        'key': 'FFmpegExtractAudio',
                                        'preferredcodec': 'mp3',
                                        'preferredquality': '192'
                                    }]
                                }
                                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                                    ydl.download([messlist[1]])
                                embed = discord.Embed(title="Video downloaded", description="Now loading file", colour=infoguild["color"])
                                await mess.edit(content=None, embed=embed)
                                for file in os.listdir("./"):
                                    if file.endswith(".mp3"):
                                        embed = discord.Embed(title="Playing", description=f'[{file.replace(".mp3", "")}]({messlist[1]})', colour=infoguild["color"])
                                        os.rename(file, "song.mp3")
                                if not message.guild.voice_client:
                                    if message.author.voice:
                                        channel = message.author.voice.channel
                                        await channel.connect()
                                        voice = discord.utils.get(self.voice_clients, guild=message.channel.guild)
                                        embed = discord.Embed(title="Joined voice channel", description=message.author.voice.channel.mention, colour=infoguild["color"])
                                        await message.channel.send(content=None, embed=embed)
                                        voice.play(discord.FFmpegPCMAudio("song.mp3"))
                                        await mess.edit(content=None, embed=embed)
                                    else:
                                        embed = discord.Embed(title="Couldn't connect to vc", description="", colour=infoguild["color"])
                                        await message.channel.send(content=None, embed=embed)
                                        return
                            else:
                                for file in os.listdir("./"):
                                    if file.endswith(".mp3"):
                                        embed = discord.Embed(title="Playing", description="something", colour=infoguild["color"])
                                        os.rename(file, "song.mp3")
                                if not message.guild.voice_client:
                                    if message.author.voice:
                                        channel = message.author.voice.channel
                                        await channel.connect()
                                        voice = discord.utils.get(self.voice_clients, guild=message.channel.guild)
                                        embed = discord.Embed(title="Joined voice channel", description=message.author.voice.channel.mention, colour=infoguild["color"])
                                        await message.channel.send(content=None, embed=embed)
                                        voice.play(discord.FFmpegPCMAudio("song.mp3"))
                                        await message.channel.send(content=None, embed=embed)
                                    else:
                                        embed = discord.Embed(title="Couldn't connect to vc", description="", colour=infoguild["color"])
                                        await message.channel.send(content=None, embed=embed)
                                        return

                    #pause
                    elif messlist[0] == p + "pause":
                        voice = discord.utils.get(self.voice_clients, guild=message.channel.guild)
                        if voice.is_playing():
                            voice.pause()
                            embed = discord.Embed(title="Paused", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            voice.resume()
                            embed = discord.Embed(title="Resumed", description="", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)

                    #stop
                    elif messlist[0] == p + "stop":
                        voice = discord.utils.get(self.voice_clients, guild=message.channel.guild)
                        voice.stop()
                        embed = discord.Embed(title="Stopped", description="", colour=infoguild["color"])
                        await message.channel.send(content=None, embed=embed)

                    # spam (pls don't abuse)
                    elif messlist[0] == p + "spam":
                        await message.delete()
                        for i in range(int(messlist[1])):
                            await message.channel.send(sortname(messlist, 2))

                    # ghost ping
                    elif messlist[0] == p + "ghost":
                        await message.channel.send(f"<@{int(messlist[1])}><@&{int(messlist[1])}>")
                        await message.channel.purge(limit=1)
                        await message.delete()

                    # botnick
                    elif messlist[0] == p + "botnick":
                        await message.delete()
                        user = message.guild.get_member(self.user.id)
                        await user.edit(nick=sortname(messlist, 1))

                    # custom commands
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

                    # setup
                    elif messlist[0] == p + "setup":
                        embed = discord.Embed(title="SETUP page", description=f"prefix: {infoguild['prefix']}", colour=infoguild["color"])
                        adminlist = ""
                        for i in range(len(infoguild["admins"])):
                            adminlist = adminlist + f'<@&{int(infoguild["admins"][i])}>'
                        blackchannels = ""
                        for i in range(len(infoguild["blackchannels"])):
                            blackchannels = blackchannels + f'<#{int(infoguild["blackchannels"][i])}>'
                        embed.add_field(name="General config", value=f'color: {infoguild["color"]}\nprefix: {infoguild["prefix"]}\nadmins: {adminlist}\nvote: <#{int(infoguild["vote"][0])}>\napp vote: <#{int(infoguild["vote"][1])}>\nblacklisted channels: {blackchannels}\nstarboard: <#{infoguild["star"][0]}> with {infoguild["star"][1]} {infoguild["star"][2]}')
                        log = ""
                        for i in infoguild["logs"][1]:
                            if infoguild["logs"][1][i]:
                                log += f'{i}: <:check:845741031344963605>\n'
                            else:
                                log += f'{i}: <:cross:845741065306112040>\n'
                        embed.add_field(name="Logs", value=f"channel: <#{infoguild['logs'][0]}>\n" + log)
                        rr = ""
                        for i in infoguild["reactrole"]:
                            channel2 = self.get_channel(i[0])
                            message2 = await channel2.fetch_message(i[1])
                            rr += f"{channel2.mention} [message]({message2.jump_url}) - {i[2]} <@&{i[3]}>\n"
                        if rr == "":
                            rr = "None"
                        embed.add_field(name="Reaction roles", value=rr)
                        cc = ""
                        for i in range(len(infoguild["command"][0])):
                            cc += f'{p}{infoguild["command"][0][i]} {str(infoguild["command"][2][i]).replace("0", "").replace("1", "embed")} {infoguild["command"][1][i]}\n'
                        if cc == "":
                            cc = "None"
                        embed.add_field(name="Custom commands", value=cc)
                        if infoguild["welcome"][3] == 0:
                            if message.guild.system_channel:
                                welcchannel = message.guild.system_channel.mention
                            else:
                                welcchannel = "disabled"
                        else:
                            welcchannel = f'<#{infoguild["welcome"][3]}>'
                        embed.add_field(name="Welcome", value=f'channel: {welcchannel}\nrole: <@&{infoguild["welcome"][2]}>\nwelcome message: {infoguild["welcome"][0]}\nleave message: {infoguild["welcome"][1]}')
                        await message.channel.send(content=None, embed=embed)

                    # resets server config
                    elif messlist[0] == p + "reset":
                        if len(messlist) > 1:
                            default = openconfig()
                            try:
                                infoguild[messlist[1]] = default[messlist[1]]
                                saveconfig(infoguild, message.guild.id)
                                embed = discord.Embed(title="Successfully reset", description=f"target: {messlist[1]}", colour=infoguild["color"])
                            except:
                                saveconfig(default, message.guild.id)
                                embed = discord.Embed(title="Successfully reset", description="target: whole confing", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            default = openconfig()
                            saveconfig(default, message.guild.id)
                            embed = discord.Embed(title="Successfully reset", description="target: whole confing", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)

                    # change embed color, must be an int
                    elif messlist[0] == p + "color":
                        try:
                            color = int(messlist[1])
                            if color < 0 or color > 16777215:
                                raise ValueError
                            infoguild["color"] = color
                            saveconfig(infoguild, message.guild.id)
                            embed = discord.Embed(title="Color has been changed to", description=color, colour=color)
                            await message.channel.send(content=None, embed=embed)                            
                        except ValueError:
                            embed = discord.Embed(title="Invalid color number", description="Make sure to provide an integer from 0 to 16777215", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)

                    # adds a prefix
                    elif messlist[0] == p + "prefix" and messlist[0] not in infoguild["prefix"]:
                        infoguild["prefix"].append(messlist[1])
                        saveconfig(infoguild, message.guild.id)
                        embed = discord.Embed(title="Added to prefix list", description=messlist[1], colour=infoguild["color"])
                        await message.channel.send(content=None, embed=embed)

                    # removes a prefix
                    elif messlist[0] == p + "prefix" and messlist[1] in infoguild["prefix"] and len(infoguild["prefix"]) > 1:
                        infoguild["prefix"].remove(messlist[1])
                        saveconfig(infoguild, message.guild.id)
                        embed = discord.Embed(title="Removed from prefix list", description=messlist[1], colour=infoguild["color"])
                        await message.channel.send(content=None, embed=embed)

                    # adds an admin role
                    elif messlist[0] == p + "op":
                        infoguild["admins"].append(int(getid(messlist[1])))
                        saveconfig(infoguild, message.guild.id)
                        embed = discord.Embed(title="Added to admin list", description=f"<@&{getid(messlist[1])}>", colour=infoguild["color"])
                        await message.channel.send(content=None, embed=embed)

                    # removes an admin role
                    elif messlist[0] == p + "unop":
                        if getid(messlist[1]) in infoguild["admins"]:
                            infoguild["admins"].remove(getid(messlist[1]))
                            saveconfig(infoguild, message.guild.id)
                            embed = discord.Embed(title="Removed from admin list", description=f"<@&{getid(messlist[1])}>", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        else:
                            embed = discord.Embed(title="Invalid admin role", description="Make sure the role is already in the admin list", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)

                    # setup vote
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

                    # welcome
                    elif messlist[0] == p + "welcome":
                        if "<#" in messlist[1]:
                            infoguild["welcome"][3] = getid(messlist[1])
                            embed = discord.Embed(title="Set welcome channel", description=f"<#{getid(messlist[1])}>", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                            saveconfig(infoguild, message.guild.id)
                        elif "<@&" in messlist[1] or getid(messlist[1]):
                            infoguild["welcome"][2] = getid(messlist[1])
                            embed = discord.Embed(title="Set welcome role", description=f"<@&{getid(messlist[1])}>", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                            saveconfig(infoguild, message.guild.id)
                        elif messlist[1] == "leave":
                            infoguild["welcome"][1] = sortname(messlist, 2)
                            embed = discord.Embed(title="Set leave message", description=sortname(messlist, 2), colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                            saveconfig(infoguild, message.guild.id)
                        else:
                            infoguild["welcome"][0] = sortname(messlist)
                            embed = discord.Embed(title="Set welcome message", description=sortname(messlist), colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                            saveconfig(infoguild, message.guild.id)

                    # blacklist
                    elif messlist[0] == p + "blacklist":
                        channel = getid(messlist[1])
                        if channel not in infoguild["blackchannels"]:
                            infoguild["blackchannels"].append(channel)
                            embed = discord.Embed(title="Blacklisted channel", description=f"<#{channel}>", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                            saveconfig(infoguild, message.guild.id)
                        else:
                            infoguild["blackchannels"].remove(channel)
                            embed = discord.Embed(title="Unblacklisted channel", description=f"<#{channel}>", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                            saveconfig(infoguild, message.guild.id)

                    # logs
                    elif messlist[0] == p + "logs" or messlist[0] == p + "log":
                        try:
                            # channel in which the logs will go
                            if messlist[1] == "channel":
                                try:
                                    infoguild["logs"][0] = getid(messlist[2])
                                    saveconfig(infoguild, message.guild.id)
                                    embed = discord.Embed(title="Set log channel", description=f"<#{getid(messlist[2])}>", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)
                                except:
                                    embed = discord.Embed(title="Could not set log channel", description="Make sure to have input a correct channel or channel id as the second argument", colour=infoguild["color"])
                                    await message.channel.send(content=None, embed=embed)

                            # enable logs
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

                            # disable logs
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
                                #logs help page
                                embed = discord.Embed(title="Logs error", description=f"Check {p}help to check the command syntax", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                        except:
                            embed = discord.Embed(title="Logs error", description=f"Check {p}help to check the command syntax", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)

                    #reaction role
                    elif messlist[0] == p + "reactionrole" or messlist[0] == p + "reaction_role" or messlist[0] == p + "rr":
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

                    #starboard:
                    elif messlist[0] == p + "starboard" or messlist[0] == p + "star":
                        try:
                            infoguild["star"][1] = int(messlist[1])
                            saveconfig(infoguild, message.guild.id)
                            embed = discord.Embed(title="Successfully set", description=f"**{int(messlist[1])}** as the number of stars required", colour=infoguild["color"])
                            await message.channel.send(content=None, embed=embed)
                        except:
                            if "<#" in messlist[1].lower():
                                infoguild["star"][0] = getid(messlist[1])
                                saveconfig(infoguild, message.guild.id)
                                embed = discord.Embed(title="Successfully set", description=f"<#{getid(messlist[1])}> as the starboard channel", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)
                            elif "<:" in messlist[1].lower() or len(messlist[1].lower()) == 1:
                                if messlist[1] in infoguild["star"][2]:
                                    infoguild["star"][2].remove(messlist[1])
                                    embed = discord.Embed(title="Successfully removed", description=f"{messlist[1]} from the star emojis", colour=infoguild["color"])
                                else:
                                    infoguild["star"][2].append(messlist[1])
                                    embed = discord.Embed(title="Successfully added", description=f"{messlist[1]} to the star emojis", colour=infoguild["color"])
                                saveconfig(infoguild, message.guild.id)
                                await message.channel.send(content=None, embed=embed)
                            else:
                                embed = discord.Embed(title="Could not setup starboard", description="check the command syntax and my perms", colour=infoguild["color"])
                                await message.channel.send(content=None, embed=embed)

        # dms
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

        # fun
        # pixel being pinged
        if "832240193020624896>" in message.content:
            await message.channel.send("https://cdn.discordapp.com/attachments/761594268405989399/845705313885880391/ezgif.com-gif-maker_28.gif")
        
        # bot being pinged
        if str(self.user.id) + ">" in message.content:
            await message.channel.send("https://cdn.discordapp.com/emojis/823170480143204383.gif?v=1")

        # everywhere commands (dms + servers)
        if p in messlist[0]:
            messlist[0] = p + messlist[0][len(p):].lower()

            #ping
            if messlist[0] == p + "ping":
                embed = discord.Embed(title="Pong", description=f"{round(self.latency * 1000)} ms", colour=infoguild["color"])
                mention = discord.AllowedMentions(replied_user=False)
                await message.reply(content=None, embed=embed, allowed_mentions=mention)

            #application help
            elif messlist[0] == p + "application" or messlist[0] == p + "app" or message.content == p + "a":
                embed = discord.Embed(title="Application help", description=application[0], colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)
            elif messlist[0] == p + "layout" or messlist[0] == p + "l":
                embed = discord.Embed(title="Application layout", description=application[1], colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)

            #logo
            elif messlist[0] == p + "logo":
                embed = discord.Embed(title="Logo", description="", colour=infoguild["color"])
                embed.set_image(url=self.user.avatar_url)
                await message.channel.send(content=None, embed=embed)

            #emoji
            elif messlist[0] == p + "emoji":
                await message.delete()
                await message.channel.send("react with the emoji you want to get")

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

            # calculator
            elif any(messlist[0].endswith(x) for x in ["calc", "calculator"]):
                await message.channel.send(urllib.request.urlopen("http://api.mathjs.org/v4/?expr=" + urllib.parse.quote_plus(" ".join(messlist[1:]))).read().decode("utf-8"))

            #invite
            elif messlist[0] == p + "invite":
                embed = discord.Embed(title="Invite link", description="Invite link: [click here](https://discordapp.com/oauth2/authorize?client_id=782922227397689345&scope=bot&permissions=1073217110)\nJoin this server to get help: [click here](https://discord.gg/q6HFJwv7gA)\nDM bot owner: <@630919091015909386>\nSource code: [click here](https://github.com/MCBE-Craft/MCBE-Bot)", colour=infoguild["color"])
                await message.channel.send(content=None, embed=embed)

intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
keep_alive()
client.run(os.getenv('token'))
