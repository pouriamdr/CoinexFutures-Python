from ..CoinexFutures import CoinexFutures
import os, time

class MonitoringBot:
    def __init__(self) -> None:
        self.coinex = CoinexFutures('YOUR ACCESSID HERE','YOUR SECRET KEY HERE', 20) # ( access id, secret key, re-tries of connection to coinex in each call )
        self.commands = {'clear': 'clear', 'slash': '/'}
        if os.name == 'nt':
            self.commands = {'clear': 'cls', 'slash': '\\'}
        self.handler()
    def handler(self):
        market = input('market >>').upper()
        position_id = input('Position id or 0 for skip this >>')
        print('Control + C for break programm.')
        input('Hit enter to start >>')
        os.system(self.commands['clear'])
        while True:
            time.sleep(1)
            os.system(self.commands['clear'])
            ohlc = self.coinex.getKlines(market, "1min", 2)
            if 'error' in ohlc:
                continue
            ohlc = ohlc[-1]
            price = self.coinex.getMarketPice(market)
            try:
                if 'error' in price:
                    continue
            except:
                None
            print('Current Price: ${} \n 1min => O:${} - H:${} - L:${} - C:${}'.format(
                price,
                ohlc[1],
                ohlc[3],
                ohlc[4],
                ohlc[2]
            ))
            if position_id == '0':
                continue
            status = self.coinex.getPositionStatus(market, position_id)
            if 'error' in status:
                if status['error'] != '0':
                    continue
            print('Profit Real: {}%'.format(status['profit_real']))

monitoring_obj = MonitoringBot()
        


