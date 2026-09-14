import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import type { FaqItem, RunSummary, Slice } from "./types";

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

const faq: FaqItem[] = [
  {
    question: "What should I click first?",
    answer: "Leave Negation trap selected and press the black button.",
  },
  {
    question: "Where did the errors go?",
    answer: "They concentrate on negation.",
  },
];

function jsonResponse(data: unknown): Promise<Response> {
  return Promise.resolve(
    new Response(JSON.stringify(data), {
      status: 200,
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
        return Promise.resolve(new Response("nope", { status: 404 }));
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the dashed step with a run picker", async () => {
    render(<App />);
    expect(screen.getByLabelText("dashed step")).toBeInTheDocument();
    expect(await screen.findByLabelText("pick a run")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Negation trap")).toBeInTheDocument();
  });

  it("has a black button that looks through the run", async () => {
    render(<App />);
    const button = await screen.findByRole("button", { name: "Look through this run" });
    expect(button).toHaveClass("black-button");
  });

  it("does not show the rust hero before search", async () => {
    render(<App />);
    await screen.findByRole("button", { name: "Look through this run" });
    expect(screen.queryByLabelText("rewrite hero")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("comparison row")).not.toBeInTheDocument();
  });

  it("shows a green screenshot hero, then a rust rewrite and comparison row", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(await screen.findByRole("button", { name: "Look through this run" }));
    expect(await screen.findByLabelText("screenshot hero")).toHaveClass("hero--screenshot");
    expect(await screen.findByLabelText("rewrite hero")).toHaveClass("hero--rewrite");
    expect(screen.getByLabelText("comparison row")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Where did the errors go?" })).toBeInTheDocument();
  });

  it("labels the comparison row screenshot / this slice / you’d have reported", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(await screen.findByRole("button", { name: "Look through this run" }));
    const row = await screen.findByLabelText("comparison row");
    expect(row).toHaveTextContent("screenshot");
    expect(row).toHaveTextContent("this slice");
    expect(row).toHaveTextContent("you’d have reported");
    expect(row).toHaveTextContent("87.8%");
    expect(row).toHaveTextContent("14.0%");
    expect(row).toHaveTextContent("96.0%");
  });

  it("shows the confirmed vs did not replicate badge legend", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(await screen.findByRole("button", { name: "Look through this run" }));
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
      screen.getByText("Leave Negation trap selected and press the black button."),
    ).toBeInTheDocument();
    const page = document.querySelector(".page") as HTMLElement;
    const children = [...page.children];
    expect(children.at(-1)).toHaveClass("faq");
  });
});
