const { useEffect, useMemo, useState } = React;

const PREFLIGHT_QUESTIONS = [
  "What is the mission objective?",
  "Who is the target audience?",
  "What style direction is mandatory?",
  "Which business KPI is primary?",
  "What SEO entities must be emphasized?",
  "What are accessibility non-negotiables?",
  "What performance budget must be held?",
  "Which components are in scope?",
  "What legal/compliance rules apply?",
  "What is the definition of done?",
];

function App() {
  const [state, setState] = useState(null);
  const [showGate, setShowGate] = useState(!localStorage.getItem("sovereign_preflight_done"));
  const [answers, setAnswers] = useState(() => {
    const next = {};
    PREFLIGHT_QUESTIONS.forEach((_, i) => {
      next[i] = "";
    });
    return next;
  });

  useEffect(() => {
    const stateUrl = window.__SOVEREIGN_STATE_URL__ || "/public/state.json";
    const load = async () => {
      const response = await fetch(stateUrl, { cache: "no-store" });
      const payload = await response.json();
      setState(payload);
    };
    load();
    const id = setInterval(load, 3000);
    return () => clearInterval(id);
  }, []);

  const gateComplete = useMemo(
    () => Object.values(answers).every((v) => v.trim().length > 0),
    [answers],
  );

  const closeGate = () => {
    if (!gateComplete) return;
    localStorage.setItem("sovereign_preflight_done", "true");
    setShowGate(false);
  };

  const runSafetyStop = async () => {
    const command = (state && state.safety && state.safety.stopCommand) || "bin/SOVEREIGN_STOP.bat";
    try {
      await navigator.clipboard.writeText(command);
    } catch (_error) {
      window.alert(`Clipboard unavailable. Run manually:\n${command}`);
      return;
    }
    window.alert(
      `Manual stop copied to clipboard:\n${command}\n\nRun this locally in a terminal.`,
    );
  };

  const logs = (state && state.dialectic && state.dialectic.arguments) || [];

  return React.createElement(
    "div",
    { className: "shell" },
    showGate
      ? React.createElement(PreflightGate, {
          answers,
          setAnswers,
          gateComplete,
          closeGate,
        })
      : null,
    React.createElement("h1", null, "Sovereign Command Center"),
    React.createElement(
      "div",
      { className: "panel" },
      React.createElement("h2", null, "System Status"),
      React.createElement("p", null, `Status: ${(state && state.status) || "loading"}`),
      React.createElement(
        "p",
        null,
        "All model API calls stay in local Python orchestrator; dashboard reads sanitized state only.",
      ),
      React.createElement("button", { className: "danger", onClick: runSafetyStop }, "Kill Switch (Manual)"),
    ),
    React.createElement(
      "div",
      { className: "panel" },
      React.createElement("h2", null, "Dialectic Loop Argument Viewer"),
      React.createElement(
        "div",
        { className: "log-list" },
        logs.length
          ? logs.map((entry, idx) =>
              React.createElement(
                "div",
                { className: "log-item", key: `${idx}-${entry.round || 0}` },
                React.createElement("strong", null, `Round ${entry.round || "-"}`),
                React.createElement("p", null, `Claude: ${entry.claude_proposal || ""}`),
                React.createElement("p", null, `Gemini: ${entry.gemini_critique || ""}`),
                React.createElement("p", null, `DeepSeek: ${entry.deepseek_verdict || ""}`),
              ),
            )
          : React.createElement("p", null, "No argument logs yet."),
      ),
    ),
    React.createElement(
      "div",
      { className: "panel" },
      React.createElement("h2", null, "Operator Prompt Panel"),
      React.createElement(
        "p",
        null,
        "Use local orchestrator CLI for execution. Current stop command: ",
        React.createElement(
          "code",
          null,
          (state && state.safety && state.safety.stopCommand) || "bin/SOVEREIGN_STOP.bat",
        ),
      ),
    ),
  );
}

function PreflightGate({ answers, setAnswers, gateComplete, closeGate }) {
  return React.createElement(
    "div",
    { className: "modal-backdrop" },
    React.createElement(
      "div",
      { className: "modal" },
      React.createElement("h2", null, "10-Question Pre-flight Gate"),
      React.createElement("p", null, "Complete all answers before orchestrator work can proceed."),
      React.createElement(
        "div",
        { className: "qa" },
        ...PREFLIGHT_QUESTIONS.map((q, index) =>
          React.createElement(
            "label",
            { key: index },
            React.createElement("span", null, `${index + 1}. ${q}`),
            React.createElement("input", {
              value: answers[index],
              onChange: (event) => setAnswers({ ...answers, [index]: event.target.value }),
            }),
          ),
        ),
      ),
      React.createElement(
        "div",
        { style: { marginTop: "14px" } },
        React.createElement(
          "button",
          { className: "primary", disabled: !gateComplete, onClick: closeGate },
          "Unlock Dashboard",
        ),
      ),
    ),
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(React.createElement(App));
