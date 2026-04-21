import { formatTime } from "./formatters";

export function createMessage({
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
