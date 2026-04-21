import { QUICK_PROMPTS } from "../../constants/prompts";
import "./Sidebar.css";
function Sidebar({
  generateAudio,
  setGenerateAudio,
  generateImage,
  setGenerateImage,
  speechLanguage,
  setSpeechLanguage,
  handlePromptClick,
}) {
  return (
    <section className="sidebar">
      <div className="brand-card">
        <p className="brand-kicker">Smart Librarian</p>
        <h1>Recommendation Studio</h1>
        <p className="brand-copy">
          A polished AI experience for book discovery, with voice input,
          hidden autoplay audio, and generated cover art previews.
        </p>
      </div>

      <div className="control-card">
        <div className="section-heading">
          <span className="section-dot" />
          Session Controls
        </div>

        <label className="switch-row">
          <div>
            <strong>Auto voice reply</strong>
            <p>Generate audio and play it automatically when the answer arrives.</p>
          </div>
          <input
            type="checkbox"
            checked={generateAudio}
            onChange={(event) => setGenerateAudio(event.target.checked)}
          />
        </label>

        <label className="switch-row">
          <div>
            <strong>Cover preview</strong>
            <p>Ask the backend to generate visual artwork for the selected book.</p>
          </div>
          <input
            type="checkbox"
            checked={generateImage}
            onChange={(event) => setGenerateImage(event.target.checked)}
          />
        </label>

        <div className="language-panel">
          <label className="language-label" htmlFor="speech-language">
            Voice recognition language
          </label>
          <select
            id="speech-language"
            className="language-select"
            value={speechLanguage}
            onChange={(event) => setSpeechLanguage(event.target.value)}
          >
            <option value="ro-RO">Romanian</option>
            <option value="en-US">English</option>
            <option value="fr-FR">French</option>
            <option value="de-DE">German</option>
            <option value="es-ES">Spanish</option>
            <option value="it-IT">Italian</option>
          </select>
        </div>
      </div>

      <div className="prompt-card">
        <div className="section-heading">
          <span className="section-dot" />
          Prompt Ideas
        </div>

        <div className="prompt-list">
          {QUICK_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="prompt-chip"
              onClick={() => handlePromptClick(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Sidebar;