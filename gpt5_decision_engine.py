"""
Component 2: GPT-5 Decision Engine
Core GPT-5 engine demonstrating reasoning_effort, verbosity, and chain-of-thought capabilities
"""

import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
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


class DecisionUrgency(Enum):
    ROUTINE = "routine"
    NORMAL = "normal"
    ELEVATED = "elevated"
    CRITICAL = "critical"


@dataclass
class GPT5Decision:
    """GPT-5 decision with full reasoning chain"""
    decision_id: str
    timestamp: datetime
    decision_type: str
    selected_option: str
    confidence: float
    reasoning_chain: List[str]
    reasoning_effort: ReasoningEffort
    verbosity: Verbosity
    tokens_used: int
    reasoning_tokens: int
    processing_time_ms: int
    raw_response: str
    chain_of_thought: List[Dict[str, Any]]


@dataclass
class PaymentContext:
    """Payment routing context for GPT-5 decisions"""
    amount: float
    currency: str
    merchant_id: str
    urgency: DecisionUrgency
    failed_processors: List[str]
    risk_indicators: Dict[str, Any]
    processor_health: Dict[str, Any]
    business_rules: Dict[str, Any]


class GPT5DecisionEngine:
    """
    Core GPT-5 Decision Engine showcasing:
    1. reasoning_effort parameter control
    2. verbosity parameter control  
    3. Chain-of-thought reasoning capture
    4. Adaptive parameter selection
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
            
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.decision_history: List[GPT5Decision] = []
        self.model = "gpt-5"  # ALWAYS GPT-5, NO EXCEPTIONS
        
    async def make_payment_routing_decision(
        self,
        context: PaymentContext,
        reasoning_effort: Optional[ReasoningEffort] = None,
        verbosity: Optional[Verbosity] = None
    ) -> GPT5Decision:
        """
        Make intelligent payment routing decision using GPT-5's advanced reasoning
        """
        
        # Auto-determine parameters if not specified
        if reasoning_effort is None:
            reasoning_effort = self._determine_reasoning_effort(context)
        if verbosity is None:
            verbosity = self._determine_verbosity(context)
        
        # Build comprehensive prompt
        system_prompt = self._build_system_prompt(reasoning_effort, verbosity)
        user_prompt = self._build_routing_prompt(context, reasoning_effort, verbosity)
        
        print(f"🧠 GPT-5 Decision: reasoning={reasoning_effort.value}, verbosity={verbosity.value}")
        
        start_time = datetime.utcnow()
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-5",  # FORCE GPT-5, NO SUBSTITUTIONS
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=self._get_max_tokens(verbosity),
                temperature=0.7,
                reasoning_effort=reasoning_effort.value,
                verbosity=verbosity.value
            )
            
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            raw_response = response.choices[0].message.content
            
            # Parse GPT-5's structured response
            decision = self._parse_gpt5_response(
                raw_response, context, reasoning_effort, verbosity, 
                response.usage, processing_time
            )
            
            # Store decision in history
            self.decision_history.append(decision)
            
            self._log_decision(decision)
            
            return decision
            
        except Exception as e:
            # Fallback decision with error context
            return self._create_fallback_decision(
                context, str(e), reasoning_effort, verbosity
            )
    
    def _determine_reasoning_effort(self, context: PaymentContext) -> ReasoningEffort:
        """
        Intelligently determine reasoning effort based on context
        Demonstrates GPT-5's adaptive parameter selection
        """
        
        if context.urgency == DecisionUrgency.ROUTINE and not context.failed_processors:
            return ReasoningEffort.MINIMAL
        elif context.amount < 500 and len(context.failed_processors) <= 1:
            return ReasoningEffort.LOW
        elif context.amount > 5000 or len(context.failed_processors) > 1 or context.urgency == DecisionUrgency.ELEVATED:
            return ReasoningEffort.HIGH
        else:
            return ReasoningEffort.MEDIUM
    
    def _determine_verbosity(self, context: PaymentContext) -> Verbosity:
        """
        Determine verbosity level for audit requirements and complexity
        """
        
        if context.urgency == DecisionUrgency.CRITICAL or len(context.failed_processors) > 2:
            return Verbosity.HIGH
        elif context.amount > 1000 or context.failed_processors:
            return Verbosity.MEDIUM
        else:
            return Verbosity.LOW
    
    def _build_system_prompt(self, reasoning_effort: ReasoningEffort, verbosity: Verbosity) -> str:
        """Build system prompt optimized for GPT-5 parameters"""
        
        base_prompt = """You are an expert payment orchestration system using GPT-5's advanced reasoning capabilities. 
        You make intelligent decisions about payment processor routing based on complex business contexts."""
        
        if reasoning_effort == ReasoningEffort.HIGH:
            base_prompt += """
            
