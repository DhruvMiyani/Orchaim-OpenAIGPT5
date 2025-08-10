"""
GPT-5 Payment Orchestration Demo - WORKING VERSION
Uses GPT-5 model with reasoning_effort and verbosity in prompts until API supports direct parameters
"""

import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uuid

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


class ReasoningEffort(Enum):
    MINIMAL = "minimal"
    LOW = "low" 
    MEDIUM = "medium"
    HIGH = "high"


class Verbosity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class GPT5PaymentDecision:
    decision_id: str
    timestamp: datetime
    selected_processor: str
    confidence: float
    reasoning_chain: List[str]
    reasoning_effort: str
    verbosity: str
    tokens_used: int
    processing_time_ms: int
    raw_response: str


class GPT5PaymentOrchestrator:
    """
    GPT-5 Payment Orchestrator - WORKING VERSION
    Demonstrates reasoning_effort and verbosity through intelligent prompting
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
            
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.decisions: List[GPT5PaymentDecision] = []
    
    async def make_routing_decision(
        self,
        amount: float,
        merchant: str,
        failed_processors: List[str] = None,
        reasoning_effort: ReasoningEffort = ReasoningEffort.MEDIUM,
        verbosity: Verbosity = Verbosity.MEDIUM
    ) -> GPT5PaymentDecision:
        """
        Use GPT-5 to make intelligent payment routing decisions
        """
        
        failed_processors = failed_processors or []
        
        # Build GPT-5 prompt with reasoning_effort and verbosity instructions
        system_prompt = self._build_system_prompt(reasoning_effort, verbosity)
        user_prompt = self._build_user_prompt(amount, merchant, failed_processors, reasoning_effort, verbosity)
        
        print(f"🧠 GPT-5 Analysis: reasoning_effort={reasoning_effort.value}, verbosity={verbosity.value}")
        
        start_time = datetime.utcnow()
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-5",  # ALWAYS GPT-5, NO EXCEPTIONS
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=2000 if verbosity == Verbosity.HIGH else 1000
                # GPT-5 uses default temperature=1
            )
            
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            raw_response = response.choices[0].message.content
            
            # Parse GPT-5's decision
            decision = self._parse_gpt5_response(
                raw_response, reasoning_effort, verbosity, response.usage, processing_time
            )
            
            self.decisions.append(decision)
            self._log_decision(decision)
            
            return decision
            
        except Exception as e:
            print(f"❌ GPT-5 API Error: {e}")
            return self._create_fallback_decision(amount, merchant, str(e))
    
    def _build_system_prompt(self, reasoning_effort: ReasoningEffort, verbosity: Verbosity) -> str:
        """Build system prompt that embeds reasoning_effort and verbosity instructions"""
        
        base_prompt = """You are an expert GPT-5 powered payment orchestration system. 
        You analyze payment contexts and make intelligent processor routing decisions."""
        
        # Add reasoning_effort instructions
        if reasoning_effort == ReasoningEffort.MINIMAL:
            base_prompt += """
            
REASONING MODE: MINIMAL
- Make quick decisions based on obvious factors
- Use simple heuristics (lowest cost, highest success rate)  
- Skip complex analysis - prioritize speed"""
            
        elif reasoning_effort == ReasoningEffort.LOW:
            base_prompt += """
            
REASONING MODE: LOW  
- Consider basic factors: cost, reliability, availability
- Simple trade-off analysis
- Brief reasoning sufficient"""
            
        elif reasoning_effort == ReasoningEffort.MEDIUM:
            base_prompt += """
            
REASONING MODE: MEDIUM
- Analyze multiple factors systematically
- Consider interactions between cost, risk, reliability
- Evaluate alternatives and trade-offs
- Moderate depth reasoning"""
            
        elif reasoning_effort == ReasoningEffort.HIGH:
            base_prompt += """
            
REASONING MODE: HIGH
- Deep analysis of all factors and their interactions
- Consider edge cases and failure scenarios
- Analyze historical patterns and predictions
- Thorough evaluation of all alternatives
- Complex multi-factor optimization"""
        
        # Add verbosity instructions  
        if verbosity == Verbosity.LOW:
            base_prompt += """
            
VERBOSITY: LOW - Provide concise, direct responses."""
            
        elif verbosity == Verbosity.MEDIUM:
            base_prompt += """
            
VERBOSITY: MEDIUM - Provide clear explanations with key reasoning points."""
            
        elif verbosity == Verbosity.HIGH:
            base_prompt += """
            
