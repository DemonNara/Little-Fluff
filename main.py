import json
import discord
from discord.ext import commands
from cogs.events import Events
from cogs.fun import Fun
from cogs.admin import Admin
from tasks import reminder_loop

with open("config.json") as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=config["prefix"],
    intents=intents
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    reminder_loop.start(bot)

bot.add_cog(Events(bot))
bot.add_cog(Fun(bot))
bot.add_cog(Admin(bot))






# Initialize the bot with intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


#Welcome message Hello/Goodbye

# Welcome messages
welcome_messages = [
    "Welcome, traveler! Prepare yourself for an adventure filled with terrible puns and questionable memes!",
    "Welcome to the madhouse! We've been expecting you... well, maybe not you specifically, but definitely someone like you.",
    "Greetings, human! Please ignore the chaos, it's a feature, not a bug.",
    "Welcome to the server! Where the rules are made up, and the points don't matter!",
    "Ahoy there! Welcome aboard our virtual ship! Just remember, we only have imaginary life jackets."
]

# Goodbye messages
goodbye_messages = [
    "Farewell, dear friend! May the memes be ever in your favor as you venture into the wilds of the internet.",
    "Goodbye, brave soul! Remember, you're leaving behind a void that can only be filled with more cat videos.",
    "Adieu, mon ami! Parting is such sweet sorrow... or so they say. We'll probably forget about you in 5 minutes.",
    "So long, and thanks for all the fish memes! Don't worry, we'll still be here, drowning in them.",
    "Auf Wiedersehen! Remember, you're always welcome back... until we forget who you are and ban you by mistake."
]

@bot.event
async def on_ready():
    print('Bot is ready.')

