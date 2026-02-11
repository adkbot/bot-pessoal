"""
Trade Journal - Trade History and Analysis
Records all trades for review and analysis
"""
from datetime import datetime
import json
import os


class TradeJournal:
    """
    Maintains detailed trade journal with:
    - Entry/exit details
    - Performance metrics
    - Market context
    - Lessons learned
    """
    
    def __init__(self, journal_file="memory/trade_journal.json"):
        self.journal_file = journal_file
        self.trades = self._load_journal()
    
    def _load_journal(self) -> list:
        """Load existing journal"""
        if os.path.exists(self.journal_file):
            try:
                with open(self.journal_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_journal(self):
        """Save journal to file"""
        os.makedirs(os.path.dirname(self.journal_file), exist_ok=True)
        with open(self.journal_file, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, indent=2, ensure_ascii=False)
    
    def log_trade(self, platform: str, symbol: str, side: str, 
                  entry_price: float, quantity: float, 
                  stop_loss: float = None, take_profit: float = None,
                  notes: str = "") -> str:
        """
        Log new trade
        
        Returns:
            str: Trade ID
        """
        trade_id = f"TRADE_{len(self.trades) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        trade = {
            "trade_id": trade_id,
            "platform": platform,
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "quantity": quantity,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "entry_time": datetime.now().isoformat(),
            "exit_time": None,
            "exit_price": None,
            "pnl": None,
            "pnl_percentage": None,
            "status": "open",
            "notes": notes
        }
        
        self.trades.append(trade)
        self._save_journal()
        
        print(f"📝 Journal: Logged trade {trade_id}")
        return trade_id
    
    def close_trade(self, trade_id: str, exit_price: float, notes: str = ""):
        """Close trade and calculate PnL"""
        trade = self._find_trade(trade_id)
        
        if not trade:
            print(f"❌ Journal: Trade {trade_id} not found")
            return
        
        trade["exit_time"] = datetime.now().isoformat()
        trade["exit_price"] = exit_price
        trade["status"] = "closed"
        
        # Calculate PnL
        if trade["side"] == "BUY":
            pnl_pct = (exit_price - trade["entry_price"]) / trade["entry_price"]
        else:  # SELL
            pnl_pct = (trade["entry_price"] - exit_price) / trade["entry_price"]
        
        trade["pnl_percentage"] = pnl_pct * 100
        trade["pnl"] = pnl_pct * trade["entry_price"] * trade["quantity"]
        
        if notes:
            trade["notes"] += f"\nExit: {notes}"
        
        self._save_journal()
        
        result = "WIN" if pnl_pct > 0 else "LOSS"
        print(f"📝 Journal: Closed {trade_id} - {result} {pnl_pct*100:.2f}%")
    
    def _find_trade(self, trade_id: str) -> dict:
        """Find trade by ID"""
        for trade in self.trades:
            if trade["trade_id"] == trade_id:
                return trade
        return None
    
    def get_open_trades(self) -> list:
        """Get all open trades"""
        return [t for t in self.trades if t["status"] == "open"]
    
    def get_closed_trades(self, limit: int = None) -> list:
        """Get closed trades"""
        closed = [t for t in self.trades if t["status"] == "closed"]
        if limit:
            return closed[-limit:]
        return closed
    
    def get_trade_stats(self) -> dict:
        """Get trade statistics"""
        closed = self.get_closed_trades()
        
        if not closed:
            return {"total_trades": 0, "win_rate": 0.0}
        
        wins = sum(1 for t in closed if t.get("pnl_percentage", 0) > 0)
        total = len(closed)
        
        avg_win = sum(t["pnl_percentage"] for t in closed if t.get("pnl_percentage", 0) > 0) / max(wins, 1)
        avg_loss = sum(t["pnl_percentage"] for t in closed if t.get("pnl_percentage", 0) < 0) / max(total - wins, 1)
        
        return {
            "total_trades": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": (wins / total) * 100,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": abs(avg_win / avg_loss) if avg_loss != 0 else 0
        }
