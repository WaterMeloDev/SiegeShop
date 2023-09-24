import discord
import asyncio
from discord.ext import commands
from discord import app_commands
import json

order_LIST_FILE = 'src/data/userOrder.json'
ITEMS_PER_PAGE = 3

try:
    with open("src/data/bad_words.txt") as file:
        bad_words = {bad_word.strip().lower() for bad_word in file}
except Exception as e:
    print(f"Error loading bad words: {e}")
    bad_words = set()

mod_team_ids = []  # add user IDs of the mod team

# Function to load the order list from a JSON file
def load_order_list():
    try:
        with open(order_LIST_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("order list file not found!")
        return []

order_list = load_order_list()

# Function to save the order list to a JSON file
def save_order_list():
    with open(order_LIST_FILE, 'w') as f:
        json.dump(order_list, f, indent=4)

class orderListCmd(commands.Cog):
    def __init__(self, client):
        self.client = client
    
        # Function to check if a reaction is valid for pagination
    def check(self, reaction, user):
        return user != self.client.user and str(reaction.emoji) in ["▶️", "◀️"]
    

    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded order.py!")

    # Command to add an item to the order list
    @app_commands.command(name="order", description="Orders an items")
    @app_commands.choices(choices=[
        app_commands.Choice(name="Mosin-Nagant", value="gun1"),
        app_commands.Choice(name="Lee-Enfield", value="gun2"),
        app_commands.Choice(name="Mannlicher M1895", value="gun3"),
        app_commands.Choice(name="Springfield M1903", value="gun4"),
        app_commands.Choice(name="Gewehr 98", value="gun5"),
        app_commands.Choice(name="Mosin-Nagant M44", value="gun6"),
        app_commands.Choice(name="Carcano M91", value="gun7"),
        app_commands.Choice(name="Chauchat", value="gun8"),
        app_commands.Choice(name="BAR M1918", value="gun9"),
        app_commands.Choice(name="Madsen", value="gun10"),
        app_commands.Choice(name="Lewis Gun", value="gun11"),
        app_commands.Choice(name="MP 18", value="gun12"),
        ])
    async def order(self, interaction: discord.Interaction, choices: app_commands.Choice[str], amount: int):
            if (choices.value == 'gun1'):
                try:
                    price = amount * 50
                    order_list.append({'item': choices.name, 'amount': amount, 'price': price, 'user': str(interaction.user.id)})  # Store user ID
                    save_order_list()

                    order_embed = discord.Embed(
                        title='📝 Order #Unknown',
                        description=f'Item: **{choices.name}**\nAmount: **{amount}**\n\nPrice: **${price}.00**\n*MC command: /pay WaterMeloDev {price}*',
                        color=0x5865F2
                    )

                    embed = discord.Embed(
                        title='📝 New item Added to order List',
                        description=f'Item: **{choices.name}**\nAmount: **{amount}**\nDiscord User: **{interaction.user}**',
                        color=0x5865F2
                    )

                    channel = self.client.get_channel(1155600913768132659)
                    scavs = '1155600913768132659'

                    await interaction.response.send_message(embed=order_embed, ephemeral=True)

                    await channel.send(f"<@&{scavs}>", embed=embed)
                except Exception as e:
                    print(f"Error: {e}")

    @app_commands.command(name="remove", description="Removes an item from the order list")
    async def remove(self, interaction: discord.Interaction, index: int):
        if 0 <= index < len(order_list):
            item = order_list[index]
            user_id = int(item['user'])

            if interaction.user.id == user_id or interaction.user.id in mod_team_ids:
                removed_item = order_list.pop(index)
                save_order_list()
                user = self.client.get_user(user_id)
                user_name = str(user) if user else 'Unknown User'

                embed = discord.Embed(
                    title='🗑️ Removed Item from Order List',
                    description=f'Removed "{removed_item["item"]}" from your order list. Added by: {user_name}.',
                    color=0x5865F2
                )
                await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                embed = discord.Embed(
                    title='🚫 Permission Denied',
                    description='You do not have permission to remove this item.',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title='❌ Invalid Index',
                description='The provided index is not valid.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


    # Command to list items in the order list with pagination
    @app_commands.command(name="order_list", description="Shows the entire order list")
    async def list_order(self, interaction: discord.Interaction, page: int = 1):
        await interaction.response.defer()
        start_idx = (page - 1) * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        items_to_display = order_list[start_idx:end_idx]

        if not items_to_display:
            await interaction.followup.send('This page is empty.')
            return

        pages = (len(order_list) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

        embed = discord.Embed(title='📋 Order List', description=f'Page {page}/{pages}', color=0x5865F2)
        
        def check(reaction, user):
            return user == interaction.user and str(reaction.emoji) in ["◀️", "▶️"]
        
        try:
            for index, item_data in enumerate(items_to_display, start=start_idx + 1):
                item = item_data['item']
                price = item_data['price']
                user_id = int(item_data['user'])
                user = self.client.get_user(user_id)
                user_name = str(user) if user else 'Unknown User'
                embed.add_field(name=f'{index}. {item}', value=f'Price: ${price}.00\nAdded by: {user_name}', inline=False)
        except Exception as e:
            print(f"Error: {e}")

        message = await interaction.followup.send(embed=embed)
        await message.add_reaction('◀️')
        await message.add_reaction('▶️')
        
        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == "▶️":
                    page += 1
                elif str(reaction.emoji) == "◀️":
                    page -= 1

                if page > pages:
                    page = 1 
                elif page < 1:
                    page = pages

                start_idx = (page - 1) * ITEMS_PER_PAGE
                end_idx = start_idx + ITEMS_PER_PAGE
                items_to_display = order_list[start_idx:end_idx]
                embed.clear_fields()
                embed.description = f'Page {page}/{pages}'
                
                for index, item_data in enumerate(items_to_display, start=start_idx + 1):
                    item = item_data['item']
                    price = item_data['price']
                    user_id = int(item_data['user'])
                    user = self.client.get_user(user_id)
                    user_name = str(user) if user else 'Unknown User'
                    embed.add_field(name=f'{index}. {item}', value=f'Price: ${price}.00\nAdded by: {user_name}', inline=False)

                await message.edit(embed=embed)
                await message.remove_reaction(reaction, user)
                
            except asyncio.TimeoutError:
                await message.delete()
                break


async def setup(client):
    await client.add_cog(orderListCmd(client))