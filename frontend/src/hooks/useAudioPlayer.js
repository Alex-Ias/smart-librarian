import { useEffect, useRef, useState } from "react";

function useAudioPlayer({ latestAudioUrl, setError }) {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (!latestAudioUrl || !audioRef.current) {
      return;
    }

    const audio = audioRef.current;
    audio.pause();
    audio.currentTime = 0;
    audio.src = latestAudioUrl;

    audio
      .play()
      .then(() => {
        setIsPlaying(true);
      })
      .catch(() => {
        // Browser autoplay can be blocked until user interaction.
      });
  }, [latestAudioUrl]);

  const handleReplayAudio = () => {
    if (!audioRef.current || !latestAudioUrl) {
      return;
    }

    audioRef.current.pause();
    audioRef.current.currentTime = 0;
    audioRef.current
      .play()
      .then(() => {
        setIsPlaying(true);
      })
      .catch(() => {
        setError("Audio playback could not start.");
      });
  };

  const handleToggleAudio = () => {
    if (!audioRef.current) {
      return;
    }

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current
        .play()
        .then(() => {
          setIsPlaying(true);
        })
        .catch(() => {
          setError("Audio playback could not start.");
        });
    }
  };

  return {
    audioRef,
    handleReplayAudio,
    handleToggleAudio,
    isPlaying,
  };
}

export default useAudioPlayer;