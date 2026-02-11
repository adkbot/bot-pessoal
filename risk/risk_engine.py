"""
Risk Engine - Position Sizing and Risk Validation
Validates trades against risk management rules and account limits
"""


class RiskEngine:
    """
    Enforces risk management rules:
    - Max risk per trade
    - Daily drawdown limits
    - Total drawdown limits
    - Concurrent trade limits
    """
    
    def __init__(self, config):
        self.config = config['risk']
        self.max_risk_per_trade = self.config['max_risk_per_trade']
        self.max_daily_drawdown = self.config['max_daily_drawdown']
        self.max_total_drawdown = self.config['max_total_drawdown']
        self.max_concurrent_trades = self.config['max_concurrent_trades']
        self.emergency_stop = self.config['emergency_stop_enabled']
        
        # State tracking
        self.current_drawdown = 0.0
        self.daily_drawdown = 0.0
        self.active_trades = 0
        self.emergency_stopped = False
    
    def validate(self, command: dict) -> bool:
        """
        Validate command against risk rules
        
        Args:
            command: Structured command dict
            
        Returns:
            bool: True if approved, False if rejected
        """
        action = command.get("action")
        
        # Only validate trading actions
        if action not in ["execute_market_order", "execute_limit_order", "execute_stop_order"]:
            return True
        
        # Emergency stop check
        if self.emergency_stopped:
            print("❌ Risk: Emergency stop activated")
            return False
        
        # Check daily drawdown
        if self.daily_drawdown >= self.max_daily_drawdown:
            print(f"❌ Risk: Daily drawdown limit reached ({self.daily_drawdown*100:.2f}%)")
            if self.emergency_stop:
                self.emergency_stopped = True
            return False
        
        # Check total drawdown
        if self.current_drawdown >= self.max_total_drawdown:
            print(f"❌ Risk: Total drawdown limit reached ({self.current_drawdown*100:.2f}%)")
            if self.emergency_stop:
                self.emergency_stopped = True
            return False
        
        # Check concurrent trades
        if self.active_trades >= self.max_concurrent_trades:
            print(f"❌ Risk: Max concurrent trades reached ({self.active_trades})")
            return False
        
        # Validate position size (placeholder - needs account balance integration)
        quantity = command.get("quantity", 0)
        risk_amount = self._calculate_risk(command)
        
        if risk_amount > self.max_risk_per_trade:
            print(f"❌ Risk: Trade risk {risk_amount*100:.2f}% exceeds max {self.max_risk_per_trade*100:.2f}%")
            return False
        
        return True
    
    def _calculate_risk(self, command: dict) -> float:
        """
        Calculate risk as percentage of account
        Placeholder - needs real account balance
        """
        # TODO: Get actual account balance
        # TODO: Calculate actual risk based on stop loss distance
        # For now, assume 2% per trade
        return self.max_risk_per_trade * 0.8  # 80% of max to be safe
    
    def register_trade_opened(self):
        """Register new trade opened"""
        self.active_trades += 1
    
    def register_trade_closed(self, pnl_percentage: float):
        """Register trade closed and update drawdown"""
        self.active_trades = max(0, self.active_trades - 1)
        
        if pnl_percentage < 0:
            # Loss - update drawdown
            loss = abs(pnl_percentage)
            self.daily_drawdown += loss
            self.current_drawdown += loss
        else:
            # Win - reduce drawdown
            self.current_drawdown = max(0, self.current_drawdown - pnl_percentage * 0.5)
    
    def reset_daily(self):
        """Reset daily counters"""
        self.daily_drawdown = 0.0
    
    def reset_emergency_stop(self):
        """Reset emergency stop (manual intervention required)"""
        self.emergency_stopped = False
        print("✅ Emergency stop reset")
    
    def get_risk_status(self) -> dict:
        """Get current risk metrics"""
        return {
            "daily_drawdown": self.daily_drawdown,
            "total_drawdown": self.current_drawdown,
            "active_trades": self.active_trades,
            "emergency_stopped": self.emergency_stopped,
            "available_slots": self.max_concurrent_trades - self.active_trades
        }
