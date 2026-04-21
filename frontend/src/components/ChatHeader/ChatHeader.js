import "./ChatHeader.css";
function ChatHeader({ loading, listening }) {
  return (
    <header className="chat-header">
      <div>
        <p className="chat-kicker">Live Conversation</p>
        <h2>Book Assistant</h2>
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
  );
}

export default ChatHeader;