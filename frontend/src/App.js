import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";
import { sendChatMessage } from "./services/api";

const AUDIO_MIME = "audio/mpeg";
const IMAGE_MIME = "image/png";
const DEFAULT_SPEECH_LANGUAGE = "ro-RO";

const QUICK_PROMPTS = [
  "I need a thrilling mystery story with twists and suspense.",
  "I want a romantic classic with emotional depth.",
  "Give me a philosophical science fiction book.",
  "I need an exciting sci-fi tale with dark tone ",
];

function formatTime(date = new Date()) {
  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function buildDataUrl(mime, base64) {
  if (!base64) return "";
  return `data:${mime};base64,${base64}`;
}

function createMessage({
  id,
  role,
  text,
  title = null,
  audioBase64 = null,
  imageBase64 = null,
}) {
  return {
    id,
    role,
    text,
    title,
    time: formatTime(),
    audioBase64,
    imageBase64,
  };
}

function App() {
  const [message, setMessage] = useState("");
  const [generateAudio, setGenerateAudio] = useState(true);
  const [generateImage, setGenerateImage] = useState(true);
  const [speechLanguage, setSpeechLanguage] = useState(DEFAULT_SPEECH_LANGUAGE);
  const [listening, setListening] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState([
    createMessage({
      id: "welcome",
      role: "assistant",
      text: "Welcome to Smart Librarian. Ask for a mood, theme, genre, or atmosphere, and I will find one strong match for you.",
      title: "Library Guide",
    }),
  ]);

  const composerRef = useRef(null);
  const audioRef = useRef(null);
  const recognitionRef = useRef(null);
  const messagesEndRef = useRef(null);

  const latestAssistantMessage = useMemo(() => {
    return [...messages].reverse().find((item) => item.role === "assistant") || null;
  }, [messages]);

  const latestAudioUrl = useMemo(() => {
    return buildDataUrl(AUDIO_MIME, latestAssistantMessage?.audioBase64);
  }, [latestAssistantMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, error]);

  useEffect(() => {
    if (!latestAudioUrl || !audioRef.current) {
      return;
    }

    const audio = audioRef.current;
    audio.pause();
    audio.currentTime = 0;
    audio.src = latestAudioUrl;

    audio.play().catch(() => {
      // Browser autoplay can be blocked until user interaction.
    });
  }, [latestAudioUrl]);

  useEffect(() => {
    return () => {
      try {
        recognitionRef.current?.stop();
      } catch {
        // ignore cleanup errors
      }
    };
  }, []);

  const handleVoiceInput = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setError("Voice input is not supported in this browser.");
      return;
    }

    if (loading || listening) {
      return;
    }

    setError("");

    try {
      recognitionRef.current?.stop();
    } catch {
      // ignore stop issues from old instances
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    recognition.lang =
      speechLanguage || window.navigator.language || DEFAULT_SPEECH_LANGUAGE;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setListening(true);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognition.onerror = () => {
      setListening(false);
      setError("Voice recognition failed. Try again.");
    };

    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript?.trim() || "";

      if (!transcript) {
        return;
      }

      setMessage((current) => (current ? `${current} ${transcript}` : transcript));
      composerRef.current?.focus();
    };

    recognition.start();
  };

  const submitMessage = async (rawText) => {
    const trimmedMessage = rawText.trim();

    if (!trimmedMessage) {
      setError("Write a message first.");
      return;
    }

    setError("");
    setLoading(true);

    const userEntry = createMessage({
      id: `user-${Date.now()}`,
      role: "user",
      text: trimmedMessage,
    });

    setMessages((current) => [...current, userEntry]);
    setMessage("");

    try {
      const response = await sendChatMessage({
        message: trimmedMessage,
        generate_audio: generateAudio,
        generate_image: generateImage,
      });

      const assistantEntry = createMessage({
        id: `assistant-${Date.now()}`,
        role: "assistant",
        text: response.response,
        title: response.title,
        audioBase64: response.audio_base64,
        imageBase64: response.image_base64,
      });

      setMessages((current) => [...current, assistantEntry]);
    } catch (err) {
      setError(err?.message || "Request failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    await submitMessage(message);
  };

  const handlePromptClick = (prompt) => {
    setMessage(prompt);
    setError("");
    composerRef.current?.focus();
  };

  const handleReplayAudio = () => {
    if (!audioRef.current || !latestAudioUrl) {
      return;
    }

    audioRef.current.pause();
    audioRef.current.currentTime = 0;
    audioRef.current.play().catch(() => {
      setError("Audio playback could not start.");
    });
  };

  return (
    <div className="app-shell">
      <div className="backdrop-grid" />
      <div className="glow glow-one" />
      <div className="glow glow-two" />

      <main className="workspace">
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

        <section className="chat-shell">
          <header className="chat-header">
            <div>
              <p className="chat-kicker">Live Conversation</p>
              <h2>Book concierge</h2>
            </div>

            <div className="status-pill">
              <span
                className={`status-dot${
                  loading ? " loading" : listening ? " listening" : ""
                }`}
              />
              {loading ? "Thinking" : listening ? "Listening" : "Ready"}
            </div>
          </header>

          <div className="messages">
            {messages.map((entry) => {
              const imageUrl = buildDataUrl(IMAGE_MIME, entry.imageBase64);

              return (
                <article
                  key={entry.id}
                  className={`message-card ${
                    entry.role === "user" ? "user-message" : "assistant-message"
                  }`}
                >
                  <div className="message-meta">
                    <span>{entry.role === "user" ? "You" : "Assistant"}</span>
                    <span>{entry.time}</span>
                  </div>

                  {entry.title ? <div className="title-chip">{entry.title}</div> : null}

                  <p className="message-text">{entry.text}</p>

                  {imageUrl ? (
                    <img
                      className="generated-image"
                      src={imageUrl}
                      alt={entry.title || "Generated book cover"}
                    />
                  ) : null}
                </article>
              );
            })}

            {error ? <div className="error-box">{error}</div> : null}
            <div ref={messagesEndRef} />
          </div>

          <footer className="composer-shell">
            <form className="composer" onSubmit={handleSubmit}>
              <textarea
                ref={composerRef}
                className="message-input"
                placeholder="Describe the kind of book you want, its mood, themes, or emotional tone."
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                rows={1}
                disabled={loading}
              />

              <div className="composer-actions">
                <button
                  className="voice-button"
                  type="button"
                  onClick={handleVoiceInput}
                  disabled={loading || listening}
                >
                  {listening ? "Listening..." : "Speak"}
                </button>

                {latestAudioUrl ? (
                  <button
                    className="voice-button secondary"
                    type="button"
                    onClick={handleReplayAudio}
                    disabled={loading}
                  >
                    Replay voice
                  </button>
                ) : null}

                <button className="send-button" type="submit" disabled={loading}>
                  {loading ? "Sending..." : "Send message"}
                </button>
              </div>
            </form>

            <audio ref={audioRef} preload="auto" style={{ display: "none" }}>
              Your browser does not support audio playback.
            </audio>
          </footer>
        </section>
      </main>
    </div>
  );
}

export default App;