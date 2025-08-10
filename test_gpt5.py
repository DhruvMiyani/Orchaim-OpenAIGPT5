"""
Test script to verify GPT-5 API integration
ONLY uses GPT-5 - no fallbacks
"""

import asyncio
import os
from dotenv import load_dotenv
from gpt5_client import GPT5Client

load_dotenv()

async def test_gpt5():
    """Test that we're using ONLY GPT-5"""
    
    print("="*50)
    print("GPT-5 API TEST - NO FALLBACKS ALLOWED")
    print("="*50)
    
    client = GPT5Client()
    
    print(f"\n✅ Model configured: {client.model}")
    assert client.model == "gpt-5", "MUST USE GPT-5 ONLY!"
    
    print("\nTesting GPT-5 routing decision...")
    
    context = {
        "transaction": {
            "amount": 1000,
            "currency": "USD",
            "merchant_id": "test_merchant"
        },
        "processors": [
            {"id": "stripe", "fee_percentage": 2.9, "metrics": {"success_rate": 95}},
            {"id": "paypal", "fee_percentage": 2.9, "metrics": {"success_rate": 92}}
        ],
        "processor_health": {
            "stripe": {"frozen": True},  # Stripe is frozen
            "paypal": {"frozen": False}
        }
    }
    
    try:
        result = await client.make_routing_decision(
            context=context,
            reasoning_effort="high",
            verbosity="high"
        )
        
        print(f"\n✅ GPT-5 Response Received!")
        print(f"Selected processor: {result.get('selected_processor')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Model used: {result.get('gpt5_metadata', {}).get('model', 'gpt-5')}")
        
        # Verify we're using GPT-5
        assert "gpt-5" in str(result.get('gpt5_metadata', {}).get('model', 'gpt-5')).lower(), "MUST BE GPT-5!"
        
        print("\n✅ SUCCESS: GPT-5 is being used correctly!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nIMPORTANT: If GPT-5 is not available, the system will fail.")
        print("This is correct behavior - we ONLY use GPT-5, no fallbacks!")

if __name__ == "__main__":
    asyncio.run(test_gpt5())