"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function FileSlot({ label, file, onChange, count }) {
  return (
    <label className="slot">
      <span className="slot-label">{label}</span>
      <input type="file" accept="application/json,.json" onChange={(e) => onChange(e.target.files?.[0] ?? null)} />
      {file && <span className="slot-meta">{file.name}{count != null ? ` - ${count} tests` : ""}</span>}
    </label>
  );
}

async function readRun(file) {
  const text = await file.text();
  const parsed = JSON.parse(text);
  if (!Array.isArray(parsed)) throw new Error(`${file.name} must contain a JSON array.`);
  return { text, count: parsed.length };
}

export default function Home() {
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [count1, setCount1] = useState(null);
  const [count2, setCount2] = useState(null);
  const [prompt, setPrompt] = useState("find flaky tests");
  const [password, setPassword] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function pick(file, setFile, setCount) {
    setError("");
    setFile(file);
    setCount(null);
    if (!file) return;
    try {
      setCount((await readRun(file)).count);
    } catch (e) {
      setFile(null);
      setError(e instanceof SyntaxError ? `${file.name} is not valid JSON.` : e.message);
    }
  }

  async function analyze() {
    setError("");
    setResult("");
    setLoading(true);
    try {
      const [r1, r2] = await Promise.all([readRun(file1), readRun(file2)]);
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run1: r1.text, run2: r2.text, prompt, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Request failed.");
      setResult(data.result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Flaky Test Finder</h1>
      <p className="sub">Upload two runs of the same test suite. Tests whose result differs between runs are flaky.</p>

      <div className="slots">
        <FileSlot label="Run 1" file={file1} count={count1} onChange={(f) => pick(f, setFile1, setCount1)} />
        <FileSlot label="Run 2" file={file2} count={count2} onChange={(f) => pick(f, setFile2, setCount2)} />
      </div>

      <label className="field">
        <span>Request</span>
        <input type="text" value={prompt} onChange={(e) => setPrompt(e.target.value)} />
      </label>
      <label className="field">
        <span>Password (if the site requires one)</span>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </label>

      <button onClick={analyze} disabled={loading || !file1 || !file2}>
        {loading ? "Analyzing..." : "Find flaky tests"}
      </button>

      {error && <p className="error">{error}</p>}
      {result && (
        <section className="result">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{result}</ReactMarkdown>
        </section>
      )}
    </main>
  );
}
