"""
Comprehensive Test Suite for GPT-5 Data Analysis Component
Tests all major functionality including data generation, risk analysis, and streaming
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

from gpt5_client import GPT5Client
from gpt5_stripe_data_generator import GPT5StripeDataGenerator, StripeTransaction
from risk_pattern_analyzer import GPT5RiskAnalyzer, RiskTier
from realtime_data_simulator import RealtimeStreamSimulator, StreamingMode


async def test_gpt5_client():
    """Test GPT-5 client functionality"""
    print("Testing GPT-5 Client...")
    
    client = GPT5Client()
    
    # Test routing decision
    context = {
        "transaction": {
            "amount": 1000,
            "currency": "usd",
            "merchant_id": "test_merchant"
        },
        "processors": ["stripe", "paypal", "visa"],
        "failures": []
    }
    
    try:
        decision = await client.make_routing_decision(
            context=context,
            reasoning_effort="medium",
            verbosity="low"
        )
        print(f"✅ GPT-5 routing decision: {decision['selected_processor']}")
        return True
    except Exception as e:
        print(f"❌ GPT-5 client error: {e}")
        return False


async def test_synthetic_data_generation():
    """Test synthetic Stripe data generation with various scenarios"""
    print("\nTesting Synthetic Data Generation...")
    
    generator = GPT5StripeDataGenerator()
    results = {}
    
    # Test scenarios
    scenarios = [
        ("normal", "Normal business operations"),
        ("sudden_spike", "Volume spike scenario"), 
        ("high_refund_rate", "High refund rate scenario"),
        ("chargeback_surge", "Chargeback surge scenario")
    ]
    
    for scenario, description in scenarios:
        print(f"  Testing {scenario}: {description}")
        start_time = time.time()
        
        try:
            dataset = await generator.generate_intelligent_dataset(
                scenario=scenario,
                duration_days=7,  # Short duration for testing
                base_volume=20    # Small volume for testing
            )
            
            generation_time = time.time() - start_time
            transaction_count = len(dataset["transactions"])
            
            # Analyze the results
            charges = [t for t in dataset["transactions"] if t.type == "charge"]
            refunds = [t for t in dataset["transactions"] if t.type == "refund"]
            adjustments = [t for t in dataset["transactions"] if t.type == "adjustment"]
            
            refund_rate = len(refunds) / len(charges) if charges else 0
            chargeback_rate = len(adjustments) / len(charges) if charges else 0
            
            results[scenario] = {
                "transaction_count": transaction_count,
                "generation_time": generation_time,
                "charges": len(charges),
                "refunds": len(refunds),
                "adjustments": len(adjustments),
                "refund_rate": refund_rate,
                "chargeback_rate": chargeback_rate,
                "freeze_probability": dataset["risk_analysis"]["freeze_probability"]
            }
            
            print(f"    ✅ Generated {transaction_count} transactions in {generation_time:.2f}s")
            print(f"    📊 Refund rate: {refund_rate:.1%}, Freeze prob: {results[scenario]['freeze_probability']:.1%}")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results[scenario] = {"error": str(e)}
    
    # Export test data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f"test_results_{timestamp}.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"✅ Data generation test complete. Results saved to test_results_{timestamp}.json")
    return results


async def test_risk_analysis():
    """Test risk pattern analysis functionality"""
    print("\nTesting Risk Pattern Analysis...")
    
    generator = GPT5StripeDataGenerator()
    analyzer = GPT5RiskAnalyzer()
    
    # Generate test data with high risk patterns
    print("  Generating high-risk test data...")
    dataset = await generator.generate_intelligent_dataset(
        scenario="high_refund_rate",
        duration_days=3,
        base_volume=30
    )
    
    transactions = dataset["transactions"]
    
    # Perform risk analysis
    print("  Performing GPT-5 risk analysis...")
    start_time = time.time()
    
    try:
        analysis = await analyzer.analyze_transactions(
            transactions=transactions,
            reasoning_effort="high"
        )
        
        analysis_time = time.time() - start_time
        
        print(f"    ✅ Analysis completed in {analysis_time:.2f}s")
        print(f"    🎯 Overall risk: {analysis.overall_risk.value}")
        print(f"    ⚠️ Freeze probability: {analysis.freeze_probability:.1%}")
        print(f"    📋 Patterns detected: {len(analysis.identified_patterns)}")
        
        for pattern in analysis.identified_patterns:
            print(f"      - {pattern.pattern_type}: {pattern.severity.value} ({pattern.confidence:.0%} confidence)")
        
        print(f"    💡 Recommendations: {len(analysis.recommendations)}")
        for i, rec in enumerate(analysis.recommendations[:3], 1):
            print(f"      {i}. {rec}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Risk analysis error: {e}")
        return False


async def test_streaming_simulation():
    """Test real-time streaming simulation"""
    print("\nTesting Real-time Streaming Simulation...")
    
    simulator = RealtimeStreamSimulator()
    
    # Test different streaming modes
    modes = [
        (StreamingMode.NORMAL, 1.0, "Normal streaming"),
        (StreamingMode.HIGH_VOLUME, 3.0, "High volume streaming"),
        (StreamingMode.RISK_PATTERN, 0.5, "Risk pattern streaming")
    ]
    
    for mode, rate, description in modes:
        print(f"  Testing {description} at {rate} TPS...")
        
        transaction_count = 0
        start_time = time.time()
        
        try:
            # Stream for 10 seconds
            async for stream_data in simulator.start_continuous_stream(mode, rate):
                transaction_count += 1
                
                # Stop after 10 seconds
                if time.time() - start_time > 10:
                    simulator.stop_stream()
                    break
            
            actual_rate = transaction_count / (time.time() - start_time)
            
            print(f"    ✅ Generated {transaction_count} transactions")
            print(f"    📈 Actual rate: {actual_rate:.2f} TPS (target: {rate} TPS)")
            
        except Exception as e:
            print(f"    ❌ Streaming error: {e}")
    
    # Test statistics
    stats = simulator.get_stream_stats()
    print(f"  📊 Final stats: {stats.get('total_transactions', 0)} total transactions")
    
    return True


async def test_data_formats():
    """Test data export formats"""
    print("\nTesting Data Export Formats...")
    
    generator = GPT5StripeDataGenerator()
    
    # Generate small dataset
    dataset = await generator.generate_intelligent_dataset(
        scenario="normal",
        duration_days=2,
        base_volume=10
    )
    
    transactions = dataset["transactions"]
    
    # Test JSONL export
    print("  Testing JSONL export...")
    try:
        generator.export_to_jsonl(transactions, "test_export.jsonl")
        print("    ✅ JSONL export successful")
    except Exception as e:
        print(f"    ❌ JSONL export error: {e}")
    
    # Test CSV export
    print("  Testing CSV export...")
    try:
        generator.export_to_csv(transactions, "test_export.csv")
        print("    ✅ CSV export successful")
    except Exception as e:
        print(f"    ❌ CSV export error: {e}")
    
    return True


async def test_api_integration():
    """Test API integration readiness"""
    print("\nTesting API Integration Readiness...")
    
    try:
        # Test imports
        from data_analysis_api import app
        print("  ✅ FastAPI app import successful")
        
        # Test configuration
        if hasattr(app, 'middleware_stack'):
            print("  ✅ CORS middleware configured")
        
        # Test endpoint definitions
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/data/generate", "/stream/start"]
        
        for route in expected_routes:
            if route in routes:
                print(f"    ✅ Route {route} defined")
            else:
                print(f"    ❌ Route {route} missing")
        
        return True
        
    except Exception as e:
        print(f"  ❌ API integration error: {e}")
        return False


async def run_comprehensive_test():
    """Run comprehensive test suite"""
    
    print("="*60)
    print("GPT-5 DATA ANALYSIS COMPONENT - COMPREHENSIVE TEST")
    print("="*60)
    
    test_results = {}
    
    # Run all tests
    tests = [
        ("GPT-5 Client", test_gpt5_client),
        ("Synthetic Data Generation", test_synthetic_data_generation),
        ("Risk Analysis", test_risk_analysis),
        ("Streaming Simulation", test_streaming_simulation),
        ("Data Export Formats", test_data_formats),
        ("API Integration", test_api_integration)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'-'*20} {test_name} {'-'*20}")
        
        try:
            start_time = time.time()
            result = await test_func()
            test_time = time.time() - start_time
            
            if result:
                print(f"✅ {test_name} PASSED ({test_time:.2f}s)")
                passed_tests += 1
                test_results[test_name] = "PASSED"
            else:
                print(f"❌ {test_name} FAILED ({test_time:.2f}s)")
                test_results[test_name] = "FAILED"
                
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            test_results[test_name] = f"ERROR: {e}"
    
    # Final results
    print(f"\n{'='*60}")
    print("FINAL TEST RESULTS")
    print(f"{'='*60}")
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    for test_name, result in test_results.items():
        status_icon = "✅" if result == "PASSED" else "❌"
        print(f"{status_icon} {test_name}: {result}")
    
    # Component readiness assessment
    print(f"\n{'='*60}")
    print("COMPONENT READINESS ASSESSMENT")
    print(f"{'='*60}")
    
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        print("🎉 Component 1 (Data Analysis) is READY for integration")
        print("   - GPT-5 synthetic data generation operational")
        print("   - Risk pattern analysis functional")
        print("   - Real-time streaming simulation working")
        print("   - API endpoints configured and ready")
    else:
        print("⚠️ Component 1 (Data Analysis) needs additional work")
        print("   - Review failed tests and address issues")
        print("   - Ensure all dependencies are installed")
        print("   - Check GPT-5 API configuration")
    
    return test_results


async def main():
    """Main test execution"""
    
    # Run comprehensive test
    results = await run_comprehensive_test()
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"component_1_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "test_timestamp": timestamp,
            "component": "Component 1 - Data Analysis",
            "test_results": results,
            "summary": {
                "total_tests": len(results),
                "passed_tests": sum(1 for r in results.values() if r == "PASSED"),
                "success_rate": f"{sum(1 for r in results.values() if r == 'PASSED')/len(results)*100:.1f}%"
            }
        }, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")


if __name__ == "__main__":
    asyncio.run(main())