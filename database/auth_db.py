import sqlite3
import hashlib
import hmac
import secrets
import time
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "cropguard.db"

PBKDF2_ITERATIONS = 200_000

# Registration OTP settings.
OTP_PENDING_EXPIRY_SECONDS = 5 * 60
OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_MAX_ATTEMPTS = 5
PASSWORD_RESET_EXPIRY_SECONDS = 5 * 60
PASSWORD_RESET_RESEND_COOLDOWN_SECONDS = 60


def get_auth_connection():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=5,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    # SQLite security settings
    conn.enable_load_extension(False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA secure_delete = ON;")
    conn.execute("PRAGMA trusted_schema = OFF;")
    conn.execute("PRAGMA busy_timeout = 5000;")

    return conn


def init_auth_db():
    conn = get_auth_connection()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mobile TEXT NOT NULL UNIQUE,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Pending registrations are kept separately from real farmer accounts.
        # The account is created only after the EMAIL OTP is verified.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS registration_otps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mobile TEXT NOT NULL UNIQUE,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                otp_request_id TEXT,
                otp_hash TEXT,
                created_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                last_sent_at INTEGER NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0
            )
        """)

        # Upgrade an existing CropGuard database without deleting registrations/users.
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(registration_otps)").fetchall()}
        if "otp_hash" not in columns:
            conn.execute("ALTER TABLE registration_otps ADD COLUMN otp_hash TEXT")

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_registration_otps_expires
            ON registration_otps(expires_at)
        """)

        # Password-reset OTPs are kept separate from registration OTPs.
        # This avoids interfering with an unfinished farmer registration.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_otps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                otp_hash TEXT NOT NULL,
                reset_token TEXT,
                verified INTEGER NOT NULL DEFAULT 0,
                created_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                last_sent_at INTEGER NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_password_reset_otps_expires
            ON password_reset_otps(expires_at)
        """)

        conn.commit()

    finally:
        conn.close()


def _hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(32)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS
    )

    return salt.hex(), password_hash.hex()


def _verify_password(password, salt_hex, stored_hash):
    try:
        salt = bytes.fromhex(salt_hex)

        _, password_hash = _hash_password(
            password,
            salt
        )

        return hmac.compare_digest(
            password_hash,
            stored_hash
        )

    except Exception:
        return False


def _cleanup_expired_pending(conn):
    conn.execute(
        "DELETE FROM registration_otps WHERE expires_at <= ?",
        (int(time.time()),)
    )


def registration_exists(mobile, email):
    mobile = (mobile or "").strip()
    email = (email or "").strip().lower()

    conn = get_auth_connection()

    try:
        _cleanup_expired_pending(conn)

        existing = conn.execute(
            """
            SELECT id
            FROM users
            WHERE mobile = ?
               OR (email IS NOT NULL AND email != '' AND email = ?)
            LIMIT 1
            """,
            (mobile, email)
        ).fetchone()

        if existing:
            return True

        pending = conn.execute(
            """
            SELECT id
            FROM registration_otps
            WHERE mobile = ?
               OR (email IS NOT NULL AND email != '' AND email = ?)
            LIMIT 1
            """,
            (mobile, email)
        ).fetchone()

        return pending is not None

    finally:
        conn.close()


def create_pending_registration(
    name,
    mobile,
    email,
    password,
    otp_hash=None,
    otp_request_id=None
):
    """Create/update a pending registration that is waiting for email OTP verification."""
    name = (name or "").strip()
    mobile = (mobile or "").strip()
    email = (email or "").strip().lower()
    password = password or ""

    if not name:
        return {"success": False, "message": "Farmer name is required."}

    if not mobile:
        return {"success": False, "message": "Mobile number is required."}

    if not email:
        return {"success": False, "message": "Email address is required."}

    if len(password) < 6:
        return {
            "success": False,
            "message": "Password must contain at least 6 characters."
        }

    salt, password_hash = _hash_password(password)
    now = int(time.time())
    expires_at = now + OTP_PENDING_EXPIRY_SECONDS

    conn = get_auth_connection()

    try:
        _cleanup_expired_pending(conn)

        existing = conn.execute(
            """
            SELECT id
            FROM users
            WHERE mobile = ?
               OR (email IS NOT NULL AND email != '' AND email = ?)
            LIMIT 1
            """,
            (mobile, email)
        ).fetchone()

        if existing:
            return {
                "success": False,
                "message": "Mobile number or email is already registered."
            }

        # Replace any older pending registration using the same mobile or email.
        conn.execute(
            "DELETE FROM registration_otps WHERE mobile = ? OR email = ?",
            (mobile, email)
        )

        conn.execute(
            """
            INSERT INTO registration_otps
            (
                name,
                mobile,
                email,
                password_hash,
                password_salt,
                otp_request_id,
                otp_hash,
                created_at,
                expires_at,
                last_sent_at,
                attempts
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                name,
                mobile,
                email,
                password_hash,
                salt,
                otp_request_id,
                otp_hash,
                now,
                expires_at,
                now
            )
        )

        conn.commit()

        return {
            "success": True,
            "message": "Email OTP registration request created.",
            "expires_in": OTP_PENDING_EXPIRY_SECONDS
        }

    except sqlite3.IntegrityError:
        return {
            "success": False,
            "message": "Mobile number or email is already registered."
        }

    finally:
        conn.close()


