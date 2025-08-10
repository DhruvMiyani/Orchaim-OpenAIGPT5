"""
GPT-5 Enhanced Stripe Balance Transaction Generator
Uses GPT-5 to intelligently generate realistic Stripe transaction patterns
Following exact Stripe schema and business rules
"""

import os
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
from openai import AsyncOpenAI


class TransactionType(Enum):
    CHARGE = "charge"
    REFUND = "refund"
    PAYOUT = "payout"
    ADJUSTMENT = "adjustment"
    APPLICATION_FEE = "application_fee"
    TRANSFER = "transfer"


class FailureCode(Enum):
    CARD_DECLINED = "card_declined"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    EXPIRED_CARD = "expired_card"
    FRAUD_DETECTED = "fraud_detected"
    PROCESSING_ERROR = "processing_error"


@dataclass
class StripeBalanceTransaction:
    """Exact Stripe balance_transaction schema"""
    id: str
    object: str = "balance_transaction"
    amount: int  # In cents
    available_on: int  # Unix timestamp
    created: int  # Unix timestamp
    currency: str = "usd"
    description: Optional[str] = None
    fee: int = 0
    fee_details: List[Dict[str, Any]] = field(default_factory=list)
    net: int = 0
    reporting_category: str = "charge"
    source: Optional[str] = None
    status: str = "available"
    type: str = "charge"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StripeCharge:
    """Exact Stripe charge schema"""
    id: str
    object: str = "charge"
    amount: int
    amount_captured: int
    amount_refunded: int = 0
    balance_transaction: str = ""
    captured: bool = True
    created: int = field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    currency: str = "usd"
    customer: Optional[str] = None
    description: Optional[str] = None
    failure_code: Optional[str] = None
    failure_message: Optional[str] = None
    paid: bool = True
    payment_method_details: Dict[str, Any] = field(default_factory=dict)
    receipt_email: Optional[str] = None
    refunded: bool = False
    status: str = "succeeded"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GPT5StripeDataGenerator:
    """
    Uses GPT-5 to generate intelligent Stripe transaction patterns
    that follow real business patterns and risk scenarios
    """
    
    def __init__(self, openai_api_key: str = None):
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            raise ValueError("OpenAI API key required for GPT-5 integration")
        
        # In-memory storage for demo
        self.balance_transactions: List[StripeBalanceTransaction] = []
        self.charges: List[StripeCharge] = []
        self.refunds: List[Dict[str, Any]] = []
        
        # Stripe risk thresholds
        self.risk_thresholds = {
            "refund_rate_warning": 0.05,  # 5% triggers review
            "refund_rate_freeze": 0.10,   # 10% likely freeze
            "chargeback_rate_freeze": 0.01,  # 1% triggers freeze
            "volume_spike_review": 10.0,  # 10x normal volume
            "amount_spike_review": 5.0    # 5x normal amount
        }
    
    async def generate_with_gpt5(
        self, 
        pattern_type: str,
        context: Dict[str, Any],
        reasoning_effort: str = "medium",
        verbosity: str = "low"
    ) -> Dict[str, Any]:
        """
        Use GPT-5 to generate realistic Stripe transaction patterns
        """
        
        system_prompt = """You are an expert in Stripe payment processing and transaction patterns.
        Generate realistic balance_transaction data following Stripe's exact schema.
        Consider real business patterns, risk factors, and Stripe's freeze policies."""
        
        user_prompt = f"""Generate a detailed plan for creating Stripe balance_transactions with pattern: {pattern_type}
        
        Context: {json.dumps(context, indent=2)}
        
        Requirements:
        1. Follow exact Stripe balance_transaction schema
        2. Include realistic fees (2.9% + $0.30 for cards)
        3. Create authentic timing patterns
        4. Include proper transaction IDs (txn_, ch_, re_, po_, etc.)
        5. Consider Stripe's risk thresholds:
           - Refund rate >5% triggers review
           - Chargeback rate >1% triggers freeze
           - Volume spike >10x triggers investigation
        
        Return a structured JSON plan with:
        - transaction_count: number of transactions to generate
        - timing_pattern: how to distribute over time
        - amount_distribution: realistic amounts for this pattern
        - risk_indicators: what risk signals this creates
        - expected_outcome: what Stripe would likely do
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-5",  # ALWAYS GPT-5, NO EXCEPTIONS
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=2000,
            response_format={"type": "json_object"},
            reasoning_effort=reasoning_effort,
            verbosity=verbosity
        )
        
        generation_plan = json.loads(response.choices[0].message.content)
        
        # Add GPT-5 metadata
        generation_plan["gpt5_metadata"] = {
            "reasoning_effort": reasoning_effort,
            "verbosity": verbosity,
            "tokens_used": response.usage.total_tokens,
            "reasoning_tokens": getattr(response.usage, 'reasoning_tokens', 0)
        }
        
        return generation_plan
    
    async def generate_normal_business_pattern(
        self, 
        days: int = 30,
        daily_volume: int = 50
    ) -> List[StripeBalanceTransaction]:
        """
        Generate normal business transactions using GPT-5 intelligence
        """
        
        context = {
            "business_type": "B2B SaaS",
            "typical_transaction": 85.00,
            "customer_base": 500,
            "days": days,
            "daily_volume": daily_volume
        }
        
        # Get GPT-5's generation plan
        plan = await self.generate_with_gpt5(
            pattern_type="normal_business",
            context=context,
            reasoning_effort="low",  # Simple pattern
            verbosity="low"
        )
        
        print(f"GPT-5 Generation Plan: {plan['expected_outcome']}")
        
        transactions = []
        start_date = datetime.utcnow() - timedelta(days=days)
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            # Follow GPT-5's timing pattern
            daily_count = self._apply_gpt5_timing(
                base_volume=daily_volume,
                day_of_week=current_date.weekday(),
                plan=plan
            )
            
            for _ in range(daily_count):
                # Generate charge
                amount = self._apply_gpt5_amount_distribution(
                    base_amount=85.00,
                    plan=plan
                )
                
                charge_id = f"ch_{uuid.uuid4().hex[:24]}"
                txn_id = f"txn_{uuid.uuid4().hex[:17]}"
                
                # Create balance transaction
                txn = StripeBalanceTransaction(
                    id=txn_id,
                    amount=int(amount * 100),  # Convert to cents
                    available_on=int((current_date + timedelta(days=2)).timestamp()),
                    created=int(current_date.timestamp()),
                    currency="usd",
                    description="Subscription payment",
                    fee=int((amount * 0.029 + 0.30) * 100),  # Stripe fees in cents
                    net=int((amount - (amount * 0.029 + 0.30)) * 100),
                    source=charge_id,
                    type="charge"
                )
                
                transactions.append(txn)
                self.balance_transactions.append(txn)
                
                # Occasionally add refunds (2% rate for normal)
                if random.random() < 0.02:
                    refund_txn = await self._generate_refund(txn, current_date)
                    transactions.append(refund_txn)
        
        return transactions
    
    async def generate_risk_scenario(
        self,
        scenario_type: str
    ) -> Dict[str, Any]:
        """
        Use GPT-5 to generate specific risk scenarios that trigger Stripe actions
        """
        
        scenarios = {
            "sudden_spike": {
                "description": "10-15x volume spike in 2 hours",
                "risk_level": "high",
                "expected_action": "account_review"
            },
            "high_refunds": {
                "description": "15% refund rate (vs 2% normal)",
                "risk_level": "critical",
                "expected_action": "account_freeze"
            },
            "chargeback_surge": {
                "description": "3% chargeback rate",
                "risk_level": "critical",
                "expected_action": "immediate_freeze"
            }
        }
        
        scenario = scenarios.get(scenario_type, scenarios["sudden_spike"])
        
        # Get GPT-5's intelligent generation plan
        plan = await self.generate_with_gpt5(
            pattern_type=scenario_type,
            context=scenario,
            reasoning_effort="high",  # Complex risk analysis
            verbosity="high"  # Detailed reasoning
        )
        
        print(f"GPT-5 Risk Analysis: {plan.get('risk_indicators', [])}")
        
        # Generate transactions based on GPT-5's plan
        transactions = await self._execute_gpt5_plan(plan, scenario_type)
        
        return {
            "scenario": scenario_type,
            "transactions": transactions,
            "risk_analysis": plan.get("risk_indicators", []),
            "expected_stripe_action": plan.get("expected_outcome", "unknown"),
            "gpt5_reasoning": plan.get("reasoning", ""),
            "gpt5_tokens_used": plan["gpt5_metadata"]["tokens_used"]
        }
    
    async def _execute_gpt5_plan(
        self, 
        plan: Dict[str, Any],
        scenario_type: str
    ) -> List[StripeBalanceTransaction]:
        """Execute GPT-5's generation plan"""
        
        transactions = []
        base_time = datetime.utcnow()
        
        if scenario_type == "sudden_spike":
            # Generate volume spike as planned by GPT-5
            spike_count = plan.get("transaction_count", 500)
            time_window = plan.get("timing_pattern", {}).get("window_hours", 2)
            
            for i in range(spike_count):
                amount = random.uniform(200, 2000)  # Large amounts
                
                txn = StripeBalanceTransaction(
                    id=f"txn_{uuid.uuid4().hex[:17]}",
                    amount=int(amount * 100),
                    available_on=int((base_time + timedelta(days=2)).timestamp()),
                    created=int((base_time + timedelta(minutes=random.randint(0, time_window*60))).timestamp()),
                    currency="usd",
                    description="Spike transaction - promotional event",
                    fee=int((amount * 0.029 + 0.30) * 100),
                    net=int((amount - (amount * 0.029 + 0.30)) * 100),
                    source=f"ch_{uuid.uuid4().hex[:24]}",
                    type="charge"
                )
                transactions.append(txn)
                
        elif scenario_type == "high_refunds":
            # Generate high refund pattern
            charge_count = plan.get("transaction_count", 100)
            refund_rate = plan.get("risk_indicators", {}).get("refund_rate", 0.15)
            
            for i in range(charge_count):
                # Create charge
                amount = random.uniform(50, 500)
                charge_time = base_time - timedelta(days=random.randint(1, 7))
                
                charge_txn = StripeBalanceTransaction(
                    id=f"txn_{uuid.uuid4().hex[:17]}",
                    amount=int(amount * 100),
                    available_on=int((charge_time + timedelta(days=2)).timestamp()),
                    created=int(charge_time.timestamp()),
                    currency="usd",
                    description="Product purchase",
                    fee=int((amount * 0.029 + 0.30) * 100),
                    net=int((amount - (amount * 0.029 + 0.30)) * 100),
                    source=f"ch_{uuid.uuid4().hex[:24]}",
                    type="charge"
                )
                transactions.append(charge_txn)
                
                # Add refund based on GPT-5's plan
                if random.random() < refund_rate:
                    refund_txn = await self._generate_refund(charge_txn, charge_time)
                    transactions.append(refund_txn)
        
        return transactions
    
    async def _generate_refund(
        self, 
        original_txn: StripeBalanceTransaction,
        original_date: datetime
    ) -> StripeBalanceTransaction:
        """Generate refund transaction"""
        
        refund_time = original_date + timedelta(hours=random.randint(2, 72))
        
        return StripeBalanceTransaction(
            id=f"txn_{uuid.uuid4().hex[:17]}",
            amount=-original_txn.amount,  # Negative amount for refund
            available_on=int((refund_time + timedelta(days=2)).timestamp()),
            created=int(refund_time.timestamp()),
            currency=original_txn.currency,
            description="Customer refund",
            fee=0,  # No fee on refunds
            net=-original_txn.amount,
            source=f"re_{uuid.uuid4().hex[:24]}",
            type="refund"
        )
    
    def _apply_gpt5_timing(
        self, 
        base_volume: int,
        day_of_week: int,
        plan: Dict[str, Any]
    ) -> int:
        """Apply GPT-5's timing pattern"""
        
        # Business days have more volume
        if day_of_week < 5:  # Monday-Friday
            multiplier = plan.get("timing_pattern", {}).get("weekday_multiplier", 1.0)
        else:  # Weekend
            multiplier = plan.get("timing_pattern", {}).get("weekend_multiplier", 0.5)
        
        return int(base_volume * multiplier * random.uniform(0.8, 1.2))
    
    def _apply_gpt5_amount_distribution(
        self, 
        base_amount: float,
        plan: Dict[str, Any]
    ) -> float:
        """Apply GPT-5's amount distribution"""
        
        distribution = plan.get("amount_distribution", {})
        
        if distribution.get("type") == "normal":
            mean = distribution.get("mean", base_amount)
            std = distribution.get("std", base_amount * 0.3)
            return max(10, random.gauss(mean, std))
        elif distribution.get("type") == "uniform":
            min_amt = distribution.get("min", base_amount * 0.5)
            max_amt = distribution.get("max", base_amount * 2.0)
            return random.uniform(min_amt, max_amt)
        else:
            return base_amount * random.uniform(0.5, 1.5)
    
    async def analyze_risk_with_gpt5(
        self,
        transactions: List[StripeBalanceTransaction]
    ) -> Dict[str, Any]:
        """
        Use GPT-5 to analyze transaction patterns for risk
        """
        
        # Calculate metrics
        charges = [t for t in transactions if t.type == "charge"]
        refunds = [t for t in transactions if t.type == "refund"]
        
        metrics = {
            "total_transactions": len(transactions),
            "charge_count": len(charges),
            "refund_count": len(refunds),
            "refund_rate": len(refunds) / max(len(charges), 1),
            "total_volume": sum(t.amount for t in charges) / 100,  # Convert to dollars
            "average_transaction": sum(t.amount for t in charges) / max(len(charges), 1) / 100
        }
        
        # GPT-5 risk analysis
        response = await self.client.chat.completions.create(
            model="gpt-5",  # ALWAYS GPT-5, NO EXCEPTIONS
            messages=[
                {
                    "role": "system",
                    "content": "You are a Stripe risk analyst. Analyze transaction patterns for freeze risk."
                },
                {
                    "role": "user",
                    "content": f"""Analyze these transaction metrics for Stripe account freeze risk:
                    
                    {json.dumps(metrics, indent=2)}
                    
                    Stripe thresholds:
                    - Refund rate >5%: Review triggered
                    - Refund rate >10%: Likely freeze
                    - Chargeback rate >1%: Immediate freeze
                    
                    Provide:
                    1. Risk level (low/medium/high/critical)
                    2. Freeze probability (0-100%)
                    3. Specific concerns
                    4. Recommendations
                    """
                }
            ],
            max_completion_tokens=1000,
            reasoning_effort="high",
            verbosity="high"
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "metrics": metrics,
            "gpt5_analysis": analysis,
            "risk_level": self._extract_risk_level(analysis),
            "freeze_probability": self._extract_freeze_probability(analysis),
            "gpt5_tokens": response.usage.total_tokens
        }
    
    def _extract_risk_level(self, analysis: str) -> str:
        """Extract risk level from GPT-5 analysis"""
        
        analysis_lower = analysis.lower()
        if "critical" in analysis_lower:
            return "critical"
        elif "high" in analysis_lower:
            return "high"
        elif "medium" in analysis_lower:
            return "medium"
        else:
            return "low"
    
    def _extract_freeze_probability(self, analysis: str) -> float:
        """Extract freeze probability from GPT-5 analysis"""
        
        import re
        match = re.search(r'(\d+)%', analysis)
        if match:
            return float(match.group(1)) / 100
        return 0.0
    
    def export_to_sql_format(self, transactions: List[StripeBalanceTransaction]) -> str:
        """Export as SQL INSERT statements matching Stripe schema"""
        
        sql_statements = []
        
        for txn in transactions:
            sql = f"""INSERT INTO balance_transactions 
            (id, amount, available_on, created, currency, description, fee, net, source, status, type)
            VALUES ('{txn.id}', {txn.amount}, {txn.available_on}, {txn.created}, 
                    '{txn.currency}', '{txn.description}', {txn.fee}, {txn.net}, 
                    '{txn.source}', '{txn.status}', '{txn.type}');"""
            
            sql_statements.append(sql)
        
        return "\n".join(sql_statements)


