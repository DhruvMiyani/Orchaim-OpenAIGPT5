"""
Simple GPT-5 Component 2 Test
Tests core GPT-5 functionality with API key
"""

import asyncio
from gpt5_decision_engine import (
    GPT5DecisionEngine, PaymentContext, DecisionUrgency,
    ReasoningEffort, Verbosity
)


async def test_gpt5_basic():
    """Basic GPT-5 functionality test"""
    
    print("🧪 TESTING GPT-5 DECISION ENGINE")
    print("=" * 50)
    
    engine = GPT5DecisionEngine()
    
    # Simple test scenario
    context = PaymentContext(
        amount=1500.00,
        currency="USD",
        merchant_id="test_merchant",
        urgency=DecisionUrgency.NORMAL,
        failed_processors=[],
        risk_indicators={"risk_score": 2.5},
        processor_health={
            "stripe": {"success_rate": 0.99, "fees": 2.9},
            "paypal": {"success_rate": 0.97, "fees": 3.5}
        },
        business_rules={"prefer_reliability": True}
    )
    
    print(f"💰 Test Payment: ${context.amount} {context.currency}")
    print(f"🏪 Merchant: {context.merchant_id}")
    print(f"⚡ Urgency: {context.urgency.value}")
    
    # Test different parameter combinations
    test_cases = [
        (ReasoningEffort.LOW, Verbosity.LOW, "Quick decision"),
        (ReasoningEffort.HIGH, Verbosity.HIGH, "Thorough analysis")
    ]
    
    for reasoning_effort, verbosity, description in test_cases:
        print(f"\n🎯 {description}")
        print(f"   Parameters: reasoning={reasoning_effort.value}, verbosity={verbosity.value}")
        
        try:
            decision = await engine.make_payment_routing_decision(
                context,
                reasoning_effort=reasoning_effort,
                verbosity=verbosity
            )
            
            print(f"   ✅ SUCCESS")
            print(f"   Processor: {decision.selected_option}")
            print(f"   Confidence: {decision.confidence:.1%}")
            print(f"   Reasoning steps: {len(decision.reasoning_chain)}")
            print(f"   Tokens used: {decision.tokens_used}")
            print(f"   Processing time: {decision.processing_time_ms}ms")
            
            # Show first reasoning step
            if decision.reasoning_chain:
                print(f"   Sample reasoning: {decision.reasoning_chain[0][:100]}...")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n🏆 GPT-5 ENGINE TEST COMPLETE")
    
    # Show decision history
    if engine.decision_history:
        print(f"\n📊 DECISIONS MADE: {len(engine.decision_history)}")
        for i, decision in enumerate(engine.decision_history, 1):
            print(f"   {i}. {decision.selected_option} (confidence: {decision.confidence:.1%})")


if __name__ == "__main__":
    asyncio.run(test_gpt5_basic())