import discord
import os
import requests
import json
import random
from replit import db

client = discord.Client()
Discord = os.getenv('DISCORD_TOKEN')
Tenor = os.getenv('TENOR_TOKEN')

sad_words = ["sad", "depressed", "unhappy", "miserable", "angry", "depressing"]

default_encouragements = [
  "That's rough but you can do it!",
  "Believe in yourself and your day will be brighter.",
  "This feeling won't last forever."
]

#get quotes from zenquotes api
def get_quote():
  response = requests.get('https://zenquotes.io/api/random')
  json_data = json.loads(response.text)
  quote = json_data[0]['q']
  author = "  -" + json_data[0]['a']
  #json_data = json.dumps(json_data, sort_keys=True, indent=4) 
  #print(json_data)
  return quote + author

#get gifs from tenor api
def get_gif():
  response = requests.get("https://api.tenor.com/v1/random?q=%s&key=%s&limit=%s&contentfilter=%s" % ("hug", Tenor, 2, "off"))
  if response.status_code == 200:
    json_gif = json.loads(response.content)
    gif = json_gif["results"][0]["media"][0]["gif"]["url"]
    #gif = json.dumps(gif, sort_keys=True, indent=4)
    return(gif)

#get humorous trump quotes from api
def get_trump():
  response = requests.get("https://api.whatdoestrumpthink.com/api/v1/quotes/random")
  json_data = json.loads(response.text)
  trump = json_data["message"]
  return trump

#add your own encouragements to database
def add_encouragement(msg):
  if "encouragements" in db.keys():
    encouragements = db["encouragements"]
    encouragements.append(msg)
    db["encouragements"] = encouragements
  else:
    db["encouragements"] = [msg]

#delete encouragements from database
def delete_encouragement(index):
  encouragements = db["encouragements"]
  if len(encouragements) > index:
    del encouragements[index]
    db["encouragements"] = encouragements

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

  @client.event
  async def on_message(message):
    if message.author == client.user:
      return

    if message.content.startswith('$inspire'):
      quote = get_quote()
      await message.channel.send(quote)
    
    if message.content.startswith('!hug'):
        gif = get_gif()
        await message.channel.send(gif)

    if message.content.startswith("!trump"):
      trump = get_trump()
      await message.channel.send(trump)
        
    options = default_encouragements
    if "encouragements" in db.keys():
      options = options + db["encouragements"]
    
    #adds options to user and commands to access
    if any(word in message.content for word in sad_words):
      await message.channel.send(random.choice(options) + "\ntext '!hug' if you'd like a hug. \ntext '!trump' for something maybe funny")

    if message.content.startswith('$add'):
      msg = message.content.split("$add ",1)[1]
      add_encouragement(msg)
      await message.channel.send("New encouraging message added")

    if message.content.startswith('$del'):
      encouragements = []
      if "encouragements" in db.keys():
        index = message.split("$del",1)[1]
        delete_encouragement(index)
        encouragements = db["encouragements"]
        await message.channel.send(encouragements)

    if message.content.startswith('!del'):
      await message.channel.purge(check=None, bulk=False)
    
client.run(Discord)