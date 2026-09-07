/**
 * CropGuard AI - Main Frontend Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  // Application State
  const state = {
    selectedFile: null,
    selectedDataUrl: null,
    currentScanResult: null,
    activeTab: "scanner",
    language: localStorage.getItem("cropguard_lang") || "en",
    sessionId: "farmer_" + Math.random().toString(36).substring(2, 9),
    weatherParams: { temp: 26, humidity: 82, rain: 4.5 }
  };

  // DOM Elements
  const elements = {
    langSelect: document.getElementById("langSelect"),
    navBtns: document.querySelectorAll(".nav-btn"),
    tabPanes: document.querySelectorAll(".tab-pane"),
    // Upload & Scanner
    dropzone: document.getElementById("dropzone"),
    fileInput: document.getElementById("fileInput"),
    cameraInput: document.getElementById("cameraInput"),
    btnPickFile: document.getElementById("btnPickFile"),
    btnCamera: document.getElementById("btnCamera"),
    samplesContainer: document.getElementById("samplesContainer"),
    // Results
    emptyState: document.getElementById("emptyState"),
    loadingState: document.getElementById("loadingState"),
    resultsContent: document.getElementById("resultsContent"),
    diagnosisImg: document.getElementById("diagnosisImg"),
    cropTag: document.getElementById("cropTag"),
    diseaseTitle: document.getElementById("diseaseTitle"),
    severityBadge: document.getElementById("severityBadge"),
    urgencyBadge: document.getElementById("urgencyBadge"),
    affectedPctVal: document.getElementById("affectedPctVal"),
    affectedFill: document.getElementById("affectedFill"),
    confidenceVal: document.getElementById("confidenceVal"),
    confidenceFill: document.getElementById("confidenceFill"),
    speechBtn: document.getElementById("speechBtn"),
    actionStepsList: document.getElementById("actionStepsList"),
    btnAskDoctorForScan: document.getElementById("btnAskDoctorForScan"),
    // Chat Doctor
    chatMessages: document.getElementById("chatMessages"),
    chatInput: document.getElementById("chatInput"),
    chatSendBtn: document.getElementById("chatSendBtn"),
    chatChips: document.querySelectorAll(".chip-btn"),
    // Weather Radar
    tempSlider: document.getElementById("tempSlider"),
    tempVal: document.getElementById("tempVal"),
    humiditySlider: document.getElementById("humiditySlider"),
    humidityVal: document.getElementById("humidityVal"),
    rainSlider: document.getElementById("rainSlider"),
    rainVal: document.getElementById("rainVal"),
    weatherOverallBadge: document.getElementById("weatherOverallBadge"),
    weatherHeadline: document.getElementById("weatherHeadline"),
    weatherSummary: document.getElementById("weatherSummary"),
    riskCardsContainer: document.getElementById("riskCardsContainer"),
    weatherChecklist: document.getElementById("weatherChecklist"),
    // History
    historyGrid: document.getElementById("historyGrid"),
    refreshHistoryBtn: document.getElementById("refreshHistoryBtn"),
    toastContainer: document.getElementById("toastContainer")
  };

  // 1. Language Initializer
  if (elements.langSelect) {
    elements.langSelect.value = state.language;
    setLanguage(state.language);
    elements.langSelect.addEventListener("change", (e) => {
      state.language = e.target.value;
      setLanguage(state.language);
      showToast(`Language set to ${e.target.options[e.target.selectedIndex].text}`);
      // If we have an active scan, re-fetch recommendation in new language
      if (state.currentScanResult) {
        refreshCurrentRecommendation();
      }
    });
  }

  // 2. Tab Navigation
  elements.navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      switchTab(targetTab);
    });
  });

  function switchTab(tabId) {
    state.activeTab = tabId;
    elements.navBtns.forEach(b => {
      b.classList.toggle("active", b.getAttribute("data-tab") === tabId);
    });
    elements.tabPanes.forEach(p => {
      p.classList.toggle("active", p.id === `tab-${tabId}`);
    });

    if (tabId === "history") {
      loadHistory();
    } else if (tabId === "weather") {
      updateWeatherRadar();
    }
  }

  // 3. Camera & Upload Setup
  const uploader = new CameraUploader({
    dropzone: elements.dropzone,
    fileInput: elements.fileInput,
    cameraInput: elements.cameraInput,
    onImageSelected: ({ file, dataUrl }) => {
      state.selectedFile = file;
      state.selectedDataUrl = dataUrl;
      submitScan(file, dataUrl);
    }
  });

  if (elements.btnPickFile) {
    elements.btnPickFile.addEventListener("click", () => elements.fileInput.click());
  }
  if (elements.btnCamera) {
    elements.btnCamera.addEventListener("click", () => elements.cameraInput.click());
  }

  // 4. Sample Leaves Loader
  loadSampleLeaves();

  async function loadSampleLeaves() {
    try {
      const resp = await fetch("/api/samples");
      const data = await resp.json();
      if (data.status === "success" && data.samples.length > 0) {
        renderSampleLeaves(data.samples);
      }
    } catch (e) {
      console.warn("Could not load samples:", e);
    }
  }

  function renderSampleLeaves(samples) {
    if (!elements.samplesContainer) return;
    elements.samplesContainer.innerHTML = "";
    samples.forEach(s => {
      const card = document.createElement("div");
      card.className = "sample-card";
      card.innerHTML = `
        <div class="sample-thumb-box">
          <img src="${s.url}" alt="${s.title}">
        </div>
        <span>${s.icon} ${s.crop}</span>
        <span style="color:var(--text-muted); font-size:0.68rem;">${s.disease}</span>
      `;
      card.addEventListener("click", async () => {
        showToast(`Loading sample: ${s.title}...`);
        const { file, dataUrl } = await uploader.loadSampleImageAsFile(s.url, s.filename);
        state.selectedFile = file;
        state.selectedDataUrl = dataUrl;
        submitScan(file, dataUrl);
      });
      elements.samplesContainer.appendChild(card);
    });
  }

  // 5. Submit Scan to Backend
  async function submitScan(file, dataUrl) {
    // Show loader UI
    elements.emptyState.style.display = "none";
    elements.resultsContent.style.display = "none";
    elements.loadingState.style.display = "flex";

    voiceAssistant.stop();

    const formData = new FormData();
    formData.append("image", file);
    formData.append("lang", state.language);
    formData.append("session_id", state.sessionId);

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData
      });

      const result = await response.json();

      elements.loadingState.style.display = "none";

      if (result.status === "success") {
        state.currentScanResult = result;
        renderResults(result, dataUrl);
        showToast(`Diagnosed: ${result.crop} - ${result.disease}!`, "success");
      } else {
        alert("Scan failed: " + (result.message || "Unknown error"));
        elements.emptyState.style.display = "flex";
      }
    } catch (err) {
      console.error("Scan error:", err);
      elements.loadingState.style.display = "none";
      elements.emptyState.style.display = "flex";
      alert("Error connecting to server. Please check backend is running.");
    }
  }

  // 6. Render Diagnostic Results
  function renderResults(res, dataUrl) {
    elements.resultsContent.style.display = "block";
    elements.emptyState.style.display = "none";

    elements.diagnosisImg.src = dataUrl || res.image_url || "/assets/samples/tomato_early_blight.jpg";
    elements.cropTag.innerHTML = `${res.crop_icon || '🌱'} ${res.crop}`;
    elements.diseaseTitle.textContent = res.disease;

    // Severity Badge
    const sevBadgeClass = `badge-${(res.severity || 'medium').toLowerCase()}`;
    elements.severityBadge.className = `badge ${sevBadgeClass} badge-pulse`;
    elements.severityBadge.innerHTML = `⚠️ ${t('severityLabel')}: ${res.severity}`;

    // Urgency Badge
    elements.urgencyBadge.innerHTML = `⏱️ ${res.urgency || 'Act within 3 days'}`;

    // Gauges
    const affectedPct = res.affected_area_pct || 0;
    elements.affectedPctVal.textContent = `${affectedPct}%`;
    elements.affectedFill.style.width = `${Math.min(100, Math.max(5, affectedPct))}%`;
    elements.affectedFill.style.background = res.severity_color || "#f59e0b";

    const confPct = Math.round((res.confidence || 0.9) * 100);
    elements.confidenceVal.textContent = `${confPct}%`;
    elements.confidenceFill.style.width = `${confPct}%`;
    elements.confidenceFill.style.background = "#10b981";

    // Action Steps List
    elements.actionStepsList.innerHTML = "";
    if (res.action_steps && res.action_steps.length > 0) {
      res.action_steps.forEach(step => {
        const stepCard = document.createElement("div");
        stepCard.className = "action-step-card";
        const iconSymbol = step.type === "critical" ? "🚨" : step.type === "organic" ? "🌿" : step.type === "chemical" ? "🧪" : "🛡️";
        stepCard.innerHTML = `
          <div class="step-icon ${step.type}">${iconSymbol}</div>
          <div class="step-body">
            <h5>${step.title}</h5>
            <p>${step.text}</p>
          </div>
        `;
        elements.actionStepsList.appendChild(stepCard);
      });
    }

    // Voice Read-Aloud Button
    elements.speechBtn.onclick = () => {
      if (voiceAssistant.isSpeaking) {
        voiceAssistant.stop();
        elements.speechBtn.classList.remove("playing");
        elements.speechBtn.innerHTML = `🔊 ${t('btnListen')}`;
      } else {
        const textToRead = `${res.crop}, ${res.disease}. ${t('severityLabel')}: ${res.severity}. ${res.summary}. ${res.organic_control || ''}.`;
        voiceAssistant.speak(
          textToRead,
          state.language,
          () => {
            elements.speechBtn.classList.add("playing");
            elements.speechBtn.innerHTML = `⏹️ Stop`;
          },
          () => {
            elements.speechBtn.classList.remove("playing");
            elements.speechBtn.innerHTML = `🔊 ${t('btnListen')}`;
          }
        );
      }
    };

    // One-Click "Ask Doctor About This"
    if (elements.btnAskDoctorForScan) {
      elements.btnAskDoctorForScan.onclick = () => {
        switchTab("doctor");
        sendChatMessage(`Tell me more about treating ${res.crop} ${res.disease} in detail, including dosage and safety precautions.`, res.crop, res.original_disease);
      };
    }
  }

  // Refresh current scan when language switches
  async function refreshCurrentRecommendation() {
    if (!state.currentScanResult) return;
    const crop = state.currentScanResult.crop;
    const disease = state.currentScanResult.original_disease || state.currentScanResult.disease;
    const sev = state.currentScanResult.severity;

    try {
      const resp = await fetch(`/api/recommendation?crop=${encodeURIComponent(crop)}&disease=${encodeURIComponent(disease)}&severity=${sev}&lang=${state.language}`);
      const data = await resp.json();
      if (data.status === "success" && data.advisory) {
        state.currentScanResult = {
          ...state.currentScanResult,
          ...data.advisory,
          disease: data.advisory.disease
        };
        renderResults(state.currentScanResult, state.selectedDataUrl);
      }
    } catch (e) {
      console.warn("Could not refresh translation:", e);
    }
  }

  // 7. Crop Doctor AI Chat
  if (elements.chatSendBtn && elements.chatInput) {
    elements.chatSendBtn.addEventListener("click", () => {
      const query = elements.chatInput.value.trim();
      if (query) {
        sendChatMessage(query);
        elements.chatInput.value = "";
      }
    });

    elements.chatInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        elements.chatSendBtn.click();
      }
    });
  }

  // Suggestion Chips
  elements.chatChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const query = chip.textContent.trim();
      sendChatMessage(query);
    });
  });

  async function sendChatMessage(query, cropHint = null, diseaseHint = null) {
    appendChatBubble("user", query);

    // Typing indicator
    const typingId = appendChatBubble("bot", "🌱 <i>Crop Doctor is analyzing your query...</i>");

    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          crop: cropHint,
          disease: diseaseHint,
          lang: state.language
        })
      });

      const data = await resp.json();
      const typingEl = document.getElementById(typingId);
      if (typingEl) typingEl.remove();

      if (data.status === "success" && data.response) {
        const formattedAnswer = data.response.answer.replace(/\n/g, "<br>");
        appendChatBubble("bot", formattedAnswer);
      } else {
        appendChatBubble("bot", "I am having trouble retrieving that answer right now. Please try again.");
      }
    } catch (e) {
      console.error("Chat error:", e);
      const typingEl = document.getElementById(typingId);
      if (typingEl) typingEl.remove();
      appendChatBubble("bot", "Network connection issue. Please ensure the backend is active.");
    }
  }

  function appendChatBubble(sender, htmlContent) {
    const msgId = "msg_" + Math.random().toString(36).substring(2, 9);
    const msgDiv = document.createElement("div");
    msgDiv.id = msgId;
    msgDiv.className = `chat-msg ${sender}`;

    const bubble = document.createElement("div");
    bubble.className = "chat-bubble";
    bubble.innerHTML = htmlContent;

    msgDiv.appendChild(bubble);
    elements.chatMessages.appendChild(msgDiv);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    return msgId;
  }

  // 8. Weather Risk Radar
  function initWeatherSliders() {
    const update = () => {
      state.weatherParams.temp = parseFloat(elements.tempSlider.value);
      state.weatherParams.humidity = parseFloat(elements.humiditySlider.value);
      state.weatherParams.rain = parseFloat(elements.rainSlider.value);

      elements.tempVal.textContent = `${state.weatherParams.temp}°C`;
      elements.humidityVal.textContent = `${state.weatherParams.humidity}%`;
      elements.rainVal.textContent = `${state.weatherParams.rain} mm`;

      updateWeatherRadar();
    };

    if (elements.tempSlider) elements.tempSlider.addEventListener("input", update);
    if (elements.humiditySlider) elements.humiditySlider.addEventListener("input", update);
    if (elements.rainSlider) elements.rainSlider.addEventListener("input", update);
  }

  initWeatherSliders();

  async function updateWeatherRadar() {
    try {
      const url = `/api/weather-risk?temp=${state.weatherParams.temp}&humidity=${state.weatherParams.humidity}&rain=${state.weatherParams.rain}`;
      const resp = await fetch(url);
      const data = await resp.json();

      if (data.status === "success" && data.risk_radar) {
        renderWeatherRadar(data.risk_radar);
      }
    } catch (e) {
      console.warn("Weather risk error:", e);
    }
  }

  function renderWeatherRadar(radar) {
    if (elements.weatherOverallBadge) {
      elements.weatherOverallBadge.textContent = radar.overall_level;
      elements.weatherOverallBadge.style.background = radar.overall_color;
      elements.weatherOverallBadge.style.color = "#fff";
    }
    if (elements.weatherHeadline) elements.weatherHeadline.textContent = radar.headline;
    if (elements.weatherSummary) elements.weatherSummary.textContent = radar.summary;

    // Risk cards
    if (elements.riskCardsContainer) {
      elements.riskCardsContainer.innerHTML = "";
      radar.risks.forEach(r => {
        const card = document.createElement("div");
        card.className = "risk-card";
        card.innerHTML = `
          <div>
            <div class="risk-card-top">
              <span class="risk-card-title">${r.category}</span>
              <span class="badge" style="background:${r.color}; color:#fff;">${r.level}</span>
            </div>
            <p style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:0.75rem;">
              Target: ${r.target_diseases.join(', ')}
            </p>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:0.8rem; color:var(--text-muted); max-width:180px;">${r.action}</span>
            <div class="risk-score-circle" style="background:${r.color}20; color:${r.color};">
              ${r.score}%
            </div>
          </div>
        `;
        elements.riskCardsContainer.appendChild(card);
      });
    }

    // Advisory checklist
    if (elements.weatherChecklist) {
      elements.weatherChecklist.innerHTML = "";
      radar.advisory_checklist.forEach(item => {
        const li = document.createElement("li");
        li.style.cssText = "margin-bottom:0.5rem; font-size:0.9rem; color:var(--text-secondary);";
        li.innerHTML = `✅ ${item}`;
        elements.weatherChecklist.appendChild(li);
      });
    }
  }

  // 9. Scan History Loader
  async function loadHistory() {
    if (!elements.historyGrid) return;
    elements.historyGrid.innerHTML = "<p style='color:var(--text-muted);'>Loading past scans...</p>";

    try {
      const resp = await fetch("/api/history?limit=30");
      const data = await resp.json();

      if (data.status === "success" && data.scans && data.scans.length > 0) {
        renderHistoryCards(data.scans);
      } else {
        elements.historyGrid.innerHTML = `<p style='color:var(--text-muted);'>${t('noHistory')}</p>`;
      }
    } catch (e) {
      elements.historyGrid.innerHTML = "<p style='color:red;'>Could not load scan history.</p>";
    }
  }

  if (elements.refreshHistoryBtn) {
    elements.refreshHistoryBtn.addEventListener("click", loadHistory);
  }

  function renderHistoryCards(scans) {
    elements.historyGrid.innerHTML = "";
    scans.forEach(scan => {
      const card = document.createElement("div");
      card.className = "history-card";
      const sevClass = `badge-${(scan.severity || 'medium').toLowerCase()}`;
      card.innerHTML = `
        <div class="history-card-header">
          <span class="history-date">📅 ${scan.created_at || 'Recent'}</span>
          <span class="badge ${sevClass}">${scan.severity}</span>
        </div>
        <div class="history-crop-title">${scan.crop} — ${scan.disease}</div>
        <p class="history-summary">${scan.recommendation}</p>
        <div style="display:flex; justify-content:space-between; margin-top:0.75rem; font-size:0.8rem; color:var(--text-muted);">
          <span>Infection: ${scan.affected_area_pct}%</span>
          <span>Confidence: ${Math.round(scan.confidence * 100)}%</span>
        </div>
      `;
      card.addEventListener("click", () => {
        showToast(`Viewing scan: ${scan.crop} ${scan.disease}`);
        switchTab("scanner");
        state.currentScanResult = {
          crop: scan.crop,
          disease: scan.disease,
          original_disease: scan.disease,
          confidence: scan.confidence,
          severity: scan.severity,
          affected_area_pct: scan.affected_area_pct,
          urgency: scan.urgency || "Act within 3 days",
          summary: scan.recommendation,
          action_steps: [
            { step: 1, title: "Recommended Treatment", text: scan.recommendation, type: "critical" }
          ]
        };
        renderResults(state.currentScanResult, scan.image_name ? `/api/uploads/${scan.image_name}` : null);
      });
      elements.historyGrid.appendChild(card);
    });
  }

  // Toast Helper
  function showToast(message, type = "info") {
    if (!elements.toastContainer) return;
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = `<span>${type === 'success' ? '✅' : 'ℹ️'}</span> <span>${message}</span>`;
    elements.toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 3200);
  }
});
