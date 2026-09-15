import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import type { DemoPack, FaqItem, Guide, RunSummary, Slice } from "./types";

const runs: RunSummary[] = [
  {
    id: "negation-trap",
    title: "Negation trap",
    blurb: "Yes/no reading.",
    n: 500,
    correct: 439,
    screenshot_accuracy: 0.878,
    discover_n: 300,
    confirm_n: 200,
  },
  {
    id: "units-dropped",
    title: "Units dropped",
    blurb: "Units.",
    n: 1000,
    correct: 843,
    screenshot_accuracy: 0.843,
    discover_n: 600,
    confirm_n: 400,
  },
];

const slice: Slice = {
  predicate: "has_negation",
  label: "has negation",
  interpretation: "The prompt contains a negation.",
  screenshot_accuracy: 0.878,
  slice_accuracy: 0.14,
  slice_n: 50,
  slice_share: 0.1,
  youd_have_reported: 0.96,
  discover: { n: 30, correct: 4, accuracy: 0.133 },
  confirm: { n: 20, correct: 3, accuracy: 0.15 },
  status: "confirmed",
  member_ids: ["neg-0001"],
  examples: [
    {
      id: "neg-0001",
      prompt: "The committee did not approve the bill. Did the committee approve the bill?",
      gold: "no",
      prediction: "yes",
      split: "discover",
    },
  ],
  rewrite:
    "Negation trap screenshots at 87.8%. On “has negation” the run is 14.0%. You’d have reported 96.0%.",
};

const guide: Guide = {
  one_line: "Yes/no questions. Some contain not.",
  success: "The model should answer no when the fact is negated.",
  expect: "A high score can hide negated questions.",
  predicates: [{ key: "has_negation", label: "has negation", meaning: "Contains not / never / no." }],
  fields: [{ key: "prompt", label: "prompt", meaning: "The question the model was asked." }],
  examples: [
    {
      id: "neg-easy",
      kind: "easy pass",
      prompt: "The committee approved the bill. Did the committee approve the bill?",
      gold: "yes",
      prediction: "yes",
      correct: true,
      split: "discover",
      why: "No trick in the question.",
    },
  ],
};

const pack: DemoPack = {
  id: "negation-trap",
  title: "Negation trap",
  blurb: "Yes/no",
  items: [{ id: "neg-0001", prompt: "x", gold: "no", prediction: "yes", split: "discover" }],
};

const faq: FaqItem[] = [
  {
    question: "What should I click first?",
    answer: "Open Negation trap, read the left column, press Find the hidden failure.",
  },
  {
    question: "Where did the errors go?",
    answer: "They concentrate on negation.",
  },
];

function jsonResponse(data: unknown, status = 200): Promise<Response> {
  return Promise.resolve(
    new Response(JSON.stringify(data), {
      status,
      headers: { "Content-Type": "application/json" },
    }),
  );
}

