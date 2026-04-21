import "./Composer.css";

function Composer({
  composerRef,
  handleSubmit,
  message,
  setMessage,
  loading,
  listening,
  handleVoiceInput,
  latestAudioUrl,
  handleReplayAudio,
  audioRef,
  handleToggleAudio,
  isPlaying,
}) {
  return (
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
            <>
              <button
                className="voice-button secondary"
                type="button"
                onClick={handleReplayAudio}
                disabled={loading}
              >
                Replay voice
              </button>

              <button
                className="voice-button secondary"
                type="button"
                onClick={handleToggleAudio}
                disabled={loading}
              >
                {isPlaying ? "Pause" : "Resume"}
              </button>
            </>
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
  );
}

export default Composer;