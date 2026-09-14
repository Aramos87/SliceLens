import { useEffect, useMemo, useState } from "react";
import {
  analyzePack,
  analyzeResidual,
  listRuns,
  loadFaq,
  loadGuide,
  loadPack,
  residualSearch,
  searchRun,
} from "./api";
import type { DemoPack, FaqItem, Guide, ResidualResponse, RunSummary, Slice } from "./types";

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

type Phase = "idle" | "screenshot" | "rewrite";

const EVAL_TYPES = [
  {
    title: "Overall score",
    body: "Percent of questions the model got right. This is the number people screenshot.",
  },
  {
    title: "Slice",
    body: "A named group of questions that share one trait, such as containing “not” or a unit.",
  },
  {
    title: "You’d have reported",
    body: "The score if you dropped that group. The headline you would have published.",
  },
  {
    title: "Check twice",
    body: "We hold out half the data. confirmed still fails there. did not replicate was a fluke.",
  },
];

export default function App() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [runId, setRunId] = useState("negation-trap");
  const [guide, setGuide] = useState<Guide | null>(null);
  const [pack, setPack] = useState<DemoPack | null>(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [editorText, setEditorText] = useState("");
  const [editorError, setEditorError] = useState<string | null>(null);
  const [editedPack, setEditedPack] = useState<DemoPack | null>(null);
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

  useEffect(() => {
    if (!runId) return;
    setGuide(null);
    setPack(null);
    setEditorText("");
    setEditorError(null);
    setEditedPack(null);
    setEditorOpen(false);
    loadGuide(runId).then((payload) => setGuide(payload.guide));
    loadPack(runId).then((payload) => {
      setPack(payload);
      setEditorText(JSON.stringify(payload, null, 2));
    });
  }, [runId]);

  const claimedIds = useMemo(
    () => slices.flatMap((slice) => slice.member_ids),
    [slices],
  );

  function resetResults() {
    setPhase("idle");
    setSlices([]);
    setOpenId(null);
    setResidual(null);
    setError(null);
  }

  function onChangeTab(next: string) {
    setRunId(next);
    resetResults();
  }

  async function onFind() {
    if (!selected) return;
    setError(null);
    setResidual(null);
    setEditedPack(null);
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
    const payload = editedPack
      ? await analyzeResidual(editedPack, claimedIds)
      : await residualSearch(selected.id, claimedIds);
    setResidual(payload);
  }

  async function onRunEdit() {
    setEditorError(null);
    setError(null);
    let parsed: DemoPack;
    try {
      parsed = JSON.parse(editorText) as DemoPack;
    } catch {
      setEditorError("That is not valid JSON. Check the commas and quotes.");
      return;
    }
    if (!parsed || !Array.isArray(parsed.items)) {
      setEditorError("JSON needs an items list of questions.");
      return;
    }
    setResidual(null);
    setPhase("screenshot");
    try {
      const payload = await analyzePack(parsed);
      setEditedPack(parsed);
      setSlices(payload.slices);
      setOpenId(payload.slices[0]?.predicate ?? null);
      setPhase("rewrite");
    } catch (err) {
      setPhase("idle");
      setEditorError(err instanceof Error ? err.message : "could not run this JSON");
    }
  }

  function onResetJson() {
    if (!pack) return;
    setEditorText(JSON.stringify(pack, null, 2));
    setEditorError(null);
    setEditedPack(null);
  }

  return (
    <div className="page">
      <header className="mast">
        <p className="kicker">Slice Lens</p>
        <h1>A pretty score can hide one weak group of questions.</h1>
        <p className="lede">
          Leave knowing this: an overall percent is a screenshot. This page names the group
          that was carrying the errors, shows the score you would have published without it,
          and checks the pattern on questions it did not use to find it.
        </p>
      </header>

      <section className="eval-types" aria-label="evaluation types">
        {EVAL_TYPES.map((card) => (
          <article key={card.title}>
            <h2>{card.title}</h2>
            <p>{card.body}</p>
          </article>
        ))}
      </section>

      <div className="tabs" role="tablist" aria-label="demos">
        {runs.map((run) => (
          <button
            key={run.id}
            type="button"
            role="tab"
            aria-selected={run.id === selected?.id}
            className={run.id === selected?.id ? "tab tab--on" : "tab"}
            onClick={() => onChangeTab(run.id)}
          >
            {run.title}
          </button>
        ))}
      </div>

      <div className="workspace">
        <section className="column column--test" aria-label="this test">
          <p className="column-kicker">This test</p>
          <h2>{selected?.title ?? "Loading"}</h2>
          {guide ? (
            <>
              <p className="story">{guide.one_line}</p>
              <p className="story">
                <strong>What “right” looks like.</strong> {guide.success}
              </p>
              <p className="story">
                <strong>What you should notice.</strong> {guide.expect}
              </p>
              {selected ? (
                <p className="counts">
                  {selected.n} questions · {selected.discover_n} to find a pattern ·{" "}
                  {selected.confirm_n} held out · overall {pct(selected.screenshot_accuracy)}
                </p>
              ) : null}

              <h3>Fields in each row</h3>
              <dl className="glossary">
                {guide.fields.map((field) => (
                  <div key={field.key}>
                    <dt>{field.label}</dt>
                    <dd>{field.meaning}</dd>
                  </div>
                ))}
                {guide.predicates.map((pred) => (
                  <div key={pred.key}>
                    <dt>{pred.label}</dt>
                    <dd>{pred.meaning}</dd>
                  </div>
                ))}
              </dl>

              <h3>Three rows from this test</h3>
              <div className="sample-cards">
                {guide.examples.map((example) => (
                  <article key={example.id} className="sample">
                    <p className="sample-kind">{example.kind}</p>
                    <p>
                      <span>Question</span>
                      {example.prompt}
                    </p>
                    <p>
                      <span>Right answer</span>
                      {example.gold}
                    </p>
                    <p>
                      <span>Model said</span>
                      {example.prediction}
                    </p>
                    <p className="why">
                      <span>Why this row matters</span>
                      {example.why}
                    </p>
                  </article>
                ))}
              </div>
            </>
          ) : (
            <p className="story">Loading the questions…</p>
          )}

          <div className="dashed-step" aria-label="dashed step">
            <p className="step-label">
              Read the rows above, then press the black button. The right column will fill in.
            </p>
            <button type="button" className="black-button" onClick={onFind}>
              Find the hidden failure
            </button>
          </div>

          <details
            className="json-play"
            open={editorOpen}
            onToggle={(event) => setEditorOpen(event.currentTarget.open)}
          >
            <summary>Edit this run (JSON)</summary>
            <p>
              Session only. Nothing is uploaded or saved. Change a gold answer or a prompt,
              then run it again.
            </p>
            <textarea
              aria-label="run JSON"
              value={editorText}
              onChange={(event) => setEditorText(event.target.value)}
              spellCheck={false}
            />
            <div className="json-actions">
              <button type="button" className="black-button" onClick={onRunEdit}>
                Run my edit
              </button>
              <button type="button" className="residual-button" onClick={onResetJson}>
                Reset
              </button>
            </div>
            {editorError ? <p className="error">{editorError}</p> : null}
          </details>
        </section>

        <section className="column column--found" aria-label="what we found">
          <p className="column-kicker">What we found</p>
          {error ? <p className="error">{error}</p> : null}

          {phase === "idle" ? (
            <div className="empty-found" aria-label="results empty">
              <h2>Press Find the hidden failure.</h2>
              <p>
                This side will show the pretty score, the weak group, and the score you’d
                have published if that group were gone.
              </p>
            </div>
          ) : null}

          {phase === "screenshot" && selected ? (
            <section className="hero hero--screenshot" aria-label="screenshot hero">
              <p className="hero-kicker">screenshot</p>
              <p className="hero-number">{pct(selected.screenshot_accuracy)}</p>
              <p className="hero-copy">The number you’d paste into a launch post. Looking…</p>
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
                    <em>All questions</em>
                  </div>
                  <div>
                    <span>this slice</span>
                    <strong>{pct(openSlice.slice_accuracy)}</strong>
                    <em>Only the weak group</em>
                  </div>
                  <div>
                    <span>you’d have reported</span>
                    <strong>{pct(openSlice.youd_have_reported)}</strong>
                    <em>If that group were gone</em>
                  </div>
                </div>
              </section>

              <section className="legend" aria-label="badge legend">
                <span className="badge badge--confirmed">confirmed</span>
                <span>held-out half still worse</span>
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
                      <span
                        className={`badge ${slice.status === "confirmed" ? "badge--confirmed" : "badge--fluke"}`}
                      >
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
                <h3>Misses in “{openSlice.label}”</h3>
                {openSlice.examples.map((example) => (
                  <figure key={example.id}>
                    <pre>{example.prompt}</pre>
                    <figcaption>
                      right answer {example.gold} · model {example.prediction} · {example.split}
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
        </section>
      </div>

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