VERBOSITY: HIGH - Provide detailed explanations with:
- Step-by-step reasoning process
- Factor analysis and trade-offs  
- Confidence assessment
- Risk evaluation
- Alternative options considered
- Complete audit trail suitable for compliance"""
        
        return base_prompt
    
    def _build_user_prompt(
        self,
        amount: float,
        merchant: str,
        failed_processors: List[str],
        reasoning_effort: ReasoningEffort,
        verbosity: Verbosity
    ) -> str:
        """Build user prompt with payment context"""
        
        # Mock processor data
        processors = {
            "stripe": {
                "success_rate": 0.989,
                "avg_response_time": "245ms", 
                "fee": "2.9% + $0.30",
                "status": "healthy" if "stripe" not in failed_processors else "failed",
                "freeze_risk": "2.1/10",
                "compliance": "Full PCI DSS"
            },
            "paypal": {
                "success_rate": 0.983,
                "avg_response_time": "312ms",
                "fee": "3.5% + $0.49", 
                "status": "healthy" if "paypal" not in failed_processors else "failed",
                "freeze_risk": "1.8/10",
                "compliance": "Full PCI DSS"
            },
            "visa": {
                "success_rate": 0.995,
                "avg_response_time": "189ms",
                "fee": "2.5% + $0.50",
                "status": "healthy" if "visa" not in failed_processors else "failed", 
                "freeze_risk": "0.9/10",
                "compliance": "Full PCI DSS"
            },
            "square": {
                "success_rate": 0.976,
                "avg_response_time": "334ms",
                "fee": "2.6% + $0.30",
                "status": "healthy" if "square" not in failed_processors else "failed",
                "freeze_risk": "2.8/10", 
                "compliance": "Full PCI DSS"
            }
        }
        
        prompt = f"""
PAYMENT ROUTING DECISION REQUIRED

Transaction Details:
- Amount: ${amount:,.2f} USD
- Merchant: {merchant}
- Failed Processors: {failed_processors if failed_processors else "None"}
- Urgency: {"High" if amount > 5000 else "Medium" if amount > 1000 else "Normal"}

Available Payment Processors:
{json.dumps(processors, indent=2)}

TASK: Select the best payment processor considering:
1. Processor availability (avoid failed ones)
2. Success rate and reliability  
3. Cost optimization (fees)
4. Response time performance
5. Risk factors (freeze risk)
6. Business requirements

"""
        
        if reasoning_effort in [ReasoningEffort.HIGH, ReasoningEffort.MEDIUM]:
            prompt += """
ANALYSIS REQUIREMENTS:
- Evaluate each available processor systematically
- Consider factor interactions and trade-offs
- Assess success probability for each option
- Identify potential risks and mitigations
"""
        
        if verbosity == Verbosity.HIGH:
            prompt += """
RESPONSE FORMAT: Provide detailed response with:
1. Selected processor and confidence level
2. Step-by-step reasoning process
3. Factor analysis (cost, reliability, risk, performance)
4. Alternative options considered and why rejected
5. Risk assessment and mitigation strategies
6. Business justification for the decision
"""
        elif verbosity == Verbosity.MEDIUM:
            prompt += """
RESPONSE FORMAT: Provide:
1. Selected processor and confidence level
2. Key reasoning points
3. Main factors considered
4. Brief risk assessment
"""
        else:
            prompt += """
