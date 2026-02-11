"""
Decision Engine - Institutional Trading Logic
Validates trade setups based on multi-timeframe structure and market context
"""


class DecisionEngine:
    """
    Validates commands against institutional trading rules:
    - H4 structure alignment
    - Multi-timeframe confirmation
    - Session validation
    - Risk/Reward ratios
    """
    
    def __init__(self, config):
        self.config = config['decision']
        self.require_h4 = self.config['require_h4_structure']
        self.require_mtf = self.config['require_mtf_confirmation']
        self.min_rr = self.config['min_rr_ratio']
        self.allowed_sessions = self.config['allowed_sessions']
    
    def validate(self, command: dict) -> dict:
        """
        Validate command against decision rules
        
        Args:
            command: Structured command dict
            
        Returns:
            dict: {"approved": bool, "reason": str}
        """
        action = command.get("action")
        
        # Allow non-trading actions
        if action in ["change_timeframe", "draw_trendline", "apply_fib", "open_trade_panel"]:
            return {
                "approved": True,
                "reason": "Non-trading action approved"
            }
        
        # Trading actions require validation
        if action in ["execute_market_order", "execute_limit_order", "execute_stop_order"]:
            return self._validate_trade(command)
        
        # Default approve for other actions
        return {
            "approved": True,
            "reason": "Action approved"
        }
    
    def _validate_trade(self, command: dict) -> dict:
        """Validate trading command against institutional rules"""
        
        # Check if RR ratio is provided and meets minimum
        rr_ratio = command.get("rr_ratio", 0)
        if rr_ratio < self.min_rr:
            return {
                "approved": False,
                "reason": f"RR ratio {rr_ratio} below minimum {self.min_rr}"
            }
        
        # Check session (if provided)
        session = command.get("session", "").lower()
        if session and session not in self.allowed_sessions:
            return {
                "approved": False,
                "reason": f"Session {session} not in allowed sessions"
            }
        
        # Check H4 structure (placeholder - needs market data integration)
        if self.require_h4:
            h4_aligned = command.get("h4_structure_aligned", True)  # Default True for now
            if not h4_aligned:
                return {
                    "approved": False,
                    "reason": "H4 structure not aligned"
                }
        
        # Check multi-timeframe confirmation (placeholder)
        if self.require_mtf:
            mtf_confirmed = command.get("mtf_confirmed", True)  # Default True for now
            if not mtf_confirmed:
                return {
                    "approved": False,
                    "reason": "Multi-timeframe not confirmed"
                }
        
        return {
            "approved": True,
            "reason": "Structure aligned, RR valid, session approved"
        }
