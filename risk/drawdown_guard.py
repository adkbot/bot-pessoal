"""
Drawdown Guard - Real-time Position Protection
Monitors open positions and triggers protection mechanisms
"""
from datetime import datetime


class DrawdownGuard:
    """
    Active protection for open positions:
    - Trailing stops
    - Break-even moves
    - Partial profit taking
    """
    
    def __init__(self, config):
        self.config = config['risk']
        self.monitored_positions = {}
        self.protection_active = True
    
    def add_position(self, position_id: str, entry_price: float, 
                     stop_loss: float, take_profit: float, side: str):
        """
        Start monitoring a position
        
        Args:
            position_id: Unique position identifier
            entry_price: Entry price
            stop_loss: Initial stop loss
            take_profit: Take profit target
            side: BUY or SELL
        """
        self.monitored_positions[position_id] = {
            'entry': entry_price,
            'sl': stop_loss,
            'tp': take_profit,
            'side': side,
            'breakeven_moved': False,
            'partial_taken': False,
            'added_at': datetime.now()
        }
        print(f"🛡️ Drawdown Guard: Monitoring {position_id}")
    
    def update_price(self, position_id: str, current_price: float):
        """
        Update current price and check protection triggers
        
        Args:
            position_id: Position to update
            current_price: Current market price
        """
        if position_id not in self.monitored_positions:
            return
        
        position = self.monitored_positions[position_id]
        entry = position['entry']
        side = position['side']
        
        # Calculate profit percentage
        if side == 'BUY':
            profit_pct = (current_price - entry) / entry
        else:  # SELL
            profit_pct = (entry - current_price) / entry
        
        # Move to breakeven at 50% of TP
        if not position['breakeven_moved'] and profit_pct >= 0.01:  # 1% profit
            self._move_to_breakeven(position_id)
            position['breakeven_moved'] = True
        
        # Take partial profit at 75% of TP
        if not position['partial_taken'] and profit_pct >= 0.015:  # 1.5% profit
            self._take_partial_profit(position_id)
            position['partial_taken'] = True
        
        # Trail stop in profit
        if profit_pct >= 0.02:  # 2% profit
            self._update_trailing_stop(position_id, current_price, profit_pct)
    
    def _move_to_breakeven(self, position_id: str):
        """Move stop loss to breakeven"""
        position = self.monitored_positions[position_id]
        position['sl'] = position['entry']
        print(f"🛡️ Drawdown Guard: {position_id} moved to breakeven")
    
    def _take_partial_profit(self, position_id: str):
        """Take partial profit (e.g., 50% of position)"""
        print(f"🛡️ Drawdown Guard: {position_id} taking 50% partial profit")
        # TODO: Integrate with execution layer
    
    def _update_trailing_stop(self, position_id: str, current_price: float, profit_pct: float):
        """Update trailing stop"""
        position = self.monitored_positions[position_id]
        
        # Trail at 50% of current profit
        trail_distance = profit_pct * 0.5
        
        if position['side'] == 'BUY':
            new_sl = current_price * (1 - trail_distance)
            position['sl'] = max(position['sl'], new_sl)
        else:  # SELL
            new_sl = current_price * (1 + trail_distance)
            position['sl'] = min(position['sl'], new_sl)
        
        print(f"🛡️ Drawdown Guard: {position_id} trailing stop updated to {position['sl']:.5f}")
    
    def remove_position(self, position_id: str):
        """Stop monitoring a position"""
        if position_id in self.monitored_positions:
            del self.monitored_positions[position_id]
            print(f"🛡️ Drawdown Guard: Stopped monitoring {position_id}")
    
    def get_protected_positions(self) -> dict:
        """Get all monitored positions"""
        return self.monitored_positions.copy()
