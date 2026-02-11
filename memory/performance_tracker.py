"""
Performance Tracker - Real-time Performance Metrics
Tracks system performance and trading statistics
"""
from datetime import datetime, timedelta
import json
import os


class PerformanceTracker:
    """
    Tracks performance metrics:
    - Daily/weekly/monthly PnL
    - Win rate and profit factor
    - Drawdown tracking
    - System uptime
    """
    
    def __init__(self, metrics_file="memory/performance_metrics.json"):
        self.metrics_file = metrics_file
        self.metrics = self._load_metrics()
        self.session_start = datetime.now()
    
    def _load_metrics(self) -> dict:
        """Load existing metrics"""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._init_metrics()
        return self._init_metrics()
    
    def _init_metrics(self) -> dict:
        """Initialize metrics structure"""
        return {
            "total_pnl": 0.0,
            "daily_pnl": {},
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "current_drawdown": 0.0,
            "best_trade": 0.0,
            "worst_trade": 0.0,
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_metrics(self):
        """Save metrics to file"""
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        self.metrics["last_updated"] = datetime.now().isoformat()
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2)
    
    def record_trade(self, pnl_percentage: float):
        """Record trade result"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Update total PnL
        self.metrics["total_pnl"] += pnl_percentage
        
        # Update daily PnL
        if today not in self.metrics["daily_pnl"]:
            self.metrics["daily_pnl"][today] = 0.0
        self.metrics["daily_pnl"][today] += pnl_percentage
        
        # Update trade counts
        self.metrics["total_trades"] += 1
        
        if pnl_percentage > 0:
            self.metrics["wins"] += 1
            if pnl_percentage > self.metrics["best_trade"]:
                self.metrics["best_trade"] = pnl_percentage
        else:
            self.metrics["losses"] += 1
            if pnl_percentage < self.metrics["worst_trade"]:
                self.metrics["worst_trade"] = pnl_percentage
        
        # Update win rate
        self.metrics["win_rate"] = (self.metrics["wins"] / self.metrics["total_trades"]) * 100
        
        # Update drawdown
        if pnl_percentage < 0:
            self.metrics["current_drawdown"] += abs(pnl_percentage)
            if self.metrics["current_drawdown"] > self.metrics["max_drawdown"]:
                self.metrics["max_drawdown"] = self.metrics["current_drawdown"]
        else:
            # Reduce drawdown on wins
            self.metrics["current_drawdown"] = max(0, self.metrics["current_drawdown"] - pnl_percentage * 0.5)
        
        self._save_metrics()
        print(f"📊 Tracker: Trade recorded - PnL: {pnl_percentage:.2f}%, Win rate: {self.metrics['win_rate']:.1f}%")
    
    def get_daily_performance(self, days: int = 7) -> dict:
        """Get performance for last N days"""
        daily = {}
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily[date] = self.metrics["daily_pnl"].get(date, 0.0)
        return daily
    
    def get_session_uptime(self) -> str:
        """Get current session uptime"""
        uptime = datetime.now() - self.session_start
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
    def get_summary(self) -> dict:
        """Get performance summary"""
        return {
            "total_pnl": self.metrics["total_pnl"],
            "total_trades": self.metrics["total_trades"],
            "wins": self.metrics["wins"],
            "losses": self.metrics["losses"],
            "win_rate": self.metrics["win_rate"],
            "max_drawdown": self.metrics["max_drawdown"],
            "current_drawdown": self.metrics["current_drawdown"],
            "best_trade": self.metrics["best_trade"],
            "worst_trade": self.metrics["worst_trade"],
            "session_uptime": self.get_session_uptime()
        }
    
    def reset_daily(self):
        """Reset daily metrics (called at start of new day)"""
        # Keep historical data, just flag new day
        print("📊 Tracker: Daily reset complete")