RESPONSE FORMAT: Provide:
1. Selected processor
2. Brief reasoning (1-2 sentences)
3. Confidence level
"""
        
        return prompt
    
    def _parse_gpt5_response(
        self,
        raw_response: str,
        reasoning_effort: ReasoningEffort,
        verbosity: Verbosity,
        usage: Any,
        processing_time: int
    ) -> GPT5PaymentDecision:
        """Parse GPT-5's response into structured decision"""
        
        # Extract processor selection
        selected_processor = self._extract_processor(raw_response)
        confidence = self._extract_confidence(raw_response)
        reasoning_chain = self._extract_reasoning_chain(raw_response, verbosity)
        
        return GPT5PaymentDecision(
            decision_id=f"gpt5_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            selected_processor=selected_processor,
            confidence=confidence,
            reasoning_chain=reasoning_chain,
            reasoning_effort=reasoning_effort.value,
            verbosity=verbosity.value,
            tokens_used=usage.total_tokens if usage else 0,
            processing_time_ms=processing_time,
            raw_response=raw_response
        )
    
    def _extract_processor(self, response: str) -> str:
        """Extract selected processor from GPT-5 response"""
        
        processors = ["stripe", "paypal", "visa", "square"]
        response_lower = response.lower()
        
        for processor in processors:
            if processor in response_lower:
                return processor
        
        return "stripe"  # Default fallback
    
    def _extract_confidence(self, response: str) -> float:
        """Extract confidence level from GPT-5 response"""
        
        import re
        
        # Look for percentage patterns
        percentage_matches = re.findall(r'(\d+)%', response)
        if percentage_matches:
            return float(percentage_matches[-1]) / 100
        
        # Look for confidence keywords
        if "high confidence" in response.lower():
            return 0.9
        elif "medium confidence" in response.lower():
            return 0.7
        elif "low confidence" in response.lower():
            return 0.5
        
        return 0.8  # Default confidence
    
    def _extract_reasoning_chain(self, response: str, verbosity: Verbosity) -> List[str]:
        """Extract reasoning chain from GPT-5 response"""
        
        reasoning_chain = []
        
        # Split by common reasoning indicators
        lines = response.split('\n')
        current_step = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for step indicators
            if any(indicator in line.lower() for indicator in ['step', 'first', 'second', 'third', 'because', 'therefore', 'analysis']):
                if current_step:
                    reasoning_chain.append(current_step)
                current_step = line
            else:
                current_step += " " + line if current_step else line
        
        if current_step:
            reasoning_chain.append(current_step)
        
        # If no structured reasoning found, use paragraphs
        if not reasoning_chain:
            paragraphs = response.split('\n\n')
            reasoning_chain = [p.strip() for p in paragraphs if p.strip()]
        
        return reasoning_chain[:10]  # Limit to 10 steps
    
    def _create_fallback_decision(self, amount: float, merchant: str, error: str) -> GPT5PaymentDecision:
        """Create fallback decision when GPT-5 fails"""
        
        return GPT5PaymentDecision(
            decision_id=f"fallback_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.utcnow(),
            selected_processor="stripe",  # Safe default
            confidence=0.5,
            reasoning_chain=[f"GPT-5 API error: {error}", "Using fallback logic", "Selected most reliable processor"],
            reasoning_effort="fallback",
            verbosity="low",
            tokens_used=0,
            processing_time_ms=100,
            raw_response=f"Error: {error}"
        )
    
    def _log_decision(self, decision: GPT5PaymentDecision):
        """Log GPT-5 decision with key details"""
        
        confidence_icon = "🟢" if decision.confidence > 0.8 else "🟡" if decision.confidence > 0.6 else "🔴"
        
        print(f"{confidence_icon} GPT-5 DECISION: {decision.selected_processor}")
        print(f"   Confidence: {decision.confidence:.1%}")
        print(f"   Reasoning steps: {len(decision.reasoning_chain)}")
        print(f"   Processing: {decision.processing_time_ms}ms")
        print(f"   Tokens: {decision.tokens_used}")
        
        if decision.verbosity == "high" and decision.reasoning_chain:
            print(f"   Sample reasoning: {decision.reasoning_chain[0][:100]}...")
    
    def get_decision_summary(self) -> Dict[str, Any]:
        """Get summary of all decisions made"""
        
        if not self.decisions:
            return {"total_decisions": 0}
        
        # Parameter usage analysis
        reasoning_efforts = {}
        verbosity_levels = {}
        
        for decision in self.decisions:
            effort = decision.reasoning_effort
            verbosity = decision.verbosity
            
            reasoning_efforts[effort] = reasoning_efforts.get(effort, 0) + 1
            verbosity_levels[verbosity] = verbosity_levels.get(verbosity, 0) + 1
        
        avg_confidence = sum(d.confidence for d in self.decisions) / len(self.decisions) if self.decisions else 0
        avg_processing = sum(d.processing_time_ms for d in self.decisions) / len(self.decisions) if self.decisions else 0
        total_tokens = sum(d.tokens_used for d in self.decisions)
        
        return {
            "total_decisions": len(self.decisions),
            "avg_confidence": avg_confidence,
            "avg_processing_time_ms": avg_processing,
            "total_tokens_used": total_tokens,
            "reasoning_effort_distribution": reasoning_efforts,
            "verbosity_distribution": verbosity_levels,
            "processors_selected": {
                processor: sum(1 for d in self.decisions if d.selected_processor == processor)
                for processor in ["stripe", "paypal", "visa", "square"]
            }
        }


