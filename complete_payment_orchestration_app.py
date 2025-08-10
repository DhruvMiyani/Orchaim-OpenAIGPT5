"""
COMPLETE PAYMENT ORCHESTRATION APP
Integrates all 3 components: Data Analysis + GPT-5 Engine + Routing Logic
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Component 1: Data Analysis imports
try:
    from component1_data_generator import GPT5StripeDataGenerator, StripeTransaction
    from component1_risk_analyzer import RiskPatternAnalyzer
    from component1_realtime_simulator import RealtimeDataSimulator
except ImportError:
    print("⚠️  Component 1 modules not found, using mock implementations")

# Component 2: GPT-5 Engine imports
from gpt5_working_demo import GPT5PaymentOrchestrator, ReasoningEffort, Verbosity

# Component 3: Routing Logic imports
try:
    import sys
    import os
    sys.path.append('/Users/dhruvmiyani/Downloads/OpenAIGPT5_windsurf/WorkTree/component-3-routing-logic')
    from processors.stripe import StripeProcessor
    from processors.paypal import PayPalProcessor
    from processors.visa import VisaProcessor
except ImportError:
    print("⚠️  Component 3 modules not found, using mock implementations")


# Pydantic models for API
class PaymentRequest(BaseModel):
    amount: float
    currency: str = "USD"
    merchant_id: str
    urgency: str = "normal"
    description: Optional[str] = None


class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    selected_processor: str
    confidence: float
    reasoning_effort: str
    verbosity: str
    processing_time_ms: int
    tokens_used: int
    reasoning_chain: List[str]
    created_at: str


@dataclass
class IntegratedPaymentFlow:
    """Complete payment flow through all 3 components"""
    flow_id: str
    payment_request: Dict[str, Any]
    
    # Component 1: Data Analysis
    risk_analysis: Optional[Dict[str, Any]] = None
    data_generation_tokens: int = 0
    
    # Component 2: GPT-5 Engine  
    gpt5_decision: Optional[Dict[str, Any]] = None
    gpt5_tokens: int = 0
    
    # Component 3: Routing Logic
    routing_result: Optional[Dict[str, Any]] = None
    final_status: str = "pending"
    
    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_processing_time: int = 0


class CompletePaymentOrchestrator:
    """
    Complete payment orchestration system integrating all 3 components:
    1. Component 1: Data Analysis & Risk Assessment
    2. Component 2: GPT-5 Engine Decision Making
    3. Component 3: Routing Logic & Processor Execution
    """
    
    def __init__(self):
        # Component 1: Data Analysis
        try:
            self.data_generator = GPT5StripeDataGenerator()
            self.risk_analyzer = RiskPatternAnalyzer()
            self.realtime_simulator = RealtimeDataSimulator()
        except:
            self.data_generator = None
            self.risk_analyzer = None
            self.realtime_simulator = None
        
        # Component 2: GPT-5 Engine
        self.gpt5_orchestrator = GPT5PaymentOrchestrator()
        
        # Component 3: Routing Logic (mock processors)
        self.processors = {
            "stripe": self._create_mock_processor("stripe", 0.989, 245),
            "paypal": self._create_mock_processor("paypal", 0.983, 312),
            "visa": self._create_mock_processor("visa", 0.995, 189),
            "square": self._create_mock_processor("square", 0.976, 334)
        }
        
        # System state
        self.active_flows: Dict[str, IntegratedPaymentFlow] = {}
        self.system_metrics = {
            "total_payments": 0,
            "successful_payments": 0,
            "gpt5_decisions": 0,
            "total_tokens_used": 0,
            "avg_processing_time": 0
        }
    
    def _create_mock_processor(self, name: str, success_rate: float, response_time: int):
        """Create mock processor for Component 3"""
        return {
            "name": name,
            "success_rate": success_rate,
            "response_time": response_time,
            "status": "healthy",
            "fee_percentage": 0.029 if name == "stripe" else 0.035 if name == "paypal" else 0.025,
            "fee_fixed": 0.30 if name != "paypal" else 0.49
        }
    
    async def process_payment(self, payment_request: PaymentRequest) -> IntegratedPaymentFlow:
        """
        Process payment through all 3 components
        """
        flow_id = f"flow_{uuid.uuid4().hex[:12]}"
        start_time = datetime.utcnow()
        
        # Create integrated flow
        flow = IntegratedPaymentFlow(
            flow_id=flow_id,
            payment_request=payment_request.dict()
        )
        self.active_flows[flow_id] = flow
        
        print(f"\n🔄 STARTING INTEGRATED PAYMENT FLOW: {flow_id}")
        print(f"   Amount: ${payment_request.amount:,.2f} {payment_request.currency}")
        print(f"   Merchant: {payment_request.merchant_id}")
        
        try:
            # COMPONENT 1: Data Analysis & Risk Assessment
            print(f"📊 Component 1: Data Analysis")
            risk_analysis = await self._component1_analysis(payment_request)
            flow.risk_analysis = risk_analysis
            flow.data_generation_tokens = risk_analysis.get("tokens_used", 0)
            print(f"   Risk Score: {risk_analysis['risk_score']}/10")
            print(f"   Risk Level: {risk_analysis['risk_level']}")
            
            # COMPONENT 2: GPT-5 Engine Decision Making
            print(f"🧠 Component 2: GPT-5 Engine")
            gpt5_decision = await self._component2_gpt5_decision(payment_request, risk_analysis)
            flow.gpt5_decision = gpt5_decision
            flow.gpt5_tokens = gpt5_decision.tokens_used
            print(f"   Selected: {gpt5_decision.selected_processor}")
            print(f"   Confidence: {gpt5_decision.confidence:.1%}")
            print(f"   Reasoning: {gpt5_decision.reasoning_effort}/{gpt5_decision.verbosity}")
            print(f"   Tokens: {gpt5_decision.tokens_used}")
            
            # COMPONENT 3: Routing Logic & Execution
            print(f"🔀 Component 3: Routing Logic")
            routing_result = await self._component3_routing(gpt5_decision.selected_processor, payment_request)
            flow.routing_result = routing_result
            flow.final_status = "success" if routing_result["success"] else "failed"
            print(f"   Execution: {'✅ SUCCESS' if routing_result['success'] else '❌ FAILED'}")
            print(f"   Response Time: {routing_result['response_time']}ms")
            
            # Complete flow
            flow.completed_at = datetime.utcnow()
            flow.total_processing_time = int((flow.completed_at - start_time).total_seconds() * 1000)
            
            # Update system metrics
            self._update_system_metrics(flow)
            
            print(f"✅ FLOW COMPLETE: {flow_id} ({flow.total_processing_time}ms)")
            
            return flow
            
        except Exception as e:
            print(f"❌ FLOW FAILED: {flow_id} - {e}")
            flow.final_status = "error"
            flow.completed_at = datetime.utcnow()
            flow.total_processing_time = int((flow.completed_at - start_time).total_seconds() * 1000)
            return flow
    
    async def _component1_analysis(self, payment_request: PaymentRequest) -> Dict[str, Any]:
        """Component 1: Data Analysis & Risk Assessment"""
        
        # Mock risk analysis (would use real Component 1)
        amount = payment_request.amount
        
        # Calculate risk score based on amount and patterns
        risk_score = min(10.0, (amount / 1000) + (2.0 if amount > 5000 else 1.0))
        
        risk_analysis = {
            "risk_score": risk_score,
            "risk_level": "low" if risk_score < 3 else "medium" if risk_score < 6 else "high",
            "risk_factors": [],
            "recommendations": [],
            "tokens_used": 0  # Would be real for Component 1 GPT-5 calls
        }
        
        # Add risk factors
        if amount > 10000:
            risk_analysis["risk_factors"].append("high_value_transaction")
        if "emergency" in payment_request.merchant_id.lower():
            risk_analysis["risk_factors"].append("emergency_merchant")
        
        return risk_analysis
    
    async def _component2_gpt5_decision(
        self, 
        payment_request: PaymentRequest, 
        risk_analysis: Dict[str, Any]
    ) -> Any:
        """Component 2: GPT-5 Engine Decision Making"""
        
        # Determine reasoning effort based on risk and amount
        if payment_request.amount < 100:
            reasoning_effort = ReasoningEffort.MINIMAL
        elif payment_request.amount > 5000 or risk_analysis["risk_level"] == "high":
            reasoning_effort = ReasoningEffort.HIGH
        else:
            reasoning_effort = ReasoningEffort.MEDIUM
        
        # Determine verbosity based on amount and risk
        if payment_request.amount > 10000 or risk_analysis["risk_level"] == "high":
            verbosity = Verbosity.HIGH
        elif payment_request.amount > 1000:
            verbosity = Verbosity.MEDIUM
        else:
            verbosity = Verbosity.LOW
        
        # Use Component 2's GPT-5 orchestrator
        decision = await self.gpt5_orchestrator.make_routing_decision(
            amount=payment_request.amount,
            merchant=payment_request.merchant_id,
            failed_processors=[],  # Would be populated from real failures
            reasoning_effort=reasoning_effort,
            verbosity=verbosity
        )
        
        return decision
    
    async def _component3_routing(
        self, 
        selected_processor: str, 
        payment_request: PaymentRequest
    ) -> Dict[str, Any]:
        """Component 3: Routing Logic & Processor Execution"""
        
        processor = self.processors.get(selected_processor)
        if not processor:
            return {
                "success": False,
                "error": f"Processor {selected_processor} not available",
                "response_time": 100
            }
        
        # Simulate processor execution
        await asyncio.sleep(processor["response_time"] / 1000)  # Convert to seconds
        
        # Simulate success/failure based on processor health
        import random
        success = random.random() < processor["success_rate"]
        
        if success:
            # Calculate fees
            fee = payment_request.amount * processor["fee_percentage"] + processor["fee_fixed"]
            net_amount = payment_request.amount - fee
            
            return {
                "success": True,
                "processor": selected_processor,
                "response_time": processor["response_time"],
                "fee_charged": fee,
                "net_amount": net_amount,
                "transaction_id": f"{selected_processor}_{uuid.uuid4().hex[:16]}"
            }
        else:
            return {
                "success": False,
                "processor": selected_processor,
                "response_time": processor["response_time"],
                "error": random.choice([
                    "Card declined",
                    "Insufficient funds", 
                    "Network timeout",
                    "Rate limit exceeded"
                ])
            }
    
    def _update_system_metrics(self, flow: IntegratedPaymentFlow):
        """Update system-wide metrics"""
        
        self.system_metrics["total_payments"] += 1
        if flow.final_status == "success":
            self.system_metrics["successful_payments"] += 1
        
        if flow.gpt5_decision:
            self.system_metrics["gpt5_decisions"] += 1
            self.system_metrics["total_tokens_used"] += flow.gpt5_tokens
        
        # Update average processing time
        total_time = (
            self.system_metrics["avg_processing_time"] * (self.system_metrics["total_payments"] - 1) +
            flow.total_processing_time
        )
        self.system_metrics["avg_processing_time"] = total_time / self.system_metrics["total_payments"]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status across all components"""
        
        return {
            "system_health": "healthy",
            "components": {
                "component_1_data_analysis": "active" if self.data_generator else "mock",
                "component_2_gpt5_engine": "active",
                "component_3_routing_logic": "active"
            },
            "metrics": self.system_metrics,
            "processors": {
                name: {
                    "status": proc["status"],
                    "success_rate": f"{proc['success_rate']:.1%}",
                    "response_time": f"{proc['response_time']}ms"
                }
                for name, proc in self.processors.items()
            },
            "active_flows": len(self.active_flows),
            "gpt5_config": {
                "model": "gpt-5",
                "reasoning_effort_available": ["minimal", "low", "medium", "high"],
                "verbosity_levels": ["low", "medium", "high"]
            }
        }