@bot.event
async def on_member_join(member):
    # Get a random welcome message
    welcome_message = random.choice(welcome_messages)
    # Get the welcome channel
    channel = bot.get_channel(1248875518951161896)  # Replace with your welcome channel ID
    
    if channel:
        embed = discord.Embed(
            title="Welcome!",
            description=f"{welcome_message} Hello {member.mention}, welcome to **{member.guild.name}**!",
            color=discord.Color.green()
        )
        embed.add_field(name="Getting Started", value="Be sure to check out the rules and introduce yourself.")
        embed.add_field(name="Need Help?", value="Feel free to ask any questions you may have in the help channel.")
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text="We're glad to have you here!")
        
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    # Get a random goodbye message
    goodbye_message = random.choice(goodbye_messages)
    # Get the goodbye channel
    channel = bot.get_channel(1248875708344963175)  # Replace with your goodbye channel ID
    
    if channel:
        embed = discord.Embed(
            title="Goodbye!",
            description=f"{goodbye_message} Goodbye {member.mention}. We're sad to see you go from **{member.guild.name}**.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text="We hope to see you again!")
        
        await channel.send(embed=embed)

#alerts section 
@bot.command(name='setalert')
async def set_alert(ctx, time: int, *, message: str):
    alert_time = time
    alert_message = message
    alerts.append((alert_time, alert_message, ctx.channel.id, ctx.author.id))
    await ctx.send(f'Alert set for {alert_time} seconds!')

@tasks.loop(seconds=1.0)
async def check_alerts():
    current_time = int(asyncio.get_event_loop().time())
    for alert in alerts[:]:
        alert_time, alert_message, channel_id, user_id = alert
        if current_time >= alert_time:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(f'<@{user_id}>: {alert_message}')
            alerts.remove(alert)
            
            
#reminder system
@bot.command(name='setreminder')
async def set_reminder(ctx, time: str, *, message: str):
    reminder_time = parse_time(time)
    if reminder_time is None:
        await ctx.send("Invalid time format. Use '1h30m' for 1 hour 30 minutes.")
        return

    reminder = {
        "time": reminder_time.timestamp(),
        "message": message,
        "channel_id": ctx.channel.id,
        "user_id": ctx.author.id
    }
    reminders.append(reminder)
    await save_reminders()
    await ctx.send(f'Reminder set for {time}!')

@tasks.loop(seconds=60.0)
async def check_reminders():
    current_time = datetime.now().timestamp()
    for reminder in reminders[:]:
        if current_time >= reminder['time']:
            channel = bot.get_channel(reminder['channel_id'])
            if channel:
                await channel.send(f'<@{reminder["user_id"]}>: {reminder["message"]}')
            reminders.remove(reminder)
            await save_reminders()

async def save_reminders():
    async with aiofiles.open('reminders.json', 'w') as f:
        await f.write(json.dumps(reminders))

async def load_reminders():
    try:
        async with aiofiles.open('reminders.json', 'r') as f:
            data = await f.read()
            global reminders
            reminders = json.loads(data)
    except FileNotFoundError:
        pass

def parse_time(time_str):
    try:
        time_dict = {'h': 0, 'm': 0, 's': 0}
        for unit in ['h', 'm', 's']:
            if unit in time_str:
                value = int(time_str.split(unit)[0].split()[-1])
                time_dict[unit] = value
                time_str = time_str.split(unit)[1]
        return datetime.now() + timedelta(hours=time_dict['h'], minutes=time_dict['m'], seconds=time_dict['s'])
    except ValueError:
        return None

# Currency System
class CurrencySystem:
    def __init__(self):
        self.users = {}

    def add_money(self, user_id, amount):
        if user_id not in self.users:
            self.users[user_id] = {'balance': 0, 'achievements': []}
        self.users[user_id]['balance'] += amount

    def get_money(self, user_id):
        return self.users.get(user_id, {}).get('balance', 0)

    def add_achievement(self, user_id, achievement):
        if user_id not in self.users:
            self.users[user_id] = {'balance': 0, 'achievements': []}
        if achievement not in self.users[user_id]['achievements']:
            self.users[user_id]['achievements'].append(achievement)

currency = CurrencySystem()


def update_user_balance(user_id, amount):
    user = get_user_data(user_id)
    if 'balance' not in user:
        user['balance'] = 0
    user['balance'] += amount
    save_user_data(user_id, user)

def get_user_balance(user_id):
    user = get_user_data(user_id)
    return user.get('balance', 0)

def transfer_balance(from_user_id, to_user_id, amount):
    from_user = get_user_data(from_user_id)
    to_user = get_user_data(to_user_id)
    if from_user.get('balance', 0) >= amount:
        from_user['balance'] -= amount
        if 'balance' not in to_user:
            to_user['balance'] = 0
        to_user['balance'] += amount
        save_user_data(from_user_id, from_user)
        save_user_data(to_user_id, to_user)


# Achievements
achievements = {
    'first_work': 'You worked for the first time!',
    'first_balance': 'You checked your balance for the first time!',
    'first_flip': 'You flipped a coin for the first time!',
    'first_roll': 'You rolled a dice for the first time!',
    'first_8ball': 'You asked the magic 8-ball for the first time!',
    'first_meme': 'You looked at a meme for the first time!',
    'first_slap': 'You slapped someone for the first time!',
    'first_hug': 'You hugged someone for the first time!',
    'first_pat': 'You patted someone on the head for the first time!',
    'first_cat': 'You looked at a cat picture for the first time!',
    'first_dog': 'You looked at a dog picture for the first time!',
    'first_compliment': 'You complimented someone for the first time!',
    'first_insult': 'You insulted someone for the first time!',
    'first_choose': 'You used the choose command for the first time!',
    'first_joke': 'You heard a joke for the first time!',
    'first_reverse': 'You reversed text for the first time!',
    'first_say': 'You echoed a message for the first time!'
}

def award_achievement(user_id, achievement):
    achievement_ref = ref.child('users').child(str(user_id)).child('achievements').push()
    achievement_ref.set({
        'achievement': achievement,
        'timestamp': int(time.time())
    })

def get_user_achievements(user_id):
    achievement_ref = ref.child('users').child(str(user_id)).child('achievements')
    achievements = achievement_ref.order_by_child('timestamp').get()
    return achievements


# Fetch a random meme from an API
async def fetch_meme():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://meme-api.com/gimme/memes') as response:
            data = await response.json()
            return data['url']

# Fetch a daily quote from an API
async def fetch_daily_quote():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://zenquotes.io/api/random') as response:
            data = await response.json()
            if data:
                quote = data[0]
                return f"{quote['q']} - {quote['a']}"
            return "No quote available today."

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    daily_quote.start()

# Daily Quote Task
@tasks.loop(hours=24)
async def daily_quote():
    quote = await fetch_daily_quote()
    channel = bot.get_channel(1241004787990925382)  # Replace YOUR_CHANNEL_ID with the ID of the channel you want to send the quote to
    if channel:
        await channel.send(f"🍦 **Daily Ice Cream**: {quote}")

# Command: Work
@bot.command(description="Earn some coins by working.")
async def work(ctx):
    earnings = random.randint(1, 100)
    currency.add_money(ctx.author.id, earnings)
    await ctx.send(f"You worked and earned {earnings} coins!")
    currency.add_achievement(ctx.author.id, 'first_work')

# Command: Balance
@bot.command(description="Check your balance.")
async def balance(ctx):
    user_balance = currency.get_money(ctx.author.id)
    await ctx.send(f"Your balance is {user_balance} coins!")
    currency.add_achievement(ctx.author.id, 'first_balance')

# Command: Flip a Coin
@bot.command(description="Flip a coin.")
async def flip(ctx):
    result = random.choice(['Heads', 'Tails'])
    await ctx.send(f"The coin landed on {result}!")
    currency.add_achievement(ctx.author.id, 'first_flip')

# Command: Roll a Dice
@bot.command(description="Roll a dice.")
async def roll(ctx):
    result = random.randint(1, 6)
    await ctx.send(f"You rolled a {result}!")
    currency.add_achievement(ctx.author.id, 'first_roll')

# Command: Magic 8 Ball
@bot.command(name="8ball", description="Ask the magic 8-ball a question.")
async def _8ball(ctx, *, question: str):
    responses = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes, definitely.",
                 "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.",
                 "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
                 "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
                 "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.",
                 "Very doubtful."]
    await ctx.send(f"Question: {question}\nAnswer: {random.choice(responses)}")
    currency.add_achievement(ctx.author.id, 'first_8ball')

