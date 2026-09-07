/**
 * CropGuard AI - Main Frontend Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  // API Base Configuration (supports URL query param, custom cloud backend URL, or local proxy)
  const getInitialApiBase = () => {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const queryApi = urlParams.get("api");
      if (queryApi) {
        const cleanApi = queryApi.replace(/\/+$/, "");
        localStorage.setItem("cropguard_api_base", cleanApi);
        return cleanApi;
      }
    } catch (e) {}
    return localStorage.getItem("cropguard_api_base") || window.CROPGUARD_API_BASE || "";
  };
  let API_BASE = getInitialApiBase();

  // Server Status & Settings Elements
  const serverStatusBtn = document.getElementById("serverStatusBtn");
  const serverStatusText = document.getElementById("serverStatusText");
  const serverModal = document.getElementById("serverModal");
  const closeServerModalBtn = document.getElementById("closeServerModalBtn");
  const serverUrlInput = document.getElementById("serverUrlInput");
  const testServerBtn = document.getElementById("testServerBtn");
  const saveServerBtn = document.getElementById("saveServerBtn");
  const serverPingResult = document.getElementById("serverPingResult");

  let backendOnline = false;

  function updateServerStatusUI(online, customMessage) {
    if (!serverStatusBtn || !serverStatusText) return;
    if (online) {
      serverStatusBtn.className = "server-status-btn online";
      serverStatusText.textContent = customMessage || "AI Server Online";
      serverStatusBtn.title = `Connected to ${API_BASE || 'current origin'} — Click to edit`;
    } else {
      serverStatusBtn.className = "server-status-btn offline";
      serverStatusText.textContent = customMessage || "AI Server Offline";
      serverStatusBtn.title = "AI Server Disconnected — Click to configure";
    }
  }

  async function pingServer(targetUrl) {
    const base = targetUrl !== undefined ? targetUrl.trim().replace(/\/+$/, "") : API_BASE;
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 4000);
      const resp = await fetch(`${base}/api/health`, {
        signal: controller.signal,
        headers: { "bypass-tunnel-reminder": "true" }
      });
      clearTimeout(timeoutId);
      if (resp.ok) {
        const data = await resp.json();
        return { ok: true, data };
      }
    } catch (err) {}
    return { ok: false };
  }

  async function checkBackendHealth() {
    updateServerStatusUI(false, "Checking Server...");
    const res = await pingServer();
    backendOnline = res.ok;
    updateServerStatusUI(backendOnline);
    return backendOnline;
  }

  if (serverStatusBtn) {
    serverStatusBtn.addEventListener("click", () => {
      if (serverUrlInput) serverUrlInput.value = API_BASE;
      if (serverPingResult) serverPingResult.style.display = "none";
      if (serverModal) serverModal.classList.add("active");
    });
  }

  if (closeServerModalBtn) {
    closeServerModalBtn.addEventListener("click", () => {
      if (serverModal) serverModal.classList.remove("active");
    });
  }

  if (serverModal) {
    serverModal.addEventListener("click", (e) => {
      if (e.target === serverModal) {
        serverModal.classList.remove("active");
      }
    });
  }

  if (testServerBtn) {
    testServerBtn.addEventListener("click", async () => {
      if (!serverPingResult || !serverUrlInput) return;
      serverPingResult.style.display = "block";
      serverPingResult.style.background = "#f1f5f9";
      serverPingResult.style.color = "#475569";
      serverPingResult.textContent = "Testing connection to server...";

      const candidateUrl = serverUrlInput.value.trim();
      const res = await pingServer(candidateUrl);
      if (res.ok) {
        serverPingResult.style.background = "#ecfdf5";
        serverPingResult.style.color = "#065f46";
        serverPingResult.textContent = "✅ Connected! AI Backend Gateway and PyTorch model are ready.";
      } else {
        serverPingResult.style.background = "#fef2f2";
        serverPingResult.style.color = "#991b1b";
        serverPingResult.textContent = "❌ Connection failed. Ensure the server or tunnel is running and accessible.";
      }
    });
  }

  if (saveServerBtn) {
    saveServerBtn.addEventListener("click", async () => {
      if (!serverUrlInput) return;
      const candidateUrl = serverUrlInput.value.trim().replace(/\/+$/, "");
      API_BASE = candidateUrl;
      if (candidateUrl) {
        localStorage.setItem("cropguard_api_base", candidateUrl);
      } else {
        localStorage.removeItem("cropguard_api_base");
      }
      if (serverModal) serverModal.classList.remove("active");
      showToast("Backend server URL updated", "info");
      await checkBackendHealth();
    });
  }


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

  // Built-in Sample Leaves (Accessible statically on Vercel & local server)
  const DEFAULT_SAMPLES = [
    { filename: "tomato_early_blight.jpg", title: "Tomato - Early Blight", crop: "Tomato", disease: "Early Blight", icon: "🍅", url: "assets/samples/tomato_early_blight.jpg" },
    { filename: "tomato_healthy.jpg", title: "Tomato - Healthy Leaf", crop: "Tomato", disease: "Healthy", icon: "🍅", url: "assets/samples/tomato_healthy.jpg" },
    { filename: "potato_late_blight.jpg", title: "Potato - Late Blight", crop: "Potato", disease: "Late Blight", icon: "🥔", url: "assets/samples/potato_late_blight.jpg" },
    { filename: "corn_common_rust.jpg", title: "Corn - Common Rust", crop: "Corn", disease: "Common Rust", icon: "🌽", url: "assets/samples/corn_common_rust.jpg" },
    { filename: "apple_scab.jpg", title: "Apple - Apple Scab", crop: "Apple", disease: "Apple Scab", icon: "🍎", url: "assets/samples/apple_scab.jpg" },
    { filename: "rice_blast.jpg", title: "Rice - Leaf Blast", crop: "Rice", disease: "Rice Blast", icon: "🌾", url: "assets/samples/rice_blast.jpg" }
  ];

  // Built-in Agronomic Diagnoses for Demo & Web Previews
  const SAMPLE_DIAGNOSES = {
    "tomato_early_blight.jpg": {
      crop: "Tomato", crop_icon: "🍅", disease: "Early Blight", original_disease: "Early Blight", pathogen_type: "Fungal",
      confidence: 0.94, severity: "Medium", severity_badge: "warning", severity_color: "#f59e0b",
      affected_area_pct: 26.5, urgency: "Act within 48 hours",
      summary: "Early blight caused by Alternaria solani. Concentric target-board rings visible on leaf tissue.",
      action_steps: [
        { type: "critical", title: "Prune Infected Foliage", text: "Remove lower infected leaves immediately and dispose away from the field. Do not compost." },
        { type: "organic", title: "Neem Oil Spray", text: "Spray 5ml/L cold-pressed neem oil with mild soap emulsifier in early morning hours." },
        { type: "chemical", title: "Fungicide Application", text: "Apply Mancozeb 75 WP @ 2.5g/L or Chlorothalonil 75 WP @ 2g/L if lesions cover >20% foliage." }
      ]
    },
    "tomato_healthy.jpg": {
      crop: "Tomato", crop_icon: "🍅", disease: "Healthy", original_disease: "Healthy", pathogen_type: "None",
      confidence: 0.98, severity: "Healthy", severity_badge: "success", severity_color: "#10b981",
      affected_area_pct: 0.0, urgency: "Routine maintenance",
      summary: "Leaf tissue displays optimal chlorophyll concentration with no signs of fungal, bacterial, or pest damage.",
      action_steps: [
        { type: "preventive", title: "Maintain Drip Irrigation", text: "Continue regular watering without splashing soil onto lower foliage." },
        { type: "organic", title: "Balanced Nutrition", text: "Apply balanced NPK foliar spray or compost tea for strong cell wall integrity." }
      ]
    },
    "potato_late_blight.jpg": {
      crop: "Potato", crop_icon: "🥔", disease: "Late Blight", original_disease: "Late Blight", pathogen_type: "Oomycete",
      confidence: 0.96, severity: "High", severity_badge: "danger", severity_color: "#ef4444",
      affected_area_pct: 42.0, urgency: "Immediate Action (24 hours)",
      summary: "Late blight (Phytophthora infestans) detected. Highly destructive water-soaked lesions under humid conditions.",
      action_steps: [
        { type: "critical", title: "Immediate Fungicide Application", text: "Spray Cymoxanil + Mancozeb (Curzate M8) @ 2.5g/L or Metalaxyl-M." },
        { type: "preventive", title: "Halt Overhead Irrigation", text: "Cease sprinkler watering immediately to shorten leaf wetness duration." }
      ]
    },
    "corn_common_rust.jpg": {
      crop: "Corn", crop_icon: "🌽", disease: "Common Rust", original_disease: "Common Rust", pathogen_type: "Fungal",
      confidence: 0.91, severity: "Medium", severity_badge: "warning", severity_color: "#f59e0b",
      affected_area_pct: 22.0, urgency: "Act within 3-4 days",
      summary: "Puccinia sorghi infection with cinnamon-brown pustules erupting across leaf surfaces.",
      action_steps: [
        { type: "chemical", title: "Foliar Triazole Spray", text: "Apply Azoxystrobin + Difenoconazole @ 1ml/L during early blister stages." },
        { type: "preventive", title: "Monitor Field Humidity", text: "Avoid dense planting to allow adequate wind circulation across rows." }
      ]
    },
    "apple_scab.jpg": {
      crop: "Apple", crop_icon: "🍎", disease: "Apple Scab", original_disease: "Apple Scab", pathogen_type: "Fungal",
      confidence: 0.93, severity: "Medium", severity_badge: "warning", severity_color: "#f59e0b",
      affected_area_pct: 18.5, urgency: "Act within 3 days",
      summary: "Venturia inaequalis lesions with olive-green velvety spots on leaves and fruit spurs.",
      action_steps: [
        { type: "chemical", title: "Protective Fungicide", text: "Apply Captan 50 WP @ 2.5g/L or Difenoconazole 25 EC @ 0.5ml/L." },
        { type: "organic", title: "Orchard Sanitation", text: "Rake and shred fallen apple leaves to reduce primary overwintering ascospores." }
      ]
    },
    "rice_blast.jpg": {
      crop: "Rice", crop_icon: "🌾", disease: "Rice Blast", original_disease: "Rice Blast", pathogen_type: "Fungal",
      confidence: 0.95, severity: "High", severity_badge: "danger", severity_color: "#ef4444",
      affected_area_pct: 35.0, urgency: "Immediate Action (24 hours)",
      summary: "Magnaporthe oryzae spindle-shaped lesions with greyish center and brownish margins.",
      action_steps: [
        { type: "critical", title: "Systemic Blast Fungicide", text: "Spray Tricyclazole 75 WP @ 0.6g/L or Isoprothiolane 40 EC @ 1.5ml/L." },
        { type: "preventive", title: "Regulate Nitrogen Application", text: "Avoid excessive urea top-dressing which increases leaf tissue susceptibility." }
      ]
    }
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

  // 4. Server Health & Sample Leaves Loader
  checkBackendHealth();
  loadSampleLeaves();

  async function loadSampleLeaves() {
    try {
      const resp = await fetch(`${API_BASE}/api/samples`);
      if (resp.ok) {
        const data = await resp.json();
        if (data.status === "success" && data.samples && data.samples.length > 0) {
          renderSampleLeaves(data.samples);
          return;
        }
      }
    } catch (e) {
      console.warn("API samples not reachable, using built-in samples:", e);
    }
    renderSampleLeaves(DEFAULT_SAMPLES);
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

  // 5. Submit Scan (AI Diagnostic Pipeline)
  async function submitScan(file, dataUrl) {
    // Show loader UI
    elements.emptyState.style.display = "none";
    elements.resultsContent.style.display = "none";
    elements.loadingState.style.display = "flex";

    voiceAssistant.stop();

    // Check if it's a known built-in sample leaf
    const matchKey = Object.keys(SAMPLE_DIAGNOSES).find(k =>
      file.name && file.name.toLowerCase().includes(k.replace(".jpg", "").replace(/_/g, ""))
    );

    const formData = new FormData();
    formData.append("image", file);
    formData.append("lang", state.language);
    formData.append("session_id", state.sessionId);

    let result = null;
    let backendErrorMsg = null;

    // 1. Primary: Query the live PyTorch Backend
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 12000);
      const response = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        headers: {
          "bypass-tunnel-reminder": "true"
        },
        signal: controller.signal,
        body: formData
      });
      clearTimeout(timeoutId);

      if (response.ok) {
        result = await response.json();
        backendOnline = true;
        updateServerStatusUI(true);
      } else {
        const errJson = await response.json().catch(() => null);
        backendErrorMsg = (errJson && errJson.message) || `Server returned status ${response.status}`;
      }
    } catch (err) {
      console.warn("Backend server connection attempt failed:", err);
      backendOnline = false;
      updateServerStatusUI(false);
      backendErrorMsg = "AI backend server is unreachable from this device.";
    }

    // 2. If PyTorch backend returned diagnosis, use it!
    if (result && (result.status === "success" || result.status === "low_confidence" || result.crop)) {
      result.status = "success";
      elements.loadingState.style.display = "none";
      state.currentScanResult = result;
      saveLocalScan(result);
      renderResults(result, dataUrl);
      showToast(`Diagnosed: ${result.crop} - ${result.disease}!`, "success");
      return;
    }

    // 3. If user clicked one of the built-in demo sample leaves, show demo diagnosis:
    if (matchKey && SAMPLE_DIAGNOSES[matchKey]) {
      result = { status: "success", ...SAMPLE_DIAGNOSES[matchKey] };
      elements.loadingState.style.display = "none";
      state.currentScanResult = result;
      saveLocalScan(result);
      renderResults(result, dataUrl);
      showToast(`Sample Leaf: ${result.crop} - ${result.disease}`, "info");
      return;
    }

    // 4. For custom user photo, if backend is disconnected: NEVER fabricate a fake diagnosis!
    elements.loadingState.style.display = "none";
    elements.emptyState.style.display = "none";
    elements.resultsContent.style.display = "block";

    renderBackendOfflineNotice(dataUrl, backendErrorMsg);
  }

  function renderBackendOfflineNotice(dataUrl, errorDetail) {
    elements.diagnosisImg.src = dataUrl || "/assets/samples/tomato_early_blight.jpg";
    elements.cropTag.innerHTML = `⚠️ Server Disconnected`;
    elements.diseaseTitle.textContent = "AI Model Unreachable";

    elements.severityBadge.className = "badge badge-danger";
    elements.severityBadge.innerHTML = `⚠️ Offline`;
    elements.urgencyBadge.innerHTML = `⏱️ Connect Backend`;

    elements.affectedPctVal.textContent = `--%`;
    elements.affectedFill.style.width = `0%`;
    elements.affectedFill.style.background = "#94a3b8";

    elements.confidenceVal.textContent = `--%`;
    elements.confidenceFill.style.width = `0%`;
    elements.confidenceFill.style.background = "#94a3b8";

    elements.diseaseSummary.innerHTML = `
      <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: var(--radius-sm); padding: 0.75rem; color: #991b1b; margin-bottom: 0.75rem;">
        <b>⚠️ AI Diagnostic Server Not Connected</b><br>
        <span style="font-size: 0.85rem;">CropGuard requires a live connection to the PyTorch AI backend to run disease inference on custom photos.</span>
      </div>
      <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
        ${errorDetail ? `Status: <code>${errorDetail}</code><br>` : ''}
        To diagnose leaves from another device, connect to your PC's IP or enter your public tunnel URL in Server Settings.
      </p>
      <button id="openServerConfigFromResultsBtn" class="btn btn-primary" style="width: 100%; font-size: 0.85rem; padding: 0.6rem; margin-bottom: 0.5rem;">
        ⚙️ Configure Backend Server Connection
      </button>
      <p style="font-size: 0.75rem; color: var(--text-muted); text-align: center;">
        You can also test the full diagnostic UI using the built-in demo leaves on the left.
      </p>
    `;

    setTimeout(() => {
      const btn = document.getElementById("openServerConfigFromResultsBtn");
      if (btn) {
        btn.addEventListener("click", () => {
          if (serverUrlInput) serverUrlInput.value = API_BASE;
          if (serverPingResult) serverPingResult.style.display = "none";
          if (serverModal) serverModal.classList.add("active");
        });
      }
    }, 50);

    elements.treatmentList.innerHTML = `
      <div class="action-card preventive" style="opacity: 0.85;">
        <div class="action-card-header">
          <span class="action-card-icon">💡</span>
          <h4 class="action-card-title">How to connect on another device:</h4>
        </div>
        <p class="action-card-body" style="font-size: 0.82rem; line-height: 1.5;">
          1. Start CropGuard on your computer: <code>python run_all.py</code><br>
          2. Tap the <b>AI Server Offline</b> badge at the top of the screen.<br>
          3. Enter your computer's IP address or tunnel URL and tap <b>Save & Connect</b>.
        </p>
      </div>
    `;

    showToast("AI Server unreachable. Tap server button at top to connect.", "error");
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
      const resp = await fetch(`${API_BASE}/api/recommendation?crop=${encodeURIComponent(crop)}&disease=${encodeURIComponent(disease)}&severity=${sev}&lang=${state.language}`);
      if (resp.ok) {
        const data = await resp.json();
        if (data.status === "success" && data.advisory) {
          state.currentScanResult = {
            ...state.currentScanResult,
            ...data.advisory,
            disease: data.advisory.disease
          };
          renderResults(state.currentScanResult, state.selectedDataUrl);
          return;
        }
      }
    } catch (e) {
      console.warn("Could not refresh translation from API:", e);
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

    let botAnswer = null;
    try {
      const resp = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          crop: cropHint,
          disease: diseaseHint,
          lang: state.language
        })
      });

      if (resp.ok) {
        const data = await resp.json();
        if (data.status === "success" && data.response && data.response.answer) {
          botAnswer = data.response.answer;
        }
      }
    } catch (e) {
      console.warn("Chat API unreachable, using built-in Crop Doctor assistant:", e);
    }

    const typingEl = document.getElementById(typingId);
    if (typingEl) typingEl.remove();

    if (!botAnswer) {
      botAnswer = generateLocalDoctorAnswer(query, cropHint, diseaseHint);
    }

    const formattedAnswer = botAnswer.replace(/\n/g, "<br>");
    appendChatBubble("bot", formattedAnswer);
  }

  function generateLocalDoctorAnswer(query, cropHint, diseaseHint) {
    const q = query.toLowerCase();
    if (q.includes("organic") || q.includes("neem") || q.includes("natural") || q.includes("home remedy")) {
      return "🌿 **Organic Management Protocol:**\n\n1. **Neem Oil Spray:** Mix 5ml pure cold-pressed neem oil (1500 ppm) with 2ml mild liquid soap per 1 liter water. Spray early mornings every 7 days.\n2. **Bio-Fungicides:** Apply *Trichoderma harzianum* (5g/L) for soil pathogens or *Pseudomonas fluorescens* for foliar spots.\n3. **Sanitation:** Prune lower diseased foliage and maintain mulch to prevent soil splashing.";
    }
    if (q.includes("chemical") || q.includes("spray") || q.includes("dose") || q.includes("dosage") || q.includes("mancozeb") || q.includes("fungicide")) {
      return "🧪 **Chemical Spray & Dosage Guidelines:**\n\n- **Preventive (Contact):** Mancozeb 75% WP @ 2.5g/L or Copper Oxychloride 50% WP @ 2.5g/L.\n- **Curative (Systemic):** Azoxystrobin + Difenoconazole @ 1ml/L or Ridomil Gold @ 2g/L.\n- **Timing:** Spray during calm morning hours. Always wear protective gloves and observe a 7-day pre-harvest interval.";
    }
    if (q.includes("blight") || (cropHint && cropHint.toLowerCase().includes("tomato"))) {
      return "🔍 **Tomato Early/Late Blight Care:**\n\n- Remove bottom leaves showing dark concentric rings.\n- Avoid overhead sprinkler watering; use drip irrigation at the root zone.\n- Apply Mancozeb 75 WP or copper hydroxide before rainy periods to prevent sporulation.";
    }
    return "🌱 **Crop Doctor Advice:**\n\nFor best results, upload a clear photo of your affected leaf in the **Scanner** tab. I will identify the pathogen type, severity percentage, and precise organic and chemical recommendations.";
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
      const url = `${API_BASE}/api/weather-risk?temp=${state.weatherParams.temp}&humidity=${state.weatherParams.humidity}&rain=${state.weatherParams.rain}`;
      const resp = await fetch(url);
      if (resp.ok) {
        const data = await resp.json();
        if (data.status === "success" && data.risk_radar) {
          renderWeatherRadar(data.risk_radar);
          return;
        }
      }
    } catch (e) {
      console.warn("Weather API unreachable, computing client-side agronomic risk:", e);
    }
    const localRadar = computeLocalWeatherRisk(state.weatherParams.temp, state.weatherParams.humidity, state.weatherParams.rain);
    renderWeatherRadar(localRadar);
  }

  function computeLocalWeatherRisk(temp, humidity, rain) {
    let fungalScore = 0;
    if (humidity > 85) fungalScore += 45;
    else if (humidity > 70) fungalScore += 30;
    else if (humidity > 50) fungalScore += 15;
    if (temp >= 18 && temp <= 27) fungalScore += 40;
    else if (temp >= 14 && temp <= 32) fungalScore += 25;
    else fungalScore += 10;
    if (rain > 10) fungalScore += 15;
    else if (rain > 2) fungalScore += 10;
    fungalScore = Math.min(100, Math.round(fungalScore));

    let rustScore = 0;
    if (temp >= 15 && temp <= 25) rustScore += 45;
    else if (temp >= 10 && temp <= 30) rustScore += 25;
    if (humidity > 80) rustScore += 40;
    else if (humidity > 60) rustScore += 25;
    if (rain > 1) rustScore += 15;
    rustScore = Math.min(100, Math.round(rustScore));

    let pestScore = 0;
    if (temp >= 24 && temp <= 34) pestScore += 45;
    else if (temp >= 18 && temp <= 36) pestScore += 30;
    if (humidity >= 50 && humidity <= 75) pestScore += 35;
    else if (humidity < 50) pestScore += 20;
    if (rain < 2) pestScore += 20;
    pestScore = Math.min(100, Math.round(pestScore));

    const overallScore = Math.round((fungalScore * 0.45) + (rustScore * 0.35) + (pestScore * 0.20));
    let level = "Low Risk", color = "#10b981", headline = "Favorable Weather for Crop Growth";
    let summary = "Current weather parameters do not favor rapid fungal sporulation or pest swarming.";

    if (fungalScore >= 75) {
      level = "High Risk"; color = "#ef4444"; headline = "High Fungal Blight Outbreak Risk Detected!";
      summary = `High relative humidity (${humidity}%) and optimal temp (${temp}°C) create prime conditions for Late Blight, Scab, and Downy Mildew.`;
    } else if (pestScore >= 70) {
      level = "Elevated Pest Risk"; color = "#f59e0b"; headline = "High Insect Vector & Sucking Pest Alert";
      summary = `Warm conditions (${temp}°C) and dry air favor rapid Whitefly, Thrip, and Spider Mite multiplication.`;
    } else if (fungalScore >= 50 || rustScore >= 50) {
      level = "Moderate Alert"; color = "#f59e0b"; headline = "Moderate Fungal Disease Caution";
      summary = `Humidity levels (${humidity}%) are elevated. Keep canopy aerated and check lower leaves for brown spots.`;
    }

    const checklist = [];
    if (fungalScore >= 50) {
      checklist.push("Apply preventive copper spray or Mancozeb before expected rain.");
      checklist.push("Avoid irrigation during evening hours to keep leaves dry overnight.");
    }
    if (pestScore >= 50) {
      checklist.push("Install yellow and blue sticky traps in crop rows.");
      checklist.push("Spray 2% neem oil to suppress early whitefly / aphid nymphs.");
    }
    if (checklist.length === 0) {
      checklist.push("Continue balanced fertilization and routine weekly field walks.");
    }

    return {
      overall_level: level,
      overall_color: color,
      headline: headline,
      summary: summary,
      risks: [
        { category: "Fungal Blight & Spot", score: fungalScore, level: fungalScore >= 75 ? "CRITICAL" : fungalScore >= 50 ? "MODERATE" : "LOW", color: fungalScore >= 75 ? "#ef4444" : fungalScore >= 50 ? "#f59e0b" : "#10b981", target_diseases: ["Late Blight", "Early Blight", "Apple Scab", "Rice Blast"], action: fungalScore >= 50 ? "Monitor fields daily" : "Routine scouting" },
        { category: "Rust & Powdery Mildew", score: rustScore, level: rustScore >= 75 ? "CRITICAL" : rustScore >= 50 ? "MODERATE" : "LOW", color: rustScore >= 75 ? "#ef4444" : rustScore >= 50 ? "#f59e0b" : "#10b981", target_diseases: ["Corn Rust", "Cedar Apple Rust"], action: rustScore >= 50 ? "Inspect under leaf surface" : "Routine scouting" },
        { category: "Insect Pests & Whiteflies", score: pestScore, level: pestScore >= 75 ? "CRITICAL" : pestScore >= 50 ? "MODERATE" : "LOW", color: pestScore >= 75 ? "#ef4444" : pestScore >= 50 ? "#f59e0b" : "#10b981", target_diseases: ["Whitefly", "Aphids", "Thrips"], action: pestScore >= 50 ? "Deploy sticky traps" : "Routine monitoring" }
      ],
      advisory_checklist: checklist
    };
  }

  // Helper to persist scans locally
  function saveLocalScan(scan) {
    try {
      const history = JSON.parse(localStorage.getItem("cropguard_scans") || "[]");
      history.unshift({
        crop: scan.crop,
        disease: scan.disease,
        severity: scan.severity,
        confidence: scan.confidence || 0.95,
        affected_area_pct: scan.affected_area_pct || 0,
        urgency: scan.urgency || "Act within 3 days",
        recommendation: scan.summary || "Routine inspection",
        created_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });
      localStorage.setItem("cropguard_scans", JSON.stringify(history.slice(0, 30)));
    } catch (e) {}
  }

  // 9. Scan History Loader
  async function loadHistory() {
    if (!elements.historyGrid) return;
    elements.historyGrid.innerHTML = "<p style='color:var(--text-muted);'>Loading past scans...</p>";

    try {
      const resp = await fetch(`${API_BASE}/api/history?limit=30`);
      if (resp.ok) {
        const data = await resp.json();
        if (data.status === "success" && data.scans && data.scans.length > 0) {
          renderHistoryCards(data.scans);
          return;
        }
      }
    } catch (e) {
      console.warn("History API unreachable, loading local storage history:", e);
    }

    const localScans = JSON.parse(localStorage.getItem("cropguard_scans") || "[]");
    if (localScans.length > 0) {
      renderHistoryCards(localScans);
    } else {
      elements.historyGrid.innerHTML = `<p style='color:var(--text-muted);'>${t('noHistory')}</p>`;
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
