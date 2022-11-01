import requests, time, traceback, hashlib

import warnings
warnings.filterwarnings('ignore')

class CoinexFutures:
    def __init__(self, accessId, secretKey, tries = 10):
        self.access_id = accessId
        self.secret_key = secretKey
        self.tries = 10
        self.urls = {
            "market": "https://api.coinex.com/perpetual/v1/market/deals",
            "klines": "https://api.coinex.com/perpetual/v1/market/kline",
            "open": "https://api.coinex.com/perpetual/v1/order/put_market",
            "close": "https://api.coinex.com/perpetual/v1/position/market_close",
            "assets": "https://api.coinex.com/perpetual/v1/asset/query",
            "leverage": "https://api.coinex.com/perpetual/v1/market/adjust_leverage",
            "position": "https://api.coinex.com/perpetual/v1/position/pending",
            "cancel": "https://api.coinex.com/perpetual/v1/order/cancel_all"
        }
    def merge_two_dicts(self, x, y):
        z = x.copy()   
        z.update(y)    
        return z
    def get_sign(self, params):
        a = '{}&secret_key={}'.format(params, self.secret_key).encode()
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
            "AccessId" : self.access_id,
            "Authorization" : ""
        }
        headers['Authorization'] = hashlib.sha256(a).hexdigest().lower()
        b = params.split('&')
        d = {}
        for f in b:
            j = f.split('=')
            if j[1].isnumeric():
                d[j[0]] = int(j[1])
            elif j[1].find('.') != -1:
                tmp = j[1].split('.')
                if tmp[0].isnumeric() and tmp[1].isnumeric():
                    try:
                        d[j[0]] = float(j[1])
                    except:
                        d[j[0]] = j[1]
                else:
                    d[j[0]] = j[1]
            else:
                d[j[0]] = j[1]
        return (d, headers)
    def getMarketPice(self, market):
        price = 0.0
        tries = 0
        while tries < self.tries:
            tries += 1
            try:
                req = requests.get(self.urls['market'], params={"market":market, "limit": 1}, headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"}, timeout=4).json()
                if 'data' in req:
                    price = float(req['data'][0]['price'])
                    break
            except:
                traceback.print_exc()
            time.sleep(0.2)
        del req
        if price == 0.0:
            return {"error": 1, "message": "Can't stablish connection with coinex"}
        return price
    def getBalance(self):
        tries = 0
        assets = {"error":1,"message":"Can't stablish connection with coinex"}
        while tries < self.tries:
            time.sleep(0.2)
            tries += 1
            try:
                params = 'timestamp={}'.format(int(time.time()*1000))
                params, h = self.get_sign(params)
                req = requests.get(self.urls['assets'], params=params, headers=h, timeout=4)
                if req.status_code != requests.codes.ok:
                    continue
                assets = req.json()
                if int(assets['code']) != 0:
                    continue
                assets = self.merge_two_dicts(assets, {"error":0,"message":""})
                break
            except:
                traceback.print_exc()
        del req
        return assets
    def adjust(self, market, leverage, ptype='isolate'):
        ptype = 1 if ptype == 'isolate' else 2
        tries = 0
        result = {"error": 1, "message": "Can't stablish connection with coinex"}
        while tries < self.tries:
            tries += 1
            try:
                params = 'market={}&leverage={}&position_type={}&timestamp={}'.format(market, leverage, ptype, int(time.time()*1000) )
                params, h = self.get_sign(params)
                req = requests.post(self.urls['leverage'], data=params, headers=h, timeout=4)
                if req.status_code == requests.codes.ok:
                    res = req.json()
                    if int(res['code']) != 0:
                        continue
                    result = {"error": 0, "message": ""}
                    break
            except:
                traceback.print_exc()
        return result
    def getKlines(self, market,timeframe="5min", limit = 1000):
        klines = {"error": 1, "message": "Can't stablish connection with coinex"}
        tries = 0
        while tries < self.tries:
            tries += 1
            try:
                req = requests.get(self.urls['klines'], params={"market":market, "limit": limit, "type": timeframe}, headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"}, timeout=4).json()
                klines = req['data']
                if 'data' in req:
                    break
            except:
                traceback.print_exc()
            time.sleep(0.5)
        del req
        return klines
    def calculateAmount(self, budge, price, min_amount, leverage):
        if str(min_amount).find('.') == -1: # integer type = integer unit
            min_amount = int(min_amount)
            amount = int(float(budge * float(leverage)) / float(price)) - 1
            if amount < min_amount:
                return 0
            else:
                return amount
        else: # float unit like BTC
            min_amount = float(min_amount)
            amount = float(budge * float(leverage)) / float(price)
            amount = str(amount)
            a = str(min_amount).split('.')
            max_float = len(a[1])
            b = amount.split('.')
            amount = b[0] + '.' + b[1][:max_float]
            amount = float(amount)
            if amount < float(min_amount):
                return 0
            else:
                return amount
    def openMarket(self, market, tamount, side):
        side = 2 if side == 'LONG' else 1
        tries = 0
        result = {"error": 1, "message": "Can't stablish connection with coinex"}
        while tries < self.tries:
            tries += 1
            try:
                params = "market={}&side={}&amount={}&timestamp={}".format(
                    market,
                    side,
                    tamount,
                    int(time.time() * 1000)
                )
                data, headers = self.get_sign(params)
                req = requests.post(self.urls['open'], data=data, headers=headers, timeout=4)
                if req.status_code != requests.codes.ok:
                    continue
                res = req.json()
                if 'code' in res:
                    if int(res['code']) == 3109: # not enough balance
                        # print('[!] skip order.[not enough balance]')
                        result['message'] = "Not enough balance"
                        break
                    elif int(res['code']) == 4002: # service timeout
                        # print('[!] re-trying for open order![timeout]')
                        time.sleep(2)
                        continue
                    elif int(res['code']) != 0: # etc
                        # print('[!] re-trying for open order![etc]')
                        time.sleep(0.1)
                        continue
                    elif int(res['code']) == 0:
                        result = {"error": 0, "message": ""}
                        break
            except:
                traceback.print_exc()
        
        if result['error'] == 1:
            return result
        return self.getPositionId(market)
    def openLimit(self, market, tamount, side, tprice):
        side = 2 if side == 'LONG' else 1
        tries = 0
        result = {"error": 1, "message": "Can't stablish connection with coinex"}
        while tries < self.tries:
            tries += 1
            try:
                params = "market={}&side={}&amount={}&price={}&timestamp={}".format(
                    market,
                    side,
                    tamount,
                    tprice,
                    int(time.time() * 1000)
                )
                data, headers = self.get_sign(params)
                req = requests.post(self.urls['open'], data=data, headers=headers, timeout=4)
                if req.status_code != requests.codes.ok:
                    continue
                res = req.json()
                if 'code' in res:
                    if int(res['code']) == 3109: # not enough balance
                        print('[!] skip order.[not enough balance]')
                        result['message'] = "Not enough balance"
                        break
                    elif int(res['code']) == 4002: # service timeout
                        # print('[!] re-trying for open order![timeout]')
                        time.sleep(2)
                        continue
                    elif int(res['code']) != 0: # etc
                        # print('[!] re-trying for open order![etc]')
                        time.sleep(0.1)
                        continue
                    elif int(res['code']) == 0:
                        result = {"error": 0, "message": ""}
                        break
            except:
                traceback.print_exc()
        return result
    def getPositionId(self, market):
        position_id = '0'
        tries = 0
        result = {"error": 1, "message": "Can't stablish connection with coinex"}
        while tries < self.tries:
            time.sleep(0.2)
            tries += 1
            try:
                params = "market={}&timestamp={}".format(market, int(time.time() * 1000) )
                params, h = self.get_sign(params)
                req = requests.get( self.urls['position'], params=params, headers=h, timeout=4)
                if req.status_code != requests.codes.ok:
                    continue
                res = req.json()
                if not 'data' in res:
                    continue
                if 'code' in res:
                    if int(res['code']) != 0:
                        continue
                if len(res['data']) < 1:
                    continue
                position_id = str(res['data'][0]['position_id'])
                break
            except:
                traceback.print_exc()
            time.sleep(0.5)
        if position_id == '0':
            return result
        else:
            return position_id
    def closeAll(self, market, positionId):
        tries = 0
        result = {"error": 1, "message": "Can't stablish connection with coinex"}
        while tries < self.tries:
            time.sleep(0.2)
            tries += 1
            try:
                params = "market={}&position_id={}&timestamp={}".format(
                    market,
                    positionId,
                    int(time.time() * 1000)
                )
                data, headers = self.get_sign(params)
                req = requests.post(self.urls['close'], data=data, headers=headers, timeout=4)
                if req.status_code != requests.codes.ok:
                    continue
                res = req.json()
                if 'code' in res:
                    if int(res['code']) == 3105 or int(res['code']) == 3103: # position closed before
                        result = {"error": 0, "message": "Position closed before"}
                        break
                    elif int(res['code']) != 0:
                        continue
                    elif int(res['code']) == 0:
                        result = {"error": 0, "message": ""}
                        break
            except:
                traceback.print_exc()
            time.sleep(0.1)
        return result
    def closeLimit(self, market, positionId, tprice):
        tries = 0
        result = {"error": 1, "message": "Can't stablish connection with coinex"}
        while tries < self.tries:
            time.sleep(0.2)
            tries += 1
            try:
                params = "market={}&position_id={}&price={}&timestamp={}".format(
                    market,
                    positionId,
                    tprice,
                    int(time.time() * 1000)
                )
                data, headers = self.get_sign(params)
                req = requests.post(self.urls['close'], data=data, headers=headers, timeout=4)
                if req.status_code != requests.codes.ok:
                    continue
                res = req.json()
                if 'code' in res:
                    if int(res['code']) == 3105 or int(res['code']) == 3103: # position closed before
                        result = {"error": 0, "message": "Position closed before"}
                        break
                    elif int(res['code']) != 0:
                        continue
                    elif int(res['code']) == 0:
                        result = {"error": 0, "message": ""}
                        break
            except:
                traceback.print_exc()
            time.sleep(0.1)
        return result
    def getPositionStatus(self, market, positionId):
        tries = 0
        result = {"error": 1, "message": "Can't stablish connection with coinex"}
        req_res = {}
        while tries < self.tries:
            time.sleep(0.2)
            tries += 1
            try:
                params = "market={}&timestamp={}".format(market, int(time.time() * 1000) )
                params, h = self.get_sign(params)
                req = requests.get( self.urls['position'], params=params, headers=h, timeout=4)
                if req.status_code != requests.codes.ok:
                    continue
                res = req.json()
                if not 'data' in res:
                    continue
                if 'code' in res:
                    if int(res['code']) != 0:
                        continue
                if len(res['data']) < 1:
                    continue
                req_res = res
                result = {"error": 0, "message": ""}
                break
            except:
                traceback.print_exc()
            time.sleep(0.5)
        if result['error'] != 0:
            return result
        result['message'] = "Can not find position"
        for pos in req_res['data']:
            if pos['position_id'] == str(positionId):
                result = pos
                break
        return result
    def cancelPending(self, market, side = 0):
        tries = 0
        result = {"error": 1, "message": "Can't stablish connection with coinex"}
        while tries < self.tries:
            time.sleep(0.2)
            tries += 1
            try:
                params = "market={}&side={}&timestamp={}".format(market, side, int(time.time() * 1000) )
                params, h = self.get_sign(params)
                req = requests.get( self.urls['cancel'], params=params, headers=h, timeout=4)
                if req.status_code != requests.codes.ok:
                    continue
                res = req.json()
                if not 'data' in res:
                    continue
                if 'code' in res:
                    if int(res['code']) != 0:
                        continue
                result = {"error": 0, "message": ""}
                break
            except:
                traceback.print_exc()
            time.sleep(0.5)
        return result
        