# Command: Meme
@bot.command(description="Get a random meme.")
async def meme(ctx):
    meme_url = await fetch_meme()
    await ctx.send(meme_url)
    currency.add_achievement(ctx.author.id, 'first_meme')

# Command: Slap a user
@bot.command(name="slap", description="Slap a user.")
async def slap(ctx, user: discord.Member = None):
    if user is None:
        await ctx.send("Please mention a user to slap.")
        return
    await ctx.send(f"{ctx.author.name} slapped {user.name}!")
    currency.add_achievement(ctx.author.id, 'first_slap')

# Command: Spank a user
@bot.command(name="spank", description="Spank a user.")
async def spank(ctx, user: discord.Member = None):
    if user is None:
        await ctx.send("Please mention a user to spank.")
        return
    await ctx.send(f"{ctx.author.name} spanked {user.name}!")
    currency.add_achievement(ctx.author.id, 'first_spank')

# Command: Hug
@bot.command(description="Hug a user.")
async def hug(ctx, user: discord.Member):
    await ctx.send(f"{ctx.author.name} gave {user.name} a hug!")
    currency.add_achievement(ctx.author.id, 'first_hug')

# Command: Pat
@bot.command(description="Pat a user on the head.")
async def pat(ctx, user: discord.Member):
    await ctx.send(f"{ctx.author.name} patted {user.name} on the head!")
    currency.add_achievement(ctx.author.id, 'first_pat')

