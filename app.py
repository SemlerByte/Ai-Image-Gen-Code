import discord
from discord.ext import commands
import aiohttp
import asyncio

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='>', intents=intents)

async def generate_image(api_url, data) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/sd", json=data) as response:
            image = await response.read()
            return image

async def telegraph_file_upload(file_bytes):
    url = 'https://telegra.ph/upload'
    try:
        # Use aiohttp's FormData for proper file handling.
        data = aiohttp.FormData()
        data.add_field('file', file_bytes, filename='image.png', content_type='image/png')

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response_data = await response.json()

                # Check if the response contains the expected data
                if response.status == 200 and response_data and isinstance(response_data, list) and 'src' in response_data[0]:
                    telegraph_url = response_data[0]['src']
                    return f'https://telegra.ph{telegraph_url}'
                else:
                    # Log unexpected response structure or status
                    print(f'Unexpected response data or status: {response_data}, Status: {response.status}')
                    return None
    except Exception as e:
        print(f'Error uploading file to Telegraph: {str(e)}')
        return None

@bot.command()
async def imagine(ctx, *, prompt: str):
    # Create an embed for "Image Is Generating"
    generating_embed = discord.Embed(
        title="Generating Image",
        description="Image Is Generating, It takes 30 ~ 50 seconds to generate",
        color=discord.Color.orange()
    )
    message = await ctx.send(embed=generating_embed)

    # Define the API endpoint and token
    api_url = "https://visioncraft.top"
    api_key = "your_api_key_here"

    # Set up the data to send in the request
    data = {
        "model": "RealVisXLV40Turbo-40",
        "prompt": prompt,
        "token": api_key,
    }

    # Generate image asynchronously
    image = await generate_image(api_url, data)
    
    # Upload the image to Telegraph
    telegraph_url = await telegraph_file_upload(image)

    # Update the message with the image embed
    image_embed = discord.Embed(title="Generated Image", color=discord.Color.blue())
    image_embed.set_image(url=telegraph_url)
    await message.edit(content=None, embed=image_embed)

bot.run('your_discord_bot_token_here')
