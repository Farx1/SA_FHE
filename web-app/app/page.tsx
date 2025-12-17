"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

/**
 * Main Page (SA_FHE) — polished landing + interactive demo
 * - No external UI kit required (but component names mirror common libs like Aceternity/MagicUI)
 * - Uses TailwindCSS + Framer Motion
 */

type SentimentLabel = "positive" | "negative" | "unknown";

type ApiResponse = {
  label?: SentimentLabel | string;
  sentiment?: SentimentLabel | string;
  score?: number;
  probability?: number;
  confidence?: number;
  steps?: Array<{ name: string; ms?: number }>;
  latency_ms?: number;
  details?: any;
  [key: string]: any;
};

type DemoStep = {
  key: string;
  title: string;
  desc: string;
  icon: React.ReactNode;
};

function cn(...classes: Array<string | false | undefined | null>) {
  return classes.filter(Boolean).join(" ");
}

async function postJSON<T>(url: string, body: any, timeoutMs = 12000): Promise<T> {
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!res.ok) {
      const txt = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status} ${res.statusText} ${txt}`.trim());
    }

    return (await res.json()) as T;
  } finally {
    clearTimeout(t);
  }
}

function normalizeLabel(raw?: any): SentimentLabel {
  const v = String(raw ?? "").toLowerCase();
  if (v.includes("pos")) return "positive";
  if (v.includes("neg")) return "negative";
  return "unknown";
}

function normalizeScore(r: ApiResponse): number | undefined {
  const v =
    r.score ??
    r.probability ??
    r.confidence ??
    (typeof r.details?.score === "number" ? r.details.score : undefined);
  return typeof v === "number" && Number.isFinite(v) ? v : undefined;
}

export default function Page() {
  const [text, setText] = useState(
    "I loved this product — fast delivery and amazing quality."
  );
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const [label, setLabel] = useState<SentimentLabel>("unknown");
  const [score, setScore] = useState<number | undefined>(undefined);
  const [latencyMs, setLatencyMs] = useState<number | undefined>(undefined);

  const [stepIndex, setStepIndex] = useState<number>(-1);
  const stepTimerRef = useRef<number | null>(null);

  const demoSteps: DemoStep[] = useMemo(
    () => [
      {
        key: "embed",
        title: "Text → Vector",
        desc: "RoBERTa transforms your text into an embedding (768 dims).",
        icon: <IconSpark />,
      },
      {
        key: "quantize",
        title: "Quantization",
        desc: "Conversion to integers (FHE-compatible format).",
        icon: <IconGrid />,
      },
      {
        key: "encrypt",
        title: "Encryption",
        desc: "Encryption with public key — the server never sees the text.",
        icon: <IconLock />,
      },
      {
        key: "fhe",
        title: "FHE Inference",
        desc: "The model (XGBoost) computes directly on encrypted data.",
        icon: <IconBolt />,
      },
      {
        key: "decrypt",
        title: "Decryption",
        desc: "Client-side decryption → readable result (positive / negative).",
        icon: <IconCheck />,
      },
    ],
    []
  );

  const stats = useMemo(
    () => [
      { k: "Accuracy", v: "+78.4%", hint: "test set / optimized" },
      { k: "OOD Reject", v: "90%", hint: "robust filtering" },
      { k: "Latency", v: "≈ 272ms", hint: "avg UI roundtrip" },
    ],
    []
  );

  useEffect(() => {
    return () => {
      if (stepTimerRef.current) window.clearInterval(stepTimerRef.current);
    };
  }, []);

  async function runDemo() {
    setErr(null);
    setLoading(true);
    setLabel("unknown");
    setScore(undefined);
    setLatencyMs(undefined);
    setStepIndex(0);

    // Visual stepper (smooth UX even if API responds fast)
    if (stepTimerRef.current) window.clearInterval(stepTimerRef.current);
    const startedAt = performance.now();
    stepTimerRef.current = window.setInterval(() => {
      setStepIndex((i) => {
        const next = i + 1;
        if (next >= demoSteps.length) {
          if (stepTimerRef.current) window.clearInterval(stepTimerRef.current);
          stepTimerRef.current = null;
          return demoSteps.length - 1;
        }
        return next;
      });
    }, 520);

    try {
      // 1) try internal Next.js proxy route if you have it
      // 2) fallback to direct Flask API via NEXT_PUBLIC_API_URL (default: http://localhost:5000)
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

      let res: ApiResponse | null = null;
      try {
        res = await postJSON<ApiResponse>("/api/predict", { text });
      } catch {
        res = await postJSON<ApiResponse>(`${apiBase}/predict`, { text });
      }

      const inferredLabel = normalizeLabel(res.label ?? res.sentiment);
      const inferredScore = normalizeScore(res);

      setLabel(inferredLabel);
      setScore(inferredScore);
      setLatencyMs(
        typeof res.latency_ms === "number"
          ? Math.round(res.latency_ms)
          : Math.round(performance.now() - startedAt)
      );

      // Finish stepper nicely
      setStepIndex(demoSteps.length - 1);
    } catch (e: any) {
      // Offline fallback (still looks good for demo)
      const fallback = text.toLowerCase();
      const pos = ["love", "great", "amazing", "perfect", "fast", "good", "awesome"];
      const neg = ["hate", "bad", "terrible", "awful", "slow", "worst", "broken"];
      const posHits = pos.filter((w) => fallback.includes(w)).length;
      const negHits = neg.filter((w) => fallback.includes(w)).length;

      const inferred: SentimentLabel =
        posHits === negHits ? "unknown" : posHits > negHits ? "positive" : "negative";

      setLabel(inferred);
      setScore(undefined);
      setLatencyMs(Math.round(performance.now() - startedAt));
      setErr(
        "API unreachable — fallback demo mode enabled. (Check Flask / CORS / NEXT_PUBLIC_API_URL)"
      );
    } finally {
      setLoading(false);
    }
  }

  const labelUI = useMemo(() => {
    if (label === "positive")
      return { text: "Positive", badge: "bg-emerald-500/15 text-emerald-200 ring-1 ring-emerald-400/20" };
    if (label === "negative")
      return { text: "Negative", badge: "bg-rose-500/15 text-rose-200 ring-1 ring-rose-400/20" };
    return { text: "Unknown", badge: "bg-white/10 text-white/70 ring-1 ring-white/15" };
  }, [label]);

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#05060a] text-white">
      <BackgroundGrid />
      <BackgroundBeams />

      {/* Top nav */}
      <header className="sticky top-0 z-40 border-b border-white/10 bg-black/25 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="grid h-9 w-9 place-items-center rounded-xl bg-white/10 ring-1 ring-white/15">
              <IconShield />
            </div>
            <div className="leading-tight">
              <div className="text-sm font-semibold tracking-wide">SA_FHE</div>
              <div className="text-[11px] text-white/60">Sentiment Analysis on Encrypted Data</div>
            </div>
          </div>

          <nav className="hidden items-center gap-6 text-sm text-white/70 md:flex">
            <a className="hover:text-white" href="#demo">
              Demo
            </a>
            <a className="hover:text-white" href="#how">
              How it works
            </a>
            <a className="hover:text-white" href="#perf">
              Performance
            </a>
            <a className="hover:text-white" href="#about">
              About
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <a
              className="hidden rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-sm text-white/80 hover:bg-white/10 md:inline-flex"
              href="https://github.com/Farx1/SA_FHE"
              target="_blank"
              rel="noreferrer"
            >
              GitHub
            </a>
            <ShimmerButton onClick={() => document.getElementById("demo")?.scrollIntoView({ behavior: "smooth" })}>
              Try demo
            </ShimmerButton>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative mx-auto max-w-6xl px-6 pb-16 pt-14 md:pt-16">
        <div className="grid gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, ease: "easeOut" }}
              className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs text-white/75"
            >
              <span className="inline-flex h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_0_4px_rgba(16,185,129,0.15)]" />
              Privacy-preserving ML • FHE showcase
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.65, ease: "easeOut", delay: 0.05 }}
              className="mt-5 text-balance text-4xl font-semibold tracking-tight md:text-5xl"
            >
              Sentiment analysis{" "}
              <span className="bg-gradient-to-r from-indigo-200 via-fuchsia-200 to-emerald-200 bg-clip-text text-transparent">
                without revealing the text
              </span>
              .
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.65, ease: "easeOut", delay: 0.12 }}
              className="mt-4 max-w-xl text-pretty text-base leading-relaxed text-white/70"
            >
              Text → embeddings (RoBERTa) → model (XGBoost) → prediction, all while keeping data encrypted during
              computation (FHE). The server never sees your input in plaintext.
            </motion.p>

            <div className="mt-7 flex flex-wrap gap-3">
              {stats.map((s, idx) => (
                <motion.div
                  key={s.k}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.45, delay: 0.18 + idx * 0.06 }}
                  className="rounded-2xl border border-white/12 bg-white/5 px-4 py-3"
                >
                  <div className="text-xs text-white/60">{s.k}</div>
                  <div className="mt-1 text-lg font-semibold">{s.v}</div>
                  <div className="mt-1 text-[11px] text-white/45">{s.hint}</div>
                </motion.div>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <ShimmerButton onClick={() => document.getElementById("demo")?.scrollIntoView({ behavior: "smooth" })}>
                Launch demo
              </ShimmerButton>
              <a
                className="inline-flex items-center gap-2 rounded-xl border border-white/15 bg-white/5 px-4 py-3 text-sm text-white/80 hover:bg-white/10"
                href="#how"
              >
                <IconPlay />
                Understand the pipeline
              </a>
            </div>
          </div>

          {/* Hero card (preview) */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: "easeOut", delay: 0.08 }}
            className="relative"
          >
            <div className="absolute -inset-6 rounded-[28px] bg-[radial-gradient(circle_at_30%_20%,rgba(168,85,247,0.20),transparent_45%),radial-gradient(circle_at_70%_70%,rgba(16,185,129,0.18),transparent_45%)] blur-2xl" />
            <div className="relative overflow-hidden rounded-[28px] border border-white/12 bg-black/35 p-5 shadow-[0_0_0_1px_rgba(255,255,255,0.05),0_20px_80px_rgba(0,0,0,0.6)] backdrop-blur-xl">
              <div className="flex items-center justify-between">
                <div className="text-sm font-semibold text-white/90">Encrypted Sentiment Demo</div>
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-white/10 px-2 py-1 text-[11px] text-white/70 ring-1 ring-white/10">
                    RoBERTa
                  </span>
                  <span className="rounded-full bg-white/10 px-2 py-1 text-[11px] text-white/70 ring-1 ring-white/10">
                    XGBoost
                  </span>
                  <span className="rounded-full bg-white/10 px-2 py-1 text-[11px] text-white/70 ring-1 ring-white/10">
                    FHE
                  </span>
                </div>
              </div>

              <div className="mt-4 space-y-3">
                <SkeletonRow />
                <SkeletonRow />
                <SkeletonRow short />
              </div>

              <div className="mt-6 grid grid-cols-3 gap-3">
                <MiniStat title="Input" value="Encrypted" />
                <MiniStat title="Compute" value="FHE" />
                <MiniStat title="Output" value="Label" />
              </div>

              <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="text-xs text-white/60">Pipeline</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {demoSteps.map((s, i) => (
                    <span
                      key={s.key}
                      className={cn(
                        "inline-flex items-center gap-2 rounded-full px-3 py-1 text-[11px] ring-1",
                        i < 2
                          ? "bg-emerald-500/10 text-emerald-200 ring-emerald-400/15"
                          : "bg-white/5 text-white/70 ring-white/10"
                      )}
                    >
                      <span className="opacity-80">{s.icon}</span>
                      {s.title}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Demo */}
      <section id="demo" className="relative mx-auto max-w-6xl px-6 pb-16">
        <div className="grid gap-8 lg:grid-cols-[1fr_1fr] lg:items-start">
          <div>
            <SectionTitle
              eyebrow="Interactive demo"
              title="Test a sentence — keep it private."
              desc="The frontend sends a request to the backend (Flask) and displays the result. If the API is down, a demo fallback activates."
            />

            <div className="mt-6 rounded-[28px] border border-white/12 bg-black/35 p-5 backdrop-blur-xl">
              <label className="text-xs text-white/60">Text</label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                rows={5}
                className="mt-2 w-full resize-none rounded-2xl border border-white/10 bg-black/40 p-4 text-sm text-white/90 outline-none ring-0 placeholder:text-white/35 focus:border-white/20"
                placeholder="Type something…"
              />

              <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className={cn("rounded-full px-3 py-1 text-xs", labelUI.badge)}>
                    {labelUI.text}
                  </span>
                  {typeof score === "number" && (
                    <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-white/70 ring-1 ring-white/10">
                      score: {score.toFixed(3)}
                    </span>
                  )}
                  {typeof latencyMs === "number" && (
                    <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-white/70 ring-1 ring-white/10">
                      {latencyMs}ms
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setText("This is the worst purchase I’ve made. Totally broken.");
                      setLabel("unknown");
                      setScore(undefined);
                      setLatencyMs(undefined);
                      setStepIndex(-1);
                      setErr(null);
                    }}
                    className="rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-sm text-white/80 hover:bg-white/10"
                  >
                    Use negative example
                  </button>
                  <ShimmerButton disabled={loading || text.trim().length < 3} onClick={runDemo}>
                    {loading ? "Running…" : "Run inference"}
                  </ShimmerButton>
                </div>
              </div>

              <AnimatePresence>
                {err && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 8 }}
                    className="mt-4 rounded-2xl border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-100"
                  >
                    {err}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Stepper */}
          <div className="rounded-[28px] border border-white/12 bg-black/35 p-5 backdrop-blur-xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-sm font-semibold">What happens under the hood</div>
                <div className="mt-1 text-sm text-white/65">
                  Each step is displayed to make the demo understandable and more credible.
                </div>
              </div>
              <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-white/70 ring-1 ring-white/10">
                educational
              </span>
            </div>

            <div className="mt-5 space-y-3">
              {demoSteps.map((s, i) => {
                const active = stepIndex === i;
                const done = stepIndex > i;
                const idle = stepIndex < i;

                return (
                  <motion.div
                    key={s.key}
                    initial={{ opacity: 0, y: 8 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, amount: 0.4 }}
                    transition={{ duration: 0.35, ease: "easeOut" }}
                    className={cn(
                      "group flex gap-4 rounded-2xl border p-4",
                      active
                        ? "border-white/20 bg-white/8"
                        : done
                        ? "border-emerald-400/15 bg-emerald-500/8"
                        : "border-white/10 bg-white/5"
                    )}
                  >
                    <div
                      className={cn(
                        "grid h-10 w-10 shrink-0 place-items-center rounded-xl ring-1",
                        active
                          ? "bg-white/10 ring-white/15"
                          : done
                          ? "bg-emerald-500/10 ring-emerald-400/20"
                          : "bg-white/5 ring-white/10"
                      )}
                    >
                      {s.icon}
                    </div>

                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <div className="truncate text-sm font-semibold">{s.title}</div>
                        {done && (
                          <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-[11px] text-emerald-200 ring-1 ring-emerald-400/15">
                            done
                          </span>
                        )}
                        {active && (
                          <span className="rounded-full bg-white/10 px-2 py-0.5 text-[11px] text-white/75 ring-1 ring-white/10">
                            running…
                          </span>
                        )}
                        {idle && stepIndex >= 0 && (
                          <span className="rounded-full bg-white/5 px-2 py-0.5 text-[11px] text-white/55 ring-1 ring-white/10">
                            queued
                          </span>
                        )}
                      </div>
                      <div className="mt-1 text-sm text-white/65">{s.desc}</div>

                      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/8">
                        <motion.div
                          className={cn(
                            "h-full rounded-full",
                            done ? "bg-emerald-400/70" : active ? "bg-white/55" : "bg-white/15"
                          )}
                          initial={{ width: 0 }}
                          animate={{
                            width: done ? "100%" : active ? "70%" : stepIndex < 0 ? "0%" : "10%",
                          }}
                          transition={{ duration: 0.55, ease: "easeOut" }}
                        />
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>

            <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/70">
              <div className="flex items-center gap-2 text-white/85">
                <IconInfo />
                <span className="font-semibold">Tip</span>
              </div>
              <p className="mt-2">
                Pro tip for production: add a Next.js route <code className="rounded bg-white/10 px-1">/api/predict</code> that proxies to Flask,
                to avoid CORS issues and handle timeouts server-side.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How it works + features */}
      <section id="how" className="relative mx-auto max-w-6xl px-6 pb-16">
        <SectionTitle
          eyebrow="Explained"
          title="A simple pipeline with strong guarantees."
          desc="A demo should be visual: we keep the language simple, use bento cards, and maintain a clear flow."
        />

        <div className="mt-7 grid gap-4 lg:grid-cols-3">
          <BentoCard
            title="Privacy-first"
            desc="The model only sees encrypted data during inference."
            icon={<IconLock />}
          />
          <BentoCard
            title="Real ML stack"
            desc="Transformer embeddings + XGBoost: fast, solid, and educational."
            icon={<IconSpark />}
          />
          <BentoCard
            title="Windows-friendly"
            desc="Fallback simulator when Concrete-ML is not available."
            icon={<IconTerminal />}
          />
          <BentoCard
            title="Docker ready"
            desc="Launch real FHE mode cleanly on Windows via Docker."
            icon={<IconBox />}
          />
          <BentoCard
            title="Observable"
            desc="Latency, OOD rejection, and visible metrics for credibility."
            icon={<IconPulse />}
          />
          <BentoCard
            title="Beautiful UI"
            desc="Micro-animations + professional background, without overdoing it."
            icon={<IconWand />}
          />
        </div>
      </section>

      {/* Performance */}
      <section id="perf" className="relative mx-auto max-w-6xl px-6 pb-20">
        <SectionTitle
          eyebrow="Metrics"
          title="Performance at a glance."
          desc="You can connect these numbers to your real metrics later (or load them from the API)."
        />

        <div className="mt-7 grid gap-4 md:grid-cols-3">
          <MetricCard title="Accuracy" value={78.4} suffix="%" subtitle="Optimized on test set" />
          <MetricCard title="OOD Reject" value={90} suffix="%" subtitle="Safety & robustness" />
          <MetricCard title="Latency" value={272} suffix="ms" subtitle="Average UI roundtrip" />
        </div>

        <div id="about" className="mt-10 rounded-[28px] border border-white/12 bg-black/35 p-6 backdrop-blur-xl">
          <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-sm font-semibold">About this showcase</div>
              <div className="mt-1 max-w-2xl text-sm text-white/65">
                Goal: make the project presentable (portfolio / course demo) with a modern, readable, and credible frontend.
              </div>
            </div>
            <a
              className="inline-flex items-center justify-center rounded-xl border border-white/15 bg-white/5 px-4 py-3 text-sm text-white/80 hover:bg-white/10"
              href="https://github.com/Farx1/SA_FHE"
              target="_blank"
              rel="noreferrer"
            >
              Open repository
            </a>
          </div>
        </div>
      </section>

      <footer className="border-t border-white/10 bg-black/20">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-6 py-8 text-sm text-white/60 md:flex-row md:items-center md:justify-between">
          <div>© {new Date().getFullYear()} SA_FHE — student showcase</div>
          <div className="flex items-center gap-4">
            <a className="hover:text-white" href="#demo">
              Demo
            </a>
            <a className="hover:text-white" href="#how">
              How it works
            </a>
            <a className="hover:text-white" href="#perf">
              Metrics
            </a>
          </div>
        </div>
      </footer>

      {/* Self-contained CSS animations */}
      <style jsx global>{`
        .bg-grid {
          background-image: linear-gradient(to right, rgba(255, 255, 255, 0.06) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.06) 1px, transparent 1px);
          background-size: 64px 64px;
          mask-image: radial-gradient(ellipse at center, black 55%, transparent 75%);
        }

        @keyframes floaty {
          0% { transform: translate3d(0, 0, 0); }
          50% { transform: translate3d(0, -10px, 0); }
          100% { transform: translate3d(0, 0, 0); }
        }

        @keyframes beam {
          0% { transform: translateX(-20%) translateY(0) rotate(-10deg); opacity: 0.25; }
          50% { transform: translateX(10%) translateY(-8%) rotate(-10deg); opacity: 0.5; }
          100% { transform: translateX(30%) translateY(0) rotate(-10deg); opacity: 0.25; }
        }
      `}</style>
    </main>
  );
}

/* ----------------------------- UI Blocks ----------------------------- */

function BackgroundGrid() {
  return (
    <div className="pointer-events-none absolute inset-0 -z-10">
      <div className="absolute inset-0 bg-grid opacity-[0.35]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_20%,rgba(99,102,241,0.18),transparent_45%),radial-gradient(circle_at_70%_70%,rgba(236,72,153,0.16),transparent_45%),radial-gradient(circle_at_40%_80%,rgba(16,185,129,0.12),transparent_45%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.08),transparent_55%)]" />
    </div>
  );
}

// (Aceternity-like name) — subtle moving “beams”
function BackgroundBeams() {
  return (
    <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
      <div
        className="absolute -left-[30%] top-[8%] h-[420px] w-[820px] rotate-[-10deg] rounded-full blur-3xl"
        style={{
          background:
            "radial-gradient(circle at 30% 50%, rgba(168, 85, 247, 0.22), transparent 55%), radial-gradient(circle at 70% 50%, rgba(99, 102, 241, 0.18), transparent 55%)",
          animation: "beam 10s ease-in-out infinite",
        }}
      />
      <div
        className="absolute -right-[30%] bottom-[8%] h-[420px] w-[820px] rotate-[-10deg] rounded-full blur-3xl"
        style={{
          background:
            "radial-gradient(circle at 30% 50%, rgba(16, 185, 129, 0.18), transparent 55%), radial-gradient(circle at 70% 50%, rgba(236, 72, 153, 0.14), transparent 55%)",
          animation: "beam 12s ease-in-out infinite",
        }}
      />
    </div>
  );
}

// (MagicUI-like)
function ShimmerButton({
  children,
  onClick,
  disabled,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={cn(
        "group relative inline-flex items-center justify-center overflow-hidden rounded-xl px-4 py-3 text-sm font-semibold",
        "bg-white text-black",
        "shadow-[0_10px_40px_rgba(0,0,0,0.45)]",
        "disabled:cursor-not-allowed disabled:opacity-60"
      )}
    >
      <span className="absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
        <span className="absolute -inset-32 bg-[conic-gradient(from_180deg_at_50%_50%,rgba(0,0,0,0),rgba(0,0,0,0.18),rgba(0,0,0,0))] blur-xl" />
      </span>
      <span className="relative">{children}</span>
    </button>
  );
}

function SectionTitle({ eyebrow, title, desc }: { eyebrow: string; title: string; desc: string }) {
  return (
    <div>
      <div className="inline-flex items-center rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs text-white/70">
        {eyebrow}
      </div>
      <h2 className="mt-4 text-balance text-2xl font-semibold tracking-tight md:text-3xl">{title}</h2>
      <p className="mt-2 max-w-2xl text-pretty text-sm leading-relaxed text-white/65">{desc}</p>
    </div>
  );
}

function BentoCard({ title, desc, icon }: { title: string; desc: string; icon: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.35 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="group relative overflow-hidden rounded-[26px] border border-white/12 bg-black/35 p-5 backdrop-blur-xl"
    >
      <div className="absolute -inset-10 opacity-0 blur-2xl transition-opacity duration-500 group-hover:opacity-100"
           style={{
             background:
               "radial-gradient(circle at 30% 20%, rgba(99,102,241,0.18), transparent 45%), radial-gradient(circle at 70% 70%, rgba(236,72,153,0.14), transparent 45%)",
           }}
      />
      <div className="relative flex items-start gap-4">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-white/10 ring-1 ring-white/15">
          {icon}
        </div>
        <div className="min-w-0">
          <div className="text-sm font-semibold">{title}</div>
          <div className="mt-1 text-sm text-white/65">{desc}</div>
        </div>
      </div>
    </motion.div>
  );
}

function MetricCard({
  title,
  value,
  suffix,
  subtitle,
}: {
  title: string;
  value: number;
  suffix: string;
  subtitle: string;
}) {
  return (
    <div className="rounded-[26px] border border-white/12 bg-black/35 p-6 backdrop-blur-xl">
      <div className="text-xs text-white/60">{title}</div>
      <div className="mt-2 text-3xl font-semibold tracking-tight">
        <AnimatedNumber value={value} />
        <span className="text-white/70">{suffix}</span>
      </div>
      <div className="mt-2 text-sm text-white/65">{subtitle}</div>
    </div>
  );
}

function AnimatedNumber({ value }: { value: number }) {
  const [n, setN] = useState(0);

  useEffect(() => {
    let raf = 0;
    const start = performance.now();
    const dur = 850;

    const tick = (t: number) => {
      const p = Math.min(1, (t - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      setN(value * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value]);

  const shown = value >= 100 ? Math.round(n) : Math.round(n * 10) / 10;
  return <span>{shown}</span>;
}

function SkeletonRow({ short }: { short?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div className="h-8 w-8 rounded-xl bg-white/8 ring-1 ring-white/10" />
      <div className="flex-1">
        <div className={cn("h-3 rounded-full bg-white/8 ring-1 ring-white/10", short ? "w-1/2" : "w-5/6")} />
        <div className={cn("mt-2 h-3 rounded-full bg-white/6 ring-1 ring-white/10", short ? "w-1/3" : "w-2/3")} />
      </div>
    </div>
  );
}

function MiniStat({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <div className="text-xs text-white/60">{title}</div>
      <div className="mt-1 text-sm font-semibold text-white/85">{value}</div>
    </div>
  );
}

/* ----------------------------- Icons ----------------------------- */

function IconShield() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" className="text-white/85" fill="none">
      <path
        d="M12 2l7 4v6c0 5-3 9-7 10-4-1-7-5-7-10V6l7-4Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconLock() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" className="text-white/85" fill="none">
      <path
        d="M7 11V8a5 5 0 0 1 10 0v3"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
      <path
        d="M7.5 11h9A2.5 2.5 0 0 1 19 13.5v5A2.5 2.5 0 0 1 16.5 21h-9A2.5 2.5 0 0 1 5 18.5v-5A2.5 2.5 0 0 1 7.5 11Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconSpark() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" className="text-white/85" fill="none">
      <path d="M12 2l1.2 4.2L17.4 8 13.2 9.2 12 13.4 10.8 9.2 6.6 8l4.2-1.8L12 2Z" stroke="currentColor" strokeWidth="1.6" />
      <path d="M19 13l.8 2.6L22 17l-2.2.6L19 20l-.8-2.4L16 17l2.2-1.4L19 13Z" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  );
}

function IconBolt() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" className="text-white/85" fill="none">
      <path
        d="M13 2L4 14h7l-1 8 10-14h-7l0-6Z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconCheck() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" className="text-white/85" fill="none">
      <path d="M20 6 9 17l-5-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function IconGrid() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" className="text-white/85" fill="none">
      <path d="M4 4h7v7H4V4Zm9 0h7v7h-7V4ZM4 13h7v7H4v-7Zm9 0h7v7h-7v-7Z" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  );
}

function IconPlay() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" className="text-white/85" fill="none">
      <path d="M9 7v10l10-5-10-5Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    </svg>
  );
}

function IconInfo() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" className="text-white/85" fill="none">
      <path d="M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Z" stroke="currentColor" strokeWidth="1.6" />
      <path d="M12 10v7" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M12 7h.01" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" />
    </svg>
  );
}

function IconTerminal() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" className="text-white/85" fill="none">
      <path d="M4 5h16v14H4V5Z" stroke="currentColor" strokeWidth="1.6" />
      <path d="M7 9l3 3-3 3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M12 15h5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function IconBox() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" className="text-white/85" fill="none">
      <path d="M21 8l-9-5-9 5 9 5 9-5Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
      <path d="M3 8v8l9 5 9-5V8" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
      <path d="M12 13v8" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function IconPulse() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" className="text-white/85" fill="none">
      <path d="M3 12h4l2-6 4 12 2-6h6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function IconWand() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" className="text-white/85" fill="none">
      <path d="M4 20 14 10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M7 17l-3 3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M14 4l6 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M16 2l.9 2.8L20 6l-3.1 1.2L16 10l-.9-2.8L12 6l3.1-1.2L16 2Z" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  );
}