# Command: Cat
@bot.command(description="Get a random cat picture.")
async def cat(ctx):
    api_url = 'https://api.thecatapi.com/v1/images/search'  # Correct API endpoint
    api_key = 'live_Zb9z4as4LOYq0QYCTFqA3aMUtKPXnJ6s5CL97ut1Phu90WIRg7KoSp8EvMNYSMLA'
    
    headers = {
        'x-api-key': api_key  # Use headers to include the API key
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()  # data should be a list
                    if data:  # Ensure data is not empty
                        cat_url = data[0]['url']  # Correctly access the URL from the response
                        await ctx.send(cat_url)
                        currency.add_achievement(ctx.author.id, 'first_cat')
                    else:
                        await ctx.send("No data received from the cat API.")
                else:
                    await ctx.send("Could not fetch a cat picture at the moment. Please try again later.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

# Command: Dog
@bot.command(description="Get a random dog picture.")
async def dog(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://random.dog/woof.json') as response:
            if response.status == 200:
                data = await response.json()
                await ctx.send(data['url'])
    currency.add_achievement(ctx.author.id, 'first_dog')

# Command: Compliment
@bot.command(description="Compliment a user.")
async def compliment(ctx, user: discord.Member):
    compliments = ["You're an awesome friend.", "You're a gift to those around you.",
                   "You're a smart cookie.", "You are awesome!"]
    await ctx.send(f"{ctx.author.name} says to {user.name}: {random.choice(compliments)}")
    currency.add_achievement(ctx.author.id, 'first_compliment')

# Command: Insult
@bot.command(description="Insult a user.")
async def insult(ctx, user: discord.Member):
    insults = ["You're as sharp as a marble.", "You're a few fries short of a Happy Meal.",
               "You're a few sandwiches short of a picnic."]
    await ctx.send(f"{ctx.author.name} says to {user.name}: {random.choice(insults)}")
    currency.add_achievement(ctx.author.id, 'first_insult')

# Command: Choose
@bot.command(description="Choose between multiple options.")
async def choose(ctx, *choices):
    await ctx.send(f"I choose: {random.choice(choices)}")
    currency.add_achievement(ctx.author.id, 'first_choose')

# Command: Joke
@bot.command(description="Tell a joke.")
async def joke(ctx):
    jokes = ["Why don't scientists trust atoms? Because they make up everything.",
             "Why did the scarecrow win an award? Because he was outstanding in his field."]
    await ctx.send(random.choice(jokes))
    currency.add_achievement(ctx.author.id, 'first_joke')

# Command: Reverse
@bot.command(description="Reverse the text.")
async def reverse(ctx, *, text: str):
    reversed_text = text[::-1]
    await ctx.send(reversed_text)
    currency.add_achievement(ctx.author.id, 'first_reverse')

# Command: Say
@bot.command(description="Echo the user's message.")
async def say(ctx, *, message: str):
    await ctx.send(message)
    currency.add_achievement(ctx.author.id, 'first_say')

# # # # Hogwarts Themed Commands # # # #

# Command: House Sorting
@bot.command(description="Get sorted into a Hogwarts house.")
async def sortme(ctx):
    house = random.choice(['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin'])
    await ctx.send(f"{ctx.author.mention}, you have been sorted into {house}!")

# Command: Spell Casting
spells = [
    {'name': 'Expelliarmus', 'effect': 'disarms your opponent'},
    {'name': 'Lumos', 'effect': 'lights up the tip of your wand'},
    {'name': 'Avada Kedavra', 'effect': 'causes instant death'}
]

@bot.command(description="Cast a spell.")
async def cast(ctx, *, spell_name: str):
    spell = next((s for s in spells if s['name'].lower() == spell_name.lower()), None)
    if spell:
        await ctx.send(f"{ctx.author.mention} casts {spell['name']}! Effect: {spell['effect']}.")
    else:
        await ctx.send(f"{ctx.author.mention}, that's not a valid spell.")

# Command: Brew Potion
potions = [
    {'name': 'Polyjuice Potion', 'ingredients': ['Lacewing flies', 'Leeches', 'Powdered Bicorn horn']},
    {'name': 'Felix Felicis', 'ingredients': ['Ashwinder egg', 'Squill bulb', 'Murtlap tentacle']}
]

@bot.command(description="Brew a potion.")
async def brew(ctx, *, potion_name: str):
    potion = next((p for p in potions if p['name'].lower() == potion_name.lower()), None)
    if potion:
        ingredients = ', '.join(potion['ingredients'])
        await ctx.send(f"To brew {potion['name']}, you need: {ingredients}.")
    else:
        await ctx.send(f"{ctx.author.mention}, that's not a valid potion.")

# Command: Quidditch Match Simulation
teams = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin']

@bot.command(description="Simulate a Quidditch match.")
async def quidditch(ctx):
    team1, team2 = random.sample(teams, 2)
    score1 = random.randint(50, 200)
    score2 = random.randint(50, 200)
    await ctx.send(f"Today's Quidditch match result:\n{team1}: {score1}\n{team2}: {score2}")

# Command: Horcrux Hunt
horcruxes = [
    "Tom Riddle's Diary", "Marvolo Gaunt's Ring", "Salazar Slytherin's Locket",
    "Helga Hufflepuff's Cup", "Rowena Ravenclaw's Diadem", "Harry Potter", "Nagini"
]

@bot.command(description="Hunt for a Horcrux.")
async def horcruxhunt(ctx):
    found_horcrux = random.choice(horcruxes)
    await ctx.send(f"{ctx.author.mention}, you found a Horcrux! It is {found_horcrux}.")

# Command: Polyjuice - Changes user nickname for a set period of time
polyjuice_names = [
    "Aberforth Dumbledore", "Abernathy", "Adrian Pucey", "Alastor Moody", 
    "Albus Dumbledore", "Alecto Carrow", "Alicia Spinnet", "Amos Diggory", 
    "Amycus Carrow", "Andromeda Tonks", "Angelina Johnson", "Arabella Figg", 
    "Argus Filch", "Ariana Dumbledore", "Arthur Weasley", "Augusta Longbottom", 
    "Aunt Petunia Dursley", "Avery", "Bartemius Crouch Jr.", "Bartemius Crouch Sr.", 
    "Bellatrix Lestrange", "Bill Weasley", "Binky", "Blaise Zabini", 
    "Cedric Diggory", "Charity Burbage", "Charlie Weasley", "Cho Chang", 
    "Colin Creevey", "Corban Yaxley", "Cormac McLaggen", "Cornelius Fudge", 
    "Daphne Greengrass", "Dean Thomas", "Dedalus Diggle", "Dennis Creevey", 
    "Dipsy", "Dirk Cresswell", "Dobby", "Dolores Umbridge", "Dorcas Meadowes", 
    "Draco Malfoy", "Dudley Dursley", "Eileen Prince", "Elizabeth Spriggs", 
    "Eloise Midgen", "Elphias Doge", "Emmeline Vance", "Ernie Macmillan", 
    "Ernie Prang", "Fabian Prewett", "Fang", "Fenrir Greyback", 
    "Filius Flitwick", "Firenze", "Fleur Delacour", "Florean Fortescue", 
    "Frank Longbottom", "Fred Weasley", "Gabrielle Delacour", "Garrick Ollivander", 
    "Gellert Grindelwald", "George Weasley", "Gibbon", "Gideon Prewett", 
    "Gilderoy Lockhart", "Ginny Weasley", "Grawp", "Gregory Goyle Jr.", 
    "Godric Gryffindor", "Gregory Goyle Sr.", "Griphook", "Groot", 
    "Harry Potter", "Helga Hufflepuff", "Hepzibah Smith", "Hermione Granger", 
    "Hokey", "Horace Slughorn", "Irma Pince", "Jacob Kowalski", 
    "James Potter", "Jimmy Peakes", "Justin Finch-Fletchley", "Katie Bell", 
    "Kendra Dumbledore", "Kingsley Shacklebolt", "Kreacher", "Laa-Laa", 
    "Lavender Brown", "Lee Jordan", "Lily Potter", "Lucius Malfoy", 
    "Luna Lovegood", "Mad-Eye Moody", "Madam Malkin", "Malcolm", 
    "Marcus Belby", "Marge Dursley", "Marjorie Cattermole", "Marvolo Gaunt", 
    "Mary Cattermole", "Merope Gaunt", "Millicent Bagnold", "Millicent Bulstrode", 
    "Minerva McGonagall", "Moaning Myrtle", "Moira Quirrell", "Molly Weasley", 
    "Mrs. Norris", "Mundungus Fletcher", "Nagini", "Narcissa Malfoy", 
    "Nearly Headless Nick", "Neville Longbottom", "Newt Scamander", "Norbert", 
    "Nymphadora Tonks", "Oliver Wood", "Padma Patil", "Pansy Parkinson", 
    "Parvati Patil", "Peeves", "Percy Weasley", "Phineas Nigellus Black", 
    "Piers Polkiss", "Po", "Pomona Sprout", "Quirinus Quirrell", 
    "Reg Cattermole", "Regulus Black", "Remus Lupin", "Rita Skeeter", 
    "Romilda Vane", "Ron Weasley", "Rowena Ravenclaw", "Rufus Scrimgeour", 
    "Salazar Slytherin", "Seamus Finnigan", "Septima Vector", "Severus Snape", 
    "Sirius Black", "Sturgis Podmore", "Sybill Trelawney", "Ted Tonks", 
    "Tinky-Winky", "The Sorting Hat", "Tom the barman", "Tom Riddle", 
    "Viktor Krum", "Vincent Crabbe Jr.", "Vincent Crabbe Sr.", "Voldemort", 
    "Walden Macnair", "Wilhelmina Grubbly-Plank", "Wilkie Twycross", 
    "Winky", "Xenophilius Lovegood", "Zacharias Smith"
]

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"The Polyjuice Potion is still brewing. Please wait {round(error.retry_after)} seconds before trying again.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to run this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide all the required arguments.")
    else:
        await ctx.send("An error occurred while executing the command.")

@bot.command(description="Transform using Polyjuice Potion.")
@commands.cooldown(1, 600, commands.BucketType.user)  # 600 seconds = 10 minutes
async def polyjuice(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    await transform(ctx, member)

async def transform(ctx, member: discord.Member):
    # Check if the bot has the manage nicknames permission
    if not ctx.guild.me.guild_permissions.manage_nicknames:
        return await ctx.send("I don't have permission to manage nicknames.")

    # Check if there are names loaded from the list
    if not polyjuice_names:
        return await ctx.send("Failed to load names for Polyjuice Potion.")

    # Randomly choose a name from the list
    random_name = random.choice(polyjuice_names)

    # Store original display name
    original_name = member.display_name

    try:
        # Change nickname to random_name
        await member.edit(nick=random_name)
        await ctx.send(f"{member.mention}, you have transformed into {random_name}!")

        # Wait for 5 minutes (300 seconds)
        await asyncio.sleep(300)

        # Restore original display name
        await member.edit(nick=original_name)
        await ctx.send(f"{member.mention} has transformed back to their original self.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to change the member's nickname.")
    except Exception as e:
        await ctx.send("Failed to change nickname.")
        print(f"Failed to change nickname: {e}")

# Command: Trivia
trivia_questions = [
    {'question': "What is the name of Harry Potter's pet owl?", 'answer': 'Hedwig'},
    {'question': "Who is the Half-Blood Prince?", 'answer': 'Severus Snape'}
]

@bot.command(description="Answer a Harry Potter trivia question.")
async def trivia(ctx):
    question = random.choice(trivia_questions)
    await ctx.send(f"Trivia question: {question['question']}")

    def check(m):
        return m.author == ctx.author and m.content.lower() == question['answer'].lower()

    try:
        answer = await bot.wait_for('message', check=check, timeout=15)
        await ctx.send(f"Correct answer, {ctx.author.mention}!")
    except asyncio.TimeoutError:
        await ctx.send(f"Time's up! The correct answer was {question['answer']}.")

# Command: Marauder's Map
@bot.command(description="Reveal your join date.")
async def map(ctx):
    await ctx.send(f"Mischief managed, {ctx.author.mention}. You joined on {ctx.author.joined_at}.")


# # # # ADMIN CODE SECTION # # # #

# Command: Kick
@bot.command(description="Kick a member from the server.")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} has been kicked.')

# Command: Ban
@bot.command(description="Ban a member from the server.")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned.')

# Command: Unban
@bot.command(description="Unban a member from the server.")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} has been unbanned.')
            return
    await ctx.send(f'Member {member} not found in ban list.')

# Command: Clear
@bot.command(description="Clear a number of messages from the channel.")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'{amount} messages cleared.', delete_after=5)

