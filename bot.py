import pymysql
import os
from dotenv import load_dotenv
from discord import Game
from discord.ext.commands import Bot
from datetime import datetime
import random
import asyncio

load_dotenv('./config.env')

token = os.getenv('TOKEN')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

random.seed(datetime.now())

PREFIX = ("rpg ")

enemies = ['goblin', 'Demogorgon']

def attack_en(enemy):
    choice = random.randint(1,6)
    if(enemy == 'goblin'):
        if choice == 1:
            dmg = random.randint(0,10)
            string = f'The goblin runs around you for a while, you fall and take {dmg} damage.'
            return (dmg,string)
        elif choice == 2:
            dmg = random.randint(20,40)
            string = f'Goblin smacks you on the ground for {dmg}.'
            return (dmg,string)
        elif choice == 3:
            dmg = random.randint(45,65)
            string = f'You have been bamboozled, Goblin steals {dmg} HP.'
            return (dmg,string)
        elif choice == 4:
            string = f'The goblin tries to be sneaky but fails.'
            return (0,string)
        elif choice == 5:
            string = f'You dodged the goblins attack'
            return (0,string)
        elif choice == 6:
            string = f'The goblin was too short to attack you'
            return (0,string)
    else:
        if choice == 1:
            dmg = random.randint(30,45)
            string = f"Since you're no eleven, you take {dmg} damage from the Demogorgen"
            return (dmg,string)
        elif choice == 2:
            dmg = random.randint(0,0)
            string = f"The demogorgon bites your will power, you are sad now."
            return (dmg,string)
        elif choice == 3:
            dmg = random.randint(20,50)
            string = f"The demogorgon sucked your blooded, you managed to escape but incurred {dmg} damage."
            return (dmg,string)
        elif choice == 4:
            string = f'Jim Hopper saved you from the demodog'
            return (0,string)
        elif choice == 5:
            string = f"You dodged the demogorgen's attack"
            return (0,string)
        elif choice == 6:
            string = f"The demogorgen is too tired to attack"
            return (0,string)

def attack_pl():
    choice = random.randint(1,6)
    if choice == 1:
        dmg = random.randint(30,50)
        string = f"You land a hit and do {dmg} damage"
        return (dmg,string)
    elif choice == 2:
        dmg = random.randint(50,65)
        string = f"You became furious and hit the enemy for {dmg} damage"
        return (dmg,string)
    elif choice == 3:
        dmg = random.randint(30,60)
        string = f"You made the enemy hit himself for {dmg} damage"
        return (dmg,string)
    elif choice == 4:
        string = "You missed your attack"
        return (0,string)
    elif choice == 5:
        string = "You fainted and missed a turn"
        return (0,string)
    elif choice == 6:
        string = "You are injured and cant get up"
        return (0,string)

