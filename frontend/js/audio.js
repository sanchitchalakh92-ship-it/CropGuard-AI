/*
 * CropGuard AI - Multilingual Voice Assistant
 * Languages: English, Hindi, Marathi
 *
 * Flow:
 * Farmer speaks
 *      ↓
 * Speech recognition
 *      ↓
 * Chat input
 *      ↓
 * Existing Crop Doctor
 *      ↓
 * Detailed answer
 *      ↓
 * Voice response
 */

(function () {
    "use strict";

    const voiceButton =
        document.getElementById("voiceAssistantBtn");

    const stopButton =
        document.getElementById("voiceAssistantStopBtn");

    const statusBox =
        document.getElementById("voiceAssistantStatus");

    const chatInput =
        document.getElementById("chatInput");

    const chatSendButton =
        document.getElementById("chatSendBtn");

    const chatMessages =
        document.getElementById("chatMessages");

    const languageSelect =
        document.getElementById("langSelect");


    // ---------------------------------------------------------
    // Check required elements
    // ---------------------------------------------------------

    if (
        !voiceButton ||
        !chatInput ||
        !chatMessages
    ) {
        console.warn(
            "CropGuard Voice Assistant: required elements not found."
        );
        return;
    }


    // ---------------------------------------------------------
    // Browser Speech Recognition
    // ---------------------------------------------------------

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    let recognition = null;
    let isListening = false;

    /*
     * This flag ensures that normal typed questions
     * are NOT automatically spoken.
     */
    window.cropGuardVoiceWaitingForAnswer = false;


    // ---------------------------------------------------------
    // Language configuration
    // ---------------------------------------------------------

    const LANGUAGE_CONFIG = {

        en: {
            recognition: "en-IN",
            speech: "en-IN",

            listening:
                "🎤 Listening... Speak your crop question.",

            heard:
                "📝 Heard: ",

            speaking:
                "🔊 CropGuard is speaking...",

            finished:
                "✅ Voice answer finished."
        },

        hi: {
            recognition: "hi-IN",
            speech: "hi-IN",

            listening:
                "🎤 सुन रहा हूँ... अपनी फसल से संबंधित प्रश्न पूछें।",

            heard:
                "📝 सुना गया: ",

            speaking:
                "🔊 CropGuard उत्तर दे रहा है...",

            finished:
                "✅ आवाज़ में उत्तर पूरा हुआ।"
        },

        mr: {
            recognition: "mr-IN",
            speech: "mr-IN",

            listening:
                "🎤 ऐकत आहे... आपल्या पिकाबद्दल प्रश्न विचारा.",

            heard:
                "📝 ऐकले: ",

            speaking:
                "🔊 CropGuard उत्तर देत आहे...",

            finished:
                "✅ आवाजातील उत्तर पूर्ण झाले."
        }
    };


    // ---------------------------------------------------------
    // Get selected language
    // ---------------------------------------------------------

    function getSelectedLanguage() {

        const selected =
            languageSelect
                ? String(
                    languageSelect.value || "en"
                ).toLowerCase()
                : "en";

        if (LANGUAGE_CONFIG[selected]) {
            return selected;
        }

        return "en";
    }


    // ---------------------------------------------------------
    // Status
    // ---------------------------------------------------------

    function setStatus(message) {

        if (statusBox) {
            statusBox.textContent = message;
        }
    }


    // ---------------------------------------------------------
    // Voice button text
    // ---------------------------------------------------------

    function setVoiceButton(message) {

        if (voiceButton) {
            voiceButton.textContent = message;
        }
    }


    // ---------------------------------------------------------
    // Stop speech
    // ---------------------------------------------------------

    function stopSpeaking() {

        if (
            "speechSynthesis" in window
        ) {
            window.speechSynthesis.cancel();
        }
    }


    // ---------------------------------------------------------
    // Speak Crop Doctor answer
    // ---------------------------------------------------------

    function speakAnswer(text) {

        if (
            !text ||
            !("speechSynthesis" in window)
        ) {
            return;
        }


        const language =
            getSelectedLanguage();

        const config =
            LANGUAGE_CONFIG[language];


        stopSpeaking();


        /*
         * Remove Markdown formatting before
         * sending the answer to speech synthesis.
         */

        const cleanText =
            String(text)
                .replace(/\*\*/g, "")
                .replace(/__/g, "")
                .replace(/#{1,6}\s*/g, "")
                .replace(/[*_`]/g, "")
                .replace(/\s+/g, " ")
                .trim();


        if (!cleanText) {
            return;
        }


        const utterance =
            new SpeechSynthesisUtterance(
                cleanText
            );


        utterance.lang =
            config.speech;

        utterance.rate =
            0.88;

        utterance.pitch =
            1.0;

        utterance.volume =
            1.0;


        utterance.onstart =
            function () {

                setStatus(
                    config.speaking
                );
            };


        utterance.onend =
            function () {

                setStatus(
                    config.finished
                );
            };


        utterance.onerror =
            function () {

                setStatus(
                    "⚠️ Voice playback could not be completed."
                );
            };


        window.speechSynthesis.speak(
            utterance
        );
    }


    // ---------------------------------------------------------
    // Extract Crop Doctor bot message
    // ---------------------------------------------------------

    function getBotText(element) {

        if (!element) {
            return "";
        }


        const bubble =
            element.querySelector(
                ".chat-bubble"
            );


        if (!bubble) {
            return "";
        }


        return bubble.innerText
            .replace(/\s+/g, " ")
            .trim();
    }


    // ---------------------------------------------------------
    // Watch Crop Doctor messages
    // ---------------------------------------------------------

    if (
        window.MutationObserver &&
        chatMessages
    ) {

        let lastSpokenMessage = "";


        const observer =
            new MutationObserver(
                function (mutations) {

                    for (
                        const mutation of mutations
                    ) {

                        for (
                            const node of mutation.addedNodes
                        ) {

                            if (
                                node.nodeType !==
                                Node.ELEMENT_NODE
                            ) {
                                continue;
                            }


                            let botText = "";


                            /*
                             * Direct bot message
                             */

                            if (
                                node.classList &&
                                (
                                    node.classList.contains(
                                        "bot"
                                    ) ||
                                    node.classList.contains(
                                        "chat-msg"
                                    )
                                )
                            ) {

                                botText =
                                    getBotText(node);
                            }


                            /*
                             * Bot message inside
                             * another newly-created element
                             */

                            if (
                                !botText &&
                                node.querySelector
                            ) {

                                const botMessage =
                                    node.querySelector(
                                        ".chat-msg.bot"
                                    );


                                if (botMessage) {

                                    botText =
                                        getBotText(
                                            botMessage
                                        );
                                }
                            }


                            /*
                             * Speak only the answer
                             * belonging to voice input.
                             */

                            if (
                                botText &&
                                botText !==
                                lastSpokenMessage
                            ) {

                                lastSpokenMessage =
                                    botText;


                                if (
                                    window
                                        .cropGuardVoiceWaitingForAnswer
                                ) {

                                    window
                                        .cropGuardVoiceWaitingForAnswer =
                                        false;

                                    speakAnswer(
                                        botText
                                    );
                                }
                            }
                        }
                    }
                }
            );


        observer.observe(
            chatMessages,
            {
                childList: true,
                subtree: true
            }
        );
    }


    // ---------------------------------------------------------
    // Check Speech Recognition support
    // ---------------------------------------------------------

    if (!SpeechRecognition) {

        voiceButton.disabled =
            true;

        voiceButton.style.opacity =
            "0.6";


        setStatus(
            "⚠️ Voice input requires Google Chrome or Microsoft Edge."
        );


        return;
    }


    // ---------------------------------------------------------
    // Create Speech Recognition
    // ---------------------------------------------------------

    recognition =
        new SpeechRecognition();


    recognition.continuous =
        false;

    recognition.interimResults =
        false;

    recognition.maxAlternatives =
        1;


    // ---------------------------------------------------------
    // Recognition started
    // ---------------------------------------------------------

    recognition.onstart =
        function () {

            isListening =
                true;


            voiceButton.classList.add(
                "listening"
            );


            setVoiceButton(
                "🔴 Listening..."
            );


            const language =
                getSelectedLanguage();


            setStatus(
                LANGUAGE_CONFIG[
                    language
                ].listening
            );
        };


    // ---------------------------------------------------------
    // Speech recognized
    // ---------------------------------------------------------

    recognition.onresult =
        function (event) {

            const transcript =
                event.results[0][0]
                    .transcript
                    .trim();


            if (!transcript) {

                setStatus(
                    "⚠️ No speech detected. Please try again."
                );

                return;
            }


            /*
             * Put spoken question into
             * Crop Doctor chat box.
             */

            chatInput.value =
                transcript;


            chatInput.dispatchEvent(
                new Event(
                    "input",
                    {
                        bubbles: true
                    }
                )
            );


            const language =
                getSelectedLanguage();


            setStatus(
                LANGUAGE_CONFIG[
                    language
                ].heard +
                transcript
            );


            /*
             * Tell CropGuard that the next
             * Crop Doctor answer should be
             * spoken.
             */

            window.cropGuardVoiceWaitingForAnswer =
                true;


            /*
             * Use your existing Send button.
             */

            if (chatSendButton) {

                setTimeout(
                    function () {

                        chatSendButton.click();

                    },
                    250
                );
            }
        };


    // ---------------------------------------------------------
    // Recognition error
    // ---------------------------------------------------------

    recognition.onerror =
        function (event) {

            isListening =
                false;


            voiceButton.classList.remove(
                "listening"
            );


            setVoiceButton(
                "🎤 Speak to CropGuard"
            );


            window.cropGuardVoiceWaitingForAnswer =
                false;


            const errors = {

                "not-allowed":
                    "❌ Microphone permission was denied. Allow microphone access in Chrome.",

                "service-not-allowed":
                    "❌ Speech recognition service is not allowed.",

                "no-speech":
                    "⚠️ No speech detected. Please speak again.",

                "audio-capture":
                    "❌ No microphone was found. Check your microphone.",

                "network":
                    "❌ Speech recognition needs a network connection.",

                "aborted":
                    "⏹ Voice recognition stopped."
            };


            setStatus(
                errors[event.error] ||
                (
                    "❌ Voice recognition error: " +
                    event.error
                )
            );
        };


    // ---------------------------------------------------------
    // Recognition ended
    // ---------------------------------------------------------

    recognition.onend =
        function () {

            isListening =
                false;


            voiceButton.classList.remove(
                "listening"
            );


            setVoiceButton(
                "🎤 Speak to CropGuard"
            );
        };


    // ---------------------------------------------------------
    // START VOICE ASSISTANT
    // ---------------------------------------------------------

    voiceButton.addEventListener(
        "click",
        function () {

            if (isListening) {
                return;
            }


            stopSpeaking();


            window.cropGuardVoiceWaitingForAnswer =
                false;


            const language =
                getSelectedLanguage();


            try {

                recognition.lang =
                    LANGUAGE_CONFIG[
                        language
                    ].recognition;


                recognition.start();

            }

            catch (error) {

                setStatus(
                    "🎤 Voice assistant is already listening. Please try again."
                );
            }
        }
    );


    // ---------------------------------------------------------
    // STOP VOICE ASSISTANT
    // ---------------------------------------------------------

    if (stopButton) {

        stopButton.addEventListener(
            "click",
            function () {

                window
                    .cropGuardVoiceWaitingForAnswer =
                    false;


                try {

                    recognition.stop();

                }

                catch (error) {}


                stopSpeaking();


                isListening =
                    false;


                voiceButton.classList.remove(
                    "listening"
                );


                setVoiceButton(
                    "🎤 Speak to CropGuard"
                );


                setStatus(
                    "⏹ Voice assistant stopped."
                );
            }
        );
    }


    // ---------------------------------------------------------
    // LANGUAGE CHANGED
    // ---------------------------------------------------------

    if (languageSelect) {

        languageSelect.addEventListener(
            "change",
            function () {

                stopSpeaking();


                window
                    .cropGuardVoiceWaitingForAnswer =
                    false;


                const selectedText =
                    languageSelect
                        .options[
                            languageSelect
                                .selectedIndex
                        ]
                        .text;


                setStatus(
                    "🌐 Voice language changed to " +
                    selectedText
                );
            }
        );
    }

})();