# Demo function
async def demo_gpt5_stripe_generator():
    """Demonstrate GPT-5 powered Stripe data generation"""
    
    print("GPT-5 STRIPE DATA GENERATOR DEMO")
    print("=" * 60)
    
    generator = GPT5StripeDataGenerator()
    
    # 1. Generate normal business pattern
    print("\n1. Generating normal business pattern with GPT-5...")
    normal_txns = await generator.generate_normal_business_pattern(days=7, daily_volume=20)
    print(f"   Generated {len(normal_txns)} normal transactions")
    
    # 2. Generate risk scenario
    print("\n2. Generating high-risk scenario with GPT-5...")
    risk_result = await generator.generate_risk_scenario("high_refunds")
    print(f"   Scenario: {risk_result['scenario']}")
    print(f"   Transactions: {len(risk_result['transactions'])}")
    print(f"   Expected Stripe action: {risk_result['expected_stripe_action']}")
    print(f"   GPT-5 tokens used: {risk_result['gpt5_tokens_used']}")
    
    # 3. Analyze risk with GPT-5
    print("\n3. Analyzing risk with GPT-5...")
    all_txns = normal_txns + risk_result['transactions']
    risk_analysis = await generator.analyze_risk_with_gpt5(all_txns)
    print(f"   Risk level: {risk_analysis['risk_level']}")
    print(f"   Freeze probability: {risk_analysis['freeze_probability']:.1%}")
    print(f"   Refund rate: {risk_analysis['metrics']['refund_rate']:.1%}")
    
    # 4. Export data
    print("\n4. Exporting data...")
    sql_export = generator.export_to_sql_format(all_txns[:5])  # Sample
    print("   Sample SQL export:")
    print(sql_export[:500] + "...")
    
    # Save to file
    with open("gpt5_stripe_transactions.json", "w") as f:
        json.dump([t.to_dict() for t in all_txns], f, indent=2)
    
    print(f"\n✅ Data saved to gpt5_stripe_transactions.json")
    print(f"   Total transactions: {len(all_txns)}")
    print(f"   Total GPT-5 tokens used: {risk_result['gpt5_tokens_used'] + risk_analysis['gpt5_tokens']}")


if __name__ == "__main__":
    asyncio.run(demo_gpt5_stripe_generator())