
import type { NextPage } from "next";
import Head from "next/head";
import Link from "next/link";
import styles from "../styles/Home.module.css";

const Home: NextPage = () => {
  return (
    <div className={styles.container}>
      <Head>
        <title>PayFlow - Payment Orchestration Platform</title>
        <meta name="description" content="Intelligent payment routing with zero-downtime fallbacks. Built for B2B reliability." />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <nav className={styles.nav}>
        <div className={styles.logo}>PayFlow</div>
        <div className={styles.navLinks}>
          <a href="#features">Features</a>
          <a href="#pricing">Pricing</a>
          <a href="#docs">Docs</a>
          <Link href="/dashboard">
            <button className={styles.ctaButton}>Get Started</button>
          </Link>
        </div>
      </nav>

      <main className={styles.main}>
        <section className={styles.hero}>
          <div className={styles.heroContent}>
            <div className={styles.badge}>GPT-5 AGENT • ZERO-DOWNTIME FALLBACK</div>
            <h1 className={styles.heroTitle}>
              Payment Orchestration that protects{" "}
              <span className={styles.highlight}>$ every second</span>
            </h1>
            <p className={styles.heroDescription}>
              Intelligent routing, instant fallbacks, and transparent reasoning. Built for B2B reliability.
            </p>
            <div className={styles.heroButtons}>
              <button className={styles.primaryButton}>Process Payment</button>
              <button className={styles.secondaryButton}>View Docs</button>
            </div>
          </div>

          <div className={styles.statsGrid}>
            <div className={styles.statCard}>
              <div className={styles.statValue}>99.9%</div>
              <div className={styles.statLabel}>Uptime</div>
            </div>
            <div className={styles.statCard}>
              <div className={styles.statValue}>$156k</div>
              <div className={styles.statLabel}>Revenue Protected</div>
            </div>
            <div className={styles.statCard}>
              <div className={styles.statValue}>1,247</div>
              <div className={styles.statLabel}>GPT-5 Decisions</div>
            </div>
            <div className={styles.statCard}>
              <div className={styles.statValue}>0s</div>
              <div className={styles.statLabel}>Downtime</div>
            </div>
          </div>
        </section>

        <section id="features" className={styles.features}>
          <h2 className={styles.sectionTitle}>Intelligent Payment Infrastructure</h2>
          <div className={styles.featureGrid}>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🚀</div>
              <h3>Smart Routing</h3>
              <p>AI-powered routing decisions that optimize for success rates and costs in real-time.</p>
            </div>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🛡️</div>
              <h3>Zero Downtime</h3>
              <p>Instant fallbacks to backup processors when primary routes fail or detect issues.</p>
            </div>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>📊</div>
              <h3>Risk Analysis</h3>
              <p>Real-time fraud detection and risk scoring with transparent AI reasoning.</p>
            </div>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>💎</div>
              <h3>Enterprise Ready</h3>
              <p>B2B-focused infrastructure with compliance, security, and reliability first.</p>
            </div>
          </div>
        </section>

        <section className={styles.cta}>
          <h2>Ready to protect every transaction?</h2>
          <p>Join thousands of businesses using PayFlow for reliable payment processing.</p>
          <Link href="/dashboard">
            <button className={styles.ctaButtonLarge}>Start Processing Payments</button>
          </Link>
        </section>
      </main>

      <footer className={styles.footer}>
        <p>© 2024 PayFlow. Built for the future of payments.</p>
      </footer>
    </div>
  );
};

export default Home;
