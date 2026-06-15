import { useEffect, useMemo, useState } from "react";
import { fetchIssues, type Issue } from "../lib/github";
import { ISSUES_URL } from "../lib/site";

const DIFFICULTY_LABEL: Record<string, string> = {
  "good-first": "good first issue",
  intermediate: "intermediate",
  research: "research",
  unlabeled: "untriaged",
};

const THRUSTS = ["foundations", "mechanisms", "robustness", "theory"] as const;

function Badge({ children, tone = "slate" }: { children: React.ReactNode; tone?: string }) {
  const tones: Record<string, string> = {
    slate: "bg-stone-100 text-ink-soft dark:bg-stone-800",
    accent: "bg-accent-100 text-accent-800 dark:bg-accent-500/20 dark:text-accent-200",
    emerald: "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300",
    amber: "bg-amber-50 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300",
    rose: "bg-rose-50 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300",
  };
  return (
    <span className={`rounded px-2 py-0.5 font-sans text-xs font-medium ${tones[tone]}`}>{children}</span>
  );
}

export default function IssueBoard() {
  const [issues, setIssues] = useState<Issue[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [difficulty, setDifficulty] = useState("all");
  const [thrust, setThrust] = useState("all");
  const [track, setTrack] = useState("all");
  const [q, setQ] = useState("");

  useEffect(() => {
    const ctrl = new AbortController();
    fetchIssues(ctrl.signal)
      .then(setIssues)
      .catch((e) => {
        if (e.name !== "AbortError") setError(String(e.message ?? e));
      });
    return () => ctrl.abort();
  }, []);

  const filtered = useMemo(() => {
    if (!issues) return [];
    return issues.filter((it) => {
      if (difficulty !== "all" && it.facets.difficulty !== difficulty) return false;
      if (thrust !== "all" && it.facets.thrust !== thrust) return false;
      if (track !== "all" && it.facets.track !== track) return false;
      if (q && !it.title.toLowerCase().includes(q.toLowerCase())) return false;
      return true;
    });
  }, [issues, difficulty, thrust, track, q]);

  const goodFirstCount = issues?.filter((it) => it.facets.difficulty === "good-first").length ?? 0;

  if (error) {
    return (
      <div className="rounded-lg border border-amber-300 bg-amber-50 p-5 text-sm text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300">
        {error}{" "}
        <a className="font-medium text-accent-700 underline dark:text-accent-400" href={ISSUES_URL}>
          Open the issues on GitHub
        </a>
        .
      </div>
    );
  }
  if (!issues) {
    return <div className="animate-pulse font-sans text-ink-soft">Loading open issues from GitHub…</div>;
  }

  return (
    <div className="font-sans">
      <div className="mb-5 flex flex-wrap items-end gap-3 text-sm">
        <label>
          <span className="mb-1 block text-ink-soft">Difficulty</span>
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="rounded border border-stone-300 bg-surface dark:border-stone-600 px-2 py-1.5 text-ink"
          >
            <option value="all">All</option>
            <option value="good-first">Good first issue</option>
            <option value="intermediate">Intermediate</option>
            <option value="research">Research</option>
            <option value="unlabeled">Untriaged</option>
          </select>
        </label>
        <label>
          <span className="mb-1 block text-ink-soft">Thrust</span>
          <select
            value={thrust}
            onChange={(e) => setThrust(e.target.value)}
            className="rounded border border-stone-300 bg-surface dark:border-stone-600 px-2 py-1.5 capitalize text-ink"
          >
            <option value="all">All</option>
            {THRUSTS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span className="mb-1 block text-ink-soft">Track</span>
          <select
            value={track}
            onChange={(e) => setTrack(e.target.value)}
            className="rounded border border-stone-300 bg-surface dark:border-stone-600 px-2 py-1.5 text-ink"
          >
            <option value="all">All</option>
            <option value="A">A · probe infra</option>
            <option value="B">B · experiment</option>
          </select>
        </label>
        <label className="flex-1">
          <span className="mb-1 block text-ink-soft">Search</span>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Filter by title…"
            className="w-full rounded border border-stone-300 bg-surface dark:border-stone-600 px-3 py-1.5 text-ink placeholder:text-stone-400"
          />
        </label>
      </div>

      <p className="mb-4 text-sm text-ink-soft">
        Showing <span className="text-ink">{filtered.length}</span> of {issues.length} open issues
        {goodFirstCount > 0 && (
          <>
            {" "}· <span className="text-accent-700">{goodFirstCount} good first issue{goodFirstCount === 1 ? "" : "s"}</span>
          </>
        )}
      </p>

      <ul className="space-y-3">
        {filtered.map((it) => (
          <li key={it.number} className="rounded-lg border border-rule bg-surface p-4 transition hover:border-stone-400">
            <div className="flex items-start justify-between gap-4">
              <div>
                <a href={it.url} className="font-serif text-lg font-semibold text-ink hover:text-accent-700">
                  <span className="text-stone-400">#{it.number}</span> {it.title}
                </a>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {it.facets.difficulty === "good-first" && <Badge tone="accent">good first issue</Badge>}
                  {it.facets.type && <Badge tone="emerald">{it.facets.type}</Badge>}
                  {it.facets.track && <Badge>track {it.facets.track}</Badge>}
                  {it.facets.thrust && <Badge tone="amber">{it.facets.thrust}</Badge>}
                  {it.facets.difficulty !== "good-first" && (
                    <Badge>{DIFFICULTY_LABEL[it.facets.difficulty]}</Badge>
                  )}
                  {it.isDraft && <Badge tone="rose">draft</Badge>}
                </div>
              </div>
              <a
                href={it.url}
                className="shrink-0 rounded-sm bg-ink px-3 py-1.5 text-sm font-semibold uppercase tracking-wide text-paper transition hover:bg-accent-800 dark:hover:bg-accent-300"
              >
                Claim →
              </a>
            </div>
          </li>
        ))}
      </ul>
      {filtered.length === 0 && (
        <p className="rounded-lg border border-rule bg-surface p-5 text-sm text-ink-soft">
          No issues match these filters. Try widening them, or{" "}
          <a className="font-medium text-accent-700 underline" href={ISSUES_URL}>
            browse all issues
          </a>
          .
        </p>
      )}
    </div>
  );
}