# Command: Change Nickname
@bot.command(description="Change a member's nickname.")
@commands.has_permissions(manage_nicknames=True)
async def changenick(ctx, member: discord.Member, *, new_nick):
    await member.edit(nick=new_nick)
    await ctx.send(f"{member.mention}'s nickname has been changed to {new_nick}.")

# Command: Create a new role
@bot.command(description="Create a new role in the server.")
@commands.has_permissions(manage_roles=True)
async def create_role(ctx, role_name):
    guild = ctx.guild
    await guild.create_role(name=role_name)
    await ctx.send(f"Role '{role_name}' created successfully.")

# Command: Assign a role to a member
@bot.command(description="Assign a role to a member.")
@commands.has_permissions(manage_roles=True)
async def assign_role(ctx, member: discord.Member, role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        await member.add_roles(role)
        await ctx.send(f"Role '{role_name}' assigned to {member.display_name}.")
    else:
        await ctx.send(f"Role '{role_name}' not found.")

# Command: Create a new text channel
@bot.command(description="Create a new text channel in the server.")
@commands.has_permissions(manage_channels=True)
async def create_channel(ctx, channel_name):
    guild = ctx.guild
    await guild.create_text_channel(channel_name)
    await ctx.send(f"Channel '{channel_name}' created successfully.")

# Command: Configure server settings (dummy function)
@bot.command(description="Configure server settings.")
@commands.has_permissions(administrator=True)
async def configure_server(ctx):
    # Dummy function, replace with your actual configuration logic
    await ctx.send("Server configured successfully.")

def log_infraction(user_id, infraction):
    infraction_ref = ref.child('users').child(str(user_id)).child('infractions').push()
    infraction_ref.set({
        'infraction': infraction,
        'timestamp': int(time.time())
    })

def get_user_infractions(user_id):
    infraction_ref = ref.child('users').child(str(user_id)).child('infractions')
    infractions = infraction_ref.order_by_child('timestamp').get()
    return infractions



# Initialize logger
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Events
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}')

