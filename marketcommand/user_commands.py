import discord

from marketcommand import market
from helper.formatter import embedder
from helper.formatter import price_formatter


async def cmds(message):


    if "$p" in message.content and not "$pos" in message.content:
        price = await market.get_price()
        if await validate(message, price):
            await message.channel.send(embed=embedder("Price", "$"  + price + " (cmd)"))

    elif "$bnb" in message.content:
        bnb = await market.get_bnb_price()
        if await validate(message, bnb):
            await message.channel.send(embed=embedder("BNB Price", "$" + str(bnb)))

    elif "$vol" in message.content:
        vol = await market.get_volume()
        if await validate(message, vol):
            vol = price_formatter(vol)
            await message.channel.send(embed=embedder("Volume", "$" + vol).set_footer(text="retrieved by coingecko"))

    elif "$mc" in message.content:
        mc = await market.get_marketcap()
        if await validate(message, mc):
            mc = price_formatter(mc)
            await message.channel.send(embed=embedder("Marketcap", "$" + mc))

    elif "$bbb" in message.content:
        bbb = await market.buy_back_burn()
        if await validate(message, bbb):
            bbb = price_formatter(bbb)
            await message.channel.send(embed=embedder("Buy Back and Burn Amount", bbb + " BNB"))

    elif "$lq" in message.content:
        bnb_lq, usd_lq = await market.get_liquidity()
        if await validate(message, bnb_lq):
            bnb_lq = price_formatter(bnb_lq)
            usd_lq = price_formatter(usd_lq)
            await message.channel.send(embed=embedder("Liquidity", "BNB: " + bnb_lq + "\n($" + usd_lq + ")"))

    elif "$%" in message.content:
        percent = await market.get_percent_change()
        if await validate(message, percent):
            await message.channel.send(embed=embedder("24HR Percent Change", str(percent) + "%").set_footer(text="retrieved by coingecko"))

    elif "$supply" in message.content:
        supply, bw = await market.get_supply()
        if await validate(message, bw):
            bw, supply = price_formatter(bw), price_formatter(supply)
            await message.channel.send(embed=embedder("Supply & Burn Wallet Size", "Supply: " + supply + " tokens\nBurn Wallet: " + bw + " tokens"))

    elif "$holders" in message.content:
        holders = await market.get_holders()
        if await validate(message, holders):
            await message.channel.send(embed=embedder("Total Holders", holders))

    elif "$pos" in message.content:
        data = await market.get_holder_position(message.content)
        if(len(data)) == 1:
            await message.channel.send(embed=embedder("Error", data[0]))
        else:
            await message.channel.send(embed=embedder("Wallet Position " + message.content.split()[1], "Address: " + data[0] + "\nBalance: " + price_formatter(data[1]) + " tokens"))





async def validate(message, args):
    if args == "" or args == None:
            await message.channel.send(embed=embedder("Error", "EMPTY STRING RETURNED, try again ):"))
            return False
    return True


async def chart_posting(ctx):
    price = await market.get_price()
    vol = await market.get_volume()
    mc = await market.get_marketcap()
    supply, bw = await market.get_supply()
    percent = await market.get_percent_change()
    bbb = await market.buy_back_burn()

    bnb_lq, usd_lq = await market.get_liquidity()

    data = [price, vol, mc, supply, percent, bbb, bnb_lq, usd_lq]


    if all(data[i] != None and data[i] != "" for i in range(len(data))):


        em = discord.Embed(title="🔥 All Stats 🔥", colour=discord.Colour.purple())
        em.add_field(name="Price 💸", value="$" + price)
        em.add_field(name="Volume 📢", value="$" + price_formatter(vol))
        em.add_field(name="MarketCap 🏛️", value="$" + price_formatter(mc))
        em.add_field(name="Supply", value=price_formatter(supply) + " Tokens")
        em.add_field(name="Burn Wallet Size", value=price_formatter(bw) + " Tokens")
        em.add_field(name="24HR Percent Change 📈", value=str(percent) + "%")
        em.add_field(name="Buy Back & Burn Amount", value=str(bbb) + " BNB")
        em.add_field(name="Liquidity 🌊", value=price_formatter(bnb_lq) + " BNB ($" + price_formatter(usd_lq) + ")")
        await ctx.send(embed=em)