import { useEffect, useMemo, useState } from "react";

type Stage = "build" | "public" | "hidden" | "security" | "quality" | "mutation" | "regression";

type Check = {
  name: string;
  stage: Stage;
  passed: boolean;
  exit_code: number;
  duration_ms: number;
  stdout: string;
  stderr: string;
  weight: number;
  timed_out: boolean;
};

type Run = {
  run_id: string;
  case_id: string;
  mode: "human" | "agent";
  created_at: string;
  provider: string | null;
  model: string | null;
  prompt_id: string | null;
  usage: null | { input_tokens: number | null; output_tokens: number | null; estimated_cost_usd: number | null };
  patch: string;
  baseline_checks: Check[];
  checks: Check[];
  score: {
    raw_score: number;
    changed_lines_penalty: number;
    regression_penalty: number;
    final_score: number;
    changed_lines: number;
    regression_count: number;
    stage_scores: Record<string, number>;
  };
  runtime_ms: number;
};

type CaseSummary = {
  id: string;
  title: string;
  stack: string[];
  defect_category: string;
  difficulty: string;
  security_implications: string | null;
};

type CaseDetail = {
  issue: string;
  manifest: CaseSummary & { expected_behavior: string[] };
};

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json() as Promise<T>;
}

function runLabel(run: Run): string {
  if (run.mode === "human") return "human";
  return `${run.provider ?? "agent"}/${run.model ?? "unknown"}`;
}

function money(value: number | null | undefined): string {
  return value == null ? "not configured" : `$${value.toFixed(6)}`;
}

function Diff({ patch }: { patch: string }) {
  return (
    <pre className="diff" aria-label="Submitted patch">
      {patch.split("\n").map((line, index) => {
        const kind = line.startsWith("+") && !line.startsWith("+++") ? "add" : line.startsWith("-") && !line.startsWith("---") ? "del" : line.startsWith("@@") ? "hunk" : "plain";
        return <span className={`diff-line ${kind}`} key={`${index}-${line}`}>{line || " "}{"\n"}</span>;
      })}
    </pre>
  );
}