@bot.event
async def on_command(ctx):
    logger.info(f'Command "{ctx.message.content}" executed by {ctx.author} in {ctx.guild}.')

# Admin Log Command
@commands.has_permissions(administrator=True)
@bot.command(description="Create a stats channel and log the creation attempt.")
async def create_stats_channel(ctx):
    guild = ctx.guild

    # Log the creation attempt
    logger.info(f'Creating stats channel in {guild.name} by {ctx.author}.')

    # Attempt to get the stats channel
    stats_channel = discord.utils.get(guild.text_channels, name="server-stats")

    if stats_channel:
        # Stats channel already exists
        logger.info(f'Stats channel already exists in {guild.name}.')
        await ctx.send("Stats channel already exists.")
    else:
        # Stats channel does not exist, create it
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                discord.utils.get(guild.roles, name="Admin"): discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            stats_channel = await guild.create_text_channel('server-stats', overwrites=overwrites)
            logger.info(f'Stats channel created successfully in {guild.name}.')
            await ctx.send("Stats channel created successfully.")
        except Exception as e:
            logger.error(f'Failed to create stats channel in {guild.name}: {e}')
            await ctx.send("Failed to create stats channel.")

config = {}
userData = {}

ref = db.reference()

def load_config():
    global config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: 'config.json' file not found. Please make sure it exists in the same directory as the script.")
        exit(1)

