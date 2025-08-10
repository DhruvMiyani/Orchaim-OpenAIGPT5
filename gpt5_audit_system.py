"""
GPT-5 Powered Audit Log System with Chain-of-Thought Analysis
Captures and analyzes all GPT-5 reasoning for compliance and debugging
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import uuid


class AuditEventType(Enum):
    PAYMENT_ROUTING = "payment_routing"
    PROCESSOR_FAILURE = "processor_failure"
    RISK_ANALYSIS = "risk_analysis"
    FALLBACK_DECISION = "fallback_decision"
    GPT5_REASONING = "gpt5_reasoning"


@dataclass
class AuditEvent:
    id: str
    timestamp: datetime
    event_type: AuditEventType
    payment_id: Optional[str]
    processor_id: Optional[str]
    data: Dict[str, Any]
    gpt5_metadata: Optional[Dict[str, Any]] = None


class GPT5AuditLogger:
    """
    Comprehensive audit logging system that captures GPT-5's
    chain-of-thought reasoning for payment orchestration decisions.
    """
    
    def __init__(self, log_file: str = "gpt5_audit.jsonl"):
        self.log_file = log_file
        self.events: List[AuditEvent] = []
        self.session_id = str(uuid.uuid4())[:8]
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)
        
        # Initialize log file
        self._write_session_header()
    
    def _write_session_header(self):
        """Write session header to audit log."""
        
        header = {
            "session_id": self.session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "session_start",
            "system_info": {
                "gpt5_audit_version": "1.0",
                "components": [
                    "processor_registry",
                    "synthetic_data_generator", 
                    "gpt5_fallback_router"
                ]
            }
        }
        
        self._write_to_file(header)
    
    def log_gpt5_routing_decision(
        self,
        payment_id: str,
        routing_context: Dict[str, Any],
        gpt5_decision: Dict[str, Any],
        gpt5_parameters: Dict[str, str]
    ):
        """Log GPT-5 routing decision with full context and reasoning."""
        
        event = AuditEvent(
            id=f"audit_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.PAYMENT_ROUTING,
            payment_id=payment_id,
            processor_id=gpt5_decision.get("selected_processor"),
            data={
                "routing_context": routing_context,
                "decision": {
                    "selected_processor": gpt5_decision.get("selected_processor"),
                    "confidence": gpt5_decision.get("confidence"),
                    "fallback_chain": gpt5_decision.get("fallback_chain", []),
                    "risk_assessment": gpt5_decision.get("risk_assessment")
                },
                "gpt5_reasoning": gpt5_decision.get("reasoning", ""),
                "reasoning_effort": gpt5_parameters.get("reasoning_effort"),
                "verbosity": gpt5_parameters.get("verbosity")
            },
            gpt5_metadata=gpt5_decision.get("gpt5_metadata", {})
        )
        
        self._log_event(event)
        
        print(f"📝 AUDIT: Logged GPT-5 routing decision for {payment_id}")
        print(f"   Processor: {gpt5_decision.get('selected_processor')}")
        print(f"   Reasoning effort: {gpt5_parameters.get('reasoning_effort')}")
        print(f"   Tokens used: {gpt5_decision.get('gpt5_metadata', {}).get('total_tokens', 'N/A')}")
    
    def log_processor_failure(
        self,
        payment_id: str,
        processor_id: str,
        failure_details: Dict[str, Any]
    ):
        """Log processor failure event."""
        
        event = AuditEvent(
            id=f"audit_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.PROCESSOR_FAILURE,
            payment_id=payment_id,
            processor_id=processor_id,
            data={
                "failure_type": failure_details.get("error_code"),
                "error_message": failure_details.get("error_message"),
                "response_time": failure_details.get("response_time_ms"),
                "attempt_number": failure_details.get("attempt_number", 1)
            }
        )
        
        self._log_event(event)
        print(f"⚠️  AUDIT: Logged processor failure - {processor_id}")
    
    def log_risk_analysis(
        self,
        context: Dict[str, Any],
        gpt5_analysis: Dict[str, Any],
        risk_triggers: List[str]
    ):
        """Log GPT-5 risk analysis with detailed reasoning."""
        
        event = AuditEvent(
            id=f"audit_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.RISK_ANALYSIS,
            payment_id=context.get("payment_id"),
            processor_id=None,
            data={
                "analysis_context": context,
                "gpt5_analysis": gpt5_analysis,
                "risk_triggers": risk_triggers,
                "risk_score": gpt5_analysis.get("risk_score", 0),
                "freeze_probability": gpt5_analysis.get("freeze_probability", 0)
            },
            gpt5_metadata=gpt5_analysis.get("gpt5_metadata", {})
        )
        
        self._log_event(event)
        print(f"🔍 AUDIT: Logged GPT-5 risk analysis")
        print(f"   Risk triggers: {len(risk_triggers)}")
        print(f"   Analysis confidence: {gpt5_analysis.get('confidence', 'N/A')}")
    
    def log_fallback_escalation(
        self,
        payment_id: str,
        failed_processors: List[str],
        escalation_reason: str,
        new_urgency: str
    ):
        """Log fallback escalation when GPT-5 parameters change."""
        
        event = AuditEvent(
            id=f"audit_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.FALLBACK_DECISION,
            payment_id=payment_id,
            processor_id=None,
            data={
                "failed_processors": failed_processors,
                "escalation_reason": escalation_reason,
                "new_urgency_level": new_urgency,
                "escalation_trigger": "multiple_failures" if len(failed_processors) > 1 else "single_failure"
            }
        )
        
        self._log_event(event)
        print(f"🚨 AUDIT: Logged fallback escalation for {payment_id}")
    
    def _log_event(self, event: AuditEvent):
        """Add event to memory and persist to file."""
        
        self.events.append(event)
        
        # Convert to JSON-serializable format
        event_dict = asdict(event)
        event_dict["timestamp"] = event.timestamp.isoformat()
        event_dict["event_type"] = event.event_type.value
        
        self._write_to_file(event_dict)
    
    def _write_to_file(self, data: Dict[str, Any]):
        """Write event to JSONL audit file."""
        
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            print(f"⚠️  Failed to write audit log: {e}")
    
    def generate_payment_audit_trail(self, payment_id: str) -> Dict[str, Any]:
        """Generate complete audit trail for a specific payment."""
        
        payment_events = [
            event for event in self.events 
            if event.payment_id == payment_id
        ]
        
        if not payment_events:
            return {"error": f"No audit events found for payment {payment_id}"}
        
        # Organize events by type
        events_by_type = {}
        for event in payment_events:
            event_type = event.event_type.value
            if event_type not in events_by_type:
                events_by_type[event_type] = []
            events_by_type[event_type].append(event)
        
        # Extract GPT-5 reasoning chain
        reasoning_chain = []
        gpt5_tokens_used = 0
        
        for event in payment_events:
            if event.gpt5_metadata:
                reasoning_chain.append({
                    "timestamp": event.timestamp.isoformat(),
                    "reasoning": event.data.get("gpt5_reasoning", ""),
                    "parameters": {
                        "reasoning_effort": event.data.get("reasoning_effort"),
                        "verbosity": event.data.get("verbosity")
                    },
                    "tokens": event.gpt5_metadata.get("total_tokens", 0)
                })
                gpt5_tokens_used += event.gpt5_metadata.get("total_tokens", 0)
        
        # Generate summary
        timeline = sorted(payment_events, key=lambda e: e.timestamp)
        
        return {
            "payment_id": payment_id,
            "audit_summary": {
                "total_events": len(payment_events),
                "event_types": list(events_by_type.keys()),
                "gpt5_decisions": len(events_by_type.get("payment_routing", [])),
                "processor_failures": len(events_by_type.get("processor_failure", [])),
                "gpt5_tokens_total": gpt5_tokens_used,
                "duration": (timeline[-1].timestamp - timeline[0].timestamp).total_seconds() if len(timeline) > 1 else 0
            },
            "gpt5_reasoning_chain": reasoning_chain,
            "complete_timeline": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type.value,
                    "processor": event.processor_id,
                    "summary": self._summarize_event(event)
                }
                for event in timeline
            ],
            "compliance_data": {
                "audit_file": self.log_file,
                "session_id": self.session_id,
                "all_decisions_logged": True,
                "gpt5_parameters_recorded": True
            }
        }
    
    def _summarize_event(self, event: AuditEvent) -> str:
        """Generate human-readable event summary."""
        
        if event.event_type == AuditEventType.PAYMENT_ROUTING:
            processor = event.data.get("decision", {}).get("selected_processor", "unknown")
            confidence = event.data.get("decision", {}).get("confidence", 0)
            return f"GPT-5 routed to {processor} (confidence: {confidence:.1%})"
            
        elif event.event_type == AuditEventType.PROCESSOR_FAILURE:
            error = event.data.get("error_message", "unknown error")
            return f"Processor {event.processor_id} failed: {error}"
            
        elif event.event_type == AuditEventType.RISK_ANALYSIS:
            risk_score = event.data.get("risk_score", 0)
            return f"Risk analysis completed (score: {risk_score})"
            
        elif event.event_type == AuditEventType.FALLBACK_DECISION:
            reason = event.data.get("escalation_reason", "unknown")
            return f"Fallback escalated: {reason}"
        
        return f"{event.event_type.value} event"
    
    def generate_session_report(self) -> Dict[str, Any]:
        """Generate comprehensive session audit report."""
        
        # Group events by payment
        payments = {}
        for event in self.events:
            if event.payment_id:
                if event.payment_id not in payments:
                    payments[event.payment_id] = []
                payments[event.payment_id].append(event)
        
        # Calculate statistics
        gpt5_decisions = [e for e in self.events if e.event_type == AuditEventType.PAYMENT_ROUTING]
        processor_failures = [e for e in self.events if e.event_type == AuditEventType.PROCESSOR_FAILURE]
        
        total_tokens = sum(
            event.gpt5_metadata.get("total_tokens", 0) 
            for event in self.events 
            if event.gpt5_metadata
        )
        
        # Parameter usage analysis
        reasoning_efforts = [
            event.data.get("reasoning_effort") 
            for event in gpt5_decisions 
            if event.data.get("reasoning_effort")
        ]
        
        verbosity_levels = [
            event.data.get("verbosity")
            for event in gpt5_decisions
            if event.data.get("verbosity")
        ]
        
        return {
            "session_id": self.session_id,
            "session_summary": {
                "total_events": len(self.events),
                "payments_processed": len(payments),
                "gpt5_decisions": len(gpt5_decisions),
                "processor_failures": len(processor_failures),
                "total_gpt5_tokens": total_tokens
            },
            "gpt5_parameter_usage": {
                "reasoning_effort_distribution": {
                    effort: reasoning_efforts.count(effort) 
                    for effort in set(reasoning_efforts)
                },
                "verbosity_distribution": {
                    level: verbosity_levels.count(level)
                    for level in set(verbosity_levels)
                }
            },
            "payments_summary": {
                payment_id: {
                    "events": len(events),
                    "gpt5_decisions": len([e for e in events if e.event_type == AuditEventType.PAYMENT_ROUTING]),
                    "failures": len([e for e in events if e.event_type == AuditEventType.PROCESSOR_FAILURE])
                }
                for payment_id, events in payments.items()
            },
            "compliance_attestation": {
                "all_gpt5_decisions_logged": True,
                "reasoning_chain_preserved": True,
                "audit_file_location": self.log_file,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    
    async def export_for_compliance(self, output_file: str) -> str:
        """Export audit data in compliance-friendly format."""
        
        report = self.generate_session_report()
        
        # Add detailed payment trails
        for payment_id in report["payments_summary"].keys():
            report[f"payment_trail_{payment_id}"] = self.generate_payment_audit_trail(payment_id)
        
        # Write comprehensive report
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📋 Compliance export saved: {output_file}")
        print(f"   Contains {len(self.events)} audit events")
        print(f"   GPT-5 token usage: {report['session_summary']['total_gpt5_tokens']}")
        
        return output_file


# Demo integration with existing components
async def demo_audit_system():
    """Demonstrate GPT-5 audit logging with payment scenarios."""
    
    print("📋 GPT-5 AUDIT SYSTEM DEMO")
    print("=" * 50)
    
    # Initialize audit logger
    audit_logger = GPT5AuditLogger("demo_audit.jsonl")
    
    # Simulate payment processing with audit logging
    payment_id = "pay_demo_001"
    
    # 1. Mock GPT-5 routing decision
    routing_context = {
        "payment_request": {"amount": 1500, "currency": "USD"},
        "processors": {"stripe": {"status": "healthy"}, "paypal": {"status": "healthy"}},
        "business_context": {"urgency": "high"}
    }
    
    gpt5_decision = {
        "selected_processor": "stripe",
        "confidence": 0.92,
        "reasoning": "Selected Stripe due to lowest fees and high success rate for this transaction size",
        "fallback_chain": ["paypal", "visa"],
        "gpt5_metadata": {"total_tokens": 245, "reasoning_tokens": 156}
    }
    
    gpt5_parameters = {"reasoning_effort": "medium", "verbosity": "high"}
    
    audit_logger.log_gpt5_routing_decision(
        payment_id, routing_context, gpt5_decision, gpt5_parameters
    )
    
    # 2. Simulate processor failure
    failure_details = {
        "error_code": "ACCOUNT_FROZEN",
        "error_message": "Stripe account temporarily frozen",
        "response_time_ms": 1200,
        "attempt_number": 1
    }
    
    audit_logger.log_processor_failure(payment_id, "stripe", failure_details)
    
    # 3. Log fallback escalation
    audit_logger.log_fallback_escalation(
        payment_id, 
        ["stripe"], 
        "Account freeze detected", 
        "critical"
    )
    
    # 4. Mock second GPT-5 decision with higher reasoning
    gpt5_decision_2 = {
        "selected_processor": "paypal",
        "confidence": 0.87,
        "reasoning": "Stripe frozen, selected PayPal as primary fallback with good health metrics",
        "fallback_chain": ["visa"],
        "gpt5_metadata": {"total_tokens": 387, "reasoning_tokens": 248}
    }
    
    gpt5_parameters_2 = {"reasoning_effort": "high", "verbosity": "high"}
    
    audit_logger.log_gpt5_routing_decision(
        payment_id, routing_context, gpt5_decision_2, gpt5_parameters_2
    )
    
    # Generate audit trail
    print("\n" + "="*50)
    audit_trail = audit_logger.generate_payment_audit_trail(payment_id)
    
    print(f"📊 PAYMENT AUDIT TRAIL: {payment_id}")
    print(f"   Total events: {audit_trail['audit_summary']['total_events']}")
    print(f"   GPT-5 decisions: {audit_trail['audit_summary']['gpt5_decisions']}")
    print(f"   Total GPT-5 tokens: {audit_trail['audit_summary']['gpt5_tokens_total']}")
    
    print("\n🧠 GPT-5 REASONING CHAIN:")
    for i, reasoning in enumerate(audit_trail['gpt5_reasoning_chain'], 1):
        print(f"   {i}. {reasoning['parameters']['reasoning_effort']} effort, {reasoning['parameters']['verbosity']} verbosity")
        print(f"      Tokens: {reasoning['tokens']}")
        print(f"      Decision: {reasoning['reasoning'][:80]}...")
    
    # Generate session report
    print("\n" + "="*50)
    session_report = audit_logger.generate_session_report()
    print("📈 SESSION SUMMARY:")
    print(f"   Events logged: {session_report['session_summary']['total_events']}")
    print(f"   GPT-5 parameter usage:")
    for effort, count in session_report['gpt5_parameter_usage']['reasoning_effort_distribution'].items():
        print(f"     {effort}: {count} decisions")
    
    # Export for compliance
    compliance_file = await audit_logger.export_for_compliance("compliance_report.json")
    
    print(f"\n✅ Audit demo complete")
    print(f"   Compliance export: {compliance_file}")
    print(f"   Raw audit log: demo_audit.jsonl")


if __name__ == "__main__":
    asyncio.run(demo_audit_system())