# FastAPI App Setup
app = FastAPI(
    title="Complete Payment Orchestration System",
    description="Integrated Components 1+2+3: Data Analysis + GPT-5 Engine + Routing Logic",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = CompletePaymentOrchestrator()


@app.post("/api/payments", response_model=PaymentResponse)
async def process_payment(payment_request: PaymentRequest):
    """Process payment through complete 3-component system"""
    
    try:
        flow = await orchestrator.process_payment(payment_request)
        
        if flow.final_status == "error":
            raise HTTPException(status_code=500, detail="Payment processing failed")
        
        gpt5_decision = flow.gpt5_decision
        
        return PaymentResponse(
            payment_id=flow.flow_id,
            status=flow.final_status,
            selected_processor=gpt5_decision.selected_processor if gpt5_decision else "unknown",
            confidence=gpt5_decision.confidence if gpt5_decision else 0.5,
            reasoning_effort=gpt5_decision.reasoning_effort if gpt5_decision else "unknown",
            verbosity=gpt5_decision.verbosity if gpt5_decision else "unknown",
            processing_time_ms=flow.total_processing_time,
            tokens_used=flow.gpt5_tokens,
            reasoning_chain=gpt5_decision.reasoning_chain if gpt5_decision else [],
            created_at=flow.created_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system/status")
async def get_system_status():
    """Get complete system status"""
    return orchestrator.get_system_status()


@app.get("/api/payments/{payment_id}")
async def get_payment_details(payment_id: str):
    """Get detailed payment flow information"""
    
    flow = orchestrator.active_flows.get(payment_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return {
        "flow_id": flow.flow_id,
        "status": flow.final_status,
        "payment_request": flow.payment_request,
        "component_1_analysis": flow.risk_analysis,
        "component_2_gpt5_decision": {
            "selected_processor": flow.gpt5_decision.selected_processor if flow.gpt5_decision else None,
            "confidence": flow.gpt5_decision.confidence if flow.gpt5_decision else None,
            "reasoning_effort": flow.gpt5_decision.reasoning_effort if flow.gpt5_decision else None,
            "verbosity": flow.gpt5_decision.verbosity if flow.gpt5_decision else None,
            "tokens_used": flow.gpt5_tokens,
            "reasoning_chain": flow.gpt5_decision.reasoning_chain if flow.gpt5_decision else []
        },
        "component_3_routing": flow.routing_result,
        "timing": {
            "created_at": flow.created_at.isoformat(),
            "completed_at": flow.completed_at.isoformat() if flow.completed_at else None,
            "total_processing_time_ms": flow.total_processing_time
        }
    }


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Complete Payment Orchestration System",
        "components": {
            "component_1": "Data Analysis & Risk Assessment",
            "component_2": "GPT-5 Engine Decision Making", 
            "component_3": "Routing Logic & Processor Execution"
        },
        "gpt5_features": {
            "reasoning_effort": "Adaptive parameter control",
            "verbosity": "Audit trail generation",
            "chain_of_thought": "Complete reasoning capture"
        },
        "endpoints": {
            "POST /api/payments": "Process payment through all components",
            "GET /api/system/status": "System health and metrics",
            "GET /api/payments/{id}": "Detailed payment flow information"
        },
        "demo": "Visit /docs for interactive API documentation"
    }


# CLI Demo Mode
async def run_demo_payments():
    """Run demo payments to show complete system"""
    
    print("\n🚀 COMPLETE PAYMENT ORCHESTRATION SYSTEM DEMO")
    print("=" * 70)
    print("Components 1 + 2 + 3 Integration")
    print("=" * 70)
    
    demo_payments = [
        PaymentRequest(
            amount=75.50,
            merchant_id="coffee_shop_main",
            description="Routine coffee purchase"
        ),
        PaymentRequest(
            amount=2500.00, 
            merchant_id="b2b_software_corp",
            description="Software license renewal"
        ),
        PaymentRequest(
            amount=15000.00,
            merchant_id="emergency_contractor_llc", 
            description="Critical infrastructure repair"
        )
    ]
    
    for i, payment in enumerate(demo_payments, 1):
        print(f"\n{'='*50}")
        print(f"DEMO PAYMENT {i}")
        print(f"{'='*50}")
        
        flow = await orchestrator.process_payment(payment)
        
        # Summary
        success_rate = (orchestrator.system_metrics["successful_payments"] / 
                       orchestrator.system_metrics["total_payments"])
        
        print(f"\n📊 SYSTEM STATUS:")
        print(f"   Success Rate: {success_rate:.1%}")
        print(f"   Total GPT-5 Tokens: {orchestrator.system_metrics['total_tokens_used']}")
        print(f"   Avg Processing: {orchestrator.system_metrics['avg_processing_time']:.0f}ms")
        
        await asyncio.sleep(1)
    
    print(f"\n🏆 COMPLETE SYSTEM DEMO FINISHED")
    print("All 3 components working together!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run CLI demo
        asyncio.run(run_demo_payments())
    else:
        # Run FastAPI server
        print("🚀 Starting Complete Payment Orchestration System")
        print("Components: Data Analysis + GPT-5 Engine + Routing Logic")
        print("API Docs: http://localhost:8000/docs")
        
        uvicorn.run(app, host="0.0.0.0", port=8000)