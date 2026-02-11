"""
Command Parser - Natural Language to Structured Commands
Converts user input into structured command dictionaries
"""
import re


class CommandParser:
    """
    Parses natural language commands into structured format
    Integrates with LLM for complex parsing (future enhancement)
    """
    
    def __init__(self):
        # Pattern matching rules
        self.patterns = {
            'timeframe': r'(?:mudar|alterar|trocar|change)?\s*(?:timeframe|tf|tempo)\s+(?:para\s+)?([HMD]\d+)',
            'buy': r'(?:comprar|buy)\s+(\w+)',
            'sell': r'(?:vender|sell)\s+(\w+)',
            'quantity': r'(?:quantidade|qty|amount)?\s*([\d.]+)',
            'stop_loss': r'(?:stop|sl)\s+(?:em|at|@)?\s*([\d.]+)',
            'take_profit': r'(?:take|tp|target)\s+(?:em|at|@)?\s*([\d.]+)'
        }
    
    def parse(self, text: str) -> list:
        """
        Parse natural language text into structured commands
        
        Args:
            text: Natural language command
            
        Returns:
            list: List of structured command dictionaries
        """
        text = text.lower().strip()
        commands = []
        
        # Timeframe change
        if 'timeframe' in text or 'tf' in text:
            match = re.search(self.patterns['timeframe'], text, re.IGNORECASE)
            if match:
                tf = match.group(1).upper()
                commands.append({
                    "action": "change_timeframe",
                    "platform": "tradingview",
                    "tf": tf
                })
        
        # Buy order
        if 'comprar' in text or 'buy' in text:
            match = re.search(self.patterns['buy'], text)
            if match:
                symbol = match.group(1).upper()
                
                # Extract quantity
                qty_match = re.search(self.patterns['quantity'], text)
                quantity = float(qty_match.group(1)) if qty_match else 0.01
                
                # Extract SL/TP
                sl_match = re.search(self.patterns['stop_loss'], text)
                tp_match = re.search(self.patterns['take_profit'], text)
                
                cmd = {
                    "action": "execute_market_order",
                    "platform": self._detect_platform(symbol),
                    "symbol": symbol if symbol.endswith('USDT') else f"{symbol}USDT",
                    "side": "BUY",
                    "quantity": quantity,
                    "rr_ratio": 2.5  # Default RR
                }
                
                if sl_match:
                    cmd['stop_loss'] = float(sl_match.group(1))
                if tp_match:
                    cmd['take_profit'] = float(tp_match.group(1))
                
                commands.append(cmd)
        
        # Sell order
        if 'vender' in text or 'sell' in text:
            match = re.search(self.patterns['sell'], text)
            if match:
                symbol = match.group(1).upper()
                
                qty_match = re.search(self.patterns['quantity'], text)
                quantity = float(qty_match.group(1)) if qty_match else 0.01
                
                cmd = {
                    "action": "execute_market_order",
                    "platform": self._detect_platform(symbol),
                    "symbol": symbol if symbol.endswith('USDT') else f"{symbol}USDT",
                    "side": "SELL",
                    "quantity": quantity,
                    "rr_ratio": 2.5
                }
                
                commands.append(cmd)
        
        # Drawing tools
        if 'linha' in text or 'trendline' in text:
            commands.append({
                "action": "draw_trendline",
                "platform": "tradingview"
            })
        
        if 'fib' in text or 'fibonacci' in text:
            commands.append({
                "action": "apply_fib",
                "platform": "tradingview"
            })
        
        if 'abrir' in text and 'painel' in text:
            commands.append({
                "action": "open_trade_panel",
                "platform": "tradingview"
            })
        
        return commands
    
    def _detect_platform(self, symbol: str) -> str:
        """Detect platform based on symbol format"""
        if symbol.endswith('USDT') or symbol.startswith('BTC'):
            return "binance"  # Default to Binance for crypto
        return "mt5"  # Default to MT5 for forex
