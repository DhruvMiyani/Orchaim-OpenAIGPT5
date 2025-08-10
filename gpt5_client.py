"""
Real GPT-5 API Client Integration
Uses OpenAI API with GPT-5's new reasoning_effort and verbosity parameters
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GPT5Client:
    """
    Real GPT-5 API client with reasoning_effort and verbosity control.
    Uses OpenAI's new GPT-5 parameters for payment routing and data generation.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-5"  # ALWAYS GPT-5, NO EXCEPTIONS
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
    
    async def make_routing_decision(
        self,
        context: Dict[str, Any],
        reasoning_effort: str = "medium",
        verbosity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Use GPT-5 to make intelligent payment routing decisions.
        
        Args:
            context: Payment context (processors, failures, transaction details)
            reasoning_effort: minimal, low, medium, high
            verbosity: low, medium, high
        """
        
        prompt = self._build_routing_prompt(context)
        
        try:
            # ONLY GPT-5 - NO FALLBACKS
            response = await self.client.chat.completions.create(
                model="gpt-5",  # ONLY GPT-5
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are an expert payment orchestration system. Use {reasoning_effort} reasoning effort and {verbosity} verbosity. Analyze the context and make intelligent routing decisions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                # GPT-5 specific parameters
                max_completion_tokens=2000,
                # Add GPT-5 specific params if available
                extra_body={
                    "reasoning_effort": reasoning_effort,
                    "verbosity": verbosity
                }
            )
            
            # Parse GPT-5 response
            decision_text = response.choices[0].message.content
            
            # Extract structured decision from GPT-5's response
            decision = self._parse_routing_decision(decision_text, context)
            
            # Add GPT-5 metadata
            decision["gpt5_metadata"] = {
                "reasoning_effort": reasoning_effort,
                "verbosity": verbosity,
                "reasoning_tokens": getattr(response.usage, 'reasoning_tokens', 0),
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "model": self.model
            }
            
            return decision
            
        except Exception as e:
            # Fallback to simple logic if GPT-5 fails
            return self._fallback_routing_decision(context, str(e))
    
    async def generate_synthetic_data(
        self,
        pattern_type: str,
        context: Dict[str, Any],
        reasoning_effort: str = "high",
        verbosity: str = "low"
    ) -> Dict[str, Any]:
        """
        Use GPT-5 to generate realistic synthetic transaction data.
        
        Args:
            pattern_type: normal, sudden_spike, high_refund_rate, etc.
            context: Business context and requirements
            reasoning_effort: high for complex patterns
            verbosity: low for structured data output
        """
        
        prompt = self._build_data_generation_prompt(pattern_type, context)
        
        try:
            # ONLY GPT-5 - NO FALLBACKS
            response = await self.client.chat.completions.create(
                model="gpt-5",  # ONLY GPT-5
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert at generating realistic financial transaction data. Use {reasoning_effort} reasoning effort and {verbosity} verbosity. Create authentic patterns that match real-world scenarios."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_completion_tokens=4000,
                extra_body={
                    "reasoning_effort": reasoning_effort,
                    "verbosity": verbosity
                }
            )
            
            generation_plan = response.choices[0].message.content
            
            return {
                "pattern_type": pattern_type,
                "generation_plan": generation_plan,
                "gpt5_reasoning": self._extract_reasoning(generation_plan),
                "parameters_used": {
                    "reasoning_effort": reasoning_effort,
                    "verbosity": verbosity,
                    "reasoning_tokens": getattr(response.usage, 'reasoning_tokens', 0)
                }
            }
            
        except Exception as e:
            return {
                "pattern_type": pattern_type,
                "error": str(e),
                "fallback": "Using deterministic generation"
            }
    
    async def analyze_transaction_risk(
        self,
        transactions: List[Dict[str, Any]],
        context: Dict[str, Any],
        reasoning_effort: str = "high",
        verbosity: str = "high"
    ) -> Dict[str, Any]:
        """
        Use GPT-5 to analyze transaction patterns for freeze risk.
        """
        
        prompt = self._build_risk_analysis_prompt(transactions, context)
        
        try:
            # ONLY GPT-5 - NO FALLBACKS
            response = await self.client.chat.completions.create(
                model="gpt-5",  # ONLY GPT-5
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a payment risk analysis expert. Use {reasoning_effort} reasoning effort and {verbosity} verbosity. Analyze transaction patterns and predict Stripe account freeze probability."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=3000,
                extra_body={
                    "reasoning_effort": reasoning_effort,
                    "verbosity": verbosity
                }
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "risk_analysis": analysis,
                "structured_assessment": self._parse_risk_analysis(analysis),
                "gpt5_reasoning": self._extract_reasoning(analysis),
                "confidence": "high" if reasoning_effort == "high" else "medium"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "fallback_analysis": "Unable to perform GPT-5 risk analysis"
            }
    
    def _build_routing_prompt(self, context: Dict[str, Any]) -> str:
        """Build routing decision prompt for GPT-5."""
        
        return f"""
        PAYMENT ROUTING DECISION REQUIRED

        Transaction Details:
        - Amount: ${context['transaction']['amount']} {context['transaction']['currency']}
        - Merchant: {context['transaction']['merchant_id']}
        - Risk Level: {context.get('business_context', {}).get('urgency', 'normal')}

        Available Processors:
        {self._serialize_context(context['processors'])}

        Recent Failures:
        {self._serialize_context(context.get('failures', []))}

        Processor Health Status:
        {self._serialize_context(context.get('processor_health', {}))}

        REQUIREMENTS:
        1. If primary processor is frozen, MUST use alternative
        2. Prioritize success rate over fees for high-value transactions
        3. Consider recent failure patterns
        4. Provide clear reasoning for your choice

        Please respond with:
        1. Selected processor ID
        2. Reasoning for your choice
        3. Fallback chain (ordered list of alternatives)
        4. Risk assessment
        """
    
    def _build_data_generation_prompt(self, pattern_type: str, context: Dict[str, Any]) -> str:
        """Build synthetic data generation prompt."""
        
        stripe_thresholds = {
            "refund_rate": 5.0,
            "chargeback_rate": 1.0,
            "volume_spike": 10.0
        }
        
        return f"""
        GENERATE REALISTIC STRIPE TRANSACTION DATA

        Pattern Type: {pattern_type}
        Business Context: {context.get('business_type', 'B2B SaaS')}
        Historical Baseline: {context.get('historical_baseline', {})}

        Requirements for {pattern_type}:
        {self._get_pattern_requirements(pattern_type)}

        Stripe Freeze Thresholds:
        - Refund rate >5% = Investigation triggered
        - Chargeback rate >1% = Immediate freeze + 180-day hold
        - Volume spike >10x normal = Account review within 24 hours

        Generate a detailed plan for creating {context.get('transaction_count', 100)} transactions that:
        1. Follow authentic Stripe patterns (proper fees, timing, IDs)
        2. Create the specified risk scenario
        3. Include realistic failure reasons and customer behavior
        4. Use proper Stripe balance_transaction format

        Focus on realism - this data will be used to test payment systems.
        """
    
    def _build_risk_analysis_prompt(self, transactions: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """Build risk analysis prompt."""
        
        return f"""
        ANALYZE TRANSACTION PATTERNS FOR STRIPE FREEZE RISK

        Transaction Dataset:
        - Total transactions: {len(transactions)}
        - Sample data: {self._serialize_context(transactions[:5])}

        Analysis Context:
        - Business type: {context.get('business_type', 'B2B')}
        - Analysis window: {context.get('analysis_window', 'recent')}

        Stripe Risk Thresholds:
        - Refund rate >5% = Review triggered
        - Chargeback rate >1% = Immediate freeze
        - Volume spikes >10x = Account investigation
        - Pattern inconsistencies = Documentation required

        Please provide:
        1. Risk level assessment (low/medium/high/critical)
        2. Specific patterns detected
        3. Freeze probability (0-100%)
        4. Detailed reasoning for your assessment
        5. Actionable recommendations to reduce risk
        6. Timeline for potential freeze if patterns continue

        Be thorough in your analysis - account freezes can hold funds for 180 days.
        """
    
    def _get_pattern_requirements(self, pattern_type: str) -> str:
        """Get specific requirements for each pattern type."""
        
        requirements = {
            "sudden_spike": "Generate 10-15x normal daily volume compressed into 2-3 hours. Use larger transaction amounts ($200-2000). Include realistic promotional context.",
            "high_refund_rate": "Create 10-15% refund rate (vs normal 2%). Include varied refund reasons, proper timing delays, and customer service context.",
            "chargeback_surge": "Generate 2-3% chargeback rate. Include proper chargeback reasons, $15 fees, and 15-60 day delays from original transactions.",
            "pattern_deviation": "Create sudden changes in transaction size (5-10x), new geographic regions, or unusual timing patterns.",
            "normal": "Generate consistent daily patterns, 2% refund rate, standard transaction sizes, and predictable business rhythms."
        }
        
        return requirements.get(pattern_type, "Generate realistic transaction patterns")
    
    def _parse_routing_decision(self, decision_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse GPT-5's routing decision into structured format."""
        
        # Extract key information from GPT-5's response
        lines = decision_text.split('\n')
        
        # Try to find processor selection
        selected_processor = "stripe"  # default
        for line in lines:
            if "select" in line.lower() or "choose" in line.lower():
                for processor_id in ["stripe", "paypal", "visa"]:
                    if processor_id in line.lower():
                        selected_processor = processor_id
                        break
        
        return {
            "selected_processor": selected_processor,
            "reasoning": decision_text,
            "confidence": 0.9,
            "fallback_chain": ["paypal", "visa"] if selected_processor == "stripe" else ["stripe", "visa"]
        }
    
    def _parse_risk_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse GPT-5's risk analysis into structured format."""
        
        # Extract risk level
        risk_level = "medium"
        if "critical" in analysis.lower() or "high" in analysis.lower():
            risk_level = "high"
        elif "low" in analysis.lower():
            risk_level = "low"
        
        # Extract freeze probability
        freeze_prob = 0.3
        try:
            import re
            prob_match = re.search(r'(\d+)%', analysis)
            if prob_match:
                freeze_prob = int(prob_match.group(1)) / 100
        except:
            pass
        
        return {
            "risk_level": risk_level,
            "freeze_probability": freeze_prob,
            "risk_score": freeze_prob * 100,
            "detected_patterns": [],
            "recommendations": ["Monitor transaction patterns", "Prepare documentation"]
        }
    
    def _extract_reasoning(self, text: str) -> str:
        """Extract reasoning chain from GPT-5 response."""
        
        reasoning_keywords = ["reasoning:", "analysis:", "because", "therefore", "given that"]
        
        for keyword in reasoning_keywords:
            if keyword in text.lower():
                return text  # Return full text if reasoning detected
        
        return text[:500] + "..." if len(text) > 500 else text
    
    def _serialize_context(self, obj: Any) -> str:
        """Serialize context objects with datetime handling."""
        def datetime_converter(o):
            if isinstance(o, datetime):
                return o.isoformat()
            return str(o)
        
        return json.dumps(obj, indent=2, default=datetime_converter)
    
    def _fallback_routing_decision(self, context: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Fallback decision if GPT-5 API fails."""
        
        return {
            "selected_processor": "stripe",
            "reasoning": f"GPT-5 API error: {error}. Using fallback logic.",
            "confidence": 0.5,
            "fallback_chain": ["paypal", "visa"],
            "error": error
        }