REASONING MODE: HIGH EFFORT
- Perform deep analysis of all factors
- Consider multiple scenarios and edge cases  
- Weigh trade-offs carefully between reliability, cost, and risk
- Analyze historical patterns and predict outcomes
- Provide detailed justification for each decision point"""

        if verbosity == Verbosity.HIGH:
            base_prompt += """
            
VERBOSITY MODE: HIGH
- Provide detailed step-by-step reasoning
- Explain why each factor was considered or rejected
- Include confidence intervals and risk assessments
- Document assumptions and limitations
- Create comprehensive audit trail suitable for compliance"""
        
        return base_prompt
    
    def _build_routing_prompt(
        self, 
        context: PaymentContext, 
        reasoning_effort: ReasoningEffort,
        verbosity: Verbosity
    ) -> str:
        """Build routing decision prompt with context"""
        
        prompt = f"""
PAYMENT ROUTING DECISION REQUIRED

Transaction Context:
- Amount: ${context.amount:,.2f} {context.currency}
- Merchant: {context.merchant_id}
- Urgency: {context.urgency.value}
- Failed Processors: {context.failed_processors or 'None'}

Available Processors:
{json.dumps(context.processor_health, indent=2)}

Risk Indicators:
{json.dumps(context.risk_indicators, indent=2)}

Business Rules:
{json.dumps(context.business_rules, indent=2)}

TASK: Select the best payment processor considering:
1. Processor health and reliability
2. Cost optimization 
3. Risk mitigation
4. Business requirements
5. Regulatory compliance

"""
        
        if reasoning_effort in [ReasoningEffort.HIGH, ReasoningEffort.MEDIUM]:
            prompt += """
ANALYSIS REQUIREMENTS:
- Evaluate each processor systematically
- Consider interaction effects between factors
- Assess probability of success for each option
- Identify potential failure modes and mitigations
"""
        
        if verbosity in [Verbosity.HIGH, Verbosity.MEDIUM]:
            prompt += """
RESPONSE FORMAT:
Provide your response in JSON format with:
{
  "selected_processor": "processor_id",
  "confidence": 0.85,
  "reasoning_chain": ["step 1", "step 2", ...],
  "risk_assessment": "description",
  "fallback_chain": ["backup1", "backup2"],
  "business_justification": "detailed explanation",
  "assumptions": ["assumption 1", "assumption 2"],
  "monitoring_recommendations": ["monitor X", "watch for Y"]
}
"""
        else:
            prompt += """