def connect_database():
    connection = pymysql.connect(host=DB_HOST,
                                 user=DB_USER,
                                 password=DB_PASSWORD,
                                 db=DB_NAME,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    print('[*] Connected to database: %s' % DB_NAME)
    return connection

class RpgBot:
    def __init__(self, token):
        self.db = connect_database()
        self.bot = Bot(command_prefix=PREFIX)
        self.bot.remove_command('help')
        self.token = token
        self.prepare_client()

    
    def run(self):
        self.bot.run(self.token)

    def prepare_client(self):
        @self.bot.event
        async def on_ready():
            await self.bot.change_presence(activity=Game(name=" Dungeon Master"))
            print("[*] Connected to Discord as: " + self.bot.user.name)

        @self.bot.event
        async def on_message(message):
            if(message.author.bot):
                return
            self.update_experience_points(message.author, 1)
            self.update_HP(message.author,1)
            await self.bot.process_commands(message)

        @self.bot.command(name = 'help', pass_context=True)
        async def help(context):
            await context.send("""`1. rpg start : Enters the user in database and enables him to play the game
2. rpg stats : Shows the players stats
3. rpg adventure : Single Player adventure mode
4. rpg duel : duel another player on the server`""")

        @self.bot.command(name='stats',
                          description="Get detailed information about your RPG character.",
                          brief="RPG player stats",
                          aliases=['statistics'],
                          pass_context=True)
        async def stats(context):
            player = self.get_player(context.message.author.id)
            await context.send("""`Stats for %s
Experience points: %s
Class: %s
HP: %s`""" % (context.message.author.name, player['xp_points'], player['class'], player['HP']))

        @self.bot.command(pass_context=True)
        async def start(ctx):
            player = ctx.message.author
            await ctx.send("""`Please Choose a Class:
1. ⚔️ Warrior
2. 🏹 Archer
3. 🧙 Mage`""")
            Class = await self.bot.wait_for('message')
            self.add_user_to_db(player,Class.content)
            await ctx.send("Welcome!! new wanderer, you are free to start your adventure")
        
        @self.bot.command(pass_context=True)
        async def duel(ctx):
            first_player = self.get_player(ctx.message.author.id)
            second_player = self.get_player(ctx.message.mentions[0].id)
            player1hp = first_player['HP']
            player2hp = second_player['HP']
            turn = 0
            while player1hp>0 and player2hp>0:
                if(turn == 0):
                    await ctx.send("""`%s choose your weapon`""" % (ctx.message.author.name))
                    await ctx.send("""`1. 🔥 Fire
2. 🔫 Pistol
3. 💉 Syringe
4. 💣 Bomb`""")
                    resp = await self.bot.wait_for('message')
                    if(resp.author == ctx.message.author):
                        (dmg,string) = attack_pl()
                        player2hp-=dmg
                        await ctx.send(string)
                else:
                    await ctx.send("""`%s choose your weapon`""" % (ctx.message.mentions[0].name))
                    await ctx.send("""`1. 🔥 Fire
2. 🔫 Pistol
3. 💉 Syringe
4. 💣 Bomb`""")
                    resp = await self.bot.wait_for('message')
                    if(resp.author == ctx.message.mentions[0]):
                        (dmg,string) = attack_pl()
                        player1hp-=dmg
                        await ctx.send(string)
                await ctx.send("""`%s's HP: %d\n %s's HP: %d`""" %(ctx.message.author.name, max(0,player1hp),ctx.message.mentions[0].name, max(0,player2hp)))
                turn = not turn
                await asyncio.sleep(2)
            player1hp = max(0,player1hp)
            player2hp = max(0,player2hp)
            if player1hp == 0:
                await ctx.send(f"{ctx.message.author.name} You have died, wait for your health to regenerate(health regenerates by 1 each time you send a message")
            if player2hp == 0:
                await ctx.send(f"{ctx.message.mentions[0].name} You have died, wait for your health to regenerate(health regenerates by 1 each time you send a message")
            sql = "UPDATE players SET HP=%s WHERE user_id=%s"
            self.db.cursor().execute(sql, (player1hp, ctx.message.author.id))
            self.db.commit()
            sql = "UPDATE players SET HP=%s WHERE user_id=%s"
            self.db.cursor().execute(sql, (player2hp, ctx.message.mentions[0].name))
            self.db.commit()

        @self.bot.command(pass_context=True)
        async def adventure(ctx):
            player = self.get_player(ctx.message.author.id)
            enemy = enemies[random.randint(0,1)]
            await ctx.send(f"You were exploring a cave when a {enemy} appeared. FIGHT!!!")
            enemy_HP = 100
            player_hp = player['HP']
            turn = 0
            while enemy_HP>0 and player_hp>0:
                if(turn == 0):
                    await ctx.send("""`1. ⚔️ Attack
2. 🏃 Evade`""")
                    resp = await self.bot.wait_for('message')
                    resp = resp.content
                    if resp == "Attack":
                        (dmg,string) = attack_pl()
                        enemy_HP-=dmg
                        await ctx.send(string)
                    elif resp == "Evade":
                        rnd = random.randint(0,1)
                        if rnd == 0:
                            await ctx.send("You tried to evade but failed")
                        else:
                            await ctx.send(f"You evaded the {enemy} and recieved {100-enemy_HP} XP")
                            sql = "UPDATE players SET xp_points=%s WHERE user_id=%s"
                            self.db.cursor().execute(sql, (100-enemy_HP, ctx.message.author.id))
                            self.db.commit()
                            break
                else:
                    (dmg,string) = attack_en(enemy)
                    player_hp-=dmg
                    await ctx.send(string)
                await ctx.send("""`Your HP: %d\n Enemies HP: %d`""" %(max(0,player_hp), max(0,enemy_HP)))
                turn = not turn
                await asyncio.sleep(2)
            player_hp = max(0,player_hp)
            if player_hp == 0:
                await ctx.send("You have died, wait for your health to regenerate(health regenerates by 1 each time you send a message")
            sql = "UPDATE players SET HP=%s WHERE user_id=%s"
            self.db.cursor().execute(sql, (player_hp, ctx.message.author.id))
            self.db.commit()
            if player_hp!=0:
                sql = "UPDATE players SET xp_points=%s WHERE user_id=%s"
                self.db.cursor().execute(sql, (300, ctx.message.author.id))
                self.db.commit()
                await ctx.send("You recieved 300 XP")

    def get_player(self, user_id):
        try:
            with self.db.cursor() as cursor:
                sql = "SELECT `user_id`, `join_server_date`, `xp_points`, `class`, `HP` FROM `players` WHERE `user_id`=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                if not result:
                    print("User does not exist: %s" % user_id)
                else:
                    return result
        except Exception as e:
            print("Error looking up userid %s.\n%s" % (user_id, e))

    def add_all_users_to_db(self):
        for member in self.bot.users:
            print(member)
            self.add_user_to_db(member)

    def add_user_to_db(self, member, Class):
        if self.get_player(member.id):
            return

        try:
            with self.db.cursor() as cursor:
                sql = "INSERT INTO `players` (`user_id`, `join_server_date`, `xp_points`, `class`, `HP`)" + \
                      " VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (member.id, member.joined_at, 0, Class, 100))
            self.db.commit()
            print("Added user %s to database." % member.id)
        except Exception as e:
            print("Error adding user: %s" % e)  

    def update_experience_points(self, member, points):
        player_info = self.get_player(member.id)
        with self.db.cursor() as cursor:
            try:
                sql = "UPDATE players SET xp_points=%s WHERE user_id=%s"
                new_point_value = player_info['xp_points'] + points
                cursor.execute(sql, (new_point_value, member.id))
                self.db.commit()
            except Exception as e:
                print("[-] Error updating xp points for %s; %s" % (member.id, e))
    
    def update_HP(self, member, points):
        player_info = self.get_player(member.id)
        with self.db.cursor() as cursor:
            try:
                sql = "SELECT HP FROM players WHERE user_id=%s"
                cursor.execute(sql,(member.id))
                HP = cursor.fetchone()
                if player_info['HP'] != 100:
                    player_info['HP'] += 1
                    sql = "UPDATE players SET HP=%s WHERE user_id=%s"
                    cursor.execute(sql, (player_info['HP'], member.id))
                    self.db.commit()
                else:
                    pass
            except Exception as e:
                print("[-] Error updating HP points for %s; %s" % (member.id, e))

if __name__ == '__main__':
    bot = RpgBot(token)
    bot.run()