def get_pending_registration(email):
    email = (email or "").strip().lower()

    conn = get_auth_connection()

    try:
        _cleanup_expired_pending(conn)

        row = conn.execute(
            """
            SELECT *
            FROM registration_otps
            WHERE email = ?
            LIMIT 1
            """,
            (email,)
        ).fetchone()

        return dict(row) if row else None

    finally:
        conn.close()


def update_pending_otp_request(email, otp_hash, otp_request_id=None):
    email = (email or "").strip().lower()
    now = int(time.time())

    conn = get_auth_connection()

    try:
        conn.execute(
            """
            UPDATE registration_otps
            SET otp_request_id = ?,
                otp_hash = ?,
                last_sent_at = ?,
                expires_at = ?,
                attempts = 0
            WHERE email = ?
            """,
            (
                otp_request_id,
                otp_hash,
                now,
                now + OTP_PENDING_EXPIRY_SECONDS,
                email
            )
        )
        conn.commit()
        return True
    finally:
        conn.close()


def can_resend_pending_otp(email):
    email = (email or "").strip().lower()
    now = int(time.time())

    conn = get_auth_connection()

    try:
        row = conn.execute(
            """
            SELECT last_sent_at
            FROM registration_otps
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if not row:
            return False, 0

        remaining = OTP_RESEND_COOLDOWN_SECONDS - (
            now - int(row["last_sent_at"])
        )

        if remaining > 0:
            return False, remaining

        return True, 0

    finally:
        conn.close()


def increment_pending_attempt(email):
    email = (email or "").strip().lower()

    conn = get_auth_connection()

    try:
        conn.execute(
            """
            UPDATE registration_otps
            SET attempts = attempts + 1
            WHERE email = ?
            """,
            (email,)
        )
        conn.commit()

        row = conn.execute(
            """
            SELECT attempts
            FROM registration_otps
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        return int(row["attempts"]) if row else OTP_MAX_ATTEMPTS

    finally:
        conn.close()


def delete_pending_registration(email):
    email = (email or "").strip().lower()

    conn = get_auth_connection()

    try:
        conn.execute(
            "DELETE FROM registration_otps WHERE email = ?",
            (email,)
        )
        conn.commit()
    finally:
        conn.close()


def finalize_pending_registration(email):
    """Create the real farmer account from a verified email-OTP registration."""
    email = (email or "").strip().lower()

    conn = get_auth_connection()

    try:
        _cleanup_expired_pending(conn)

        pending = conn.execute(
            """
            SELECT
                name,
                mobile,
                email,
                password_hash,
                password_salt
            FROM registration_otps
            WHERE email = ?
            LIMIT 1
            """,
            (email,)
        ).fetchone()

        if not pending:
            return {
                "success": False,
                "message": "Registration request expired. Please register again."
            }

        existing = conn.execute(
            """
            SELECT id
            FROM users
            WHERE mobile = ?
               OR (
                    email IS NOT NULL
                    AND email != ''
                    AND email = ?
               )
            LIMIT 1
            """,
            (pending["mobile"], pending["email"] or "")
        ).fetchone()

        if existing:
            conn.execute(
                "DELETE FROM registration_otps WHERE email = ?",
                (email,)
            )
            conn.commit()

            return {
                "success": False,
                "message": "Mobile number or email is already registered."
            }

        cursor = conn.execute(
            """
            INSERT INTO users
            (
                name,
                mobile,
                email,
                password_hash,
                password_salt
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                pending["name"],
                pending["mobile"],
                pending["email"],
                pending["password_hash"],
                pending["password_salt"]
            )
        )

        user_id = cursor.lastrowid

        conn.execute(
            "DELETE FROM registration_otps WHERE email = ?",
            (email,)
        )
        conn.commit()

        return {
            "success": True,
            "message": "Farmer account created successfully.",
            "user": {
                "id": user_id,
                "name": pending["name"],
                "mobile": pending["mobile"],
                "email": pending["email"]
            }
        }

    except sqlite3.IntegrityError:
        return {
            "success": False,
            "message": "Mobile number or email is already registered."
        }

    finally:
        conn.close()


def _cleanup_expired_password_resets(conn):
    conn.execute(
        "DELETE FROM password_reset_otps WHERE expires_at <= ?",
        (int(time.time()),)
    )


def find_farmer_by_email(email):
    """Return a farmer account by email without exposing the password hash."""
    email = (email or "").strip().lower()
    if not email:
        return None

    conn = get_auth_connection()
    try:
        row = conn.execute(
            """
            SELECT id, name, mobile, email, created_at
            FROM users
            WHERE LOWER(email) = LOWER(?)
            LIMIT 1
            """,
            (email,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_password_reset_otp(email, otp_hash):
    """Create a new password-reset OTP record for a registered farmer."""
    email = (email or "").strip().lower()
    now = int(time.time())

    if not email or not otp_hash:
        return {"success": False, "message": "Invalid password reset request."}

    conn = get_auth_connection()
    try:
        _cleanup_expired_password_resets(conn)

        farmer = conn.execute(
            "SELECT id FROM users WHERE LOWER(email) = LOWER(?) LIMIT 1",
            (email,)
        ).fetchone()
        if not farmer:
            return {"success": False, "message": "Farmer account not found."}

        conn.execute(
            "DELETE FROM password_reset_otps WHERE email = ?",
            (email,)
        )

        conn.execute(
            """
            INSERT INTO password_reset_otps
            (email, otp_hash, reset_token, verified, created_at,
             expires_at, last_sent_at, attempts)
            VALUES (?, ?, NULL, 0, ?, ?, ?, 0)
            """,
            (
                email,
                otp_hash,
                now,
                now + PASSWORD_RESET_EXPIRY_SECONDS,
                now
            )
        )
        conn.commit()
        return {
            "success": True,
            "message": "Password reset OTP created.",
            "expires_in": PASSWORD_RESET_EXPIRY_SECONDS
        }
    except sqlite3.IntegrityError:
        return {
            "success": False,
            "message": "Could not create password reset request."
        }
    finally:
        conn.close()


def get_password_reset_otp(email):
    email = (email or "").strip().lower()
    conn = get_auth_connection()
    try:
        _cleanup_expired_password_resets(conn)
        row = conn.execute(
            """
            SELECT *
            FROM password_reset_otps
            WHERE email = ?
            LIMIT 1
            """,
            (email,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def can_resend_password_reset_otp(email):
    email = (email or "").strip().lower()
    now = int(time.time())
    conn = get_auth_connection()
    try:
        row = conn.execute(
            """
            SELECT last_sent_at
            FROM password_reset_otps
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if not row:
            return True, 0

        remaining = PASSWORD_RESET_RESEND_COOLDOWN_SECONDS - (
            now - int(row["last_sent_at"])
        )
        if remaining > 0:
            return False, remaining
        return True, 0
    finally:
        conn.close()


def update_password_reset_otp(email, otp_hash, reset_token=None, verified=False):
    """Replace OTP or mark a valid OTP as verified for password reset."""
    email = (email or "").strip().lower()
    now = int(time.time())
    conn = get_auth_connection()
    try:
        if reset_token is None:
            conn.execute(
                """
                UPDATE password_reset_otps
                SET otp_hash = ?,
                    reset_token = NULL,
                    verified = 0,
                    created_at = ?,
                    expires_at = ?,
                    last_sent_at = ?,
                    attempts = 0
                WHERE email = ?
                """,
                (
                    otp_hash,
                    now,
                    now + PASSWORD_RESET_EXPIRY_SECONDS,
                    now,
                    email
                )
            )
        else:
            conn.execute(
                """
                UPDATE password_reset_otps
                SET reset_token = ?,
                    verified = ?,
                    expires_at = ?
                WHERE email = ?
                """,
                (
                    reset_token,
                    1 if verified else 0,
                    now + PASSWORD_RESET_EXPIRY_SECONDS,
                    email
                )
            )

        if conn.total_changes == 0:
            conn.rollback()
            return {"success": False, "message": "Password reset request not found."}

        conn.commit()
        return {"success": True}
    finally:
        conn.close()


def increment_password_reset_attempt(email):
    email = (email or "").strip().lower()
    conn = get_auth_connection()
    try:
        conn.execute(
            """
            UPDATE password_reset_otps
            SET attempts = attempts + 1
            WHERE email = ?
            """,
            (email,)
        )
        conn.commit()

        row = conn.execute(
            "SELECT attempts FROM password_reset_otps WHERE email = ?",
            (email,)
        ).fetchone()
        return int(row["attempts"]) if row else OTP_MAX_ATTEMPTS
    finally:
        conn.close()


def delete_password_reset_otp(email):
    email = (email or "").strip().lower()
    conn = get_auth_connection()
    try:
        conn.execute(
            "DELETE FROM password_reset_otps WHERE email = ?",
            (email,)
        )
        conn.commit()
    finally:
        conn.close()


def update_farmer_password(email, password):
    """Securely replace a farmer password after email OTP verification."""
    email = (email or "").strip().lower()
    password = password or ""

    if len(password) < 6:
        return {
            "success": False,
            "message": "Password must contain at least 6 characters."
        }

    salt, password_hash = _hash_password(password)
    conn = get_auth_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE users
            SET password_hash = ?, password_salt = ?
            WHERE LOWER(email) = LOWER(?)
            """,
            (password_hash, salt, email)
        )

        if cursor.rowcount != 1:
            conn.rollback()
            return {
                "success": False,
                "message": "Farmer account not found."
            }

        conn.commit()
        return {
            "success": True,
            "message": "Password updated successfully."
        }
    finally:
        conn.close()


def register_farmer(name, mobile, email, password):
    """
    Backward-compatible direct registration function.

    The web registration flow should use:
    create_pending_registration()
    -> email OTP verification
    -> finalize_pending_registration()
    """
    name = (name or "").strip()
    mobile = (mobile or "").strip()
    email = (email or "").strip().lower()
    password = password or ""

    if not name:
        return {
            "success": False,
            "message": "Farmer name is required."
        }

    if not mobile:
        return {
            "success": False,
            "message": "Mobile number is required."
        }

    if len(password) < 6:
        return {
            "success": False,
            "message": "Password must contain at least 6 characters."
        }

    salt, password_hash = _hash_password(password)

    conn = get_auth_connection()

    try:
        existing = conn.execute(
            """
            SELECT id
            FROM users
            WHERE mobile = ?
               OR (email IS NOT NULL AND email != '' AND email = ?)
            """,
            (mobile, email)
        ).fetchone()

        if existing:
            return {
                "success": False,
                "message": "Mobile number or email is already registered."
            }

        cursor = conn.execute(
            """
            INSERT INTO users
            (
                name,
                mobile,
                email,
                password_hash,
                password_salt
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                mobile,
                email if email else None,
                password_hash,
                salt
            )
        )

        conn.commit()

        return {
            "success": True,
            "message": "Farmer registered successfully.",
            "user": {
                "id": cursor.lastrowid,
                "name": name,
                "mobile": mobile,
                "email": email
            }
        }

    except sqlite3.IntegrityError:
        return {
            "success": False,
            "message": "Mobile number or email is already registered."
        }

    finally:
        conn.close()


def login_farmer(identifier, password):
    identifier = (identifier or "").strip()
    password = password or ""

    conn = get_auth_connection()

    try:
        user = conn.execute(
            """
            SELECT
                id,
                name,
                mobile,
                email,
                password_hash,
                password_salt,
                created_at
            FROM users
            WHERE mobile = ?
               OR LOWER(email) = LOWER(?)
            LIMIT 1
            """,
            (identifier, identifier)
        ).fetchone()

        if not user:
            return {
                "success": False,
                "message": "Invalid mobile/email or password."
            }

        if not _verify_password(
            password,
            user["password_salt"],
            user["password_hash"]
        ):
            return {
                "success": False,
                "message": "Invalid mobile/email or password."
            }

        return {
            "success": True,
            "message": "Login successful.",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "mobile": user["mobile"],
                "email": user["email"],
                "created_at": user["created_at"]
            }
        }

    finally:
        conn.close()