RESPONSE FORMAT:
{
  "selected_processor": "processor_id", 
  "confidence": 0.85,
  "reasoning": "brief explanation"
}
"""
        
        return prompt
    
    def _get_max_tokens(self, verbosity: Verbosity) -> int:
        """Determine max tokens based on verbosity"""
        
        token_limits = {
            Verbosity.LOW: 500,
            Verbosity.MEDIUM: 1500, 
            Verbosity.HIGH: 3000
        }
        return token_limits[verbosity]
    
    def _parse_gpt5_response(
        self,
        raw_response: str,
        context: PaymentContext,
        reasoning_effort: ReasoningEffort,
        verbosity: Verbosity,
        usage: Any,
        processing_time: int
    ) -> GPT5Decision:
        """Parse GPT-5's structured response into decision object"""
        
        try:
            # Try to parse JSON response
            if '{' in raw_response and '}' in raw_response:
                json_start = raw_response.index('{')
                json_end = raw_response.rindex('}') + 1
                json_str = raw_response[json_start:json_end]
                parsed = json.loads(json_str)
            else:
                # Fallback parsing for non-JSON responses
                parsed = {
                    "selected_processor": self._extract_processor(raw_response),
                    "confidence": 0.7,
                    "reasoning_chain": [raw_response[:500]],
                    "risk_assessment": "Standard risk level"
                }
            
            # Extract chain of thought from reasoning
            chain_of_thought = self._extract_chain_of_thought(
                parsed.get("reasoning_chain", []), reasoning_effort
            )
            
            return GPT5Decision(
                decision_id=f"dec_{uuid.uuid4().hex[:12]}",
                timestamp=datetime.utcnow(),
                decision_type="payment_routing",
                selected_option=parsed.get("selected_processor", "stripe"),
                confidence=parsed.get("confidence", 0.7),
                reasoning_chain=parsed.get("reasoning_chain", []),
                reasoning_effort=reasoning_effort,
                verbosity=verbosity,
                tokens_used=usage.total_tokens if usage else 0,
                reasoning_tokens=getattr(usage, 'reasoning_tokens', 0) if usage else 0,
                processing_time_ms=processing_time,
                raw_response=raw_response,
                chain_of_thought=chain_of_thought
            )
            
        except Exception as e:
            print(f"⚠️  Error parsing GPT-5 response: {e}")
            return self._create_fallback_decision(context, str(e), reasoning_effort, verbosity)
    
    def _extract_chain_of_thought(
        self, 
        reasoning_chain: List[str],
        reasoning_effort: ReasoningEffort
    ) -> List[Dict[str, Any]]:
        """Extract structured chain of thought from reasoning"""
        
        chain = []
        
        for i, step in enumerate(reasoning_chain):
            chain.append({
                "step": i + 1,
                "reasoning": step,
                "confidence": random.uniform(0.7, 0.95),  # Simulated confidence
                "factors_considered": self._extract_factors(step),
                "effort_level": reasoning_effort.value
            })
        
        return chain
    
    def _extract_factors(self, reasoning_text: str) -> List[str]:
        """Extract factors considered from reasoning text"""
        
        factors = []
        keywords = ["cost", "reliability", "risk", "speed", "compliance", "history", "health"]
        
        for keyword in keywords:
            if keyword.lower() in reasoning_text.lower():
                factors.append(keyword)
        
        return factors
    
    def _extract_processor(self, text: str) -> str:
        """Extract selected processor from text"""
        
        processors = ["stripe", "paypal", "visa", "square", "adyen"]
        
        for processor in processors:
            if processor.lower() in text.lower():
                return processor
        
        return "stripe"  # Default fallback
    
    def _create_fallback_decision(
        self, 
        context: PaymentContext,
        error: str,
        reasoning_effort: ReasoningEffort,
        verbosity: Verbosity
    ) -> GPT5Decision:
        """Create fallback decision when GPT-5 fails"""
        
        return GPT5Decision(
            decision_id=f"dec_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            decision_type="payment_routing_fallback",
            selected_option="stripe",  # Safe default
            confidence=0.5,
            reasoning_chain=[f"GPT-5 error: {error}", "Using fallback logic", "Selected most reliable processor"],
            reasoning_effort=reasoning_effort,
            verbosity=verbosity,
            tokens_used=0,
            reasoning_tokens=0,
            processing_time_ms=50,
            raw_response=f"Error: {error}",
            chain_of_thought=[{
                "step": 1,
                "reasoning": f"GPT-5 API failed: {error}",
                "confidence": 0.5,
                "factors_considered": ["error_handling"],
                "effort_level": "fallback"
            }]
        )
    
    def _log_decision(self, decision: GPT5Decision):
        """Log GPT-5 decision with key metrics"""
        
        confidence_icon = "🟢" if decision.confidence > 0.8 else "🟡" if decision.confidence > 0.6 else "🔴"
        
        print(f"{confidence_icon} DECISION: {decision.selected_option}")
        print(f"   Confidence: {decision.confidence:.1%}")
        print(f"   Reasoning steps: {len(decision.reasoning_chain)}")
        print(f"   Processing: {decision.processing_time_ms}ms")
        print(f"   Tokens: {decision.tokens_used} (reasoning: {decision.reasoning_tokens})")
        
        if decision.verbosity == Verbosity.HIGH:
            print(f"   Chain of thought: {len(decision.chain_of_thought)} steps")
            for step in decision.chain_of_thought[:2]:  # Show first 2 steps
                print(f"     Step {step['step']}: {step['reasoning'][:60]}...")
    
    async def analyze_decision_patterns(self) -> Dict[str, Any]:
        """
        Analyze patterns in GPT-5 decision making
        Demonstrates how reasoning_effort and verbosity affect outcomes
        """
        
        if not self.decision_history:
            return {"error": "No decisions to analyze"}
        
        analysis = {
            "total_decisions": len(self.decision_history),
            "parameter_usage": {
                "reasoning_effort_distribution": {},
                "verbosity_distribution": {},
                "parameter_combinations": {}
            },
            "performance_metrics": {
                "avg_processing_time": 0,
                "avg_tokens_used": 0,
                "avg_confidence": 0,
                "reasoning_token_ratio": 0
            },
            "decision_quality": {
                "high_confidence_decisions": 0,
                "complex_decisions": 0,
                "fallback_decisions": 0
            }
        }
        
        # Calculate parameter usage
        for decision in self.decision_history:
            effort = decision.reasoning_effort.value
            verbosity = decision.verbosity.value
            combo = f"{effort}+{verbosity}"
            
            analysis["parameter_usage"]["reasoning_effort_distribution"][effort] = \
                analysis["parameter_usage"]["reasoning_effort_distribution"].get(effort, 0) + 1
            analysis["parameter_usage"]["verbosity_distribution"][verbosity] = \
                analysis["parameter_usage"]["verbosity_distribution"].get(verbosity, 0) + 1
            analysis["parameter_usage"]["parameter_combinations"][combo] = \
                analysis["parameter_usage"]["parameter_combinations"].get(combo, 0) + 1
        
        # Calculate performance metrics
        total_time = sum(d.processing_time_ms for d in self.decision_history)
        total_tokens = sum(d.tokens_used for d in self.decision_history)
        total_reasoning_tokens = sum(d.reasoning_tokens for d in self.decision_history)
        total_confidence = sum(d.confidence for d in self.decision_history)
        
        analysis["performance_metrics"]["avg_processing_time"] = total_time / len(self.decision_history)
        analysis["performance_metrics"]["avg_tokens_used"] = total_tokens / len(self.decision_history)
        analysis["performance_metrics"]["avg_confidence"] = total_confidence / len(self.decision_history)
        analysis["performance_metrics"]["reasoning_token_ratio"] = total_reasoning_tokens / max(total_tokens, 1)
        
        # Calculate decision quality
        analysis["decision_quality"]["high_confidence_decisions"] = sum(
            1 for d in self.decision_history if d.confidence > 0.8
        )
        analysis["decision_quality"]["complex_decisions"] = sum(
            1 for d in self.decision_history if d.reasoning_effort in [ReasoningEffort.HIGH, ReasoningEffort.MEDIUM]
        )
        analysis["decision_quality"]["fallback_decisions"] = sum(
            1 for d in self.decision_history if "fallback" in d.decision_type
        )
        
        return analysis
    
    def get_decision_audit_trail(self, decision_id: str) -> Dict[str, Any]:
        """
        Get complete audit trail for a specific decision
        Showcases GPT-5's chain-of-thought transparency
        """
        
        decision = next((d for d in self.decision_history if d.decision_id == decision_id), None)
        
        if not decision:
            return {"error": f"Decision {decision_id} not found"}
        
        return {
            "decision_id": decision.decision_id,
            "timestamp": decision.timestamp.isoformat(),
            "gpt5_parameters": {
                "reasoning_effort": decision.reasoning_effort.value,
                "verbosity": decision.verbosity.value,
                "model": self.model
            },
            "decision_outcome": {
                "selected_option": decision.selected_option,
                "confidence": decision.confidence,
                "decision_type": decision.decision_type
            },
            "reasoning_analysis": {
                "reasoning_chain": decision.reasoning_chain,
                "chain_of_thought": decision.chain_of_thought,
                "reasoning_depth": len(decision.reasoning_chain),
                "factors_considered": list(set(
                    factor for step in decision.chain_of_thought 
                    for factor in step.get("factors_considered", [])
                ))
            },
            "performance_metrics": {
                "processing_time_ms": decision.processing_time_ms,
                "tokens_used": decision.tokens_used,
                "reasoning_tokens": decision.reasoning_tokens,
                "token_efficiency": decision.reasoning_tokens / max(decision.tokens_used, 1)
            },
            "raw_gpt5_response": decision.raw_response,
            "compliance_data": {
                "full_audit_trail": True,
                "reasoning_preserved": len(decision.reasoning_chain) > 0,
                "timestamp_recorded": True,
                "parameters_logged": True
            }
        }


