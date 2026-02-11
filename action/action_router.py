"""
Action Router - Platform Command Routing
Routes commands to appropriate platform skill registries
"""
from skills.tradingview_skill_registry import SKILLS as TV_SKILLS
from skills.binance_skill_registry import SKILLS as BINANCE_SKILLS
from skills.bybit_skill_registry import SKILLS as BYBIT_SKILLS
from skills.mt5_skill_registry import SKILLS as MT5_SKILLS
from skills.system_skill_registry import SKILLS as SYSTEM_SKILLS


class ActionRouter:
    """
    Routes commands to the appropriate platform execution layer
    Manages skill registries and platform-specific logic
    """
    
    def __init__(self, config):
        self.config = config
        self.platforms = {
            'tradingview': TV_SKILLS,
            'binance': BINANCE_SKILLS,
            'bybit': BYBIT_SKILLS,
            'mt5': MT5_SKILLS,
            'system': SYSTEM_SKILLS
        }
    
    def route(self, command: dict):
        """
        Route command to appropriate platform skill
        
        Args:
            command: Structured command dict with 'platform' and 'action' keys
            
        Raises:
            Exception: If platform not supported or action not found
        """
        platform = command.get("platform")
        action = command.get("action")
        
        if not platform:
            raise Exception("Platform not specified in command")
        
        if platform not in self.platforms:
            raise Exception(f"Platform '{platform}' not supported")
        
        # Check if platform is enabled
        if platform in self.config['platforms']:
            if not self.config['platforms'][platform].get('enabled', False):
                raise Exception(f"Platform '{platform}' is disabled")
        
        # Get skill registry for platform
        skill_registry = self.platforms[platform]
        
        if action not in skill_registry:
            raise Exception(f"Action '{action}' not found in {platform} skills")
        
        # Execute the skill
        skill_function = skill_registry[action]
        return skill_function(**command)
    
    def list_skills(self, platform: str = None) -> dict:
        """List available skills for a platform or all platforms"""
        if platform:
            return {platform: list(self.platforms.get(platform, {}).keys())}
        return {p: list(skills.keys()) for p, skills in self.platforms.items()}
