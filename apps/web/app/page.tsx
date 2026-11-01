export default function HomePage() {
  return (
    <main style={{ padding: "48px 24px", maxWidth: 720, margin: "0 auto" }}>
      <p style={{ color: "#C8A84B", fontWeight: 700, letterSpacing: "0.08em" }}>
        BRIDGIT AI
      </p>
      <h1 style={{ margin: "12px 0 8px" }}>Separate app. Engine first.</h1>
      <p style={{ color: "#555", lineHeight: 1.6 }}>
        This UI is a placeholder. Week 1 work is the FastAPI engine: upload a
        bank file, categorise lines, flag real questions, write the Excel.
        Track progress in docs/ai-accounting/17-build-plan.md.
      </p>
    </main>
  );
}
