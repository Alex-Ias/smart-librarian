import MessageCard from "../MessageCard/MessageCard";
import "./MessageList.css";

function MessageList({ messages, error, messagesEndRef }) {
  return (
    <div className="messages">
      {messages.map((entry) => (
        <MessageCard key={entry.id} entry={entry} />
      ))}

      {error ? <div className="error-box">{error}</div> : null}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default MessageList;