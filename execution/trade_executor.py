"""
Trade Executor - Unified Execution Interface
Provides consistent execution interface across all platforms
"""
from datetime import datetime


class TradeExecutor:
    """
    Unified trade execution layer
    Handles order submission, modification, and cancellation
    """
    
    def __init__(self, action_router):
        self.router = action_router
        self.active_orders = {}
        self.order_counter = 0
    
    def execute_trade(self, platform: str, symbol: str, side: str, 
                     quantity: float, order_type: str = "market", 
                     price: float = None, stop_loss: float = None, 
                     take_profit: float = None) -> dict:
        """
        Execute trade across any platform
        
        Args:
            platform: Platform to execute on
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            order_type: market, limit, stop
            price: Limit/stop price (if applicable)
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            dict: Execution result
        """
        self.order_counter += 1
        order_id = f"ORD_{self.order_counter}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Build command
        command = {
            "platform": platform,
            "action": f"execute_{order_type}_order",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "order_id": order_id
        }
        
        if price:
            command["price"] = price
        
        # Execute main order
        result = self.router.route(command)
        
        # Store active order
        self.active_orders[order_id] = {
            "platform": platform,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "status": "active",
            "timestamp": datetime.now()
        }
        
        # Set SL/TP if provided
        if stop_loss:
            self._set_stop_loss(platform, symbol, stop_loss)
        
        if take_profit:
            self._set_take_profit(platform, symbol, take_profit)
        
        return {
            "order_id": order_id,
            "status": "executed",
            "result": result
        }
    
    def _set_stop_loss(self, platform: str, symbol: str, price: float):
        """Set stop loss for position"""
        command = {
            "platform": platform,
            "action": "set_stop_loss",
            "symbol": symbol,
            "price": price
        }
        return self.router.route(command)
    
    def _set_take_profit(self, platform: str, symbol: str, price: float):
        """Set take profit for position"""
        command = {
            "platform": platform,
            "action": "set_take_profit",
            "symbol": symbol,
            "price": price
        }
        return self.router.route(command)
    
    def modify_order(self, order_id: str, **kwargs):
        """Modify existing order"""
        if order_id not in self.active_orders:
            raise Exception(f"Order {order_id} not found")
        
        order = self.active_orders[order_id]
        print(f"🔧 Executor: Modifying order {order_id}")
        
        # TODO: Implement platform-specific modification
        return {"status": "modified", "order_id": order_id}
    
    def cancel_order(self, order_id: str):
        """Cancel order"""
        if order_id not in self.active_orders:
            raise Exception(f"Order {order_id} not found")
        
        order = self.active_orders[order_id]
        print(f"❌ Executor: Canceling order {order_id}")
        
        # TODO: Implement platform-specific cancellation
        order["status"] = "canceled"
        
        return {"status": "canceled", "order_id": order_id}
    
    def get_active_orders(self):
        """Get all active orders"""
        return [
            {"order_id": oid, **order} 
            for oid, order in self.active_orders.items() 
            if order["status"] == "active"
        ]
