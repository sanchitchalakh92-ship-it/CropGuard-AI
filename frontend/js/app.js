/**
 * CropGuard AI - Main Frontend Controller
 * ---------------------------------------------------------
 * Features:
 * - Leaf scanning
 * - AI backend connection
 * - Sample leaves
 * - Disease results
 * - Voice read-aloud compatibility
 * - Crop Doctor
 * - Weather Risk Radar
 * - Complete scan history
 * - Improving / Stable / Worsening detection
 * ---------------------------------------------------------
 */

document.addEventListener("DOMContentLoaded", () => {

  // =========================================================
  // 1. API BASE CONFIGURATION
  // =========================================================

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

    return (
      localStorage.getItem("cropguard_api_base") ||
      window.CROPGUARD_API_BASE ||
      ""
    );
  };

  let API_BASE = getInitialApiBase();

  // =========================================================
  // 2. SERVER STATUS ELEMENTS
  // =========================================================

  const serverStatusBtn = document.getElementById("serverStatusBtn");
  const serverStatusText = document.getElementById("serverStatusText");
  const serverModal = document.getElementById("serverModal");
  const closeServerModalBtn =
    document.getElementById("closeServerModalBtn");
  const serverUrlInput = document.getElementById("serverUrlInput");
  const testServerBtn = document.getElementById("testServerBtn");
  const saveServerBtn = document.getElementById("saveServerBtn");
  const serverPingResult =
    document.getElementById("serverPingResult");

  let backendOnline = false;

  function updateServerStatusUI(online, customMessage) {
    if (!serverStatusBtn || !serverStatusText) return;

    if (online) {
      serverStatusBtn.className = "server-status-btn online";
      serverStatusText.textContent =
        customMessage || "AI Server Online";

      serverStatusBtn.title =
        `Connected to ${API_BASE || "current origin"} — Click to edit`;
    } else {
      serverStatusBtn.className =
        "server-status-btn offline";

      serverStatusText.textContent =
        customMessage || "AI Server Offline";

      serverStatusBtn.title =
        "AI Server Disconnected — Click to configure";
    }
  }

  async function pingServer(targetUrl) {

    const base =
      targetUrl !== undefined
        ? targetUrl.trim().replace(/\/+$/, "")
        : API_BASE;

    try {

      const controller = new AbortController();

      const timeoutId = setTimeout(
        () => controller.abort(),
        4000
      );

      const resp = await fetch(
        `${base}/api/health`,
        {
          signal: controller.signal,
          headers: {
            "bypass-tunnel-reminder": "true"
          }
        }
      );

      clearTimeout(timeoutId);

      if (resp.ok) {
        const data = await resp.json();

        return {
          ok: true,
          data
        };
      }

    } catch (err) {}

    return {
      ok: false
    };
  }

  async function checkBackendHealth() {

    updateServerStatusUI(
      false,
      "Checking Server..."
    );

    const res = await pingServer();

    backendOnline = res.ok;

    updateServerStatusUI(
      backendOnline
    );

    return backendOnline;
  }

  if (serverStatusBtn) {

    serverStatusBtn.addEventListener(
      "click",
      () => {

        if (serverUrlInput) {
          serverUrlInput.value = API_BASE;
        }

        if (serverPingResult) {
          serverPingResult.style.display = "none";
        }

        if (serverModal) {
          serverModal.classList.add("active");
        }
      }
    );
  }

  if (closeServerModalBtn) {

    closeServerModalBtn.addEventListener(
      "click",
      () => {

        if (serverModal) {
          serverModal.classList.remove("active");
        }
      }
    );
  }

  if (serverModal) {

    serverModal.addEventListener(
      "click",
      (e) => {

        if (e.target === serverModal) {
          serverModal.classList.remove("active");
        }

      }
    );
  }

  if (testServerBtn) {

    testServerBtn.addEventListener(
      "click",
      async () => {

        if (!serverPingResult || !serverUrlInput) {
          return;
        }

        serverPingResult.style.display = "block";
        serverPingResult.style.background = "#f1f5f9";
        serverPingResult.style.color = "#475569";

        serverPingResult.textContent =
          "Testing connection to server...";

        const candidateUrl =
          serverUrlInput.value.trim();

        const res =
          await pingServer(candidateUrl);

        if (res.ok) {

          serverPingResult.style.background =
            "#ecfdf5";

          serverPingResult.style.color =
            "#065f46";

          serverPingResult.textContent =
            "✅ Connected! AI Backend Gateway and PyTorch model are ready.";

        } else {

          serverPingResult.style.background =
            "#fef2f2";

          serverPingResult.style.color =
            "#991b1b";

          serverPingResult.textContent =
            "❌ Connection failed. Ensure the server or tunnel is running and accessible.";
        }
      }
    );
  }

  if (saveServerBtn) {

    saveServerBtn.addEventListener(
      "click",
      async () => {

        if (!serverUrlInput) return;

        const candidateUrl =
          serverUrlInput.value
            .trim()
            .replace(/\/+$/, "");

        API_BASE = candidateUrl;

        if (candidateUrl) {

          localStorage.setItem(
            "cropguard_api_base",
            candidateUrl
          );

        } else {

          localStorage.removeItem(
            "cropguard_api_base"
          );
        }

        if (serverModal) {
          serverModal.classList.remove("active");
        }

        showToast(
          "Backend server URL updated",
          "info"
        );

        await checkBackendHealth();
      }
    );
  }

  // =========================================================
  // 3. APPLICATION STATE
  // =========================================================

  const state = {

    selectedFile: null,

    selectedDataUrl: null,

    currentScanResult: null,

    activeTab: "scanner",

    language:
      localStorage.getItem("cropguard_lang") ||
      "en",

    sessionId:
      localStorage.getItem("cropguard_session_id") ||
      (
        "farmer_" +
        Math.random()
          .toString(36)
          .substring(2, 9)
      ),

    weatherParams: {
      temp: 26,
      humidity: 82,
      rain: 4.5
    }

  };

  localStorage.setItem(
    "cropguard_session_id",
    state.sessionId
  );

  // =========================================================
  // 4. SAMPLE LEAVES
  // =========================================================

  const DEFAULT_SAMPLES = [

    {
      filename: "tomato_early_blight.jpg",
      title: "Tomato - Early Blight",
      crop: "Tomato",
      disease: "Early Blight",
      icon: "🍅",
      url: "assets/samples/tomato_early_blight.jpg"
    },

    {
      filename: "tomato_healthy.jpg",
      title: "Tomato - Healthy Leaf",
      crop: "Tomato",
      disease: "Healthy",
      icon: "🍅",
      url: "assets/samples/tomato_healthy.jpg"
    },

    {
      filename: "potato_late_blight.jpg",
      title: "Potato - Late Blight",
      crop: "Potato",
      disease: "Late Blight",
      icon: "🥔",
      url: "assets/samples/potato_late_blight.jpg"
    },

    {
      filename: "corn_common_rust.jpg",
      title: "Corn - Common Rust",
      crop: "Corn",
      disease: "Common Rust",
      icon: "🌽",
      url: "assets/samples/corn_common_rust.jpg"
    },

    {
      filename: "apple_scab.jpg",
      title: "Apple - Apple Scab",
      crop: "Apple",
      disease: "Apple Scab",
      icon: "🍎",
      url: "assets/samples/apple_scab.jpg"
    },

    {
      filename: "rice_blast.jpg",
      title: "Rice - Leaf Blast",
      crop: "Rice",
      disease: "Rice Blast",
      icon: "🌾",
      url: "assets/samples/rice_blast.jpg"
    }

  ];

  // =========================================================
  // 5. SAMPLE DIAGNOSES
  // =========================================================

  const SAMPLE_DIAGNOSES = {

    "tomato_early_blight.jpg": {

      crop: "Tomato",

      crop_icon: "🍅",

      disease: "Early Blight",

      original_disease: "Early Blight",

      pathogen_type: "Fungal",

      confidence: 0.94,

      severity: "Medium",

      severity_badge: "warning",

      severity_color: "#f59e0b",

      affected_area_pct: 26.5,

      urgency: "Act within 48 hours",

      summary:
        "Early blight caused by Alternaria solani. Concentric target-board rings may appear on leaf tissue.",

      action_steps: [

        {
          type: "critical",
          title: "Prune Infected Foliage",
          text:
            "Remove severely infected leaves and dispose of them away from the field."
        },

        {
          type: "organic",
          title: "Organic Management",
          text:
            "Use locally recommended biological or botanical control according to the crop advisory."
        },

        {
          type: "preventive",
          title: "Improve Air Circulation",
          text:
            "Avoid prolonged leaf wetness and maintain adequate spacing."
        }

      ]

    },

    "tomato_healthy.jpg": {

      crop: "Tomato",

      crop_icon: "🍅",

      disease: "Healthy",

      original_disease: "Healthy",

      pathogen_type: "None",

      confidence: 0.98,

      severity: "Healthy",

      severity_badge: "success",

      severity_color: "#10b981",

      affected_area_pct: 0,

      urgency: "Routine maintenance",

      summary:
        "No obvious disease symptoms were detected in this demonstration image.",

      action_steps: [

        {
          type: "preventive",
          title: "Continue Monitoring",
          text:
            "Inspect leaves regularly for early signs of disease."
        },

        {
          type: "preventive",
          title: "Maintain Good Irrigation",
          text:
            "Water near the root zone and avoid unnecessary leaf wetness."
        }

      ]

    },

    "potato_late_blight.jpg": {

      crop: "Potato",

      crop_icon: "🥔",

      disease: "Late Blight",

      original_disease: "Late Blight",

      pathogen_type: "Oomycete",

      confidence: 0.96,

      severity: "High",

      severity_badge: "danger",

      severity_color: "#ef4444",

      affected_area_pct: 42,

      urgency: "Immediate Action",

      summary:
        "Late blight symptoms can spread rapidly under cool, wet and humid conditions.",

      action_steps: [

        {
          type: "critical",
          title: "Inspect the Field",
          text:
            "Check nearby plants for rapidly expanding water-soaked lesions."
        },

        {
          type: "preventive",
          title: "Reduce Leaf Wetness",
          text:
            "Avoid unnecessary overhead irrigation and improve canopy airflow."
        }

      ]

    },

    "corn_common_rust.jpg": {

      crop: "Corn",

      crop_icon: "🌽",

      disease: "Common Rust",

      original_disease: "Common Rust",

      pathogen_type: "Fungal",

      confidence: 0.91,

      severity: "Medium",

      severity_badge: "warning",

      severity_color: "#f59e0b",

      affected_area_pct: 22,

      urgency: "Act within 3-4 days",

      summary:
        "Common rust produces characteristic rust-colored pustules on corn leaves.",

      action_steps: [

        {
          type: "preventive",
          title: "Monitor New Leaves",
          text:
            "Regularly inspect leaves for increasing rust pustules."
        },

        {
          type: "preventive",
          title: "Maintain Field Airflow",
          text:
            "Avoid excessively dense crop conditions where possible."
        }

      ]

    },

    "apple_scab.jpg": {

      crop: "Apple",

      crop_icon: "🍎",

      disease: "Apple Scab",

      original_disease: "Apple Scab",

      pathogen_type: "Fungal",

      confidence: 0.93,

      severity: "Medium",

      severity_badge: "warning",

      severity_color: "#f59e0b",

      affected_area_pct: 18.5,

      urgency: "Act within 3 days",

      summary:
        "Apple scab can cause olive-green to dark lesions on leaves and fruit.",

      action_steps: [

        {
          type: "preventive",
          title: "Orchard Sanitation",
          text:
            "Remove or manage fallen infected leaves to reduce disease carryover."
        },

        {
          type: "preventive",
          title: "Monitor New Growth",
          text:
            "Inspect young leaves after periods of wet weather."
        }

      ]

    },

    "rice_blast.jpg": {

      crop: "Rice",

      crop_icon: "🌾",

      disease: "Rice Blast",

      original_disease: "Rice Blast",

      pathogen_type: "Fungal",

      confidence: 0.95,

      severity: "High",

      severity_badge: "danger",

      severity_color: "#ef4444",

      affected_area_pct: 35,

      urgency: "Immediate Action",

      summary:
        "Rice blast can produce spindle-shaped lesions and spread rapidly under favorable conditions.",

      action_steps: [

        {
          type: "critical",
          title: "Inspect the Crop",
          text:
            "Check surrounding plants for similar lesions."
        },

        {
          type: "preventive",
          title: "Balanced Nutrition",
          text:
            "Avoid excessive nitrogen and follow local crop nutrition recommendations."
        }

      ]

    }

  };

  // =========================================================
  // 6. DOM ELEMENTS
  // =========================================================

  const elements = {

    langSelect:
      document.getElementById("langSelect"),

    navBtns:
      document.querySelectorAll(".nav-btn"),

    tabPanes:
      document.querySelectorAll(".tab-pane"),

    dropzone:
      document.getElementById("dropzone"),

    fileInput:
      document.getElementById("fileInput"),

    cameraInput:
      document.getElementById("cameraInput"),

    btnPickFile:
      document.getElementById("btnPickFile"),

    btnCamera:
      document.getElementById("btnCamera"),

    samplesContainer:
      document.getElementById("samplesContainer"),

    emptyState:
      document.getElementById("emptyState"),

    loadingState:
      document.getElementById("loadingState"),

    resultsContent:
      document.getElementById("resultsContent"),

    diagnosisImg:
      document.getElementById("diagnosisImg"),

    cropTag:
      document.getElementById("cropTag"),

    diseaseTitle:
      document.getElementById("diseaseTitle"),

    severityBadge:
      document.getElementById("severityBadge"),

    urgencyBadge:
      document.getElementById("urgencyBadge"),

    affectedPctVal:
      document.getElementById("affectedPctVal"),

    affectedFill:
      document.getElementById("affectedFill"),

    confidenceVal:
      document.getElementById("confidenceVal"),

    confidenceFill:
      document.getElementById("confidenceFill"),

    speechBtn:
      document.getElementById("speechBtn"),

    actionStepsList:
      document.getElementById("actionStepsList"),

    btnAskDoctorForScan:
      document.getElementById("btnAskDoctorForScan"),

    chatMessages:
      document.getElementById("chatMessages"),

    chatInput:
      document.getElementById("chatInput"),

    chatSendBtn:
      document.getElementById("chatSendBtn"),

    chatChips:
      document.querySelectorAll(".chip-btn"),

    tempSlider:
      document.getElementById("tempSlider"),

    tempVal:
      document.getElementById("tempVal"),

    humiditySlider:
      document.getElementById("humiditySlider"),

    humidityVal:
      document.getElementById("humidityVal"),

    rainSlider:
      document.getElementById("rainSlider"),

    rainVal:
      document.getElementById("rainVal"),

    weatherOverallBadge:
      document.getElementById("weatherOverallBadge"),

    weatherHeadline:
      document.getElementById("weatherHeadline"),

    weatherSummary:
      document.getElementById("weatherSummary"),

    riskCardsContainer:
      document.getElementById("riskCardsContainer"),

    weatherChecklist:
      document.getElementById("weatherChecklist"),

    historyGrid:
      document.getElementById("historyGrid"),

    refreshHistoryBtn:
      document.getElementById("refreshHistoryBtn"),

    toastContainer:
      document.getElementById("toastContainer"),

    diseaseSummary:
      document.getElementById("diseaseSummary"),

    treatmentList:
      document.getElementById("treatmentList")

  };

  // =========================================================
  // 7. LANGUAGE
  // =========================================================

  if (elements.langSelect) {

    elements.langSelect.value =
      state.language;

    if (typeof setLanguage === "function") {
      setLanguage(state.language);
    }

    elements.langSelect.addEventListener(
      "change",
      (e) => {

        state.language =
          e.target.value;

        localStorage.setItem(
          "cropguard_lang",
          state.language
        );

        if (typeof setLanguage === "function") {
          setLanguage(state.language);
        }

        showToast(
          `Language set to ${e.target.options[e.target.selectedIndex].text}`
        );

        if (state.currentScanResult) {
          refreshCurrentRecommendation();
        }

      }
    );
  }

  // =========================================================
  // 8. TAB NAVIGATION
  // =========================================================

  elements.navBtns.forEach(btn => {

    btn.addEventListener(
      "click",
      () => {

        const targetTab =
          btn.getAttribute("data-tab");

        switchTab(targetTab);

      }
    );

  });

  function switchTab(tabId) {

    state.activeTab = tabId;

    elements.navBtns.forEach(btn => {

      btn.classList.toggle(
        "active",
        btn.getAttribute("data-tab") === tabId
      );

    });

    elements.tabPanes.forEach(pane => {

      pane.classList.toggle(
        "active",
        pane.id === `tab-${tabId}`
      );

    });

    if (tabId === "history") {
      loadHistory();
    }

    if (tabId === "weather") {
      updateWeatherRadar();
    }

  }

  // =========================================================
  // 9. CAMERA / UPLOAD
  // =========================================================

  let uploader = null;

  if (typeof CameraUploader !== "undefined") {

    uploader = new CameraUploader({

      dropzone: elements.dropzone,

      fileInput: elements.fileInput,

      cameraInput: elements.cameraInput,

      onImageSelected: ({
        file,
        dataUrl
      }) => {

        state.selectedFile = file;

        state.selectedDataUrl =
          dataUrl;

        submitScan(
          file,
          dataUrl
        );

      }

    });

  }

  if (elements.btnPickFile) {

    elements.btnPickFile.addEventListener(
      "click",
      () => {

        if (elements.fileInput) {
          elements.fileInput.click();
        }

      }
    );

  }

  if (elements.btnCamera) {

    elements.btnCamera.addEventListener(
      "click",
      () => {

        if (elements.cameraInput) {
          elements.cameraInput.click();
        }

      }
    );

  }

  // =========================================================
  // 10. SERVER + SAMPLES
  // =========================================================

  checkBackendHealth();

  loadSampleLeaves();

  async function loadSampleLeaves() {

    try {

      const resp =
        await fetch(
          `${API_BASE}/api/samples`
        );

      if (resp.ok) {

        const data =
          await resp.json();

        if (
          data.status === "success" &&
          data.samples &&
          data.samples.length > 0
        ) {

          renderSampleLeaves(
            data.samples
          );

          return;
        }

      }

    } catch (e) {

      console.warn(
        "API samples not reachable:",
        e
      );

    }

    renderSampleLeaves(
      DEFAULT_SAMPLES
    );

  }

  function renderSampleLeaves(samples) {

    if (!elements.samplesContainer) {
      return;
    }

    elements.samplesContainer.innerHTML = "";

    samples.forEach(sample => {

      const card =
        document.createElement("div");

      card.className =
        "sample-card";

      card.innerHTML = `

        <div class="sample-thumb-box">

          <img
            src="${sample.url}"
            alt="${sample.title}"
          >

        </div>

        <span>
          ${sample.icon || "🌱"}
          ${sample.crop || ""}
        </span>

        <span
          style="
            color:var(--text-muted);
            font-size:0.68rem;
          "
        >
          ${sample.disease || ""}
        </span>

      `;

      card.addEventListener(
        "click",
        async () => {

          if (!uploader) {
            showToast(
              "Camera uploader is unavailable.",
              "error"
            );

            return;
          }

          try {

            showToast(
              `Loading sample: ${sample.title}...`
            );

            const loaded =
              await uploader.loadSampleImageAsFile(
                sample.url,
                sample.filename
              );

            state.selectedFile =
              loaded.file;

            state.selectedDataUrl =
              loaded.dataUrl;

            submitScan(
              loaded.file,
              loaded.dataUrl
            );

          } catch (error) {

            console.error(error);

            showToast(
              "Could not load sample image.",
              "error"
            );

          }

        }
      );

      elements.samplesContainer.appendChild(
        card
      );

    });

  }

  // =========================================================
  // 11. SUBMIT SCAN
  // =========================================================

  async function submitScan(
    file,
    dataUrl
  ) {

    if (!file) {
      return;
    }

    if (elements.emptyState) {
      elements.emptyState.style.display =
        "none";
    }

    if (elements.resultsContent) {
      elements.resultsContent.style.display =
        "none";
    }

    if (elements.loadingState) {
      elements.loadingState.style.display =
        "flex";
    }

    try {

      if (
        typeof voiceAssistant !== "undefined" &&
        voiceAssistant.stop
      ) {
        voiceAssistant.stop();
      }

    } catch (e) {}

    const matchKey =
      Object.keys(SAMPLE_DIAGNOSES).find(
        key => {

          const fileName =
            String(file.name || "")
              .toLowerCase();

          const sampleName =
            key
              .replace(".jpg", "")
              .replace(/_/g, "");

          return fileName.includes(
            sampleName
          );

        }
      );

    const formData =
      new FormData();

    formData.append(
      "image",
      file
    );

    formData.append(
      "lang",
      state.language
    );

    formData.append(
      "session_id",
      state.sessionId
    );

    let result = null;

    let backendErrorMsg = null;

    // -------------------------------------------------------
    // Primary backend request
    // -------------------------------------------------------

    try {

      const controller =
        new AbortController();

      const timeoutId =
        setTimeout(
          () => controller.abort(),
          12000
        );

      const response =
        await fetch(
          `${API_BASE}/api/upload`,
          {
            method: "POST",

            headers: {
              "bypass-tunnel-reminder":
                "true"
            },

            signal:
              controller.signal,

            body:
              formData
          }
        );

      clearTimeout(
        timeoutId
      );

      if (response.ok) {

        result =
          await response.json();

        backendOnline = true;

        updateServerStatusUI(
          true
        );

      } else {

        const errJson =
          await response
            .json()
            .catch(() => null);

        backendErrorMsg =
          (
            errJson &&
            errJson.message
          ) ||
          `Server returned status ${response.status}`;

      }

    } catch (err) {

      console.warn(
        "Backend connection failed:",
        err
      );

      backendOnline = false;

      updateServerStatusUI(
        false
      );

      backendErrorMsg =
        "AI backend server is unreachable from this device.";

    }

    // -------------------------------------------------------
    // Backend diagnosis
    // -------------------------------------------------------

    if (
      result &&
      (
        result.status === "success" ||
        result.status === "low_confidence" ||
        result.crop
      )
    ) {

      if (result.status !== "low_confidence") {
        result.status = "success";
      }

      if (elements.loadingState) {
        elements.loadingState.style.display =
          "none";
      }

      state.currentScanResult =
        result;

      saveLocalScan(
        result
      );

      renderResults(
        result,
        dataUrl
      );

      showToast(
        `Diagnosed: ${result.crop} - ${result.disease}!`,
        "success"
      );

      return;
    }

    // -------------------------------------------------------
    // Built-in demo sample
    // -------------------------------------------------------

    if (
      matchKey &&
      SAMPLE_DIAGNOSES[matchKey]
    ) {

      result = {
        status: "success",
        ...SAMPLE_DIAGNOSES[matchKey]
      };

      if (elements.loadingState) {
        elements.loadingState.style.display =
          "none";
      }

      state.currentScanResult =
        result;

      saveLocalScan(
        result
      );

      renderResults(
        result,
        dataUrl
      );

      showToast(
        `Sample Leaf: ${result.crop} - ${result.disease}`,
        "info"
      );

      return;
    }

    // -------------------------------------------------------
    // Backend unavailable
    // -------------------------------------------------------

    if (elements.loadingState) {
      elements.loadingState.style.display =
        "none";
    }

    if (elements.emptyState) {
      elements.emptyState.style.display =
        "none";
    }

    if (elements.resultsContent) {
      elements.resultsContent.style.display =
        "block";
    }

    renderBackendOfflineNotice(
      dataUrl,
      backendErrorMsg
    );

  }

  // =========================================================
  // 12. BACKEND OFFLINE NOTICE
  // =========================================================

  function renderBackendOfflineNotice(
    dataUrl,
    errorDetail
  ) {

    if (elements.diagnosisImg) {
      elements.diagnosisImg.src =
        dataUrl ||
        "/assets/samples/tomato_early_blight.jpg";
    }

    if (elements.cropTag) {
      elements.cropTag.innerHTML =
        "⚠️ Server Disconnected";
    }

    if (elements.diseaseTitle) {
      elements.diseaseTitle.textContent =
        "AI Model Unreachable";
    }

    if (elements.severityBadge) {

      elements.severityBadge.className =
        "badge badge-danger";

      elements.severityBadge.innerHTML =
        "⚠️ Offline";
    }

    if (elements.urgencyBadge) {

      elements.urgencyBadge.innerHTML =
        "⏱️ Connect Backend";
    }

    if (elements.affectedPctVal) {
      elements.affectedPctVal.textContent =
        "--%";
    }

    if (elements.affectedFill) {
      elements.affectedFill.style.width =
        "0%";
    }

    if (elements.confidenceVal) {
      elements.confidenceVal.textContent =
        "--%";
    }

    if (elements.confidenceFill) {
      elements.confidenceFill.style.width =
        "0%";
    }

    if (elements.diseaseSummary) {

      elements.diseaseSummary.innerHTML = `

        <div
          style="
            background:#fef2f2;
            border:1px solid #fecaca;
            border-radius:var(--radius-sm);
            padding:.75rem;
            color:#991b1b;
            margin-bottom:.75rem;
          "
        >

          <b>
            ⚠️ AI Diagnostic Server Not Connected
          </b>

          <br>

          <span
            style="
              font-size:.85rem;
            "
          >
            CropGuard requires a live
            connection to the PyTorch AI
            backend to diagnose custom photos.
          </span>

        </div>

        ${
          errorDetail
            ? `<p>Status: <code>${escapeHtml(errorDetail)}</code></p>`
            : ""
        }

      `;

    }

    if (elements.treatmentList) {

      elements.treatmentList.innerHTML = `

        <div
          class="action-card preventive"
          style="opacity:.85;"
        >

          <div class="action-card-header">

            <span class="action-card-icon">
              💡
            </span>

            <h4 class="action-card-title">
              How to connect:
            </h4>

          </div>

          <p
            class="action-card-body"
            style="
              font-size:.82rem;
              line-height:1.5;
            "
          >

            1. Start CropGuard backend.<br>

            2. Tap the
            <b>AI Server Offline</b>
            button.<br>

            3. Enter your backend URL.<br>

            4. Tap
            <b>Save & Connect</b>.

          </p>

        </div>

      `;

    }

    showToast(
      "AI Server unreachable. Connect the backend.",
      "error"
    );

  }

  // =========================================================
  // 13. RENDER RESULTS
  // =========================================================

  function renderResults(
    res,
    dataUrl
  ) {

    if (!res) {
      return;
    }

    if (elements.resultsContent) {
      elements.resultsContent.style.display =
        "block";
    }

    if (elements.emptyState) {
      elements.emptyState.style.display =
        "none";
    }

    if (elements.diagnosisImg) {

      elements.diagnosisImg.src =
        dataUrl ||
        res.image_url ||
        "/assets/samples/tomato_early_blight.jpg";

    }

    if (elements.cropTag) {

      elements.cropTag.innerHTML =
        `${res.crop_icon || "🌱"} ${escapeHtml(res.crop || "Unknown Crop")}`;

    }

    if (elements.diseaseTitle) {

      elements.diseaseTitle.textContent =
        res.disease ||
        "Unknown Disease";

    }

    // -------------------------------------------------------
    // Severity
    // -------------------------------------------------------

    if (elements.severityBadge) {

      const severity =
        res.severity ||
        "Medium";

      const sevBadgeClass =
        `badge-${severity.toLowerCase()}`;

      elements.severityBadge.className =
        `badge ${sevBadgeClass} badge-pulse`;

      const severityLabel =
        typeof t === "function"
          ? t("severityLabel")
          : "Severity";

      elements.severityBadge.innerHTML =
        `⚠️ ${severityLabel}: ${escapeHtml(severity)}`;

    }

    // -------------------------------------------------------
    // Urgency
    // -------------------------------------------------------

    if (elements.urgencyBadge) {

      elements.urgencyBadge.innerHTML =
        `⏱️ ${escapeHtml(
          res.urgency ||
          "Act within 3 days"
        )}`;

    }

    // -------------------------------------------------------
    // Affected area
    // -------------------------------------------------------

    const affectedPct =
      Number(
        res.affected_area_pct || 0
      );

    if (elements.affectedPctVal) {

      elements.affectedPctVal.textContent =
        `${affectedPct.toFixed(1)}%`;

    }

    if (elements.affectedFill) {

      elements.affectedFill.style.width =
        `${Math.min(
          100,
          Math.max(
            0,
            affectedPct
          )
        )}%`;

      elements.affectedFill.style.background =
        res.severity_color ||
        "#f59e0b";

    }

    // -------------------------------------------------------
    // Confidence
    // -------------------------------------------------------

    const confidence =
      Number(
        res.confidence || 0
      );

    const confidencePct =
      Math.round(
        confidence * 100
      );

    if (elements.confidenceVal) {

      elements.confidenceVal.textContent =
        `${confidencePct}%`;

    }

    if (elements.confidenceFill) {

      elements.confidenceFill.style.width =
        `${Math.min(
          100,
          Math.max(
            0,
            confidencePct
          )
        )}%`;

      elements.confidenceFill.style.background =
        "#10b981";

    }

    // -------------------------------------------------------
    // Disease summary
    // -------------------------------------------------------

    if (elements.diseaseSummary) {

      elements.diseaseSummary.innerHTML = `

        <p>
          ${
            escapeHtml(
              res.summary ||
              res.description ||
              "No detailed summary available."
            )
          }
        </p>

        ${
          res.pathogen_type
            ? `
              <p style="margin-top:.5rem;">
                <strong>Pathogen:</strong>
                ${escapeHtml(res.pathogen_type)}
              </p>
            `
            : ""
        }

      `;

    }

    // -------------------------------------------------------
    // Action steps
    // -------------------------------------------------------

    if (elements.actionStepsList) {

      elements.actionStepsList.innerHTML =
        "";

      if (
        res.action_steps &&
        res.action_steps.length > 0
      ) {

        res.action_steps.forEach(
          step => {

            const stepCard =
              document.createElement(
                "div"
              );

            stepCard.className =
              "action-step-card";

            let iconSymbol = "🛡️";

            if (step.type === "critical") {
              iconSymbol = "🚨";
            } else if (
              step.type === "organic"
            ) {
              iconSymbol = "🌿";
            } else if (
              step.type === "chemical"
            ) {
              iconSymbol = "🧪";
            }

            stepCard.innerHTML = `

              <div
                class="step-icon ${escapeHtml(step.type || "preventive")}"
              >
                ${iconSymbol}
              </div>

              <div class="step-body">

                <h5>
                  ${escapeHtml(
                    step.title ||
                    "Recommended Action"
                  )}
                </h5>

                <p>
                  ${escapeHtml(
                    step.text ||
                    ""
                  )}
                </p>

              </div>

            `;

            elements.actionStepsList.appendChild(
              stepCard
            );

          }
        );

      } else {

        const defaultStep =
          document.createElement(
            "div"
          );

        defaultStep.className =
          "action-step-card";

        defaultStep.innerHTML = `

          <div class="step-icon preventive">
            🛡️
          </div>

          <div class="step-body">

            <h5>
              Monitor the Crop
            </h5>

            <p>
              Continue monitoring the affected
              plant and rescan if symptoms change.
            </p>

          </div>

        `;

        elements.actionStepsList.appendChild(
          defaultStep
        );

      }

    }

    // -------------------------------------------------------
    // Additional advisory information
    // -------------------------------------------------------

    if (elements.treatmentList) {

      const organic =
        res.organic_control || "";

      const chemical =
        res.chemical_control || "";

      const prevention =
        res.prevention_tips || "";

      elements.treatmentList.innerHTML = `

        ${
          organic
            ? `
              <div
                class="action-card organic"
                style="margin-bottom:.75rem;"
              >

                <div class="action-card-header">

                  <span class="action-card-icon">
                    🌿
                  </span>

                  <h4 class="action-card-title">
                    Organic Control
                  </h4>

                </div>

                <p class="action-card-body">
                  ${escapeHtml(organic)}
                </p>

              </div>
            `
            : ""
        }

        ${
          chemical
            ? `
              <div
                class="action-card chemical"
                style="margin-bottom:.75rem;"
              >

                <div class="action-card-header">

                  <span class="action-card-icon">
                    🧪
                  </span>

                  <h4 class="action-card-title">
                    Chemical Control
                  </h4>

                </div>

                <p class="action-card-body">
                  ${escapeHtml(chemical)}
                </p>

              </div>
            `
            : ""
        }

        ${
          prevention
            ? `
              <div
                class="action-card preventive"
              >

                <div class="action-card-header">

                  <span class="action-card-icon">
                    🛡️
                  </span>

                  <h4 class="action-card-title">
                    Prevention
                  </h4>

                </div>

                <p class="action-card-body">
                  ${escapeHtml(prevention)}
                </p>

              </div>
            `
            : ""
        }

      `;

    }

    // =======================================================
    // VOICE READ-ALOUD
    // =======================================================

    if (elements.speechBtn) {

      elements.speechBtn.onclick =
        () => {

          try {

            if (
              typeof voiceAssistant ===
              "undefined"
            ) {
              showToast(
                "Voice assistant is unavailable.",
                "error"
              );

              return;
            }

            if (
              voiceAssistant.isSpeaking
            ) {

              voiceAssistant.stop();

              elements.speechBtn
                .classList
                .remove("playing");

              elements.speechBtn.innerHTML =
                `🔊 ${
                  typeof t === "function"
                    ? t("btnListen")
                    : "Listen"
                }`;

            } else {

              const textToRead =
                `${res.crop || ""}. ` +
                `${res.disease || ""}. ` +
                `Severity: ${
                  res.severity || ""
                }. ` +
                `${res.summary || ""}. ` +
                `${res.organic_control || ""}.`;

              voiceAssistant.speak(

                textToRead,

                state.language,

                () => {

                  elements.speechBtn
                    .classList
                    .add("playing");

                  elements.speechBtn.innerHTML =
                    "⏹️ Stop";

                },

                () => {

                  elements.speechBtn
                    .classList
                    .remove("playing");

                  elements.speechBtn.innerHTML =
                    `🔊 ${
                      typeof t === "function"
                        ? t("btnListen")
                        : "Listen"
                    }`;

                }

              );

            }

          } catch (error) {

            console.error(
              "Voice error:",
              error
            );

          }

        };

    }

    // =======================================================
    // ASK CROP DOCTOR
    // =======================================================

    if (elements.btnAskDoctorForScan) {

      elements.btnAskDoctorForScan.onclick =
        () => {

          switchTab(
            "doctor"
          );

          sendChatMessage(

            `Tell me more about ${res.crop || ""} ${res.disease || ""}.`,

            res.crop,

            res.original_disease ||
            res.disease

          );

        };

    }

  }

  // =========================================================
  // 14. REFRESH RECOMMENDATION
  // =========================================================

  async function refreshCurrentRecommendation() {

    if (!state.currentScanResult) {
      return;
    }

    const crop =
      state.currentScanResult.crop;

    const disease =
      state.currentScanResult.original_disease ||
      state.currentScanResult.disease;

    const severity =
      state.currentScanResult.severity;

    try {

      const resp =
        await fetch(

          `${API_BASE}/api/recommendation` +

          `?crop=${encodeURIComponent(crop)}` +

          `&disease=${encodeURIComponent(disease)}` +

          `&severity=${encodeURIComponent(severity || "")}` +

          `&lang=${encodeURIComponent(state.language)}`

        );

      if (resp.ok) {

        const data =
          await resp.json();

        if (
          data.status === "success" &&
          data.advisory
        ) {

          state.currentScanResult = {

            ...state.currentScanResult,

            ...data.advisory

          };

          renderResults(
            state.currentScanResult,
            state.selectedDataUrl
          );

        }

      }

    } catch (e) {

      console.warn(
        "Could not refresh recommendation:",
        e
      );

    }

  }

  // =========================================================
  // 15. CROP DOCTOR CHAT
  // =========================================================

  if (
    elements.chatSendBtn &&
    elements.chatInput
  ) {

    elements.chatSendBtn.addEventListener(
      "click",
      () => {

        const query =
          elements.chatInput.value.trim();

        if (query) {

          sendChatMessage(
            query
          );

          elements.chatInput.value =
            "";

        }

      }
    );

    elements.chatInput.addEventListener(
      "keypress",
      (e) => {

        if (e.key === "Enter") {

          elements.chatSendBtn.click();

        }

      }
    );

  }

  elements.chatChips.forEach(
    chip => {

      chip.addEventListener(
        "click",
        () => {

          const query =
            chip.textContent.trim();

          sendChatMessage(
            query
          );

        }
      );

    }
  );

  async function sendChatMessage(
    query,
    cropHint = null,
    diseaseHint = null
  ) {

    appendChatBubble(
      "user",
      escapeHtml(query)
    );

    const typingId =
      appendChatBubble(
        "bot",
        "🌱 <i>Crop Doctor is analyzing your query...</i>"
      );

    let botAnswer = null;

    try {

      const resp =
        await fetch(
          `${API_BASE}/api/chat`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json"
            },

            body: JSON.stringify({

              query: query,

              crop: cropHint,

              disease: diseaseHint,

              lang: state.language

            })

          }
        );

      if (resp.ok) {

        const data =
          await resp.json();

        if (
          data.status === "success" &&
          data.response &&
          data.response.answer
        ) {

          botAnswer =
            data.response.answer;

        }

      }

    } catch (e) {

      console.warn(
        "Chat API unreachable:",
        e
      );

    }

    const typingEl =
      document.getElementById(
        typingId
      );

    if (typingEl) {
      typingEl.remove();
    }

    if (!botAnswer) {

      botAnswer =
        generateLocalDoctorAnswer(
          query,
          cropHint,
          diseaseHint
        );

    }

    const formattedAnswer =
      escapeHtml(
        botAnswer
      ).replace(
        /\n/g,
        "<br>"
      );

    appendChatBubble(
      "bot",
      formattedAnswer
    );

  }

  function generateLocalDoctorAnswer(
    query,
    cropHint,
    diseaseHint
  ) {

    const q =
      String(query)
        .toLowerCase();

    if (
      q.includes("organic") ||
      q.includes("neem") ||
      q.includes("natural") ||
      q.includes("home remedy")
    ) {

      return `
🌿 Organic Management:

• Remove severely infected leaves.
• Keep the field clean.
• Avoid prolonged leaf wetness.
• Use locally recommended biological or botanical controls.
• Follow crop-specific agricultural guidance.
      `.trim();

    }

    if (
      q.includes("chemical") ||
      q.includes("spray") ||
      q.includes("fungicide") ||
      q.includes("pesticide")
    ) {

      return `
🧪 Chemical Management:

Use only products registered for the identified crop and disease. Follow the product label, local agricultural recommendations, protective-equipment requirements and pre-harvest interval.

Do not apply a pesticide only because a disease name is suspected from a low-confidence image.
      `.trim();

    }

    if (
      diseaseHint
    ) {

      return `
🔍 Crop Doctor:

The current scan is associated with ${cropHint || "the crop"} and ${diseaseHint}.

For better diagnosis, use a clear close-up image of the affected leaf and compare future scans of the same crop and disease in Scan History.
      `.trim();

    }

    return `
🌱 Crop Doctor:

For best results, upload a clear photo of the affected leaf in the Scanner tab. CropGuard will use the AI model to identify the crop and disease and provide an advisory.
    `.trim();

  }

  function appendChatBubble(
    sender,
    htmlContent
  ) {

    if (!elements.chatMessages) {
      return null;
    }

    const msgId =
      "msg_" +
      Math.random()
        .toString(36)
        .substring(2, 9);

    const msgDiv =
      document.createElement(
        "div"
      );

    msgDiv.id =
      msgId;

    msgDiv.className =
      `chat-msg ${sender}`;

    const bubble =
      document.createElement(
        "div"
      );

    bubble.className =
      "chat-bubble";

    bubble.innerHTML =
      htmlContent;

    msgDiv.appendChild(
      bubble
    );

    elements.chatMessages.appendChild(
      msgDiv
    );

    elements.chatMessages.scrollTop =
      elements.chatMessages.scrollHeight;

    return msgId;

  }

  // =========================================================
  // 16. WEATHER RADAR
  // =========================================================

  function initWeatherSliders() {

    const update =
      () => {

        if (
          elements.tempSlider
        ) {

          state.weatherParams.temp =
            parseFloat(
              elements.tempSlider.value
            );

        }

        if (
          elements.humiditySlider
        ) {

          state.weatherParams.humidity =
            parseFloat(
              elements.humiditySlider.value
            );

        }

        if (
          elements.rainSlider
        ) {

          state.weatherParams.rain =
            parseFloat(
              elements.rainSlider.value
            );

        }

        if (elements.tempVal) {

          elements.tempVal.textContent =
            `${state.weatherParams.temp}°C`;

        }

        if (elements.humidityVal) {

          elements.humidityVal.textContent =
            `${state.weatherParams.humidity}%`;

        }

        if (elements.rainVal) {

          elements.rainVal.textContent =
            `${state.weatherParams.rain} mm`;

        }

        updateWeatherRadar();

      };

    if (elements.tempSlider) {
      elements.tempSlider.addEventListener(
        "input",
        update
      );
    }

    if (elements.humiditySlider) {
      elements.humiditySlider.addEventListener(
        "input",
        update
      );
    }

    if (elements.rainSlider) {
      elements.rainSlider.addEventListener(
        "input",
        update
      );
    }

  }

  initWeatherSliders();

  async function updateWeatherRadar() {

    try {

      const url =
        `${API_BASE}/api/weather-risk` +

        `?temp=${state.weatherParams.temp}` +

        `&humidity=${state.weatherParams.humidity}` +

        `&rain=${state.weatherParams.rain}`;

      const resp =
        await fetch(url);

      if (resp.ok) {

        const data =
          await resp.json();

        if (
          data.status === "success" &&
          data.risk_radar
        ) {

          renderWeatherRadar(
            data.risk_radar
          );

          return;

        }

      }

    } catch (e) {

      console.warn(
        "Weather API unreachable:",
        e
      );

    }

    const localRadar =
      computeLocalWeatherRisk(
        state.weatherParams.temp,
        state.weatherParams.humidity,
        state.weatherParams.rain
      );

    renderWeatherRadar(
      localRadar
    );

  }

  function computeLocalWeatherRisk(
    temp,
    humidity,
    rain
  ) {

    let fungalScore = 0;

    if (humidity > 85) {
      fungalScore += 45;
    } else if (humidity > 70) {
      fungalScore += 30;
    } else if (humidity > 50) {
      fungalScore += 15;
    }

    if (
      temp >= 18 &&
      temp <= 27
    ) {
      fungalScore += 40;
    } else if (
      temp >= 14 &&
      temp <= 32
    ) {
      fungalScore += 25;
    } else {
      fungalScore += 10;
    }

    if (rain > 10) {
      fungalScore += 15;
    } else if (rain > 2) {
      fungalScore += 10;
    }

    fungalScore =
      Math.min(
        100,
        Math.round(fungalScore)
      );

    let rustScore = 0;

    if (
      temp >= 15 &&
      temp <= 25
    ) {
      rustScore += 45;
    } else if (
      temp >= 10 &&
      temp <= 30
    ) {
      rustScore += 25;
    }

    if (humidity > 80) {
      rustScore += 40;
    } else if (humidity > 60) {
      rustScore += 25;
    }

    if (rain > 1) {
      rustScore += 15;
    }

    rustScore =
      Math.min(
        100,
        Math.round(rustScore)
      );

    let pestScore = 0;

    if (
      temp >= 24 &&
      temp <= 34
    ) {
      pestScore += 45;
    } else if (
      temp >= 18 &&
      temp <= 36
    ) {
      pestScore += 30;
    }

    if (
      humidity >= 50 &&
      humidity <= 75
    ) {
      pestScore += 35;
    } else if (
      humidity < 50
    ) {
      pestScore += 20;
    }

    if (rain < 2) {
      pestScore += 20;
    }

    pestScore =
      Math.min(
        100,
        Math.round(pestScore)
      );

    const overallScore =
      Math.round(
        (fungalScore * 0.45) +
        (rustScore * 0.35) +
        (pestScore * 0.20)
      );

    let level =
      "Low Risk";

    let headline =
      "Favorable Weather for Crop Growth";

    let summary =
      "Current weather parameters do not strongly favor rapid fungal disease development or pest activity.";

    if (fungalScore >= 75) {

      level =
        "High Risk";

      headline =
        "High Fungal Disease Risk";

      summary =
        `Humidity (${humidity}%) and temperature (${temp}°C) may favor fungal disease development.`;

    } else if (
      pestScore >= 70
    ) {

      level =
        "Elevated Pest Risk";

      headline =
        "Elevated Insect Pest Risk";

      summary =
        `Current temperature (${temp}°C) and humidity (${humidity}%) may favor some insect pests.`;

    } else if (
      fungalScore >= 50 ||
      rustScore >= 50
    ) {

      level =
        "Moderate Alert";

      headline =
        "Moderate Disease Caution";

      summary =
        `Humidity (${humidity}%) is elevated. Inspect leaves regularly.`;

    }

    const checklist = [];

    if (fungalScore >= 50) {

      checklist.push(
        "Inspect lower and inner canopy leaves regularly."
      );

      checklist.push(
        "Avoid unnecessary leaf wetness and improve airflow."
      );

    }

    if (pestScore >= 50) {

      checklist.push(
        "Check the crop for whiteflies, aphids and thrips."
      );

      checklist.push(
        "Use appropriate integrated pest management practices."
      );

    }

    if (checklist.length === 0) {

      checklist.push(
        "Continue balanced fertilization and routine field scouting."
      );

    }

    return {

      overall_level:
        level,

      overall_color:
        overallScore >= 70
          ? "#ef4444"
          : overallScore >= 50
          ? "#f59e0b"
          : "#10b981",

      headline:
        headline,

      summary:
        summary,

      risks: [

        {
          category:
            "Fungal Disease",

          score:
            fungalScore,

          level:
            fungalScore >= 75
              ? "CRITICAL"
              : fungalScore >= 50
              ? "MODERATE"
              : "LOW",

          color:
            fungalScore >= 75
              ? "#ef4444"
              : fungalScore >= 50
              ? "#f59e0b"
              : "#10b981",

          target_diseases: [
            "Late Blight",
            "Early Blight",
            "Downy Mildew"
          ],

          action:
            fungalScore >= 50
              ? "Inspect fields frequently"
              : "Routine scouting"

        },

        {
          category:
            "Rust & Powdery Mildew",

          score:
            rustScore,

          level:
            rustScore >= 75
              ? "CRITICAL"
              : rustScore >= 50
              ? "MODERATE"
              : "LOW",

          color:
            rustScore >= 75
              ? "#ef4444"
              : rustScore >= 50
              ? "#f59e0b"
              : "#10b981",

          target_diseases: [
            "Rust",
            "Powdery Mildew"
          ],

          action:
            rustScore >= 50
              ? "Inspect leaf surfaces"
              : "Routine scouting"

        },

        {
          category:
            "Insect Pests",

          score:
            pestScore,

          level:
            pestScore >= 75
              ? "CRITICAL"
              : pestScore >= 50
              ? "MODERATE"
              : "LOW",

          color:
            pestScore >= 75
              ? "#ef4444"
              : pestScore >= 50
              ? "#f59e0b"
              : "#10b981",

          target_diseases: [
            "Whitefly",
            "Aphids",
            "Thrips"
          ],

          action:
            pestScore >= 50
              ? "Inspect plants"
              : "Routine monitoring"

        }

      ],

      advisory_checklist:
        checklist

    };

  }

  function renderWeatherRadar(
    radar
  ) {

    if (!radar) {
      return;
    }

    if (elements.weatherOverallBadge) {

      elements.weatherOverallBadge.textContent =
        radar.overall_level ||
        "Risk Unknown";

    }

    if (elements.weatherHeadline) {

      elements.weatherHeadline.textContent =
        radar.headline ||
        "Weather Risk";

    }

    if (elements.weatherSummary) {

      elements.weatherSummary.textContent =
        radar.summary ||
        "";

    }

    if (elements.riskCardsContainer) {

      elements.riskCardsContainer.innerHTML =
        "";

      (radar.risks || [])
        .forEach(
          risk => {

            const card =
              document.createElement(
                "div"
              );

            card.className =
              "risk-card";

            card.innerHTML = `

              <div>
                <strong>
                  ${escapeHtml(
                    risk.category ||
                    "Risk"
                  )}
                </strong>
              </div>

              <div
                style="
                  font-size:1.4rem;
                  font-weight:700;
                  margin:.4rem 0;
                "
              >
                ${Number(
                  risk.score || 0
                )}%
              </div>

              <div
                style="
                  font-size:.75rem;
                  color:var(--text-muted);
                "
              >
                ${escapeHtml(
                  risk.level ||
                  ""
                )}
              </div>

              <div
                style="
                  margin-top:.4rem;
                  font-size:.75rem;
                "
              >
                ${escapeHtml(
                  risk.action ||
                  ""
                )}
              </div>

            `;

            elements.riskCardsContainer.appendChild(
              card
            );

          }
        );

    }

    if (elements.weatherChecklist) {

      elements.weatherChecklist.innerHTML =
        "";

      (
        radar.advisory_checklist ||
        []
      ).forEach(
        item => {

          const li =
            document.createElement(
              "li"
            );

          li.textContent =
            item;

          elements.weatherChecklist.appendChild(
            li
          );

        }
      );

    }

  }

  // =========================================================
  // 17. LOCAL SCAN HISTORY
  // =========================================================

  function saveLocalScan(
    scan
  ) {

    try {

      const history =
        JSON.parse(
          localStorage.getItem(
            "cropguard_scans"
          ) || "[]"
        );

      history.unshift({

        id:
          scan.id ||
          `local_${Date.now()}_${Math.random()
            .toString(36)
            .substring(2, 7)}`,

        session_id:
          state.sessionId,

        crop:
          scan.crop,

        disease:
          scan.disease,

        original_disease:
          scan.original_disease ||
          scan.disease,

        severity:
          scan.severity,

        confidence:
          scan.confidence || 0,

        affected_area_pct:
          scan.affected_area_pct || 0,

        urgency:
          scan.urgency ||
          "Act within 3 days",

        recommendation:
          scan.summary ||
          scan.recommendation ||
          "Routine inspection",

        image_name:
          scan.image_name ||
          null,

        created_at:
          scan.created_at ||
          new Date().toISOString()

      });

      localStorage.setItem(
        "cropguard_scans",
        JSON.stringify(
          history.slice(0, 100)
        )
      );

    } catch (e) {

      console.warn(
        "Could not save local scan:",
        e
      );

    }

  }

  // =========================================================
  // 18. HISTORY LOADER
  // =========================================================

 async function loadHistory() {

  if (!elements.historyGrid) {
    return;
  }

  elements.historyGrid.innerHTML = `
    <p style="color:var(--text-muted);">
      Loading past scans...
    </p>
  `;

  try {

    const resp = await fetch(
      `${API_BASE}/api/history?limit=100`,
      {
        method: "GET",
        credentials: "include",
        cache: "no-store"
      }
    );

    if (resp.status === 401) {
      window.location.replace("/login.html");
      return;
    }

    if (!resp.ok) {
      throw new Error(`History API returned ${resp.status}`);
    }

    const data = await resp.json();

    if (data.status === "success") {

      /*
       * IMPORTANT:
       * The backend is the single source of truth.
       * If this farmer has zero scans, DO NOT load
       * another farmer's localStorage history.
       */

      if (Array.isArray(data.scans) && data.scans.length > 0) {

        renderHistoryCards(data.scans);

      } else {

        elements.historyGrid.innerHTML = `
          <p style="color:var(--text-muted);">
            ${
              typeof t === "function"
                ? t("noHistory")
                : "No scan history yet."
            }
          </p>
        `;

      }

      return;
    }

    throw new Error(
      data.message || "Unable to load history."
    );

  } catch (error) {

    console.error(
      "Could not load farmer-specific history:",
      error
    );

    elements.historyGrid.innerHTML = `
      <p style="color:var(--text-muted);">
        Unable to load scan history. Please try again.
      </p>
    `;
  }
}

  // =========================================================
  // 19. PROGRESS CALCULATION
  // =========================================================

  function severityRank(
    severity
  ) {

    const value =
      String(
        severity || ""
      )
        .trim()
        .toLowerCase();

    const ranks = {

      healthy: 0,

      low: 1,

      mild: 1,

      medium: 2,

      moderate: 2,

      high: 3,

      severe: 3,

      critical: 4

    };

    return (
      ranks[value] ||
      0
    );

  }

  function getPreviousScan(
    currentScan,
    allScans
  ) {

    const currentId =
      String(
        currentScan.id ||
        ""
      );

    const currentCrop =
      String(
        currentScan.crop ||
        ""
      )
        .trim()
        .toLowerCase();

    const currentDisease =
      String(
        currentScan.original_disease ||
        currentScan.disease ||
        ""
      )
        .trim()
        .toLowerCase();

    const currentTime =
      new Date(
        currentScan.created_at ||
        0
      ).getTime();

    const candidates =
      allScans

        .filter(
          scan => {

            if (
              String(
                scan.id || ""
              ) === currentId
            ) {
              return false;
            }

            const crop =
              String(
                scan.crop ||
                ""
              )
                .trim()
                .toLowerCase();

            const disease =
              String(
                scan.original_disease ||
                scan.disease ||
                ""
              )
                .trim()
                .toLowerCase();

            const time =
              new Date(
                scan.created_at ||
                0
              ).getTime();

            return (

              crop ===
                currentCrop &&

              disease ===
                currentDisease &&

              time < currentTime

            );

          }
        )

        .sort(
          (a, b) => {

            const timeA =
              new Date(
                a.created_at ||
                0
              ).getTime();

            const timeB =
              new Date(
                b.created_at ||
                0
              ).getTime();

            return (
              timeB -
              timeA
            );

          }
        );

    return (
      candidates[0] ||
      null
    );

  }

  function calculateProgress(
    currentScan,
    allScans
  ) {

    const previous =
      getPreviousScan(
        currentScan,
        allScans
      );

    if (!previous) {

      return {

        status:
          "first_scan",

        label:
          "🔵 First scan",

        reason:
          "No previous scan of the same crop and disease.",

        areaChange:
          null

      };

    }

    const previousArea =
      Number(
        previous.affected_area_pct ||
        0
      );

    const currentArea =
      Number(
        currentScan.affected_area_pct ||
        0
      );

    const areaChange =
      Number(
        (
          currentArea -
          previousArea
        ).toFixed(2)
      );

    const previousSeverity =
      severityRank(
        previous.severity
      );

    const currentSeverity =
      severityRank(
        currentScan.severity
      );

    // -------------------------------------------------------
    // Improvement
    // -------------------------------------------------------

    if (
      areaChange <= -5 ||
      currentSeverity <
        previousSeverity
    ) {

      let reason =
        "Disease severity decreased.";

      if (
        areaChange <= -5
      ) {

        reason =
          `Affected area decreased by ${Math.abs(
            areaChange
          ).toFixed(1)}%.`;

      }

      return {

        status:
          "improving",

        label:
          "🟢 Improving",

        reason:
          reason,

        areaChange:
          areaChange,

        previousArea:
          previousArea,

        currentArea:
          currentArea

      };

    }

    // -------------------------------------------------------
    // Worsening
    // -------------------------------------------------------

    if (
      areaChange >= 5 ||
      currentSeverity >
        previousSeverity
    ) {

      let reason =
        "Disease severity increased.";

      if (
        areaChange >= 5
      ) {

        reason =
          `Affected area increased by ${areaChange.toFixed(
            1
          )}%.`;

      }

      return {

        status:
          "worsening",

        label:
          "🔴 Worsening",

        reason:
          reason,

        areaChange:
          areaChange,

        previousArea:
          previousArea,

        currentArea:
          currentArea

      };

    }

    // -------------------------------------------------------
    // Stable
    // -------------------------------------------------------

    return {

      status:
        "stable",

      label:
        "🟡 Stable",

      reason:
        "No significant change detected.",

      areaChange:
        areaChange,

      previousArea:
        previousArea,

      currentArea:
        currentArea

    };

  }

  // =========================================================
  // 20. HISTORY CARD RENDERER
  // =========================================================

  function renderHistoryCards(
    scans
  ) {

    if (!elements.historyGrid) {
      return;
    }

    elements.historyGrid.innerHTML =
      "";

    // Sort newest first.
    const sortedScans =
      [...scans].sort(
        (a, b) => {

          const dateA =
            new Date(
              a.created_at ||
              0
            ).getTime();

          const dateB =
            new Date(
              b.created_at ||
              0
            ).getTime();

          return (
            dateB -
            dateA
          );

        }
      );

    sortedScans.forEach(
      scan => {

        const progress =
          calculateProgress(
            scan,
            sortedScans
          );

        const sevClass =
          `badge-${String(
            scan.severity ||
            "medium"
          ).toLowerCase()}`;

        let borderColor =
          "#cbd5e1";

        let backgroundColor =
          "#f8fafc";

        if (
          progress.status ===
          "improving"
        ) {

          borderColor =
            "#86efac";

          backgroundColor =
            "#f0fdf4";

        } else if (
          progress.status ===
          "worsening"
        ) {

          borderColor =
            "#fca5a5";

          backgroundColor =
            "#fef2f2";

        } else if (
          progress.status ===
          "stable"
        ) {

          borderColor =
            "#fde68a";

          backgroundColor =
            "#fffbeb";

        } else {

          borderColor =
            "#93c5fd";

          backgroundColor =
            "#eff6ff";

        }

        const infection =
          Number(
            scan.affected_area_pct ||
            0
          );

        const confidence =
          Number(
            scan.confidence ||
            0
          );

        const card =
          document.createElement(
            "div"
          );

        card.className =
          "history-card";

        card.innerHTML = `

          <div class="history-card-header">

            <span class="history-date">

              📅 ${
                formatDateTime(
                  scan.created_at
                )
              }

            </span>

            <span class="badge ${sevClass}">

              ${escapeHtml(
                scan.severity ||
                "Unknown"
              )}

            </span>

          </div>

          <div class="history-crop-title">

            ${
              escapeHtml(
                scan.crop ||
                "Unknown Crop"
              )
            }

            —

            ${
              escapeHtml(
                scan.disease ||
                "Unknown Disease"
              )
            }

          </div>

          <p class="history-summary">

            ${
              escapeHtml(
                scan.recommendation ||
                "No recommendation recorded."
              )
            }

          </p>

          <div
            style="
              display:flex;
              justify-content:space-between;
              margin-top:.75rem;
              font-size:.8rem;
              color:var(--text-muted);
            "
          >

            <span>
              Infection:
              ${infection.toFixed(1)}%
            </span>

            <span>
              Confidence:
              ${Math.round(
                confidence * 100
              )}%
            </span>

          </div>

          <!-- ==========================================
               DISEASE PROGRESS
               ========================================== -->

          <div
            style="
              margin-top:.75rem;
              padding:.75rem;
              border-radius:10px;
              border:1px solid ${borderColor};
              background:${backgroundColor};
            "
          >

            <div
              style="
                display:flex;
                justify-content:space-between;
                align-items:center;
              "
            >

              <strong>
                ${progress.label}
              </strong>

              ${
                progress.areaChange !== null
                  ? `
                    <span
                      style="
                        font-size:.75rem;
                        color:var(--text-muted);
                      "
                    >
                      ${
                        progress.areaChange > 0
                          ? "+"
                          : ""
                      }${progress.areaChange.toFixed(1)}%
                    </span>
                  `
                  : ""
              }

            </div>

            <div
              style="
                margin-top:.3rem;
                font-size:.75rem;
                color:var(--text-muted);
              "
            >

              ${escapeHtml(
                progress.reason
              )}

            </div>

          </div>

        `;

        // ---------------------------------------------------
        // Click history card
        // ---------------------------------------------------

        card.addEventListener(
          "click",
          () => {

            showToast(
              `Viewing scan: ${scan.crop} ${scan.disease}`
            );

            switchTab(
              "scanner"
            );

            state.currentScanResult = {

              crop:
                scan.crop,

              disease:
                scan.disease,

              original_disease:
                scan.original_disease ||
                scan.disease,

              confidence:
                scan.confidence,

              severity:
                scan.severity,

              affected_area_pct:
                scan.affected_area_pct,

              urgency:
                scan.urgency ||
                "Act within 3 days",

              summary:
                scan.recommendation ||
                "No recommendation recorded.",

              action_steps: [

                {
                  step: 1,

                  title:
                    "Recommended Treatment",

                  text:
                    scan.recommendation ||
                    "No recommendation recorded.",

                  type:
                    "critical"

                }

              ]

            };

            renderResults(

              state.currentScanResult,

              scan.image_name

                ? `${API_BASE}/api/uploads/${encodeURIComponent(
                    scan.image_name
                  )}`

                : null

            );

          }
        );

        elements.historyGrid.appendChild(
          card
        );

      }
    );

  }

  // =========================================================
  // 21. DATE FORMATTER
  // =========================================================

  function formatDateTime(
    value
  ) {

    if (!value) {
      return "Recent";
    }

    const date =
      new Date(value);

    if (
      Number.isNaN(
        date.getTime()
      )
    ) {

      return String(value);

    }

    return date.toLocaleString(
      [],
      {
        dateStyle: "medium",
        timeStyle: "short"
      }
    );

  }

  // =========================================================
  // 22. HTML ESCAPE
  // =========================================================

  function escapeHtml(
    value
  ) {

    const div =
      document.createElement(
        "div"
      );

    div.textContent =
      String(
        value ?? ""
      );

    return div.innerHTML;

  }

  // =========================================================
  // 23. TOAST
  // =========================================================

  function showToast(
    message,
    type = "info"
  ) {

    if (!elements.toastContainer) {
      return;
    }

    const toast =
      document.createElement(
        "div"
      );

    toast.className =
      "toast";

    const icon =
      type === "success"
        ? "✅"
        : type === "error"
        ? "❌"
        : "ℹ️";

    toast.innerHTML = `

      <span>
        ${icon}
      </span>

      <span>
        ${escapeHtml(message)}
      </span>

    `;

    elements.toastContainer.appendChild(
      toast
    );

    setTimeout(
      () => {

        toast.remove();

      },
      3200
    );

  }

});