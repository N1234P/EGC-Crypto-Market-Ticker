import asyncio
import requests
import discord

from marketcommand import market
from helper.setup import bot
from helper.formatter import price_formatter
from datetime import datetime

API_KEY = "Q37RXRC1DMTEFIPBU9MTTEGKHI37NVVVXR"
previous_arr, offset = [], 3
CONTRACT, INTERVAL, LIMIT = "0xd254a3c351dad83f8b369554b420047a1ed60f1c", 60, 30
CONTRACT = CONTRACT.lower()
burn_count_prev = 0
BITQUERY = "sign_up on bitquery, graphql ide"
BITQUERY2 = ""

async def get_block_height():
    query = """{
  ethereum(network: bsc) {
    blocks(options: {desc: "height", limit: 1}) {
      timestamp {
        time(format: "%Y-%m-%d %H:%M:%S")
      }
      height
      transactionCount
      address: miner {
        address
        annotation
      }
      reward
      rewardCurrency {
        symbol
      }
    }
  }
}
"""
    headers = {'X-API-KEY': BITQUERY2}

    try:
        json = requests.post('https://graphql.bitquery.io/',
                             json={'query': query}, headers=headers).json()

        return json['data']['ethereum']['blocks'][0]['height'] - 200

    except ValueError:
        await asyncio.sleep(10)
        pass


async def get_blockchain_data():
    global previous_arr
    await bot.wait_until_ready()
    while not bot.is_closed():

        try:
            block = await get_block_height()
            params = {
                'key': 'ckey_76dca41983414ee1a5da0a1fb56',
            }
            print(block)
            json = requests.get("https://api.covalenthq.com/v1/56/address/0xd254a3c351dad83f8b369554b420047a1ed60f1c"
                                "/transfers_v2/?quote-currency=USD&format=JSON&contract-address"
                                "=0xC001BBe2B87079294C63EcE98BdD0a88D761434e&starting-block=" + str(block) + "&key"
                                                                                                             "=ckey_76dca41983414ee1a5da0a1fb56",
                                params=params).json()

            whale = await find_whale(json)
            if len(whale) == 0:
                await asyncio.sleep(INTERVAL)  # nothing has been found, go to sleep

            else:
                print("COMMENCING WHALE RELEASE")
                await output_whale_data(whale)
                print("whale info released :)")
                await asyncio.sleep(INTERVAL)
        except Exception as e:
            print(e)
            await asyncio.sleep(10)
            pass  # api returned an error, loop until api gives result


async def find_whale(transfers):
    global previous_arr

    transfers = transfers['data']['items']
    whale = []

    for i, t in enumerate(transfers):

        if i == LIMIT:

            break

        t = t['transfers'][0]
        amount = t['delta']

        ind = 11 - (20 - len(str(amount)))

        if ind >= len(str(amount)) or ind < 1:
            pass

        elif int(str(amount)[:ind]) >= 20000000000 and t['tx_hash'] not in previous_arr:
            previous_arr.append(t['tx_hash'])
            whale.append("https://bscscan.com/tx/" + t['tx_hash'])
            whale.append(str(amount)[:ind])

            if t['from_address'].lower() == CONTRACT:
                transfer_type = "WHALE BUY"
                address = t['to_address']
            elif t['to_address'].lower() == CONTRACT:
                transfer_type = "WHALE SELL"
                address = t['from_address']
            else:
                transfer_type = "???"
                address = t['from_address'] + "->" + t['to_address']

            whale.append(address)
            whale.append(transfer_type)
            whale.append(t['block_signed_at'])
            break
    return whale


async def output_whale_data(whale):
    whale = list(map(str, whale))

    price = str(await market.get_price())

    bal = await get_whale_balance(whale[2])

    bal = price_formatter(bal)

    if whale[3] == "WHALE BUY":
        em = discord.Embed(title="🐳 WHALE BUY 🐳", colour=discord.Colour.green())
        em.add_field(name="Exchange", value="PancakeSwap")
        em.add_field(name="Whale Address", value=whale[2])
        em.add_field(name="Tokens Bought", value=price_formatter(whale[1]) + " EGC")


    elif whale[3] == "WHALE SELL":
        em = discord.Embed(title="🐳 WHALE SELL 🐳", colour=discord.Colour.red())
        em.add_field(name="Exchange", value="PancakeSwap")
        em.add_field(name="Whale Address", value=whale[2])
        em.add_field(name="Tokens Sold", value=price_formatter(whale[1]) + " EGC")

    else:
        em = discord.Embed(title="🐳 WHALE TRANSFER 🐳", colour=discord.Colour.dark_blue())
        em.add_field(name="Exchange", value="???")
        em.add_field(name="Whale Address", value=whale[2])
        em.add_field(name="Tokens Moved", value=price_formatter(whale[1]) + " EGC")

    em.add_field(name="USD Equivalent", value="$" + price_formatter(float(whale[1]) * float(price)))
    em.add_field(name="Current Token Balance", value=bal + " EGC")
    em.add_field(name="Hash Link", value=whale[0])
    em.add_field(name="Timestamp (UTC)", value=whale[4])
    em.set_footer(text="data retrieved by the blockchain, testing phase")

    channel = bot.get_channel(896653155310383104)
    await channel.send(embed=em)


async def get_whale_balance(balance):
    try:
        json = requests.get("https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress"
                            "=0xc001bbe2b87079294c63ece98bdd0a88d761434e&address=" + str(balance) +
                            "&tag=latest&apikey=" + API_KEY).json()
        ind = 11 - (20 - len(str(json.get('result'))))

        if ind >= len(str(json['result'])) or ind < 1:
            return str(json['result'])

        return str(json['result'][:ind])


    except:
        return ""


async def init_buy_back_burn():
    global burn_count_prev
    burn_count_prev = float(await market.buy_back_burn())


async def track_buy_back_burn():
    global burn_count_prev

    await bot.wait_until_ready()
    await init_buy_back_burn()

    while not bot.is_closed():
        await asyncio.sleep(600)
        burn_curr = await market.buy_back_burn()
        if burn_curr != "":
            burn_curr = float(burn_curr)
            if burn_curr < burn_count_prev:
                bbb_amount = burn_count_prev - burn_curr

                em = discord.Embed(title="BUY BACK AND BURN DETECTED", colour=discord.Colour.orange())
                em.add_field(name="Amount", value=str(bbb_amount) + " BNB")
                em.add_field(name="Remaining Buy Back & Burn", value=str(burn_curr))

                em.set_footer(text="total of last 10 minutes + (" + str(datetime.now()) + ")")
                channel = bot.get_channel(896653155310383104)
                await channel.send(embed=em)

            burn_count_prev = burn_curr