def get_farmer(user_id):
    conn = get_auth_connection()

    try:
        user = conn.execute(
            """
            SELECT
                id,
                name,
                mobile,
                email,
                created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        if not user:
            return None

        return dict(user)

    finally:
        conn.close()

def delete_farmer_account(user_id, current_password):
    """
    Permanently delete one authenticated farmer and that farmer's data.

    The caller must supply the current password.  The function uses the
    authenticated numeric user_id, never a frontend-supplied email/name.
    It also removes this farmer's scan-history rows and returns the stored
    upload filenames so the Flask layer can remove the corresponding files.
    """
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return {
            "success": False,
            "message": "Invalid farmer account."
        }

    current_password = current_password or ""
    if not current_password:
        return {
            "success": False,
            "message": "Current password is required."
        }

    conn = get_auth_connection()

    try:
        conn.execute("BEGIN IMMEDIATE")

        user = conn.execute(
            """
            SELECT id, email, mobile, password_hash, password_salt
            FROM users
            WHERE id = ?
            LIMIT 1
            """,
            (user_id,)
        ).fetchone()

        if not user:
            conn.rollback()
            return {
                "success": False,
                "message": "Farmer account not found."
            }

        if not _verify_password(
            current_password,
            user["password_salt"],
            user["password_hash"]
        ):
            conn.rollback()
            return {
                "success": False,
                "message": "Current password is incorrect."
            }

        email = (user["email"] or "").strip().lower()
        mobile = (user["mobile"] or "").strip()

        # Scan records are tied to the backend-controlled session ID.
        farmer_session_id = f"farmer_{user_id}"
        image_names = []

        # Keep deletion compatible with older databases where scans may
        # not yet exist.
        scans_exists = conn.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = 'scans'
            LIMIT 1
            """
        ).fetchone()

        if scans_exists:
            rows = conn.execute(
                """
                SELECT image_name
                FROM scans
                WHERE session_id = ?
                """,
                (farmer_session_id,)
            ).fetchall()

            image_names = [
                str(row["image_name"]).strip()
                for row in rows
                if row["image_name"]
            ]

            conn.execute(
                "DELETE FROM scans WHERE session_id = ?",
                (farmer_session_id,)
            )

        # Remove unfinished registration/reset records belonging to this
        # farmer as well.
        if email:
            conn.execute(
                "DELETE FROM registration_otps WHERE email = ?",
                (email,)
            )
            conn.execute(
                "DELETE FROM password_reset_otps WHERE email = ?",
                (email,)
            )

        if mobile:
            conn.execute(
                "DELETE FROM registration_otps WHERE mobile = ?",
                (mobile,)
            )

        # Delete the actual farmer account last.
        cursor = conn.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )

        if cursor.rowcount != 1:
            conn.rollback()
            return {
                "success": False,
                "message": "Account deletion could not be completed."
            }

        conn.commit()

        return {
            "success": True,
            "message": "Farmer account and associated data deleted successfully.",
            "image_names": image_names
        }

    except Exception as exc:
        conn.rollback()
        print(f"[AUTH] delete_farmer_account error: {exc}")
        return {
            "success": False,
            "message": "Account deletion failed. No account changes were saved."
        }

    finally:
        conn.close()

