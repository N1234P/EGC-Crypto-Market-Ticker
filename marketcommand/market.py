import requests
import pandas as pd

API_KEY = "Q37RXRC1DMTEFIPBU9MTTEGKHI37NVVVXR"


async def get_price():
    API_KEY = "MJYCR4Q2Z98ZDHTWAMFFCTJXTEKEDPKFQQ"

    try:
        bnb_lq = requests.get("https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress"
                              "=0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c&address"
                              "=0xd254a3c351dad83f8b369554b420047a1ed60f1c"
                              "&tag=latest&apikey=" + API_KEY).json()

        bnb_lq = bnb_lq['result'][:len(str(bnb_lq['result'])) - 18]

        egc_bnb_lq = requests.get("https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress"
                                  "=0xC001BBe2B87079294C63EcE98BdD0a88D761434e&address"
                                  "=0xd254a3c351dad83f8b369554b420047a1ed60f1c"
                                  "&tag=latest&apikey=" + API_KEY).json()['result']

        ind = 11 - (20 - len(str(egc_bnb_lq)))

        egc_bnb_lq = egc_bnb_lq[:ind]

        price = (float(bnb_lq) / float(egc_bnb_lq)) * float(await get_bnb_price())

        return "{:.10f}".format(price)

    except ValueError:
        return ""


async def get_volume():
    try:
        json = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=evergrowcoin&order=market_cap_desc"
            "&per_page=100&page=1&sparkline=false").json()
        return json[0]['total_volume']
    except:
        return None


async def get_percent_change():
    try:
        json = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=evergrowcoin&order=market_cap_desc"
            "&per_page=100&page=1&sparkline=false").json()
        return json[0]['price_change_percentage_24h']
    except:
        return None


async def get_liquidity():
    t = "https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress=0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c&address=0xD254a3C351DAd83F8B369554B420047A1ED60f1C&tag=latest&apikey=Q37RXRC1DMTEFIPBU9MTTEGKHI37NVVVXR"
    try:
        bnb = requests.get("https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress"
                           "=0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c&address"
                           "=0xD254a3C351DAd83F8B369554B420047A1ED60f1C"
                           "&tag=latest&apikey=" + API_KEY).json()

        bnb = bnb['result'][:len(str(bnb['result'])) - 18]
        usd = float(bnb) * await get_bnb_price()
        return bnb, usd
    except:
        return "", ""


async def get_supply():
    try:
        json = requests.get("https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress"
                            "=0xc001bbe2b87079294c63ece98bdd0a88d761434e&address=0x000000000000000000000000000000000000dead"
                            "&tag=latest&apikey=" + API_KEY).json()
        ind = 11 - (20 - len(str(json.get('result'))))
        bw = json['result'][:ind]

        return 1000000000000000 - float(bw), float(bw)
    except:
        return "", ""


async def get_marketcap():
    try:
        supply, unused = await get_supply()
        price = float(await get_price())
        return supply * price
    except:
        return ""


async def get_bnb_price():
    try:
        json = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=binancecoin&order=market_cap_desc&per_page=100&page=1&sparkline=false").json()
    except:
        return ""
    return json[0]['current_price']


async def buy_back_burn():
    try:
        json = requests.get("https://api.bscscan.com/api?module=account&action=balance&address"
                            "=0xc001bbe2b87079294c63ece98bdd0a88d761434e"
                            "&tag=latest&apikey=" + API_KEY).json()

    except:
        return ""

    return json['result'][:len(json['result']) - 18]


async def get_holders():
    params = {
        'key': 'ckey_76dca41983414ee1a5da0a1fb56',

    }
    url = "https://api.covalenthq.com/v1/56/tokens/0xc001bbe2b87079294c63ece98bdd0a88d761434e/token_holders/"

    try:
        json = requests.get(url, params=params).json()
    except:
        return ""

    return json['data']['pagination']['total_count']


async def get_holder_position(args):

    if len(args.split()) < 2:
        return ["specify a position number!"]

    df = pd.read_excel('EGC Holders.xlsx')
    bal = df['EGC Balances (SORTED)'].tolist()
    bal = bal[:len(bal) - 8]
    addr = df['Wallet Addresses'].tolist()
    addr = addr[:len(addr) - 8]


    pos = args.split()[1]
    if pos.isnumeric():
        pos = int(pos)
        if pos >= len(bal) or pos < 1:
            return ["position out of bounds!"]
        else:
            return [str(addr[pos]), str(bal[pos])]
    else:
        return ["invalid argument"]