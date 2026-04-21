import { useEffect, useMemo, useRef, useState } from "react";
import { sendChatMessage } from "../services/api";
import { AUDIO_MIME, DEFAULT_SPEECH_LANGUAGE } from "../constants/config";
import { buildDataUrl } from "../utils/media";
import { createMessage } from "../utils/messageFactory";
import useSpeechRecognition from "./useSpeechRecognition";
import useAudioPlayer from "./useAudioPlayer";

function useSmartLibrarian() {
  const [message, setMessage] = useState("");
  const [generateAudio, setGenerateAudio] = useState(true);
  const [generateImage, setGenerateImage] = useState(true);
  const [speechLanguage, setSpeechLanguage] = useState(DEFAULT_SPEECH_LANGUAGE);
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

  const { listening, handleVoiceInput } = useSpeechRecognition({
    loading,
    speechLanguage,
    setError,
    setMessage,
    composerRef,
  });

  const { audioRef, handleReplayAudio, handleToggleAudio, isPlaying } = useAudioPlayer({
    latestAudioUrl,
    setError,
  });

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

  return {
    message,
    setMessage,
    generateAudio,
    setGenerateAudio,
    generateImage,
    setGenerateImage,
    speechLanguage,
    setSpeechLanguage,
    listening,
    loading,
    error,
    messages,
    composerRef,
    audioRef,
    messagesEndRef,
    latestAudioUrl,
    handleVoiceInput,
    handleSubmit,
    handlePromptClick,
    handleReplayAudio,
    handleToggleAudio,
    isPlaying,
  };
}

export default useSmartLibrarian;
