from requests_html import HTMLSession
from random import randint, choice
import discord
import json
import os

#Get the bot's token.
token = os.environ.get("TOKEN")
#Make the bot.
client = discord.Client()
#Make a session to get the questions from either.io.
session = HTMLSession()

#Make a function that saves all of the prefixs.
def save_prefixs():
    global prefixs
    with open("prefixs.json", "w") as f:
        f.write(json.dumps(prefixs))

 #Make a function that load in the prefixs.
def load_prefixs():
    global prefixs
    try:
        with open("prefixs.json", "r") as f:
            prefixs = json.loads((f.read()))
    except:
        prefixs = {}

#Make a function that set the server's prefix to .
def new_prefix(guild):
    global prefixs
    prefixs[str(guild.id)] = "."
    save_prefixs()

#Make a function that saves all of the custom questions.
def save_cwyrs():
    global cwyrs
    with open("cwyrs.json", "w") as f:
        f.write(json.dumps(cwyrs))

#Make a function that load in all of the custom questions.
def load_cwyrs():
    global cwyrs
    try:
        with open("cwyrs.json", "r") as f:
            cwyrs = json.loads((f.read()))
    except:
        cwyrs = {}

#Make a function that grabs a random question from either.io.
def wyr():
    #grabs the source code of a random question 
    r = session.get(f'https://www.either.io/{str(randint(3, 100000))}')

    #Check if there was no errors getting it.
    if r.status_code == 200:
        #Saves the two question. NOTE: Blue is option 1 and red is option 2. It was easier for me to call it blue and red cause thats how the website is formated.
        for count, option in enumerate(r.html.find(".option-text")):
            if count == 0:
                blue = option.text
            elif count == 1:
                red = option.text
        #Saves how many people pick each option.
        for count, option in enumerate(r.html.find(".count")):
            if count == 0:
                blue_count = option.text
            elif count == 1:
                red_count = option.text

         #format the question and responce
        question = f"would you rather {blue} or {red}?"
        responce = f"{blue_count} pick {blue} and {red_count} picked {red}."

        return question, responce

#make a function that make a custom question
def make_cwyrs(blue, red):
    global cwyrs
    id = len(cwyrs)
    cwyrs[str(id)] = [blue, red, 0, 0]
    save_cwyrs()

@client.event
async def on_ready():
    #load in the prefix and custom questions
    load_prefixs()
    load_cwyrs()
    #change the presence to .help for help
    await client.change_presence(activity=discord.Game(name=".help for help"))
    print(f'We have logged in as {client.user}')

@client.event
#when someone joins in, make a prefix for them
async def on_join(guild):
    new_prefix(guild)
    channel = client.get_user(306934440897282050)
    await channel.send(f'I have just join {guild.name} and there are {guild.member_count} people there.')

@client.event
async def on_message(message):
    global prefixs, cwyrs
    try:
        #check to see if the user type in their server's prefix with the command
        if message.content.startswith(f"{prefixs[str(message.guild.id)]}wyr"):
            #saves the channel id, question, and responce
            channel = message.channel
            question, responce = wyr()
            
            #send the question
            await message.channel.send(question)

            #check to see if the user replay and show the user how many people pick each option 
            def check(m):
                return m.channel == channel
            await client.wait_for("message", check=check)
            await message.channel.send(responce)

        elif message.content.startswith(f"{prefixs[str(message.guild.id)]}make cwyr"):
            #separate the questions and save it
            blue = message.content.split(",")[1]
            red = message.content.split(",")[2]
            make_cwyrs(blue, red)
            await message.channel.send(f"Saved the question. Question preview: `Would you rather {blue} or {red}?`")

        elif message.content.startswith(f"{prefixs[str(message.guild.id)]}cwyr"):
            #grabs the info
            id = choice(list(cwyrs.keys()))
            blue = cwyrs[id][0]
            red = cwyrs[id][1]
            blue_status = cwyrs[id][2]
            red_status = cwyrs[id][3]

            #sends  the question to the user
            await message.channel.send(f"Would you rather {red} or {blue}? (type in first for option 1 or second for option 2)?")
            #check to see if they respond back
            def check(m):
                return m.content.lower() == "first" or m.content.lower() == "second"
            msg = await client.wait_for("message", check=check)

            #increase the total count for that option and send the results
            if msg.content.lower() == "first":
                cwyrs[id][2] += 1
                blue_status = cwyrs[id][2]
                save_cwyrs()
            elif msg.content.lower() == "second":
                cwyrs[id][3] += 1
                red_status = cwyrs[id][3]
                save_cwyrs()
            await message.channel.send(f"{blue_status} people picked {blue}, and {red_status} picked {red}")

        elif message.content.startswith(f"{prefixs[str(message.guild.id)]}prefix"):
            #change the prefix for the server
            prefix = message.content.split(" ")[1]
            prefixs[str(message.guild.id)] = prefix
            save_prefixs()
            await message.channel.send(f"Prefix set to `{prefix}`")

        elif message.content.startswith(f"{prefixs[str(message.guild.id)]}help"):
            #shows the help screen
            embed = discord.Embed()
            embed.title = "Commends for wyr bot"
            embed.colour = 0x272727
            embed.image = "logo.png"
            embed.add_field(name = f"{prefixs[str(message.guild.id)]}help", value = "Shows this very lovely help message that tells you all of the commands.")
            embed.add_field(name = f"{prefixs[str(message.guild.id)]}wyr", value = "Grabs a random question from https://either.io and ask you that, then tell the bot that option you pick, and the bot will tell you how many people pick each side.")
            embed.add_field(name = f"{prefixs[str(message.guild.id)]}cwyr", value = "Grabs a custom question that someone made, and shows you how many people pick each option.")
            embed.add_field(name = f"{prefixs[str(message.guild.id)]}make cwyr,<option 1>,<option2>", value = "Make your own custom question. Replace <option 1> and <option 2> with your question. EX: `.make cwyr,lose your arms,lose your legs`.")
            embed.add_field(name = f"{prefixs[str(message.guild.id)]}prefix <new perfix>", value = "Change the prefix of the bot for this server. Replace <new prefix> with the new prefix. EX: `.prefix ,`.")
            embed.add_field(name = f"Upvote the bot.", value = "If you want to help me out, then you can upvote the bot here: https://discordbots.org/bot/572255256927535124/vote")
            embed.add_field(name = f"Source code.", value = "you can find the source code here: https://github.com/glaidtors/Would-You-Rather-Discord-Bot")
            embed.add_field(name = f"Feedback & support.", value = "You can DM me feedback or report bugs @glaidtors#6988, and if you want to support me, you can donate at https://paypal.me/glaidtors412")
            await message.channel.send(content = None, embed = embed)

    except KeyError:
        #the prefix is not defined, so the bot define it for you
        new_prefix(message.guild)
        await message.channel.send("For some reason, the prefix was not set, so I set it to `.`. Please type in the commend in again")
    except Exception as e:
        print(e)

client.run(token)
