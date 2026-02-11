"""
State Manager - System State Tracking
Manages current system state, active trades, and session information
"""
from datetime import datetime
from typing import Dict, List, Any


class StateManager:
    """
    Centralized state management for the trading system
    Tracks active trades, system status, and session data
    """
    
    def __init__(self):
        self.active_trades: List[Dict] = []
        self.system_status = "idle"
        self.current_session = None
        self.last_update = datetime.now()
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.trade_count = 0
    
    def add_trade(self, trade: Dict):
        """Add new active trade"""
        trade['timestamp'] = datetime.now()
        trade['id'] = f"TRADE_{self.trade_count + 1}"
        self.active_trades.append(trade)
        self.trade_count += 1
        self.last_update = datetime.now()
    
    def remove_trade(self, trade_id: str):
        """Remove closed trade"""
        self.active_trades = [t for t in self.active_trades if t.get('id') != trade_id]
        self.last_update = datetime.now()
    
    def update_pnl(self, amount: float, daily: bool = True):
        """Update PnL tracking"""
        self.total_pnl += amount
        if daily:
            self.daily_pnl += amount
        self.last_update = datetime.now()
    
    def reset_daily(self):
        """Reset daily counters"""
        self.daily_pnl = 0.0
        self.last_update = datetime.now()
    
    def set_session(self, session: str):
        """Set current trading session"""
        self.current_session = session
        self.last_update = datetime.now()
    
    def get_state(self) -> Dict[str, Any]:
        """Get current system state"""
        return {
            "status": self.system_status,
            "active_trades": len(self.active_trades),
            "current_session": self.current_session,
            "daily_pnl": self.daily_pnl,
            "total_pnl": self.total_pnl,
            "trade_count": self.trade_count,
            "last_update": self.last_update.isoformat()
        }
    
    def get_active_trades(self) -> List[Dict]:
        """Get list of active trades"""
        return self.active_trades.copy()
