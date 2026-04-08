const API_BASE_URL = "http://127.0.0.1:8000";

async function parseError(response) {
  let fallbackMessage = `Request failed with status ${response.status}.`;

  try {
    const data = await response.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }
  } catch (error) {
    return fallbackMessage;
  }

  return fallbackMessage;
}

export async function sendChatMessage(payload) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  return response.json();
}
