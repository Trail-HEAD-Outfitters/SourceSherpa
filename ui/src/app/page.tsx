'use client';

import { useState } from "react";
import styles from "./page.module.css";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [modelId, setModelId] = useState("us.amazon.nova-premier-v1:0");
  const [maxContextDocs, setMaxContextDocs] = useState(50);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [debug, setDebug] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("http://localhost:8000/v1/stage1/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          model_id: modelId,
          max_context_docs: maxContextDocs,
          debug, // <-- send debug flag
        }),
      });
      if (!res.ok) {
        const err = await res.text();
        throw new Error(err);
      }
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  // Utility to extract the actual Mongo filter from LLM/debug output, refactored for low complexity
  function extractMongoFilter(raw: any): string {
    // Helper to parse JSON safely
    function tryParse(val: any) {
      if (typeof val !== 'string') return val;
      try {
        return JSON.parse(val);
      } catch {
        return val;
      }
    }
    // Helper to unwrap common wrappers
    function unwrap(val: any): any {
      let current = val;
      const wrappers = ['output', 'message', 'content'];
      for (const key of wrappers) {
        if (current && typeof current === 'object' && key in current) {
          current = current[key];
        }
      }
      return current;
    }
    // Unwrap and parse repeatedly until stable
    let prev;
    let filter = raw;
    do {
      prev = filter;
      filter = tryParse(filter);
      filter = unwrap(filter);
    } while (filter !== prev && typeof filter === 'string');
    // Final parse if still string
    filter = tryParse(filter);
    if (typeof filter === 'object') {
      return JSON.stringify(filter, null, 2);
    }
    return String(filter);
  }

  return (
    <div className={styles.nesPage}>
      <main className={styles.nesMain}>
        <div className={styles.nesLogoRow}>
          {/* Remove animation from N logo */}
          <span className={styles.nesLogoN}>N</span>
          <span className={styles.nesLogoE}>E</span>
          <span className={styles.nesLogoS}>S</span>
          <span className={styles.nesLogoDot}>.</span>
          <span className={styles.nesLogoJs}>JS</span>
        </div>
        <h1 className={styles.nesTitle}>SourceSherpa</h1>
        <h2 className={styles.nesSubtitle}>Ask a Codebase Question</h2>
        <form onSubmit={handleSubmit} className={styles.nesForm}>
          <label className={styles.nesLabel} htmlFor="question-input">
            Question:
          </label>
          <textarea
            id="question-input"
            className={styles.nesTextarea}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            required
          />
          <label className={styles.nesLabel} htmlFor="modelid-input">
            Model ID:
          </label>
          <input
            id="modelid-input"
            className={styles.nesInput}
            type="text"
            value={modelId}
            onChange={(e) => setModelId(e.target.value)}
            required
          />
          <label className={styles.nesLabel} htmlFor="maxdocs-input">
            Max Context Docs:
          </label>
          <input
            id="maxdocs-input"
            className={styles.nesInput}
            type="number"
            value={maxContextDocs}
            min={1}
            max={1000}
            onChange={(e) => setMaxContextDocs(Number(e.target.value))}
          />
          <label className={styles.nesLabel} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <input
              type="checkbox"
              checked={debug}
              onChange={e => setDebug(e.target.checked)}
              style={{ marginRight: 8 }} /> Show Debug Info
          </label>
          <button
            type="submit"
            className={styles.nesButton}
            disabled={loading}
          >
            {loading ? <span className={styles.nesBlink}>Loading...</span> : "Ask"}
          </button>
        </form>
        {error && (
          <div className={styles.nesError}>{error}</div>
        )}
        {result && (
          <div className={styles.nesResultPanel}>
            <div className={styles.nesResultTitle}>LLM Final Response</div>
            <div className={styles.nesResultSections}>
              {result.llm_answer && (
                <section className={styles.nesResultSection}>
                  <div className={styles.nesResultSectionTitle}>LLM Answer</div>
                  <pre className={styles.nesResultTextScrollable}>{(() => {
                    const answer = result.llm_answer;
                    if (answer && typeof answer === 'object' && 'content' in answer) {
                      const content = answer.content;
                      if (Array.isArray(content)) {
                        return content.map((c: any) => typeof c === 'string' ? c : JSON.stringify(c, null, 2)).join('\n\n');
                      } else {
                        return typeof content === 'string' ? content : JSON.stringify(content, null, 2);
                      }
                    } else {
                      return typeof answer === 'string' ? answer : JSON.stringify(answer, null, 2);
                    }
                  })()}</pre>
                </section>
              )}
            </div>
          </div>
        )}
        {result && result._debug && (
          <div className={styles.nesResultPanel}>
            <div className={styles.nesResultTitle}>Debug Details</div>
            <div className={styles.nesResultSections}>
              {result._debug.mongo_filter && result._debug.mongo_filter.content && (
                <section className={styles.nesResultSection}>
                  <div className={styles.nesResultSectionTitle}>Mongo Query</div>
                  <pre className={styles.nesResultTextScrollable}>{
                    extractMongoFilter(result._debug.mongo_filter.content)
                  }</pre>
                </section>
              )}
              {Object.entries(result._debug).map(([key, value]) => (
                key !== 'mongo_filter' && (
                  <section key={key} className={styles.nesResultSection}>
                    <div className={styles.nesResultSectionTitle}>{key.replace(/_/g, ' ')}</div>
                    <pre className={styles.nesResultTextScrollable}>{typeof value === 'string' ? value : JSON.stringify(value, null, 2)}</pre>
                  </section>
                )
              ))}
            </div>
          </div>
        )}
      </main>
      <footer className={styles.nesFooter}>
        <span className={styles.nesFooterBlink}>N</span>
        <span className={styles.nesFooterText}>Nintendo Style UI</span>
      </footer>
    </div>
  );
}
