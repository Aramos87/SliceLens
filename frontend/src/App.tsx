import { useEffect, useMemo, useState } from "react";
import { listRuns, loadFaq, residualSearch, searchRun } from "./api";
import type { FaqItem, ResidualResponse, RunSummary, Slice } from "./types";

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

type Phase = "idle" | "screenshot" | "rewrite";

export default function App() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [runId, setRunId] = useState("negation-trap");
  const [phase, setPhase] = useState<Phase>("idle");
  const [slices, setSlices] = useState<Slice[]>([]);
  const [openId, setOpenId] = useState<string | null>(null);
  const [residual, setResidual] = useState<ResidualResponse | null>(null);
  const [faq, setFaq] = useState<FaqItem[]>([]);
  const [openFaq, setOpenFaq] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const selected = runs.find((run) => run.id === runId) ?? runs[0];
  const openSlice = slices.find((slice) => slice.predicate === openId) ?? slices[0];

  useEffect(() => {
    listRuns().then((payload) => {
      setRuns(payload.runs);
      if (payload.runs[0]) setRunId(payload.runs[0].id);
    });
    loadFaq().then((payload) => setFaq(payload.items));
  }, []);

  const claimedIds = useMemo(
    () => slices.flatMap((slice) => slice.member_ids),
    [slices],
  );

  async function onLook() {
    if (!selected) return;
    setError(null);
    setResidual(null);
    setPhase("screenshot");
    try {
      const payload = await searchRun(selected.id);
      setSlices(payload.slices);
      setOpenId(payload.slices[0]?.predicate ?? null);
      setPhase("rewrite");
    } catch (err) {
      setError(err instanceof Error ? err.message : "search failed");
      setPhase("idle");
    }
  }

  async function onResidual() {
    if (!selected) return;
    const payload = await residualSearch(selected.id, claimedIds);
    setResidual(payload);
  }

  function onChangeRun(next: string) {
    setRunId(next);
    setPhase("idle");
    setSlices([]);
    setOpenId(null);
    setResidual(null);
  }

  return (
    <div className="page">
      <header className="mast">
        <p className="kicker">Slice Lens</p>
        <h1>Headline accuracy is a screenshot, not a finding.</h1>
        <p className="lede">
          One click names the slice that was carrying the errors, rewrites what you’d have
          reported, and asks a held-out split whether the name still holds.
        </p>
      </header>

      <section className="dashed-step" aria-label="dashed step">
        <p className="step-label">1. Pick a run, then press the black button.</p>
        <label className="run-picker">
          Run
          <select
            value={selected?.id ?? runId}
            onChange={(event) => onChangeRun(event.target.value)}
            aria-label="pick a run"
          >
            {runs.map((run) => (
              <option key={run.id} value={run.id}>
                {run.title}
              </option>
            ))}
          </select>
        </label>
        {selected ? <p className="blurb">{selected.blurb}</p> : null}
        <button type="button" className="black-button" onClick={onLook}>
          Look through this run
        </button>
      </section>

      {error ? <p className="error">{error}</p> : null}

      {phase === "screenshot" && selected ? (
        <section className="hero hero--screenshot" aria-label="screenshot hero">
          <p className="hero-kicker">screenshot</p>
          <p className="hero-number">{pct(selected.screenshot_accuracy)}</p>
          <p className="hero-copy">
            This is the number you’d paste into a launch post. Looking through the run…
          </p>
        </section>
      ) : null}

      {phase === "rewrite" && openSlice ? (
        <>
          <section className="hero hero--rewrite" aria-label="rewrite hero">
            <p className="hero-kicker">rewrite of the open slice</p>
            <p className="hero-number">{pct(openSlice.slice_accuracy)}</p>
            <p className="hero-copy">{openSlice.rewrite}</p>
          </section>

          <section className="errors-section" aria-label="Where did the errors go?">
            <h2>Where did the errors go?</h2>
            <div className="comparison" aria-label="comparison row">
              <div>
                <span>screenshot</span>
                <strong>{pct(openSlice.screenshot_accuracy)}</strong>
              </div>
              <div>
                <span>this slice</span>
                <strong>{pct(openSlice.slice_accuracy)}</strong>
              </div>
              <div>
                <span>you’d have reported</span>
                <strong>{pct(openSlice.youd_have_reported)}</strong>
              </div>
            </div>
          </section>

          <section className="legend" aria-label="badge legend">
            <span className="badge badge--confirmed">confirmed</span>
            <span>held-out split still worse</span>
            <span className="badge badge--fluke">did not replicate</span>
            <span>discovery only</span>
          </section>

          <ul className="slice-list">
            {slices.map((slice) => (
              <li key={slice.predicate}>
                <button
                  type="button"
                  className={slice.predicate === openSlice.predicate ? "slice slice--open" : "slice"}
                  onClick={() => setOpenId(slice.predicate)}
                >
                  <span className={`badge ${slice.status === "confirmed" ? "badge--confirmed" : "badge--fluke"}`}>
                    {slice.status}
                  </span>
                  <strong>{slice.label}</strong>
                  <em>{pct(slice.slice_accuracy)}</em>
                  <p>{slice.interpretation}</p>
                </button>
              </li>
            ))}
          </ul>

          <section className="examples">
            <h3>Failures in “{openSlice.label}”</h3>
            {openSlice.examples.map((example) => (
              <figure key={example.id}>
                <pre>{example.prompt}</pre>
                <figcaption>
                  gold {example.gold} · model {example.prediction} · {example.split}
                </figcaption>
              </figure>
            ))}
          </section>

          <section className="residual">
            <button type="button" className="residual-button" onClick={onResidual}>
              Search the residual
            </button>
            {residual?.empty ? <p className="empty">{residual.message}</p> : null}
            {residual && !residual.empty
              ? residual.slices.map((slice) => (
                  <p key={slice.predicate}>
                    Residual slice: {slice.label} {pct(slice.slice_accuracy)}
                  </p>
                ))
              : null}
          </section>
        </>
      ) : null}

      <section className="faq" aria-label="FAQ">
        <h2>FAQ</h2>
        {faq.map((item) => (
          <article key={item.question}>
            <button
              type="button"
              className="faq-q"
              aria-expanded={openFaq === item.question}
              onClick={() => setOpenFaq(openFaq === item.question ? null : item.question)}
            >
              {item.question}
            </button>
            {openFaq === item.question ? <p className="faq-a">{item.answer}</p> : null}
          </article>
        ))}
      </section>
    </div>
  );
}
