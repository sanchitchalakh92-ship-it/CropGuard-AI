/*
============================================================
CropGuard AI - Farmer Authentication
============================================================
Registration
Login
Logout
Current User
Dashboard Protection
Scanner Protection
============================================================
*/

const API_BASE = window.location.origin;


// ============================================================
// MESSAGE
// ============================================================

function showMessage(message, type = "error") {

    const element = document.getElementById("message");

    if (!element) return;

    element.textContent = message;
    element.className = "message " + type;
}


// ============================================================
// REGISTRATION
// ============================================================

const registerForm =
    document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const name =
                document.getElementById("name").value.trim();

            const mobile =
                document.getElementById("mobile").value.trim();

            const email =
                document.getElementById("email").value.trim();

            const password =
                document.getElementById("password").value;

            const confirmPassword =
                document.getElementById("confirmPassword").value;


            if (!name) {

                showMessage(
                    "Please enter your name."
                );

                return;
            }


            if (!mobile) {

                showMessage(
                    "Please enter mobile number."
                );

                return;
            }


            if (password.length < 6) {

                showMessage(
                    "Password must contain at least 6 characters."
                );

                return;
            }


            if (password !== confirmPassword) {

                showMessage(
                    "Passwords do not match."
                );

                return;
            }


            try {

                showMessage(
                    "Creating your account...",
                    "success"
                );


                const response =
                    await fetch(
                        `${API_BASE}/api/register`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            credentials: "include",

                            body: JSON.stringify({

                                name: name,

                                mobile: mobile,

                                email: email,

                                password: password

                            })
                        }
                    );


                const data =
                    await response.json();


                if (!response.ok || !data.success) {

                    showMessage(
                        data.message ||
                        "Registration failed."
                    );

                    return;
                }


                localStorage.removeItem(
                    "cropguard_user"
                );


                showMessage(
                    "Registration successful! Redirecting to login...",
                    "success"
                );


                setTimeout(
                    function () {

                        window.location.replace(
                            "/login.html"
                        );

                    },
                    1000
                );


            } catch (error) {

                console.error(
                    "Registration error:",
                    error
                );

                showMessage(
                    "Unable to connect to CropGuard server."
                );

            }

        }
    );

}


// ============================================================
// LOGIN
// ============================================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const identifier =
            document.getElementById("identifier").value.trim();

        const password =
            document.getElementById("password").value;

        if (!identifier || !password) {
            showMessage(
                "Please enter your login details."
            );
            return;
        }

        try {

            showMessage(
                "Logging in...",
                "success"
            );

            const response = await fetch(
                `${API_BASE}/api/login`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    credentials: "include",

                    cache: "no-store",

                    body: JSON.stringify({
                        identifier: identifier,
                        password: password
                    })
                }
            );

            const data = await response.json();

            /*
             * Your login API may return either:
             * success: true
             * OR
             * status: "success"
             */

            const loginOK =
                response.ok &&
                (
                    data.success === true ||
                    data.status === "success"
                );

            if (!loginOK) {

                showMessage(
                    data.message ||
                    "Invalid mobile/email or password."
                );

                return;
            }

            // Store farmer information for display only.
            if (data.user) {

                localStorage.setItem(
                    "cropguard_user",
                    JSON.stringify(data.user)
                );

            }

            showMessage(
                "Login successful! Opening CropGuard...",
                "success"
            );

            /*
             * Flask session cookie has already been created
             * by /api/login.
             *
             * Open the protected main page.
             */

            setTimeout(function () {

                window.location.replace("/");

            }, 500);

        } catch (error) {

            console.error(
                "Login error:",
                error
            );

            showMessage(
                "Unable to connect to CropGuard server."
            );

        }

    });

}

// ============================================================
// GET CURRENT USER
// ============================================================

async function getCurrentUser() {
    try {
        const response = await fetch(`${API_BASE}/api/me`, {
            method: "GET",
            credentials: "include",
            cache: "no-store"
        });

        if (!response.ok) {
            return null;
        }

        const data = await response.json();

        if (data.status === "success" && data.user) {
            localStorage.setItem(
                "cropguard_user",
                JSON.stringify(data.user)
            );

            return data.user;
        }

        return null;

    } catch (error) {
        console.error("getCurrentUser error:", error);
        return null;
    }
}

// ============================================================
// LOGOUT
// ============================================================

async function logoutFarmer() {

    try {

        await fetch(
            `${API_BASE}/api/logout`,
            {
                method: "POST",

                credentials: "include",

                cache: "no-store"
            }
        );


    } catch (error) {

        console.warn(
            "Logout request failed:",
            error
        );

    }


    localStorage.removeItem(
        "cropguard_user"
    );


    localStorage.removeItem(
        "cropguard_session_id"
    );

    localStorage.removeItem(
        "cropguard_scan"
    );    

    window.location.replace(
        "/login.html"
    );

}


// ============================================================
// PROTECT DASHBOARD
// ============================================================

async function requireLogin() {

    const user =
        await getCurrentUser();


    if (!user) {

        window.location.replace(
            "/login.html"
        );

        return null;

    }


    return user;

}


// ============================================================
// PROTECT SCANNER
// ============================================================

async function protectScannerPage() {

    const user =
        await getCurrentUser();


    // --------------------------------------------------------
    // User is NOT logged in
    // --------------------------------------------------------

    if (!user) {

        window.location.replace(
            "/login.html"
        );

        return null;

    }


    // --------------------------------------------------------
    // Display farmer name
    // --------------------------------------------------------

    const farmerName =
        document.getElementById(
            "farmerName"
        );


    if (
        farmerName &&
        user.name
    ) {

        farmerName.textContent =
            user.name;

    }


    // --------------------------------------------------------
    // Authentication successful
    //
    // index.html hides the page while authentication
    // is being checked using:
    //
    // html.cropguard-auth-check body {
    //     visibility: hidden;
    // }
    //
    // Remove that class after successful login.
    // --------------------------------------------------------

    document.documentElement.classList.remove(
        "cropguard-auth-check"
    );


    return user;

}


// ============================================================
// STORED FARMER
// ============================================================

function getStoredFarmer() {

    try {

        const stored =
            localStorage.getItem(
                "cropguard_user"
            );


        if (!stored) {

            return null;

        }


        return JSON.parse(
            stored
        );


    } catch (error) {

        localStorage.removeItem(
            "cropguard_user"
        );


        return null;

    }

}