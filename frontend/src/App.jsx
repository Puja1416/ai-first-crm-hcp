import { useEffect, useMemo, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  addUserMessage,
  fetchHcps,
  fetchInteractions,
  saveInteraction,
  sendAgentMessage,
} from "./interactionSlice";

const initialForm = {
  hcp_id: "",
  interaction_type: "Meeting",
  interaction_date: new Date().toISOString().slice(0, 10),
  interaction_time: new Date().toTimeString().slice(0, 5),
  attendees: "",
  topics_discussed: "",
  materials_shared: "",
  samples_distributed: "",
  sentiment: "Neutral",
  outcomes: "",
  follow_up_actions: "",
};

function App() {
  const dispatch = useDispatch();
  const { hcps, items, messages, loading, error } = useSelector(
    (state) => state.interactions
  );
  const [form, setForm] = useState(initialForm);
  const [chat, setChat] = useState("");

  useEffect(() => {
    dispatch(fetchHcps());
    dispatch(fetchInteractions());
  }, [dispatch]);

  const selectedHcp = useMemo(
    () => hcps.find((hcp) => String(hcp.id) === String(form.hcp_id)),
    [hcps, form.hcp_id]
  );

  const update = (event) => {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const submitForm = async (event) => {
    event.preventDefault();
    const payload = {
      ...form,
      hcp_id: Number(form.hcp_id),
      interaction_time:
        form.interaction_time.length === 5
          ? `${form.interaction_time}:00`
          : form.interaction_time,
    };
    const result = await dispatch(saveInteraction(payload));
    if (!result.error) {
      setForm((current) => ({
        ...initialForm,
        hcp_id: current.hcp_id,
      }));
    }
  };

  const sendChat = async (event) => {
    event.preventDefault();
    const text = chat.trim();
    if (!text) return;
    dispatch(addUserMessage(text));
    setChat("");
    await dispatch(sendAgentMessage(text));
    dispatch(fetchInteractions());
  };

  return (
    <main className="page-shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">AI-FIRST CRM</span>
          <h1>Log HCP Interaction</h1>
          <p>Capture field activity through a structured form or AI conversation.</p>
        </div>
        <div className="status-pill">
          <span className="status-dot" />
          System ready
        </div>
      </header>

      <section className="workspace">
        <form className="panel form-panel" onSubmit={submitForm}>
          <div className="panel-heading">
            <div>
              <h2>Interaction details</h2>
              <p>Complete the key facts from your HCP engagement.</p>
            </div>
            <span className="step-chip">Structured form</span>
          </div>

          <div className="form-grid">
            <label className="field field-wide">
              <span>HCP name</span>
              <select name="hcp_id" value={form.hcp_id} onChange={update} required>
                <option value="">Select an HCP</option>
                {hcps.map((hcp) => (
                  <option key={hcp.id} value={hcp.id}>
                    {hcp.name} — {hcp.specialty}
                  </option>
                ))}
              </select>
              {selectedHcp && (
                <small>
                  {selectedHcp.organization}, {selectedHcp.city}
                </small>
              )}
            </label>

            <label className="field">
              <span>Interaction type</span>
              <select
                name="interaction_type"
                value={form.interaction_type}
                onChange={update}
              >
                <option>Meeting</option>
                <option>Phone call</option>
                <option>Virtual meeting</option>
                <option>Conference</option>
                <option>Email</option>
              </select>
            </label>

            <label className="field">
              <span>Date</span>
              <input
                type="date"
                name="interaction_date"
                value={form.interaction_date}
                onChange={update}
                required
              />
            </label>

            <label className="field">
              <span>Time</span>
              <input
                type="time"
                name="interaction_time"
                value={form.interaction_time}
                onChange={update}
                required
              />
            </label>

            <label className="field field-wide">
              <span>Attendees</span>
              <input
                name="attendees"
                value={form.attendees}
                onChange={update}
                placeholder="Names or roles of attendees"
              />
            </label>

            <label className="field field-wide">
              <span>Topics discussed</span>
              <textarea
                name="topics_discussed"
                value={form.topics_discussed}
                onChange={update}
                placeholder="Products, patient profile, clinical questions, objections…"
                required
              />
            </label>

            <label className="field">
              <span>Materials shared</span>
              <input
                name="materials_shared"
                value={form.materials_shared}
                onChange={update}
                placeholder="Brochure, study, visual aid"
              />
            </label>

            <label className="field">
              <span>Samples distributed</span>
              <input
                name="samples_distributed"
                value={form.samples_distributed}
                onChange={update}
                placeholder="Product and quantity"
              />
            </label>

            <fieldset className="field field-wide sentiment-field">
              <legend>Observed HCP sentiment</legend>
              <div className="sentiment-options">
                {["Positive", "Neutral", "Negative"].map((value) => (
                  <label key={value}>
                    <input
                      type="radio"
                      name="sentiment"
                      value={value}
                      checked={form.sentiment === value}
                      onChange={update}
                    />
                    <span>{value}</span>
                  </label>
                ))}
              </div>
            </fieldset>

            <label className="field field-wide">
              <span>Outcomes</span>
              <textarea
                name="outcomes"
                value={form.outcomes}
                onChange={update}
                placeholder="Key decisions or commitments"
              />
            </label>

            <label className="field field-wide">
              <span>Follow-up actions</span>
              <textarea
                name="follow_up_actions"
                value={form.follow_up_actions}
                onChange={update}
                placeholder="Next meeting, materials, medical information request…"
              />
            </label>
          </div>

          {error && <div className="error-box">{error}</div>}

          <div className="form-actions">
            <button type="button" className="secondary-button" onClick={() => setForm(initialForm)}>
              Reset
            </button>
            <button className="primary-button" disabled={loading}>
              {loading ? "Saving…" : "Save interaction"}
            </button>
          </div>
        </form>

        <aside className="panel assistant-panel">
          <div className="assistant-header">
            <div className="assistant-icon">AI</div>
            <div>
              <h2>AI Assistant</h2>
              <p>Powered by LangGraph + Groq</p>
            </div>
          </div>

          <div className="messages">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.role}`}>
                <div>{message.text}</div>
                {message.data && (
                  <pre>{JSON.stringify(message.data, null, 2)}</pre>
                )}
              </div>
            ))}
            {loading && <div className="message assistant">Working…</div>}
          </div>

          <div className="suggestions">
            <button onClick={() => setChat("Search HCPs in Pune")}>Search HCP</button>
            <button onClick={() => setChat("Summarize: Dr. Sharma discussed adherence concerns and requested a follow-up study.")}>
              Summarize
            </button>
            <button onClick={() => setChat("Recommend follow-up for a positive discussion about adherence concerns")}>
              Recommend
            </button>
          </div>

          <form className="chat-box" onSubmit={sendChat}>
            <textarea
              value={chat}
              onChange={(event) => setChat(event.target.value)}
              placeholder="Ask the CRM agent to use one of its five tools…"
            />
            <button disabled={loading || !chat.trim()}>Send</button>
          </form>
        </aside>
      </section>

      <section className="panel recent-panel">
        <div className="panel-heading">
          <div>
            <h2>Recent interactions</h2>
            <p>Latest records saved in MySQL.</p>
          </div>
          <span className="step-chip">{items.length} records</span>
        </div>

        <div className="interaction-list">
          {items.length === 0 ? (
            <p className="empty-state">No interactions logged yet.</p>
          ) : (
            items.slice(0, 6).map((item) => (
              <article key={item.id} className="interaction-card">
                <div>
                  <strong>{item.hcp_name}</strong>
                  <span>{item.interaction_type}</span>
                </div>
                <p>{item.ai_summary || item.topics_discussed}</p>
                <small>
                  {item.interaction_date} · {item.sentiment}
                </small>
              </article>
            ))
          )}
        </div>
      </section>
    </main>
  );
}

export default App;
