# GPT-5 Payment Orchestration Dashboard

A Next.js frontend for the GPT-5 powered payment orchestration system inspired by the Orachaim design.

## Features

### 🧠 GPT-5 Integration
- **Real-time Decision Making**: Configurable reasoning effort (minimal/medium/high)
- **Verbosity Control**: Adjustable output detail for different scenarios
- **Chain-of-Thought Visualization**: See GPT-5's reasoning process in real-time

### 💳 Payment Processing
- **Intelligent Routing**: Automatic processor selection based on GPT-5 analysis
- **Multi-Processor Support**: Stripe, PayPal, Visa Direct integration
- **Fallback Logic**: Automatic rerouting when processors fail or freeze

### 📊 Synthetic Data Generation
- **Pattern Generation**: Normal baseline, volume spikes, refund surges, chargeback patterns
- **Risk Analysis**: Real-time freeze risk assessment
- **Stripe Format Compliance**: Perfect API format for testing

### 🎨 Modern UI
- **Clean Dashboard**: Inspired by Orachaim design patterns
- **Terminal-style Displays**: Real-time API response visualization
- **Status Indicators**: Live processor health monitoring
- **Responsive Design**: Mobile-friendly layout

## Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Open Dashboard**
   Navigate to [http://localhost:3000/dashboard](http://localhost:3000/dashboard)

## API Endpoints

### Payment Processing
- `POST /api/payments/process` - Process payment with GPT-5 routing
- Parameters: amount, currency, description, reasoning_effort, verbosity

### Data Generation
- `POST /api/data/generate` - Generate synthetic transaction data
- Parameters: pattern_type, reasoning_effort, verbosity

## GPT-5 Features Demonstrated

### Reasoning Effort Control
```javascript
{
  "reasoning_effort": "high",    // Deep analysis for complex scenarios
  "verbosity": "high",          // Detailed audit trails
  "context_aware": true         // Adapts to transaction complexity
}
```

### Decision Visualization
- Real-time GPT-5 reasoning display
- Chain-of-thought process tracking
- Performance metrics (decision time, confidence)
- Audit log generation

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Next.js   │────▶│     API      │────▶│   GPT-5     │
│  Frontend   │     │  Endpoints   │     │   Engine    │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                ┌───────────┼───────────┐
                ▼           ▼           ▼
         ┌──────────┐ ┌──────────┐ ┌──────────┐
         │  Stripe  │ │  PayPal  │ │   Visa   │
         └──────────┘ └──────────┘ └──────────┘
```

## Tech Stack

- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: CSS Modules
- **API**: Next.js API Routes
- **Backend**: FastAPI (payment_router_clean)

## Demo Scenarios

1. **Normal Payment** ($25,000) - Fast routing with minimal reasoning
2. **High-Risk Transaction** - Deep analysis with high reasoning effort
3. **Stripe Freeze Simulation** - Automatic PayPal fallback
4. **Synthetic Data Generation** - Create realistic test patterns

## Production Integration

To connect with the FastAPI backend, update the API endpoints in:
- `/pages/api/payments/process.ts`
- `/pages/api/data/generate.ts`

Replace demo logic with actual backend calls:
```javascript
const response = await fetch('http://localhost:8000/payments/process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(requestData)
});
```
