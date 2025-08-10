"""
Intelligent Payment Router with GPT-5 Reasoning
Solves the core problem: When Stripe fails/freezes, intelligently reroute payments
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import asyncio
import json
from enum import Enum

from processors.base import (
    PaymentProcessor, 
    PaymentRequest, 
    PaymentResponse, 
    PaymentStatus,
    ProcessorStatus
)


class FailureType(Enum):
    ACCOUNT_FROZEN = "account_frozen"
    RATE_LIMITED = "rate_limited"  
    NETWORK_ERROR = "network_error"
    DECLINED = "declined"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    FRAUD_SUSPECTED = "fraud_suspected"
    COMPLIANCE_ISSUE = "compliance_issue"
    TEMPORARY_OUTAGE = "temporary_outage"


@dataclass
class ProcessorFailure:
    processor_id: str
    failure_type: FailureType
    error_code: str
    error_message: str
    timestamp: datetime
    retry_after: Optional[datetime] = None
    permanent: bool = False


@dataclass 
class RoutingDecision:
    selected_processor: str
    reasoning: str
    confidence: float
    fallback_chain: List[str]
    gpt5_params: Dict[str, Any]
    decision_time_ms: float


class GPT5Router:
    """
    Uses GPT-5's reasoning to intelligently route payments when processors fail.
    Key scenarios:
    - Stripe account frozen → route to PayPal/Visa
    - High-risk transaction → use processor with best fraud protection
    - Network issues → retry with different region processor
    """
    
    def __init__(self, openai_api_key: str = None):
        self.api_key = openai_api_key or "mock_key_for_demo"
        self.failure_history: List[ProcessorFailure] = []
        self.routing_decisions: List[RoutingDecision] = []
        
        # Processor health tracking
        self.processor_health = {
            "stripe": {"frozen": False, "last_success": None, "failure_count": 0},
            "paypal": {"frozen": False, "last_success": None, "failure_count": 0},
            "visa": {"frozen": False, "last_success": None, "failure_count": 0}
        }
    
    async def make_routing_decision(
        self,
        request: PaymentRequest,
        available_processors: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        reasoning_effort: str = "medium"
    ) -> RoutingDecision:
        """
        Core routing logic using GPT-5's reasoning capabilities.
        
        reasoning_effort options:
        - "minimal": Fast decisions for routine payments
        - "low": Basic analysis for standard transactions  
        - "medium": Balanced reasoning for most cases
        - "high": Deep analysis for high-value or complex scenarios
        """
        
        start_time = datetime.utcnow()
        
        # Determine reasoning effort based on transaction
        if not reasoning_effort:
            reasoning_effort = self._determine_reasoning_effort(request, context)
        
        # Prepare context for GPT-5
        gpt5_context = self._prepare_gpt5_context(
            request, 
            available_processors, 
            context
        )
        
        # Simulate GPT-5 API call (replace with actual OpenAI call)
        decision = await self._call_gpt5_reasoning(
            gpt5_context,
            reasoning_effort=reasoning_effort,
            verbosity="low" if request.amount < 100 else "medium"
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        routing = RoutingDecision(
            selected_processor=decision["processor"],
            reasoning=decision["reasoning"],
            confidence=decision["confidence"],
            fallback_chain=decision["fallback_chain"],
            gpt5_params={
                "reasoning_effort": reasoning_effort,
                "verbosity": decision.get("verbosity", "medium"),
                "reasoning_tokens": decision.get("reasoning_tokens", 0)
            },
            decision_time_ms=processing_time
        )
        
        self.routing_decisions.append(routing)
        return routing
    
    def _determine_reasoning_effort(
        self, 
        request: PaymentRequest,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Automatically determine reasoning effort based on transaction characteristics.
        """
        
        # Minimal effort for small, routine transactions
        if request.amount < 10 and not context.get("failures"):
            return "minimal"
        
        # Low effort for standard transactions with no issues
        if request.amount < 100 and not context.get("high_risk"):
            return "low"
        
        # High effort for complex scenarios
        if any([
            request.amount > 10000,
            context.get("account_frozen"),
            context.get("multiple_failures"),
            context.get("high_risk"),
            context.get("compliance_check")
        ]):
            return "high"
        
        # Default to medium
        return "medium"
    
    def _prepare_gpt5_context(
        self,
        request: PaymentRequest,
        available_processors: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepare context for GPT-5 to make routing decision.
        """
        
        # Get recent failures for this merchant
        recent_failures = [
            f for f in self.failure_history
            if f.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]
        
        return {
            "transaction": {
                "amount": request.amount,
                "currency": request.currency,
                "merchant_id": request.merchant_id,
                "risk_indicators": context.get("risk_indicators", {})
            },
            "processors": available_processors,
            "failures": [
                {
                    "processor": f.processor_id,
                    "type": f.failure_type.value,
                    "message": f.error_message,
                    "permanent": f.permanent
                }
                for f in recent_failures
            ],
            "processor_health": self.processor_health,
            "business_context": {
                "primary_processor_frozen": context.get("account_frozen", False),
                "urgency": context.get("urgency", "normal"),
                "customer_type": context.get("customer_type", "standard")
            }
        }
    
    async def _call_gpt5_reasoning(
        self,
        context: Dict[str, Any],
        reasoning_effort: str = "medium",
        verbosity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Simulate GPT-5 API call with reasoning parameters.
        In production, replace with actual OpenAI API call.
        """
        
        # Build the prompt based on context
        prompt = self._build_routing_prompt(context)
        
        # Simulate different reasoning efforts
        await asyncio.sleep(0.1 if reasoning_effort == "minimal" else 0.3)
        
        # Simulate GPT-5 decision logic
        if context["business_context"]["primary_processor_frozen"]:
            # Stripe is frozen - must use alternative
            if "paypal" in [p["id"] for p in context["processors"]]:
                return {
                    "processor": "paypal",
                    "reasoning": "Primary processor (Stripe) is frozen. Routing to PayPal as it has good acceptance rates and is immediately available.",
                    "confidence": 0.95,
                    "fallback_chain": ["paypal", "visa"],
                    "verbosity": verbosity,
                    "reasoning_tokens": 150 if reasoning_effort == "high" else 50
                }
            else:
                return {
                    "processor": "visa",
                    "reasoning": "Stripe account frozen. Using Visa Direct as fallback for card processing.",
                    "confidence": 0.90,
                    "fallback_chain": ["visa"],
                    "verbosity": verbosity,
                    "reasoning_tokens": 100
                }
        
        # Normal routing - choose based on success rates and fees
        best_processor = self._select_best_processor(context)
        
        return {
            "processor": best_processor,
            "reasoning": self._generate_reasoning(best_processor, context, reasoning_effort),
            "confidence": 0.85,
            "fallback_chain": self._generate_fallback_chain(best_processor, context),
            "verbosity": verbosity,
            "reasoning_tokens": self._estimate_reasoning_tokens(reasoning_effort)
        }
    
    def _build_routing_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for GPT-5 based on context."""
        
        prompt = f"""
        Payment routing decision needed:
        Amount: ${context['transaction']['amount']} {context['transaction']['currency']}
        
        Available processors:
        {json.dumps(context['processors'], indent=2)}
        
        Recent failures:
        {json.dumps(context['failures'], indent=2)}
        
        Requirements:
        1. Maximize payment success probability
        2. Minimize fees where possible
        3. Avoid processors with recent failures
        4. Consider compliance and risk factors
        
        Select the best processor and explain your reasoning.
        """
        
        if context["business_context"]["primary_processor_frozen"]:
            prompt += "\nCRITICAL: Primary processor (Stripe) is currently frozen. Must use alternative."
        
        return prompt
    
    def _select_best_processor(self, context: Dict[str, Any]) -> str:
        """Simple processor selection logic for demo."""
        
        processors = context["processors"]
        
        # Filter out recently failed processors
        failed_ids = [f["processor"] for f in context["failures"] if not f.get("permanent")]
        available = [p for p in processors if p["id"] not in failed_ids]
        
        if not available:
            available = processors  # Use all if none available
        
        # Sort by success rate and fees
        available.sort(
            key=lambda p: (-p.get("metrics", {}).get("success_rate", 0), 
                          p.get("fee_percentage", 99))
        )
        
        return available[0]["id"] if available else "stripe"
    
    def _generate_reasoning(
        self, 
        processor: str, 
        context: Dict[str, Any],
        effort: str
    ) -> str:
        """Generate reasoning explanation based on effort level."""
        
        if effort == "minimal":
            return f"Selected {processor} - available and suitable."
        
        elif effort == "low":
            return f"Chose {processor} based on availability and success rate."
        
        elif effort == "high":
            amount = context['transaction']['amount']
            failures = len(context['failures'])
            return (
                f"After analyzing {len(context['processors'])} processors with "
                f"{failures} recent failures, selected {processor}. "
                f"Key factors: Transaction amount ${amount} fits processor limits, "
                f"processor has 95%+ success rate, no recent failures, "
                f"and acceptable fee structure. This provides optimal balance of "
                f"reliability and cost-effectiveness."
            )
        
        # Medium (default)
        return (
            f"Selected {processor} as primary processor. "
            f"It offers good success rates with reasonable fees for this transaction type."
        )
    
    def _generate_fallback_chain(
        self, 
        primary: str, 
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate ordered fallback processor list."""
        
        all_processors = ["stripe", "paypal", "visa"]
        fallbacks = [p for p in all_processors if p != primary]
        
        # Prioritize based on context
        if context['transaction']['amount'] > 1000:
            # For large amounts, prioritize reliability
            fallbacks.sort(key=lambda p: p == "visa")
        
        return fallbacks
    
    def _estimate_reasoning_tokens(self, effort: str) -> int:
        """Estimate reasoning tokens based on effort level."""
        
        tokens = {
            "minimal": 10,
            "low": 50,
            "medium": 150,
            "high": 500
        }
        return tokens.get(effort, 150)
    
    def record_failure(
        self,
        processor_id: str,
        failure_type: FailureType,
        error_code: str,
        error_message: str,
        permanent: bool = False
    ):
        """Record a processor failure for future routing decisions."""
        
        failure = ProcessorFailure(
            processor_id=processor_id,
            failure_type=failure_type,
            error_code=error_code,
            error_message=error_message,
            timestamp=datetime.utcnow(),
            permanent=permanent,
            retry_after=datetime.utcnow() + timedelta(minutes=30) if not permanent else None
        )
        
        self.failure_history.append(failure)
        
        # Update processor health
        if processor_id in self.processor_health:
            self.processor_health[processor_id]["failure_count"] += 1
            if permanent or failure_type == FailureType.ACCOUNT_FROZEN:
                self.processor_health[processor_id]["frozen"] = True
    
    def record_success(self, processor_id: str):
        """Record successful payment for processor health tracking."""
        
        if processor_id in self.processor_health:
            self.processor_health[processor_id]["last_success"] = datetime.utcnow()
            self.processor_health[processor_id]["failure_count"] = 0
    
    def get_routing_analytics(self) -> Dict[str, Any]:
        """Get analytics on routing decisions and performance."""
        
        total_decisions = len(self.routing_decisions)
        if total_decisions == 0:
            return {"message": "No routing decisions yet"}
        
        # Analyze reasoning effort distribution
        effort_dist = {}
        for decision in self.routing_decisions:
            effort = decision.gpt5_params.get("reasoning_effort", "medium")
            effort_dist[effort] = effort_dist.get(effort, 0) + 1
        
        # Average decision time by effort
        avg_time_by_effort = {}
        for effort in ["minimal", "low", "medium", "high"]:
            times = [
                d.decision_time_ms for d in self.routing_decisions
                if d.gpt5_params.get("reasoning_effort") == effort
            ]
            if times:
                avg_time_by_effort[effort] = sum(times) / len(times)
        
        return {
            "total_routing_decisions": total_decisions,
            "reasoning_effort_distribution": effort_dist,
            "average_decision_time_ms": {
                "by_effort": avg_time_by_effort,
                "overall": sum(d.decision_time_ms for d in self.routing_decisions) / total_decisions
            },
            "processor_health": self.processor_health,
            "recent_failures": len([
                f for f in self.failure_history
                if f.timestamp > datetime.utcnow() - timedelta(hours=1)
            ])
        }