describe("Slice Lens", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo) => {
        const url = String(input);
        if (url === "/api/runs") return jsonResponse({ runs });
        if (url === "/api/faq") return jsonResponse({ items: faq });
        if (url === "/api/runs/negation-trap/examples") {
          return jsonResponse({ run: runs[0], guide });
        }
        if (url === "/api/runs/negation-trap/pack") return jsonResponse(pack);
        if (url === "/api/runs/negation-trap/search") {
          return new Promise((resolve) => {
            setTimeout(() => {
              resolve(
                new Response(JSON.stringify({ run: runs[0], slices: [slice] }), {
                  status: 200,
                  headers: { "Content-Type": "application/json" },
                }),
              );
            }, 40);
          });
        }
        if (url === "/api/runs/negation-trap/residual") {
          return jsonResponse({
            run: runs[0],
            slices: [],
            empty: true,
            message: "Nothing else is hiding",
          });
        }
        if (url === "/api/analyze") {
          return jsonResponse({ run: runs[0], slices: [slice] });
        }
        return Promise.resolve(new Response("nope", { status: 404 }));
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders demo tabs and two columns", async () => {
    render(<App />);
    expect(await screen.findByRole("tab", { name: "Negation trap" })).toHaveAttribute(
      "aria-selected",
      "true",
    );
    expect(screen.getByRole("tab", { name: "Units dropped" })).toBeInTheDocument();
    expect(screen.getByLabelText("this test")).toBeInTheDocument();
    expect(screen.getByLabelText("what we found")).toBeInTheDocument();
    expect(screen.getByLabelText("evaluation types")).toBeInTheDocument();
  });

  it("has a black button that finds the hidden failure", async () => {
    render(<App />);
    const button = await screen.findByRole("button", { name: "Find the hidden failure" });
    expect(button).toHaveClass("black-button");
    expect(screen.getByLabelText("dashed step")).toBeInTheDocument();
  });

  it("shows an empty results column before search", async () => {
    render(<App />);
    await screen.findByRole("button", { name: "Find the hidden failure" });
    expect(screen.getByLabelText("results empty")).toHaveTextContent("Press Find the hidden failure.");
    expect(screen.queryByLabelText("rewrite hero")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("comparison row")).not.toBeInTheDocument();
  });

  it("shows a green screenshot hero, then a rust rewrite and comparison row", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(await screen.findByRole("button", { name: "Find the hidden failure" }));
    expect(await screen.findByLabelText("screenshot hero")).toHaveClass("hero--screenshot");
    expect(await screen.findByLabelText("rewrite hero")).toHaveClass("hero--rewrite");
    expect(screen.getByLabelText("comparison row")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Where did the errors go?" })).toBeInTheDocument();
  });

  it("labels the comparison row screenshot / this slice / you’d have reported", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(await screen.findByRole("button", { name: "Find the hidden failure" }));
    const row = await screen.findByLabelText("comparison row");
    expect(row).toHaveTextContent("screenshot");
    expect(row).toHaveTextContent("this slice");
    expect(row).toHaveTextContent("you’d have reported");
    expect(row).toHaveTextContent("All questions");
    expect(row).toHaveTextContent("Only the weak group");
    expect(row).toHaveTextContent("If that group were gone");
    expect(row).toHaveTextContent("87.8%");
    expect(row).toHaveTextContent("14.0%");
    expect(row).toHaveTextContent("96.0%");
  });

  it("shows the confirmed vs did not replicate badge legend", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(await screen.findByRole("button", { name: "Find the hidden failure" }));
    const legend = await screen.findByLabelText("badge legend");
    expect(legend).toHaveTextContent("confirmed");
    expect(legend).toHaveTextContent("did not replicate");
  });

  it("puts the FAQ accordion at the bottom with What should I click first?", async () => {
    const user = userEvent.setup();
    render(<App />);
    const question = await screen.findByRole("button", { name: "What should I click first?" });
    expect(question.closest("section")).toHaveAttribute("aria-label", "FAQ");
    await user.click(question);
    expect(
      screen.getByText("Open Negation trap, read the left column, press Find the hidden failure."),
    ).toBeInTheDocument();
    const page = document.querySelector(".page") as HTMLElement;
    expect([...page.children].at(-1)).toHaveClass("faq");
  });

  it("shows an editor error for invalid JSON and fills results for a valid edit", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(await screen.findByText("Edit this run (JSON)"));
    const box = await screen.findByLabelText("run JSON");
    fireEvent.change(box, { target: { value: "{not json" } });
    await user.click(screen.getByRole("button", { name: "Run my edit" }));
    expect(screen.getByText("That is not valid JSON. Check the commas and quotes.")).toBeInTheDocument();

    fireEvent.change(box, {
      target: { value: '{"title":"Edited","items":[{"prompt":"x","gold":"a","prediction":"b"}]}' },
    });
    await user.click(screen.getByRole("button", { name: "Run my edit" }));
    expect(await screen.findByLabelText("rewrite hero")).toBeInTheDocument();
    expect(screen.getByLabelText("comparison row")).toHaveTextContent("87.8%");
  });
});
