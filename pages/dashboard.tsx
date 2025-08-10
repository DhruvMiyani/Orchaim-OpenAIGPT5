
import type { NextPage } from "next";
import Head from "next/head";
import Link from "next/link";
import { useState } from "react";
import styles from "../styles/Dashboard.module.css";

const Dashboard: NextPage = () => {
  const [amount, setAmount] = useState("15000");
  const [currency, setCurrency] = useState("USD");
  const [description, setDescription] = useState("AI Agent Purchase - Electronics");
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
    console.log("Generated 500 agent transactions");
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>Orchaim Dashboard - MCP Server Management</title>
        <meta name="description" content="Manage AI agent shopping transactions with intelligent payment orchestration" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <nav className={styles.nav}>
        <Link href="/" className={styles.logo}>
          <span className={styles.logoIcon}>⚡</span>
          Orchaim
        </Link>
        <div className={styles.navLinks}>
          <span>Dashboard</span>
          <span>Agents</span>
          <span>Analytics</span>
          <span>Settings</span>
        </div>
      </nav>

      <main className={styles.main}>
        <div className={styles.dashboardGrid}>
          {/* MCP Transaction Processing */}
          <div className={styles.card}>
            <h2>Agent Transaction Processing</h2>
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
                <label>Shopping Context</label>
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
                {isProcessing ? "Processing..." : "Execute Transaction"}
              </button>
              <button className={styles.agentButton}>Agent Override</button>
            </div>
            {lastResult && (
              <div className={styles.terminal}>
                <div className={styles.terminalHeader}>
                  MCP /transaction/process<br />
                  {`{"amount":${amount},"currency":"${currency}","context":"${description}","agent_id":"gpt-5-shopping"}`}
                </div>
                <div className={styles.success}>✓ {lastResult}</div>
              </div>
            )}
          </div>

          {/* Payment Processors */}
          <div className={styles.card}>
            <h2>Payment Processors</h2>
            <div className={styles.processorList}>
              <div className={styles.processor}>
                <div className={styles.processorHeader}>
                  <span className={styles.processorName}>Stripe</span>
                  <span className={styles.statusActive}>● ACTIVE</span>
                </div>
                <div className={styles.processorStats}>
                  success 99.2% • latency 95ms • agents: 847
                </div>
                <div className={styles.processorButtons}>
                  <button className={styles.freezeButton}>Pause</button>
                  <button className={styles.unfreezeButton}>Resume</button>
                </div>
              </div>
              <div className={styles.processor}>
                <div className={styles.processorHeader}>
                  <span className={styles.processorName}>PayPal</span>
                  <span className={styles.statusActive}>● ACTIVE</span>
                </div>
                <div className={styles.processorStats}>
                  success 98.8% • latency 110ms • agents: 623
                </div>
                <div className={styles.processorButtons}>
                  <button className={styles.freezeButton}>Pause</button>
                  <button className={styles.unfreezeButton}>Resume</button>
                </div>
              </div>
              <div className={styles.processor}>
                <div className={styles.processorHeader}>
                  <span className={styles.processorName}>Visa Direct</span>
                  <span className={styles.statusActive}>● ACTIVE</span>
                </div>
                <div className={styles.processorStats}>
                  success 99.5% • latency 85ms • agents: 401
                </div>
                <div className={styles.processorButtons}>
                  <button className={styles.freezeButton}>Pause</button>
                  <button className={styles.unfreezeButton}>Resume</button>
                </div>
              </div>
            </div>
          </div>

          {/* Agent Session Management */}
          <div className={styles.card}>
            <h2>Agent Session Terminal</h2>
            <div className={styles.tagGroup}>
              <span className={styles.tag}>GPT-5</span>
              <span className={styles.tag}>CLAUDE-3.5</span>
              <span className={styles.tag}>PERPLEXITY</span>
            </div>
            <div className={styles.riskLevels}>
              <span className={styles.riskMinimal}>TRUSTED</span>
              <span className={styles.riskMedium}>MONITORED</span>
              <span className={styles.riskHigh}>RESTRICTED</span>
            </div>
            <div className={styles.terminal}>
              <div className={styles.terminalText}>
                Orchaim MCP Server v1.2.0 Ready<br />
                POST /mcp/agent/session<br />
                {`{"agent":"gpt-5","session_type":"shopping","compliance":"enabled"}`}<br />
                <span className={styles.success}>✓ Connected 24 active agent sessions</span>
              </div>
            </div>
            <button onClick={generateTestData} className={styles.generateButton}>
              Simulate Agent Traffic
            </button>
          </div>

          {/* Compliance & Risk */}
          <div className={styles.card}>
            <h2>Compliance Monitoring</h2>
            <div className={styles.riskMetrics}>
              <div className={styles.riskScore}>
                <div className={styles.riskLabel}>Trust Score</div>
                <div className={styles.riskValue}>92</div>
              </div>
              <div className={styles.riskScore}>
                <div className={styles.riskLabel}>Agent Compliance</div>
                <div className={styles.riskValue}>98%</div>
              </div>
            </div>
            <div className={styles.riskChart}></div>
            <div className={styles.riskAnalysis}>
              <div className={styles.analysisHeader}>Pattern: COMPLIANCE_CLEAN</div>
              <div>Trust Score: 92/100</div>
              <div>Agent Compliance: 98%</div>
              <div className={styles.analysisReason}>
                Analysis: All agents operating within defined boundaries
              </div>
            </div>
          </div>
        </div>

        <div className={styles.reasoningBar}>
          MCP Agent Intelligence: Account freeze detected → intelligent rerouting to PayPal for transaction continuity.
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
