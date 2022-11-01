# CoinexFutures-Python
This is Coinex(Futures) cryptocurrency exchange library.<br>
Some methods included and listed blow:<br>
<ul>
  <li>
  getMarketPice: get latest dealed(excution) price in market.
  </li>
  <li>
  getBalance: get balance of future account's wallet.
  </li>
  <li>
  adjust: set leverage and position type(isolated or cross margin).
  </li>
  <li>
  getKlines: get last up to 1000 klines in diferrent time frames.
  </li>
  <li>
  calculateAmount: calculate amount before open position.
  </li>
  <li>
  openMarket: open order( also returns position id ) in market price( always latest excution is matter ).
  </li>
  <li>
  openLimit: open order( must get position id with below method ) in given target price.
  </li>
  <li>
  getPositionId: get position id after opening a limit order.
  </li>
  <li>
  closeAll: close order( needs position id taken in open method or getPositionId method) in market price but as a limit close!
  </li>
  <li>
  closeLimit: close order( needs position id taken in open method or getPositionId method) in given target price.
  </li>
  <li>
   getPositionStatus: get position details such as amount of position,  unreal profit etc...
  </li>
  <li>
  cancelPending: cancel pending order(s) of an asset.
  </li>
</ul>

Note: if you have an open position, you can use another openMarket/openLimit in same direction( if main position was long, open another long ) for add amount to
 your position or you can use another openMarket/openLimit in opposite direction( if main position was long, open short ) for sell some amount of your position.
 <br>
 <h3>How to use/install:</h3>
Download library file, put in same dir with your project and import it in your project like this:
<br>
<code>
from .CoinexFutures import CoinexFutures
</code>
<br>
Or clone source code in your project.
<br>
<h3>How to use:</h3>
<br>
Simple example of openning order:
<br>

```python

from .CoinexFutures import CoinexFutures
import sys
coinex = CoinexFutures( "Your AccessID", "Your SecretKey" )
market = "BTCUSDT"
leverage = 10
minimum_amount = 0.0005
adjust_res = coinex.adjust(market, leverage)
if 'error' in adjust_res:
  if adjust_res['error'] != 0:
    print('[!] Failed to adjust position: {}'.format(adjust_res['message']) )
    sys.exit(0)
balanceUsdt = coinex.getBalance()['USDT']['available']
currentPrice = coinex.getMarketPrice(market)
amount = coinex.calculateAmount(balanceUsdt, currentPrice, minimum_amount, leverage)
feedback = coinex.openMarket(market, amount, 'LONG')
if 'error' in feedback:
  if feedback['error'] != 0: # means failed to open position
    print('[!] Failed to open position: {}'.format(feedback['message']) )
    sys.exit(0)
positionId = feedback['positionId']

```

<br>
Simple example of closing position:
<br>

```python

.
.
.
status = coinex.getPositionStatus(market, positionId)
if 'error' in status:
  if status['error'] != 0: # means having trouble for getting position status
    print('[!] Failed to get position status: {}'.format(status['message']) )
    sys.exit(0)
if float(status['profit_pnl']) >= 15.0: # means this position is 15% in profit at least.
  print('[+] Closing position with {}% profits.'.format(status['profit_pnl']))
  res = coinex.closeAll(market, positionId)
  print(res['message'])
  
```

<br>
Also check examples in repo files.
<br>
<hr>
As soon as posible i'll share this library to pypi for install easier using pip.
