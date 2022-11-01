from ..CoinexFutures import CoinexFutures
import os

class MarketBot:
    def __init__(self) -> None:
        self.coinex = CoinexFutures('YOUR ACCESSID HERE','YOUR SECRET KEY HERE', 20) # ( access id, secret key, re-tries of connection to coinex in each call )
        self.commands = {'clear': 'clear', 'slash': '/'}
        if os.name == 'nt':
            self.commands = {'clear': 'cls', 'slash': '\\'}
        self.handler()
    def handler(self):
        # Getting ready for open position, you can automate everything or contact me for create any automation
        # - trading bot
        market = input('Market >>').upper() # like BTCUSDT, ETCUSDT ...
        leverage = int(input('Leverage (number 3-100) >>'))
        ptype = input('Isolate or cross (isolate - cross) >>')
        if ptype.find('i') != -1:
            ptype = 'isolate'
        else:
            ptype = 'cross'
        side = input('Long or short (long - short) >>').upper()
        basket = int(input('Percent of balance to use (number 1-100) >>'))
        min_amount = input('Minimum ammount of asset can be trade >>')
        if int(min_amount) == float(min_amount):
            min_amount = int(min_amount)
        else:
            min_amount = float(min_amount)
        
        os.system(self.commands['clear'])
        print('Getting things up... pleas wait.')
        balance = self.coinex.getBalance()
        try:
            if 'error' in balance:
                if balance['error'] != 0:
                    print('[!] Failed to get account balance: {}'.format(balance['message']))
                    return False
        except:
            None
        adjust = self.coinex.adjust(market, leverage, ptype)
        try:
            if 'error' in adjust:
                if adjust['error'] != 0:
                    print('[!] Failed to adjust: {}'.format(adjust['message']))
                    return False
        except:
            None
        budge = float(balance['USDT']['available'])
        print('Done.\n')
        input('Hit enter for start >>')
        amount = self.coinex.calculateAmount( (budge * basket / 100), self.coinex.getMarketPice(market), min_amount, leverage )
        position_id = self.coinex.openMarket(market, amount, side)
        try:
            if 'error' in position_id:
                if position_id['error'] != 0:
                    print('[!] Failed to open position: {}'.format(position_id['message']))
                    return False
        except:
            None
        os.system(self.commands['clear'])
        print('Position has been open.Position ID: {}\n'.format(position_id))
        input('Hit enter for close position >>')
        close_respond = self.coinex.closeAll(market, position_id)
        try:
            if 'error' in close_respond:
                if close_respond['error'] != 0:
                    print('[!] Failed to close position, pleas close it directly from your coinex panel: {}'.format(close_respond['message']))
                    return False
        except:
            None
        print('Done.')

market_obj = MarketBot()
        