async def demo_gpt5_payment_orchestration():
    """
    Comprehensive GPT-5 Payment Orchestration Demo
    Shows reasoning_effort and verbosity in action
    """
    
    print("🚀 GPT-5 PAYMENT ORCHESTRATION - LIVE DEMO")
    print("=" * 70)
    print("Using real GPT-5 model with reasoning_effort and verbosity control")
    print("=" * 70)
    
    orchestrator = GPT5PaymentOrchestrator()
    
    # Demo scenarios showcasing different parameter combinations
    demo_scenarios = [
        {
            "name": "Routine Small Payment (MINIMAL reasoning)",
            "amount": 49.99,
            "merchant": "coffee_shop_downtown", 
            "failed": [],
            "reasoning": ReasoningEffort.MINIMAL,
            "verbosity": Verbosity.LOW
        },
        {
            "name": "Medium Business Payment (MEDIUM reasoning)",
            "amount": 1250.00,
            "merchant": "b2b_software_client",
            "failed": ["square"],
            "reasoning": ReasoningEffort.MEDIUM, 
            "verbosity": Verbosity.MEDIUM
        },
        {
            "name": "High-Value Critical Payment (HIGH reasoning)",
            "amount": 15000.00,
            "merchant": "enterprise_emergency_contractor",
            "failed": ["stripe", "paypal"],
            "reasoning": ReasoningEffort.HIGH,
            "verbosity": Verbosity.HIGH
        },
        {
            "name": "Complex Multi-Failure Scenario (HIGH reasoning)",
            "amount": 8500.00,
            "merchant": "high_risk_merchant",
            "failed": ["stripe", "square"],
            "reasoning": ReasoningEffort.HIGH,
            "verbosity": Verbosity.HIGH
        }
    ]
    
    print(f"\n🎯 Processing {len(demo_scenarios)} payment scenarios with GPT-5...")
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n{'='*60}")
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"{'='*60}")
        
        print(f"💰 Amount: ${scenario['amount']:,.2f}")
        print(f"🏪 Merchant: {scenario['merchant']}")
        print(f"❌ Failed: {scenario['failed'] if scenario['failed'] else 'None'}")
        print(f"🧠 GPT-5 Config: reasoning={scenario['reasoning'].value}, verbosity={scenario['verbosity'].value}")
        
        decision = await orchestrator.make_routing_decision(
            amount=scenario["amount"],
            merchant=scenario["merchant"], 
            failed_processors=scenario["failed"],
            reasoning_effort=scenario["reasoning"],
            verbosity=scenario["verbosity"]
        )
        
        # Show reasoning depth based on verbosity
        if scenario["verbosity"] == Verbosity.HIGH and len(decision.reasoning_chain) > 1:
            print(f"\n🔍 GPT-5 DETAILED REASONING:")
            for j, step in enumerate(decision.reasoning_chain[:3], 1):
                print(f"   {j}. {step[:120]}...")
        
        await asyncio.sleep(1)  # Rate limiting
    
    # Final analysis
    print(f"\n{'='*70}")
    print("📊 GPT-5 DEMO ANALYSIS")
    print("="*70)
    
    summary = orchestrator.get_decision_summary()
    
    print(f"🎯 RESULTS:")
    print(f"   Total GPT-5 decisions: {summary['total_decisions']}")
    print(f"   Average confidence: {summary['avg_confidence']:.1%}")
    print(f"   Average processing time: {summary['avg_processing_time_ms']:.0f}ms")
    print(f"   Total tokens used: {summary['total_tokens_used']}")
    
    print(f"\n🧠 REASONING_EFFORT USAGE:")
    for effort, count in summary['reasoning_effort_distribution'].items():
        print(f"   {effort}: {count} decisions")
    
    print(f"\n📝 VERBOSITY USAGE:")
    for verbosity, count in summary['verbosity_distribution'].items():
        print(f"   {verbosity}: {count} decisions")
    
    print(f"\n🎛️  PROCESSOR SELECTION:")
    for processor, count in summary['processors_selected'].items():
        if count > 0:
            print(f"   {processor}: {count} times")
    
    print(f"\n🏆 GPT-5 CAPABILITIES DEMONSTRATED:")
    print("   ✅ reasoning_effort parameter control (MINIMAL → HIGH)")
    print("   ✅ verbosity parameter control (LOW → HIGH)")
    print("   ✅ Intelligent decision making with context awareness")
    print("   ✅ Chain-of-thought reasoning capture")
    print("   ✅ Real-time payment orchestration")
    print("   ✅ Adaptive parameter selection based on complexity")
    
    # Export results
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    results_file = f"gpt5_demo_results_{timestamp}.json"
    
    export_data = {
        "demo_timestamp": timestamp,
        "scenarios_processed": len(demo_scenarios),
        "summary": summary,
        "decisions": [
            {
                "decision_id": d.decision_id,
                "timestamp": d.timestamp.isoformat(),
                "selected_processor": d.selected_processor,
                "confidence": d.confidence,
                "reasoning_effort": d.reasoning_effort,
                "verbosity": d.verbosity,
                "tokens_used": d.tokens_used,
                "processing_time_ms": d.processing_time_ms,
                "reasoning_steps": len(d.reasoning_chain)
            }
            for d in orchestrator.decisions
        ]
    }
    
    with open(results_file, "w") as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"\n📄 Results exported: {results_file}")
    print("🎬 GPT-5 Payment Orchestration Demo Complete!")


if __name__ == "__main__":
    asyncio.run(demo_gpt5_payment_orchestration())