function Checks({ checks }: { checks: Check[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>Stage</th><th>Check</th><th>Result</th><th>Weight</th><th>Runtime</th></tr></thead>
        <tbody>
          {checks.map((check) => (
            <tr key={`${check.stage}-${check.name}`}>
              <td><span className="chip">{check.stage}</span></td>
              <td>{check.name}</td>
              <td><span className={check.passed ? "status pass" : "status fail"}>{check.passed ? "PASS" : check.timed_out ? "TIMEOUT" : "FAIL"}</span></td>
              <td>{check.weight}</td>
              <td>{check.duration_ms} ms</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function App() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [caseDetail, setCaseDetail] = useState<CaseDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getJson<CaseSummary[]>("/api/cases"), getJson<Run[]>("/api/runs")])
      .then(([caseRows, runRows]) => {
        setCases(caseRows);
        setRuns(runRows);
        setSelectedId(runRows[0]?.run_id ?? null);
      })
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : String(reason)));
  }, []);

  const selected = runs.find((run) => run.run_id === selectedId) ?? null;
  useEffect(() => {
    if (!selected) {
      setCaseDetail(null);
      return;
    }
    getJson<CaseDetail>(`/api/cases/${encodeURIComponent(selected.case_id)}`)
      .then(setCaseDetail)
      .catch((reason: unknown) => setError(reason instanceof Error ? reason.message : String(reason)));
  }, [selected?.case_id]);

  const comparisons = useMemo(() => {
    const groups = new Map<string, Run[]>();
    for (const run of runs) {
      const key = `${run.case_id}|${runLabel(run)}|${run.prompt_id ?? "default"}`;
      groups.set(key, [...(groups.get(key) ?? []), run]);
    }
    return [...groups.entries()].map(([key, group]) => ({
      key,
      caseId: group[0].case_id,
      label: runLabel(group[0]),
      prompt: group[0].prompt_id ?? "default",
      trials: group.length,
      mean: group.reduce((sum, run) => sum + run.score.final_score, 0) / group.length,
      min: Math.min(...group.map((run) => run.score.final_score)),
      max: Math.max(...group.map((run) => run.score.final_score)),
    }));
  }, [runs]);

  const baselineFailures = selected?.baseline_checks.filter((check) => !check.passed) ?? [];
  const securityChecks = selected?.checks.filter((check) => check.stage === "security") ?? [];

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Deterministic software repair evaluation</p>
          <h1>AI Code Rescue Bench</h1>
          <p className="lede">Transparent scoring for human patches and coding-agent attempts. Hidden evaluators, sandbox limits, regressions, diffs, runtime, and provider cost stay inspectable.</p>
        </div>
        <div className="hero-stats">
          <div><strong>{cases.length}</strong><span>benchmark cases</span></div>
          <div><strong>{runs.length}</strong><span>recorded runs</span></div>
          <div><strong>{comparisons.length}</strong><span>comparison groups</span></div>
        </div>
      </header>

      {error && <div className="error" role="alert">API error: {error}</div>}

      <section className="panel">
        <div className="section-head"><div><p className="eyebrow">Experiments</p><h2>Run comparison</h2></div><p>Repeated trials are grouped by case, provider/model, and prompt id.</p></div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Benchmark</th><th>Human / model</th><th>Prompt</th><th>Trials</th><th>Mean</th><th>Range</th></tr></thead>
            <tbody>{comparisons.map((row) => <tr key={row.key}><td>{row.caseId}</td><td>{row.label}</td><td>{row.prompt}</td><td>{row.trials}</td><td>{row.mean.toFixed(2)}</td><td>{row.min.toFixed(2)}–{row.max.toFixed(2)}</td></tr>)}</tbody>
          </table>
        </div>
      </section>

      <section className="layout">
        <aside className="panel run-list">
          <div className="section-head compact"><div><p className="eyebrow">Artifacts</p><h2>Runs</h2></div></div>
          {runs.length === 0 && <p className="muted">No results yet. Run the deterministic mock demo to populate this view.</p>}
          {runs.map((run) => (
            <button className={run.run_id === selectedId ? "run active" : "run"} key={run.run_id} onClick={() => setSelectedId(run.run_id)}>
              <span>{run.case_id}</span><strong>{run.score.final_score.toFixed(2)}</strong><small>{runLabel(run)}</small>
            </button>
          ))}
        </aside>

        <div className="detail">
          {!selected && <section className="panel empty"><h2>No evaluation selected</h2><p>Run <code>make demo</code> or evaluate a human patch to create a scorecard.</p></section>}
          {selected && (
            <>
              <section className="panel score-panel">
                <div><p className="eyebrow">{selected.case_id}</p><h2>{caseDetail?.manifest.title ?? selected.case_id}</h2><p className="muted">{caseDetail?.manifest.defect_category} · {caseDetail?.manifest.difficulty}</p></div>
                <div className="score"><strong>{selected.score.final_score.toFixed(2)}</strong><span>/ 100</span></div>
              </section>

              <section className="metrics">
                <div className="metric"><span>Runtime</span><strong>{(selected.runtime_ms / 1000).toFixed(2)}s</strong></div>
                <div className="metric"><span>Changed lines</span><strong>{selected.score.changed_lines}</strong></div>
                <div className="metric"><span>Regressions</span><strong>{selected.score.regression_count}</strong></div>
                <div className="metric"><span>Provider cost</span><strong>{money(selected.usage?.estimated_cost_usd)}</strong></div>
                <div className="metric"><span>Input tokens</span><strong>{selected.usage?.input_tokens ?? "n/a"}</strong></div>
                <div className="metric"><span>Output tokens</span><strong>{selected.usage?.output_tokens ?? "n/a"}</strong></div>
              </section>

              <section className="panel"><div className="section-head"><div><p className="eyebrow">Original failure</p><h2>Baseline before patch</h2></div><span>{baselineFailures.length} failing checks</span></div><p className="issue">{caseDetail?.issue ?? "Loading issue description…"}</p><Checks checks={baselineFailures} /></section>
              <section className="panel"><div className="section-head"><div><p className="eyebrow">Submitted patch</p><h2>Unified diff</h2></div><span>{selected.mode === "human" ? "human" : runLabel(selected)}</span></div><Diff patch={selected.patch} /></section>
              <section className="panel"><div className="section-head"><div><p className="eyebrow">Evaluation</p><h2>Deterministic checks</h2></div><span>raw {selected.score.raw_score.toFixed(2)} · penalties {(selected.score.changed_lines_penalty + selected.score.regression_penalty).toFixed(2)}</span></div><Checks checks={selected.checks} /></section>
              <section className="panel"><div className="section-head"><div><p className="eyebrow">Security</p><h2>Security checks</h2></div></div><Checks checks={securityChecks} />{caseDetail?.manifest.security_implications && <p className="callout"><strong>Impact:</strong> {caseDetail.manifest.security_implications}</p>}</section>
            </>
          )}
        </div>
      </section>
    </main>
  );
}
