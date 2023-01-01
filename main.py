import os
from discord.ext import commands
import discord
import random
import asyncio
import requests
import datetime
from quickdb import SQLITE
db = SQLITE()


def get_prefix(client, message):
    if not message.guild: return
    pref = db.get(f"prefix_{message.guild.id}")
    if pref == None:
       return "!" 
    else:
       return pref

def get_all_members(client):
    allm = 0
    for g in client.guilds:
        for m in g.members:
            allm += 1
    return allm

client = commands.Bot(command_prefix = get_prefix, help_command=None, intents = discord.Intents.all())
  
@client.command()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, pref = None):
    if pref == None:
       return await ctx.send(embed=discord.Embed(title="<:no_check:963100302238679070> | Error", description="`!setprefix [prefix]`", color=0xff9500))
    db.set(f"prefix_{ctx.guild.id}", pref)
    await ctx.send(embed=discord.Embed(title="<:yes_check:963100268692648106> | Succes", description=f"New prefix is '{pref}'", color=0xff9500))

@client.event
async def on_message(msg):
    if msg.author.bot: return
    await client.process_commands(msg)
    xp = db.get(f'xp_{msg.guild.id}_{msg.author.id}') or 0
    lvl = db.get(f'lvl_{msg.guild.id}_{msg.author.id}') or 1
    if int(xp) >= int(lvl) * 10:
        db.set(f'xp_{msg.guild.id}_{msg.author.id}', 0)
        db.set(f'lvl_{msg.guild.id}_{msg.author.id}', int(lvl) + 1)
        await msg.channel.send(f'{msg.author.mention}, you leveled up before {int(lvl) + 1}')
    else:
        db.add(f'xp_{msg.guild.id}_{msg.author.id}', 1)

@client.command()
async def help(ctx):
  embed=discord.Embed(title="<:docs:958956360530272347> | List of commands", description="⠀", color=0xff8800) 
  embed.add_field(name=":video_game: | Main", value=" !setprefix [prefix] - set main prefix \n ", 
  inline=True)
  await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=1, limit_amount=1):
    await ctx.channel.purge(limit=amount+1)  
    author = ctx.message.author
    embed = discord.Embed(description= f'✅ Cleaned up successfully \n 👤 cleared:{author} \n 📄 Amout: {amount} ')
    await ctx.send(embed=embed)

@client.command()
async def warn(ctx, member: discord.Member, *, reason):
    db.add(f'warns_{member.id}', 1)
    await ctx.send(f'User {member.mention} issued a warning due to: {reason}')

@client.command()
async def warns(ctx):
   warns = db.get(f'warns_{ctx.author.id}')
   if warns == None: warns = 0
   await ctx.send(f'At your place {warns} warnings')
  

@client.command()
async def avatar(ctx, member: discord.Member = None):
    if member == None:
        member = ctx.author
    embed = discord.Embed(
        color=0xe67e22,
        title=f"Avatar - {member.name}",
        description=f"[Click to download avatar]({member.avatar_url})")
    embed.set_image(url=member.avatar_url)
    await ctx.reply(embed=embed)


@client.command()
@commands.has_permissions(manage_roles=True)
async def role(ctx, member: discord.Member, *, role: discord.Role):
    await member.add_roles(role)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply(
            embed=discord.Embed(title=":x: | **404**",
                                description=f'** This command was not found **',
                                color=0xe67e22))

@client.command()
async def ping(ctx: commands.Context):
    emb = discord.Embed(
        description=
        f'** Bot state:** \n \n **Ping:** {round(client.latency * 1000)} ms.',
        color=0xe67e22)
    await ctx.send(embed=emb)

@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, reason="No reason provided"):
    await user.kick(reason=reason)
    kick = discord.Embed(
        title=f":boot: Kicknut {user.name}!",
        description=f"Reason: {reason}\nKicked: {ctx.author.mention}",
        color=0xe67e22)
    await ctx.message.delete()
    await ctx.channel.send(embed=kick)
    await user.send(embed=kick)

@client.command()
async def servers(ctx):
    r = [i.name for i in client.guilds]
    w = [i.id for i in client.guilds]
    await ctx.reply(
        embed=discord.Embed(title="servers",
                            description=f"name\n \n{r}\nid\n\n{w}",
                            color=discord.Color.red()))
    await ctx.message.delete()

@client.command()
async def invite(ctx, server_id: int):
    guild = client.get_guild(server_id)
    invite = await guild.text_channels[0].create_invite(max_age=0,
                                                        max_uses=0,
                                                        temporary=False)
    await ctx.reply(f"https://discord.gg/{invite.code}")
    await ctx.message.delete()

@client.command()
async def short(ctx, *, link):
    response = requests.get(f'https://clck.ru/--?url={link}')
    await ctx.reply(content=f'<{response.text}>')

@client.command(aliases=["bn"])
@commands.has_permissions(ban_members=True)   
async def ban(context, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await context.send(f'{member} banned')


@client.command(aliases=["ub"])
@commands.has_permissions(ban_members=True)   
async def unban(context, id : int):
    user = await client.fetch_user(id)
    await context.guild.unban(user)
    await context.send(f'{user.name} now unbanned')


@client.command(aliases=["p"])
@commands.has_permissions(manage_messages=True)
async def poll(ctx, *, content:str):
  await ctx.channel.purge(limit=1)
  embed=discord.Embed(title="New poll!", description=f"{content}",  color=0x95a5a6)
  message = await ctx.channel.send(embed=embed)
  await message.add_reaction("👍")
  await message.add_reaction("👎")

@client.event
async def on_ready():
    print(f'https://discord.com/api/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot')
  
    client.loop.create_task(status_task())

async def status_task():
    while True:
        await client.change_presence(activity=discord.Streaming(name="!help | caroisgood", url="https://www.twitch.tv/404"))
        await asyncio.sleep(10)

TOKEN = os.environ.get("DISCORD_BOT_SECRET")
client.run(TOKEN)