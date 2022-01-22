import asyncio

from marketcommand import user_commands
from helper.setup import bot

from time import sleep
from marketcommand import market
from helper.formatter import embedder
from whales.whalewatcher import get_blockchain_data
from whales.whalewatcher import track_buy_back_burn



TOKEN_AUTH = "OTM0MzE5NDc2MTk3OTgyMjU4.YeuW0Q.GNOYrE48ZDpw-SlqnhMcjI-szzg"


sleep(30)


@bot.event
async def on_ready():
    print("bot is ready...")


@bot.event
async def on_message(message):
    await user_commands.cmds(message)


async def price_update():
    countdown, refresher = 0, 240
    await bot.wait_until_ready()

    channel = bot.get_channel(896653155310383104)

    while not bot.is_closed():
        price = await market.get_price()

        if price != "" and price != None:
            await channel.send(embed=embedder("Price", "$" + price))
            await asyncio.sleep(60)

        if countdown == 0:
            # display all stats every 3 mins

            await user_commands.chart_posting(channel)
            countdown = 6

        if refresher == 0:

            sleep(30)
            refresher = 240

        countdown -= 1
        refresher -= 1


bot.loop.create_task(price_update())
bot.loop.create_task(get_blockchain_data())
bot.loop.create_task(track_buy_back_burn())
bot.run(TOKEN_AUTH)