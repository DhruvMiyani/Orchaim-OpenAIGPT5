
import type { NextPage } from "next";
import Head from "next/head";
import Link from "next/link";
import { useState } from "react";
import styles from "../styles/Dashboard.module.css";

const Dashboard: NextPage = () => {
  const [amount, setAmount] = useState("15000");
  const [currency, setCurrency] = useState("USD");
  const [description, setDescription] = useState("High-risk B2B payment");
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastResult, setLastResult] = useState<string | null>(null);

  const handleSubmit = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setLastResult("Success: routed to PAYPAL");
      setIsProcessing(false);
    }, 2000);
  };

  const generateTestData = () => {
    // Simulate data generation
    console.log("Generated 500 transactions (sudden_spike)");
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>PayFlow Dashboard - Payment Processing</title>
        <meta name="description" content="Process payments with intelligent routing and risk analysis" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <nav className={styles.nav}>
        <Link href="/" className={styles.logo}>PayFlow</Link>
        <div className={styles.navLinks}>
          <span>Dashboard</span>
          <span>Analytics</span>
          <span>Settings</span>
        </div>
      </nav>

      <main className={styles.main}>
        <div className={styles.dashboardGrid}>
          {/* Payment Processing Section */}
          <div className={styles.card}>
            <h2>Payment Processing</h2>
            <div className={styles.formGrid}>
              <div className={styles.inputGroup}>
                <label>Amount</label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className={styles.input}
                />
              </div>
              <div className={styles.inputGroup}>
                <label>Currency</label>
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className={styles.select}
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                </select>
              </div>
              <div className={styles.inputGroup}>
                <label>Description</label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className={styles.input}
                />
              </div>
            </div>
            <div className={styles.buttonGroup}>
              <button
                onClick={handleSubmit}
                disabled={isProcessing}
                className={styles.submitButton}
              >
                {isProcessing ? "Processing..." : "Submit"}
              </button>
              <button className={styles.highRiskButton}>High-Risk Payment</button>
            </div>
            {lastResult && (
              <div className={styles.terminal}>
                <div className={styles.terminalHeader}>
                  POST /payments/process<br />
                  {`{"amount":${amount},"currency":"${currency}","description":"${description}"}`}
                </div>
                <div className={styles.success}>✓ {lastResult}</div>
              </div>
            )}
          </div>

          {/* Processors Section */}
          <div className={styles.card}>
            <h2>Processors</h2>
            <div className={styles.processorList}>
              <div className={styles.processor}>
                <div className={styles.processorHeader}>
                  <span className={styles.processorName}>Stripe</span>
                  <span className={styles.statusActive}>● ACTIVE</span>
                </div>
                <div className={styles.processorStats}>
                  success 99.0% • latency 120ms
                </div>
                <div className={styles.processorButtons}>
                  <button className={styles.freezeButton}>Freeze</button>
                  <button className={styles.unfreezeButton}>Unfreeze</button>
                </div>
              </div>
              <div className={styles.processor}>
                <div className={styles.processorHeader}>
                  <span className={styles.processorName}>PayPal</span>
                  <span className={styles.statusActive}>● ACTIVE</span>
                </div>
                <div className={styles.processorStats}>
                  success 99.0% • latency 120ms
                </div>
                <div className={styles.processorButtons}>
                  <button className={styles.freezeButton}>Freeze</button>
                  <button className={styles.unfreezeButton}>Unfreeze</button>
                </div>
              </div>
              <div className={styles.processor}>
                <div className={styles.processorHeader}>
                  <span className={styles.processorName}>Visa Direct</span>
                  <span className={styles.statusActive}>● ACTIVE</span>
                </div>
                <div className={styles.processorStats}>
                  success 99.0% • latency 120ms
                </div>
                <div className={styles.processorButtons}>
                  <button className={styles.freezeButton}>Freeze</button>
                  <button className={styles.unfreezeButton}>Unfreeze</button>
                </div>
              </div>
            </div>
          </div>

          {/* Data Generation Terminal */}
          <div className={styles.card}>
            <h2>Data Generation Terminal</h2>
            <div className={styles.tagGroup}>
              <span className={styles.tag}>SUDDEN_SPIKE</span>
              <span className={styles.tag}>HIGH_REFUNDS</span>
              <span className={styles.tag}>CHARGEBACKS</span>
            </div>
            <div className={styles.riskLevels}>
              <span className={styles.riskMinimal}>MINIMAL</span>
              <span className={styles.riskMedium}>MEDIUM</span>
              <span className={styles.riskHigh}>HIGH</span>
            </div>
            <div className={styles.terminal}>
              <div className={styles.terminalText}>
                GPT-5 Data Generation Terminal Ready<br />
                POST /data/generate<br />
                {`{"pattern_type":"sudden_spike","reasoning_effort":"medium"}`}<br />
                <span className={styles.success}>✓ Generated 500 transactions (sudden_spike)</span>
              </div>
            </div>
            <button onClick={generateTestData} className={styles.generateButton}>
              Generate Data
            </button>
          </div>

          {/* Risk Analysis */}
          <div className={styles.card}>
            <h2>Risk Analysis</h2>
            <div className={styles.riskMetrics}>
              <div className={styles.riskScore}>
                <div className={styles.riskLabel}>Risk Score</div>
                <div className={styles.riskValue}>78</div>
              </div>
              <div className={styles.riskScore}>
                <div className={styles.riskLabel}>Freeze Probability</div>
                <div className={styles.riskValue}>62%</div>
              </div>
            </div>
            <div className={styles.riskChart}></div>
            <div className={styles.riskAnalysis}>
              <div className={styles.analysisHeader}>Pattern: ANALYSIS</div>
              <div>Risk Score: 78/100</div>
              <div>Freeze Probability: ~62%</div>
              <div className={styles.analysisReason}>
                Analysis: Chargeback pattern - elevated dispute risk
              </div>
            </div>
          </div>
        </div>

        <div className={styles.reasoningBar}>
          GPT-5 HIGH reasoning: Account frozen detected → route to PayPal for reliability.
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
