import { IMAGE_MIME } from "../../constants/config";
import { buildDataUrl } from "../../utils/media";
import "./MessageCard.css";

function MessageCard({ entry }) {
  const imageUrl = buildDataUrl(IMAGE_MIME, entry.imageBase64);

  return (
    <article
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

     {entry.id === "welcome" && (
      <audio className="welcome-audio" controls>
        <source src="/audio/media.mpeg" type="audio/mpeg" />
        Your browser does not support the audio element.
      </audio>
    )}

      {imageUrl ? (
        <img
          className="generated-image"
          src={imageUrl}
          alt={entry.title || "Generated book cover"}
        />
      ) : null}
    </article>
  );
}

export default MessageCard;