/**
 * CropGuard AI - Speech Synthesis (Voice Read-Aloud Engine)
 * Reads out farmer recommendations in the chosen regional language.
 */

class VoiceAssistant {
  constructor() {
    this.synth = window.speechSynthesis;
    this.isSpeaking = false;
    this.currentUtterance = null;
  }

  getLangCode(lang) {
    const map = {
      en: "en-US",
      hi: "hi-IN",
      mr: "mr-IN",
      es: "es-ES",
      te: "te-IN"
    };
    return map[lang] || "en-US";
  }

  speak(text, lang = "en", onStart = null, onEnd = null) {
    if (!this.synth) {
      console.warn("[Voice] Web Speech API not supported on this device.");
      return;
    }

    if (this.isSpeaking) {
      this.stop();
      if (onEnd) onEnd();
      return;
    }

    this.stop();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = this.getLangCode(lang);
    utterance.rate = 0.95; // Clear slightly slower pace for rural farmers
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      this.isSpeaking = true;
      if (onStart) onStart();
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      if (onEnd) onEnd();
    };

    utterance.onerror = (err) => {
      console.error("[Voice] Speech synthesis error:", err);
      this.isSpeaking = false;
      if (onEnd) onEnd();
    };

    this.currentUtterance = utterance;
    this.synth.speak(utterance);
  }

  stop() {
    if (this.synth) {
      this.synth.cancel();
    }
    this.isSpeaking = false;
  }
}

const voiceAssistant = new VoiceAssistant();
