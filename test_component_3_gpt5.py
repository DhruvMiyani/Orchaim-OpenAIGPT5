"""
Component 3 Test Module: GPT-5 Integration
Tests GPT-5 API integration, reasoning effort, and verbosity
"""

import asyncio
import os
import sys
from datetime import datetime
sys.path.append('..')
sys.path.append('../..')
from gpt5_client import GPT5Client


class GPT5IntegrationTester:
    """Isolated tester for GPT-5 integration component"""
    
    def __init__(self):
        self.client = GPT5Client()
        self.results = []
    
    def test_gpt5_initialization(self) -> dict:
        """Test GPT-5 client initialization"""
        try:
            assert self.client.model == "gpt-5", "Must use GPT-5 model"
            assert self.client.api_key is not None, "API key required"
            
            return {
                "test_name": "gpt5_initialization",
                "success": True,
                "model": self.client.model,
                "api_key_present": bool(self.client.api_key)
            }
        except Exception as e:
            return {
                "test_name": "gpt5_initialization", 
                "success": False,
                "error": str(e)
            }
    
    async def test_routing_decision(self) -> dict:
        """Test GPT-5 routing decision making"""
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
                "stripe": {"frozen": False},
                "paypal": {"frozen": False}
            }
        }
        
        try:
            result = await self.client.make_routing_decision(
                context=context,
                reasoning_effort="medium",
                verbosity="medium"
            )
            
            return {
                "test_name": "routing_decision",
                "success": True,
                "selected_processor": result.get("selected_processor"),
                "confidence": result.get("confidence"),
                "has_reasoning": bool(result.get("reasoning"))
            }
        except Exception as e:
            return {
                "test_name": "routing_decision",
                "success": False,
                "error": str(e)
            }
    
    async def test_reasoning_effort_levels(self) -> dict:
        """Test different reasoning effort levels"""
        context = {
            "transaction": {"amount": 100, "currency": "USD", "merchant_id": "test"},
            "processors": [{"id": "stripe", "fee_percentage": 2.9}],
            "processor_health": {"stripe": {"frozen": False}}
        }
        
        efforts = ["minimal", "medium", "high"]
        results = {}
        
        try:
            for effort in efforts:
                start_time = datetime.now()
                
                result = await self.client.make_routing_decision(
                    context=context,
                    reasoning_effort=effort,
                    verbosity="low"
                )
                
                elapsed = (datetime.now() - start_time).total_seconds() * 1000
                results[effort] = {
                    "time_ms": elapsed,
                    "success": bool(result.get("selected_processor"))
                }
            
            return {
                "test_name": "reasoning_effort_levels",
                "success": True,
                "results": results
            }
        except Exception as e:
            return {
                "test_name": "reasoning_effort_levels",
                "success": False,
                "error": str(e)
            }
    
    async def test_synthetic_data_generation(self) -> dict:
        """Test GPT-5 synthetic data generation"""
        try:
            result = await self.client.generate_synthetic_data(
                pattern_type="normal",
                context={
                    "business_type": "B2B SaaS",
                    "transaction_count": 10
                },
                reasoning_effort="high",
                verbosity="low"
            )
            
            return {
                "test_name": "synthetic_data_generation",
                "success": True,
                "pattern_type": result.get("pattern_type"),
                "has_generation_plan": bool(result.get("generation_plan")),
                "reasoning_tokens": result.get("parameters_used", {}).get("reasoning_tokens", 0)
            }
        except Exception as e:
            return {
                "test_name": "synthetic_data_generation",
                "success": False,
                "error": str(e)
            }
    
    async def test_verbosity_control(self) -> dict:
        """Test GPT-5 verbosity parameter control"""
        context = {
            "transaction": {"amount": 500, "currency": "USD"},
            "processors": [{"id": "stripe"}],
            "processor_health": {"stripe": {"frozen": False}}
        }
        
        verbosity_levels = ["low", "medium", "high"]
        results = {}
        
        try:
            for verbosity in verbosity_levels:
                result = await self.client.make_routing_decision(
                    context=context,
                    reasoning_effort="medium",
                    verbosity=verbosity
                )
                
                reasoning_length = len(result.get("reasoning", ""))
                results[verbosity] = {
                    "reasoning_length": reasoning_length,
                    "success": bool(result.get("selected_processor"))
                }
            
            return {
                "test_name": "verbosity_control",
                "success": True,
                "results": results
            }
        except Exception as e:
            return {
                "test_name": "verbosity_control",
                "success": False,
                "error": str(e)
            }
    
    async def run_all_tests(self) -> list:
        """Execute all GPT-5 integration tests"""
        print("Testing Component 3: GPT-5 Integration...")
        
        # Sync test
        init_result = self.test_gpt5_initialization()
        self.results.append(init_result)
        
        # Async tests
        async_tests = [
            self.test_routing_decision(),
            self.test_reasoning_effort_levels(),
            self.test_synthetic_data_generation(),
            self.test_verbosity_control()
        ]
        
        async_results = await asyncio.gather(*async_tests, return_exceptions=True)
        
        for result in async_results:
            if isinstance(result, Exception):
                self.results.append({
                    "test_name": "async_error",
                    "success": False,
                    "error": str(result)
                })
            else:
                self.results.append(result)
        
        return self.results


async def validate_component_3():
    """Main validation function for Component 3"""
    tester = GPT5IntegrationTester()
    results = await tester.run_all_tests()
    
    passed = sum(1 for r in results if r.get("success", False))
    total = len(results)
    
    print(f"\nComponent 3 Results: {passed}/{total} tests passed")
    
    for result in results:
        status = "PASS" if result.get("success") else "FAIL"
        test_name = result.get("test_name", "unknown")
        print(f"[{status}] {test_name}")
        
        if result.get("success"):
            # Show key metrics for passed tests
            if test_name == "gpt5_initialization":
                print(f"      Model: {result.get('model')}")
            elif test_name == "routing_decision":
                print(f"      Selected: {result.get('selected_processor')}")
                print(f"      Confidence: {result.get('confidence')}")
            elif test_name == "reasoning_effort_levels":
                for effort, data in result.get("results", {}).items():
                    print(f"      {effort}: {data.get('time_ms', 0):.0f}ms")
        else:
            print(f"      Error: {result.get('error', 'Unknown error')}")
    
    return passed >= total * 0.8  # 80% pass rate acceptable


if __name__ == "__main__":
    success = asyncio.run(validate_component_3())
    print(f"\nComponent 3 Status: {'VALIDATED' if success else 'NEEDS REVIEW'}")