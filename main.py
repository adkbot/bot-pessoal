"""
AntiGravity System - Main Orchestrator
Central control system that processes natural language commands
and routes them through decision, risk, and execution layers.
"""
from core.decision_engine import DecisionEngine
from action.command_parser import CommandParser
from action.action_router import ActionRouter
from risk.risk_engine import RiskEngine
import yaml


class AntiGravitySystem:
    """Main orchestrator for the trading system"""
    
    def __init__(self):
        # Load configuration
        with open('config.yaml', 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.parser = CommandParser()
        self.decision_engine = DecisionEngine(self.config)
        self.risk_engine = RiskEngine(self.config)
        self.router = ActionRouter(self.config)
        
        print("🚀 AntiGravity System Initialized")
        print(f"Mode: {self.config['system']['mode']}")
        print(f"Risk per trade: {self.config['risk']['max_risk_per_trade']*100}%")
    
    def process_input(self, natural_command: str):
        """
        Process natural language input through the complete pipeline:
        1. Parse natural language → structured commands
        2. Validate through decision engine
        3. Check risk management
        4. Route to appropriate platform
        """
        print(f"\n📥 Processing: {natural_command}")
        
        # Step 1: Parse natural language
        structured_commands = self.parser.parse(natural_command)
        
        if not structured_commands:
            print("❌ Could not parse command")
            return
        
        # Step 2-4: Process each command
        for cmd in structured_commands:
            print(f"\n📋 Command: {cmd['action']} on {cmd.get('platform', 'unknown')}")
            
            # Decision Engine validation
            decision = self.decision_engine.validate(cmd)
            if not decision["approved"]:
                print(f"🚫 Blocked by Decision Engine: {decision['reason']}")
                continue
            print(f"✅ Decision Engine: {decision['reason']}")
            
            # Risk Engine validation
            risk_ok = self.risk_engine.validate(cmd)
            if not risk_ok:
                print("🚫 Blocked by Risk Engine")
                continue
            print("✅ Risk Engine: Approved")
            
            # Route to execution
            try:
                self.router.route(cmd)
                print("✅ Command executed successfully")
            except Exception as e:
                print(f"❌ Execution failed: {e}")


def main():
    """Main entry point"""
    system = AntiGravitySystem()
    
    print("\n" + "="*50)
    print("AntiGravity Trading System - Interactive Mode")
    print("Type 'exit' to quit")
    print("="*50 + "\n")
    
    while True:
        try:
            user_input = input(">> ")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("👋 Shutting down AntiGravity System")
                break
            
            if user_input.strip():
                system.process_input(user_input)
                
        except KeyboardInterrupt:
            print("\n👋 Shutting down AntiGravity System")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
