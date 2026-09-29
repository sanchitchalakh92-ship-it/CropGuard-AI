/*
============================================================
CropGuard AI - Farmer Dashboard
============================================================
Displays:
- Farmer information
- Total scans
- Improving diseases
- Stable diseases
- Worsening diseases
- Crop list
- Complete scan history
============================================================
*/


// ============================================================
// PAGE INITIALIZATION
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    async function() {

        const user =
            await requireLogin();

        if (!user) return;


        displayFarmer(user);

        setupLogout();

        loadDashboard();

    }
);


// ============================================================
// DISPLAY FARMER
// ============================================================

function displayFarmer(user) {

    const farmerName =
        document.getElementById("farmerName");


    if (farmerName) {

        farmerName.textContent =
            user.name || "Farmer";

    }

}


// ============================================================
// LOGOUT
// ============================================================

function setupLogout() {

    const logoutBtn =
        document.getElementById("logoutBtn");


    if (!logoutBtn) return;


    logoutBtn.addEventListener(
        "click",
        async function() {

            await logoutFarmer();

        }
    );

}


// ============================================================
// LOAD DASHBOARD
// ============================================================

async function loadDashboard() {

    const historyContainer =
        document.getElementById("history");


    try {

        const response =
            await fetch(
                `${API_BASE}/api/my-dashboard`,
                {
                    credentials: "include"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Dashboard request failed"
            );

        }


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                data.message ||
                "Unable to load dashboard"
            );

        }


        updateStatistics(data);

        renderCrops(data.crops || []);

        renderHistory(data.history || []);


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );


        if (historyContainer) {

            historyContainer.innerHTML = `
                <div class="empty">
                    Unable to load your history.
                    <br><br>
                    Please make sure the CropGuard
                    backend is running.
                </div>
            `;

        }

    }

}


// ============================================================
// STATISTICS
// ============================================================

function updateStatistics(data) {

    setText(
        "totalScans",
        data.total_scans || 0
    );


    setText(
        "improving",
        data.improving || 0
    );


    setText(
        "stable",
        data.stable || 0
    );


    setText(
        "worsening",
        data.worsening || 0
    );

}


// ============================================================
// CROPS
// ============================================================

function renderCrops(crops) {

    const container =
        document.getElementById("cropList");


    if (!container) return;


    if (!crops.length) {

        container.innerHTML = `
            <div class="empty">
                No crop scans yet.
            </div>
        `;

        return;

    }


    container.innerHTML =
        crops
            .map(
                crop => `
                    <div class="crop-tag">
                        🌱 ${escapeHtml(crop)}
                    </div>
                `
            )
            .join("");

}


// ============================================================
// HISTORY
// ============================================================

function renderHistory(history) {

    const container =
        document.getElementById("history");


    if (!container) return;


    if (!history.length) {

        container.innerHTML = `
            <div class="empty">
                <h3>No scans yet 🌱</h3>
                <p>
                    Scan your first crop using CropGuard AI
                    to start tracking disease progress.
                </p>
            </div>
        `;

        return;

    }


    container.innerHTML =
        history
            .map(
                scan => createHistoryCard(scan)
            )
            .join("");

}


// ============================================================
// HISTORY CARD
// ============================================================

function createHistoryCard(scan) {

    const progress =
        scan.progress || {};


    const status =
        progress.status || "first_scan";


    const label =
        progress.label || "🔵 First scan";


    const reason =
        progress.reason ||
        "Baseline scan."


    const area =
        Number(
            scan.affected_area_pct || 0
        ).toFixed(1);


    const confidence =
        (
            Number(
                scan.confidence || 0
            ) * 100
        ).toFixed(1);


    const date =
        formatDate(
            scan.created_at
        );


    return `

        <div class="history-card">

            <div class="history-main">

                <h4>
                    🌱
                    ${escapeHtml(scan.crop || "Unknown Crop")}
                </h4>

                <p>
                    <strong>Disease:</strong>
                    ${escapeHtml(
                        scan.disease || "Unknown Disease"
                    )}
                </p>

                <p>
                    <strong>Severity:</strong>
                    ${escapeHtml(
                        scan.severity || "Unknown"
                    )}
                </p>

                <p>
                    <strong>Affected Area:</strong>
                    ${area}%
                </p>

                <p>
                    <strong>Confidence:</strong>
                    ${confidence}%
                </p>

                <p>
                    <strong>Date:</strong>
                    ${escapeHtml(date)}
                </p>

                <p>
                    ${escapeHtml(reason)}
                </p>

            </div>


            <div
                class="progress ${status}"
            >

                ${escapeHtml(label)}

            </div>

        </div>

    `;

}


// ============================================================
// HELPERS
// ============================================================

function setText(id, value) {

    const element =
        document.getElementById(id);


    if (element) {

        element.textContent = value;

    }

}


function formatDate(dateValue) {

    if (!dateValue) {

        return "Unknown date";

    }


    const date =
        new Date(
            dateValue.replace(" ", "T")
        );


    if (isNaN(date.getTime())) {

        return dateValue;

    }


    return date.toLocaleString(
        [],
        {
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        }
    );

}


function escapeHtml(value) {

    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}