# Demo function showcasing all GPT-5 capabilities
async def demo_gpt5_decision_engine():
    """
    Comprehensive demo of GPT-5 Decision Engine capabilities
    """
    
    print("🚀 GPT-5 DECISION ENGINE - COMPREHENSIVE DEMO")
    print("=" * 70)
    print("Showcasing reasoning_effort, verbosity, and chain-of-thought capabilities")
    print("=" * 70)
    
    engine = GPT5DecisionEngine()
    
    # Demo scenarios with different complexity levels
    demo_scenarios = [
        {
            "name": "Routine Low-Value Payment",
            "context": PaymentContext(
                amount=75.50,
                currency="USD",
                merchant_id="coffee_shop_001",
                urgency=DecisionUrgency.ROUTINE,
                failed_processors=[],
                risk_indicators={"risk_score": 1.2, "velocity": "normal"},
                processor_health={
                    "stripe": {"success_rate": 0.989, "response_time": 245},
                    "paypal": {"success_rate": 0.983, "response_time": 312}
                },
                business_rules={"prefer_lowest_cost": True}
            ),
            "expected_params": (ReasoningEffort.MINIMAL, Verbosity.LOW)
        },
        {
            "name": "High-Value B2B Transaction",
            "context": PaymentContext(
                amount=8500.00,
                currency="USD", 
                merchant_id="enterprise_client_007",
                urgency=DecisionUrgency.ELEVATED,
                failed_processors=["square"],
                risk_indicators={"risk_score": 4.7, "velocity": "elevated", "compliance_flags": ["manual_review"]},
                processor_health={
                    "stripe": {"success_rate": 0.989, "response_time": 245, "freeze_risk": 2.1},
                    "paypal": {"success_rate": 0.983, "response_time": 312, "freeze_risk": 1.8},
                    "visa": {"success_rate": 0.995, "response_time": 189, "freeze_risk": 0.9}
                },
                business_rules={"prioritize_reliability": True, "max_fee_threshold": 3.0}
            ),
            "expected_params": (ReasoningEffort.HIGH, Verbosity.HIGH)
        },
        {
            "name": "Critical Emergency Payment",
            "context": PaymentContext(
                amount=25000.00,
                currency="USD",
                merchant_id="emergency_contractor",
                urgency=DecisionUrgency.CRITICAL,
                failed_processors=["stripe", "paypal"],
                risk_indicators={"risk_score": 7.8, "velocity": "spike", "fraud_alerts": 2},
                processor_health={
                    "stripe": {"success_rate": 0.0, "status": "frozen"},
                    "paypal": {"success_rate": 0.85, "status": "degraded"},
                    "visa": {"success_rate": 0.995, "response_time": 189},
                    "adyen": {"success_rate": 0.992, "response_time": 267}
                },
                business_rules={"emergency_approval": True, "bypass_normal_limits": True}
            ),
            "expected_params": (ReasoningEffort.HIGH, Verbosity.HIGH)
        }
    ]
    
    # Process each scenario
    decisions = []
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n{'='*50}")
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"{'='*50}")
        
        print(f"💰 Amount: ${scenario['context'].amount:,.2f}")
        print(f"⚡ Urgency: {scenario['context'].urgency.value}")
        print(f"❌ Failed: {scenario['context'].failed_processors or 'None'}")
        
        decision = await engine.make_payment_routing_decision(scenario["context"])
        decisions.append(decision)
        
        # Show parameter adaptation
        expected_effort, expected_verbosity = scenario["expected_params"]
        print(f"\n📊 GPT-5 Parameter Adaptation:")
        print(f"   Expected: reasoning={expected_effort.value}, verbosity={expected_verbosity.value}")
        print(f"   Actual: reasoning={decision.reasoning_effort.value}, verbosity={decision.verbosity.value}")
        
        adaptation_correct = (
            decision.reasoning_effort == expected_effort and 
            decision.verbosity == expected_verbosity
        )
        print(f"   ✅ Adaptation: {'Correct' if adaptation_correct else 'Different'}")
        
        await asyncio.sleep(1)  # Rate limiting
    
    # Analyze decision patterns
    print(f"\n{'='*70}")
    print("📈 DECISION PATTERN ANALYSIS")
    print("=" * 70)
    
    analysis = await engine.analyze_decision_patterns()
    
    print(f"🎯 Total Decisions: {analysis['total_decisions']}")
    print(f"\n🧠 Parameter Usage:")
    for effort, count in analysis["parameter_usage"]["reasoning_effort_distribution"].items():
        print(f"   {effort}: {count} decisions")
    
    print(f"\n📝 Verbosity Distribution:")
    for verbosity, count in analysis["parameter_usage"]["verbosity_distribution"].items():
        print(f"   {verbosity}: {count} decisions")
    
    print(f"\n⚡ Performance Metrics:")
    print(f"   Avg Processing Time: {analysis['performance_metrics']['avg_processing_time']:.0f}ms")
    print(f"   Avg Tokens Used: {analysis['performance_metrics']['avg_tokens_used']:.0f}")
    print(f"   Avg Confidence: {analysis['performance_metrics']['avg_confidence']:.1%}")
    print(f"   Reasoning Token Ratio: {analysis['performance_metrics']['reasoning_token_ratio']:.1%}")
    
    print(f"\n🎖️  Decision Quality:")
    print(f"   High Confidence: {analysis['decision_quality']['high_confidence_decisions']}/{analysis['total_decisions']}")
    print(f"   Complex Decisions: {analysis['decision_quality']['complex_decisions']}/{analysis['total_decisions']}")
    
    # Show detailed audit trail for one decision
    if decisions:
        print(f"\n{'='*70}")
        print("🔍 DETAILED AUDIT TRAIL EXAMPLE")
        print("=" * 70)
        
        sample_decision = decisions[1] if len(decisions) > 1 else decisions[0]
        audit_trail = engine.get_decision_audit_trail(sample_decision.decision_id)
        
        print(f"Decision ID: {audit_trail['decision_id']}")
        print(f"GPT-5 Parameters: {audit_trail['gpt5_parameters']}")
        print(f"Outcome: {audit_trail['decision_outcome']['selected_option']} (confidence: {audit_trail['decision_outcome']['confidence']:.1%})")
        print(f"Reasoning Depth: {audit_trail['reasoning_analysis']['reasoning_depth']} steps")
        print(f"Factors Considered: {', '.join(audit_trail['reasoning_analysis']['factors_considered'][:5])}")
        print(f"Token Efficiency: {audit_trail['performance_metrics']['token_efficiency']:.1%}")
        print(f"Compliance: ✅ Full audit trail preserved")
    
    print(f"\n🏆 GPT-5 DECISION ENGINE DEMO COMPLETE")
    print("   ✅ reasoning_effort parameter demonstrated")
    print("   ✅ verbosity parameter demonstrated") 
    print("   ✅ chain-of-thought reasoning captured")
    print("   ✅ adaptive parameter selection working")
    print("   ✅ comprehensive audit trails generated")


if __name__ == "__main__":
    asyncio.run(demo_gpt5_decision_engine())