def get_user_data(user_id):
    user_ref = ref.child('users').child(str(user_id))
    user = user_ref.get()
    if not user:
        user = {'xp': 0, 'level': 1}
        user_ref.set(user)
    return user

def save_user_data(user_id, data):
    user_ref = ref.child('users').child(str(user_id))
    user_ref.update(data)

def add_user_xp(user_id, xp_to_add):
    user = get_user_data(user_id)
    user['xp'] += xp_to_add
    save_user_data(user_id, user)

def get_xp_needed_for_level(level):
    # Placeholder formula for XP needed to level up
    return level * 100

async def display_leaderboard(message):
    users_ref = ref.child('users')
    users = users_ref.order_by_child('level').get()
    sorted_users = sorted(users.items(), key=lambda x: x[1]['level'], reverse=True)

    leaderboard = 'Leaderboard:\n'
    for i, (user_id, data) in enumerate(sorted_users[:10]):
        level = data['level']
        leaderboard += f"{i + 1}. <@{user_id}> - Level {level}\n"

    await message.channel.send(leaderboard)

async def handle_message(message):
    if message.author.bot or isinstance(message.channel, discord.DMChannel):
        return

    xp_to_add = random.randint(1, 10)
    if '.gif' in message.content or '.gifv' in message.content:
        xp_to_add *= 2
    add_user_xp(message.author.id, xp_to_add)

    user = get_user_data(message.author.id)
    current_level = user['level']
    xp_needed = get_xp_needed_for_level(current_level + 1)
    if user['xp'] >= xp_needed:
        user['level'] += 1
        user['xp'] -= xp_needed  # Subtract the needed XP for the next level up
        save_user_data(message.author.id, user)
        await message.channel.send(f"{message.author.mention}, congratulations! You leveled up to level {user['level']}!")
        # Add level-up rewards here
    else:
        save_user_data(message.author.id, user)

    if message.content.startswith(config['prefix']):
        args = message.content[len(config['prefix']):].strip().split()
        command = args.pop(0).lower()

        if command == 'leaderboard':
            await display_leaderboard(message)

class MyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await handle_message(message)

def run_bot():
    load_config()
    load_user_data()
    intents = discord.Intents.default()
    intents.messages = True

    bot = commands.Bot(command_prefix=config.get('prefix', '!'), intents=intents)
    bot.add_cog(MyBot(bot))
    bot.run(config.get('token'))  # Make sure the token is in your config.json

#bot backup
    #Command to backup the database
@bot.command(description="Backup the database.")
@commands.has_permissions(administrator=True)
async def backup_db(ctx):
    backup_file = 'bot_backup.db'
    try:
        shutil.copy('bot.db', backup_file)
        await ctx.send(f"Database backup created successfully: {backup_file}")
    except Exception as e:
        await ctx.send(f"Error creating backup: {e}")

# Command to restore the database from a backup
@bot.command(description="Restore the database from a backup.")
@commands.has_permissions(administrator=True)
async def restore_db(ctx, backup_file: str):
    try:
        shutil.copy(backup_file, 'bot.db')
        await ctx.send(f"Database restored successfully from: {backup_file}")
    except Exception as e:
        await ctx.send(f"Error restoring database: {e}")

    @client.event
    async def on_ready():
        print('Bot is online!')

    @client.event
    async def on_message(message):
        await handle_message(message)

    client.run(config['token'])




# cmd.die run = True #910
 