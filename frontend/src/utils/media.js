export function buildDataUrl(mime, base64) {
  if (!base64) return "";
  return `data:${mime};base64,${base64}`;
}