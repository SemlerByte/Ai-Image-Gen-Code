import discord
from discord.ext import commands
import aiohttp
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='>', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await update_stats()

async def generate_image(api_url, data) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/sd", json=data) as response:
            image = await response.read()
            return image

async def telegraph_file_upload(file_bytes):
    url = 'https://telegra.ph/upload'
    try:
        data = aiohttp.FormData()
        data.add_field('file', file_bytes, filename='image.png', content_type='image/png')

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response_data = await response.json()
                if response.status == 200 and response_data and isinstance(response_data, list) and 'src' in response_data[0]:
                    telegraph_url = response_data[0]['src']
                    full_url = f'https://telegra.ph{telegraph_url}'
                    print(f"Image uploaded successfully: {full_url}")  # Print the URL to console
                    return full_url
                else:
                    print(f'Unexpected response data or status: {response_data}, Status: {response.status}')
                    return None
    except Exception as e:
        print(f'Error uploading file to Telegraph: {str(e)}')
        return None

@bot.command()
async def imagine(ctx, *, prompt: str):
    generating_embed = discord.Embed(
        title="Generating Image",
        description="Image Is Generating, It takes 30 ~ 50 seconds to generate",
        color=discord.Color.orange()
    )
    message = await ctx.send(embed=generating_embed)

    api_url = "https://visioncraft.top"
    api_key = "api"
    data = {
        "model": "RealVisXLV40Turbo-40",
        "prompt": prompt,
        "token": "api",
    }

    image = await generate_image(api_url, data)
    telegraph_url = await telegraph_file_upload(image)

    if telegraph_url:
        image_embed = discord.Embed(title="Generated Image", color=discord.Color.blue())
        image_embed.set_image(url=telegraph_url)
        await message.edit(content=None, embed=image_embed)
        print(f"Image URL: {telegraph_url}")  # Log the image URL to the console
    else:
        await message.edit(content="Failed to upload image.", embed=None)


bot.run('token')
