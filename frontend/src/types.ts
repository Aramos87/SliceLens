export type RunSummary = {
  id: string;
  title: string;
  blurb: string;
  n: number;
  correct: number;
  screenshot_accuracy: number;
  discover_n: number;
  confirm_n: number;
};

export type Slice = {
  predicate: string;
  label: string;
  interpretation: string;
  screenshot_accuracy: number;
  slice_accuracy: number;
  slice_n: number;
  slice_share: number;
  youd_have_reported: number;
  discover: { n: number; correct: number; accuracy: number };
  confirm: { n: number; correct: number; accuracy: number };
  status: "confirmed" | "did not replicate";
  member_ids: string[];
  examples: {
    id: string;
    prompt: string;
    gold: string;
    prediction: string;
    split: string;
  }[];
  rewrite: string;
};

export type SearchResponse = {
  run: RunSummary;
  slices: Slice[];
};

export type ResidualResponse = {
  run: RunSummary;
  slices: Slice[];
  empty: boolean;
  message: string | null;
};

export type FaqItem = {
  question: string;
  answer: string;
};

export type GuideTerm = {
  key: string;
  label: string;
  meaning: string;
};

export type GuideExample = {
  id: string;
  kind: string;
  prompt: string;
  gold: string;
  prediction: string;
  correct: boolean;
  split: string;
  why: string;
};

export type Guide = {
  one_line: string;
  success: string;
  expect: string;
  predicates: GuideTerm[];
  fields: GuideTerm[];
  examples: GuideExample[];
};

export type DemoPack = {
  id: string;
  title: string;
  blurb: string;
  items: unknown[];
};
