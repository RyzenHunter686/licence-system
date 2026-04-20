import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

class BacktestRunner:
    def __init__(self, symbol="NQ=F", interval="5m", period="30d"):
        self.symbol = symbol
        self.interval = interval
        self.period = period
        self.initial_balance = 5000
        self.risk = 0.01
        self.rr = 2.5
        self.max_trades = 2
        self.DAILY_DD = 0.04 * self.initial_balance
        self.MAX_DD = 0.10 * self.initial_balance

    def run(self):
        data = yf.download(self.symbol, interval=self.interval, period=self.period, progress=False)
        if data is None or data.empty:
            data = yf.download(self.symbol, interval=self.interval, period="15d", progress=False)
        
        if data is None or data.empty:
            return "❌ Data fetch failed", None

        # Clean Data
        data.columns = [str(c) for c in data.columns]
        data['Open'] = data.filter(like='Open').iloc[:, 0]
        data['High'] = data.filter(like='High').iloc[:, 0]
        data['Low'] = data.filter(like='Low').iloc[:, 0]
        data['Close'] = data.filter(like='Close').iloc[:, 0]
        data = data[['Open','High','Low','Close']]

        # Indicators
        data['hour'] = data.index.hour
        data['ny'] = (data['hour'] >= 13) & (data['hour'] <= 16)
        data['body'] = abs(data['Close'] - data['Open'])
        data['avg_body'] = data['body'].rolling(20).mean()
        data['bull'] = (data['Close'] > data['Open']) & (data['body'] > data['avg_body'])
        data['bear'] = (data['Close'] < data['Open']) & (data['body'] > data['avg_body'])
        data['range_size'] = data['High'].rolling(20).max() - data['Low'].rolling(20).min()
        data['avg_range'] = data['range_size'].rolling(20).mean()
        data['is_trending'] = data['range_size'] > data['avg_range']
        data['prev_high'] = data['High'].rolling(10).max().shift(1)
        data['prev_low'] = data['Low'].rolling(10).min().shift(1)
        data['break_high'] = data['High'] > data['prev_high']
        data['break_low'] = data['Low'] < data['prev_low']
        data['sweep_low'] = data['Low'] < data['prev_low']
        data['sweep_high'] = data['High'] > data['prev_high']
        data['tr'] = data['High'] - data['Low']
        data['atr'] = data['tr'].rolling(14).mean()

        # Strategy
        data['buy'] = data['ny'] & (
            (data['is_trending'] & data['break_high'] & data['bull']) |
            (~data['is_trending'] & data['sweep_low'] & data['bull'])
        )
        data['sell'] = data['ny'] & (
            (data['is_trending'] & data['break_low'] & data['bear']) |
            (~data['is_trending'] & data['sweep_high'] & data['bear'])
        )
        data.dropna(inplace=True)

        # Backtest
        balance = self.initial_balance
        balances = [balance]
        current_day = None
        daily_loss = 0
        trades_today = 0
        losses_today = 0
        wins = 0
        losses = 0

        for i in range(len(data)-1):
            day = data.index[i].date()
            if day != current_day:
                current_day = day
                daily_loss = 0
                trades_today = 0
                losses_today = 0

            if balance <= self.initial_balance - self.MAX_DD:
                break
            if daily_loss <= -self.DAILY_DD:
                continue
            if losses_today >= 2:
                continue
            if trades_today >= self.max_trades:
                continue

            if data['buy'].iloc[i] or data['sell'].iloc[i]:
                entry = data['Close'].iloc[i]
                atr = data['atr'].iloc[i]
                if data['buy'].iloc[i]:
                    sl = entry - atr
                    tp = entry + atr * self.rr
                else:
                    sl = entry + atr
                    tp = entry - atr * self.rr
                
                result = None
                for j in range(i+1, min(i+25, len(data))):
                    h = data['High'].iloc[j]
                    l = data['Low'].iloc[j]
                    if data['buy'].iloc[i]:
                        if l <= sl: result = -1; break
                        if h >= tp: result = self.rr; break
                    else:
                        if h >= sl: result = -1; break
                        if l <= tp: result = self.rr; break
                
                if result is not None:
                    pnl = balance * self.risk * result
                    balance += pnl
                    daily_loss += pnl
                    trades_today += 1
                    balances.append(balance)
                    if result > 0: wins += 1
                    else: losses += 1; losses_today += 1

        # Results
        total = wins + losses
        wr = wins / total if total > 0 else 0
        report = (
            f"📊 **Backtest Results**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Final Balance: ${round(balance, 2)}\n"
            f"📈 Total Trades: {total}\n"
            f"✅ Wins: {wins} | ❌ Losses: {losses}\n"
            f"🎯 Win Rate: {round(wr*100,2)}%\n"
            f"📉 ROI: {round(((balance/self.initial_balance)-1)*100, 2)}%"
        )

        # Plot
        plt.figure(figsize=(10, 5))
        plt.plot(balances, marker='o', linestyle='-', color='#00FFCC')
        plt.title(f"Equity Curve - {self.symbol}")
        plt.xlabel("Trade #")
        plt.ylabel("Balance ($)")
        plt.grid(True, alpha=0.3)
        img_path = "equity_curve.png"
        plt.savefig(img_path)
        plt.close()

        return report, img_path
