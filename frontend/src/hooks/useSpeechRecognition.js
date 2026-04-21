import { useEffect, useRef, useState } from "react";
import { DEFAULT_SPEECH_LANGUAGE } from "../constants/config";

function useSpeechRecognition({
  loading,
  speechLanguage,
  setError,
  setMessage,
  composerRef,
}) {
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

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

  return {
    listening,
    handleVoiceInput,
  };
}

export default useSpeechRecognition;