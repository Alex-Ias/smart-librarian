import Sidebar from "../components/Sidebar/Sidebar";
import ChatHeader from "../components/ChatHeader/ChatHeader";
import MessageList from "../components/MessageList/MessageList";
import Composer from "../components/Composer/Composer";
import useSmartLibrarian from "../hooks/useSmartLibrarian";

function SmartLibrarianPage() {
  const {
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
  } = useSmartLibrarian();

  return (
    <div className="app-shell">
      <div className="backdrop-grid" />
      <div className="glow glow-one" />
      <div className="glow glow-two" />

      <main className="workspace">
        <Sidebar
          generateAudio={generateAudio}
          setGenerateAudio={setGenerateAudio}
          generateImage={generateImage}
          setGenerateImage={setGenerateImage}
          speechLanguage={speechLanguage}
          setSpeechLanguage={setSpeechLanguage}
          handlePromptClick={handlePromptClick}
        />

        <section className="chat-shell">
          <ChatHeader loading={loading} listening={listening} />

          <MessageList
            messages={messages}
            error={error}
            messagesEndRef={messagesEndRef}
          />

          <Composer
            composerRef={composerRef}
            handleSubmit={handleSubmit}
            message={message}
            setMessage={setMessage}
            loading={loading}
            listening={listening}
            handleVoiceInput={handleVoiceInput}
            latestAudioUrl={latestAudioUrl}
            handleReplayAudio={handleReplayAudio}
            handleToggleAudio={handleToggleAudio}
            isPlaying={isPlaying}
            audioRef={audioRef}
          />
        </section>
      </main>
    </div>
  );
}

export default SmartLibrarianPage;