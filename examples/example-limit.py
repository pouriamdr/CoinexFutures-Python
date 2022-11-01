from ..CoinexFutures import CoinexFutures
import os, time

class MakerBot:
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
        price = float(input('Start price >>'))
        amount = self.coinex.calculateAmount( (budge * basket / 100), price, min_amount, leverage )
        position = self.coinex.openLimit(market, amount, side, price)
        try:
            if 'error' in position:
                if position['error'] != 0:
                    print('[!] Failed to open position: {}'.format(position['message']))
                    return False
        except:
            None
        os.system(self.commands['clear'])
        print('Getting position id...')
        while True:
            time.sleep(1)
            position_id = self.coinex.getPositionId(market)
            if isinstance(position_id, str): # means we got position id which is numerical string and result is not dict(include errors)
                break
        print('Done.')
        print('Position will be open.Position ID: {}\n'.format(position_id))
        command = input('For Cancel enter cancel(or c) or enter target price to close limit >>')
        if command.find('c') != -1:
            cancel = self.coinex.cancelPending(market, 0) # 0 for all pending orders, 1 for short pending orders and 2 for long
            if 'error' in cancel:
                if cancel['error'] != 0:
                    print('[!] Failed to cancel position, pleas cancel it directly from your coinex panel: {}'.format(cancel['message']))
                    return False
            else:
                print('Position cancelled successfully.')
                return False
        price = float(command)
        close_respond = self.coinex.closeLimit(market, position_id, price)
        try:
            if 'error' in close_respond:
                if close_respond['error'] != 0:
                    print('[!] Failed to close position, pleas close it directly from your coinex panel: {}'.format(close_respond['message']))
                    return False
        except:
            None
        print('Done.Position will be close at target price.')

market_obj = MakerBot()
        


