import os
import json
import sqlite3
import hashlib
import random
from datetime import datetime, timedelta

import cv2
import joblib
import numpy as np
import pandas as pd

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    session
)

from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from tensorflow.keras.models import load_model


# ============================================================
# ROADGUARD DIRECTORIES
# ============================================================

# This file is:
# RoadGuard/backend/app.py

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# RoadGuard/
PROJECT_DIR = os.path.dirname(
    BASE_DIR
)

# RoadGuard/ai/
AI_DIR = os.path.join(
    PROJECT_DIR,
    "ai"
)

# RoadGuard/backend/uploads/
UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

# RoadGuard/backend/roadguard.db
DATABASE_PATH = os.path.join(
    BASE_DIR,
    "roadguard.db"
)


# Make sure uploads folder exists
os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

# Session secret. Set ROADGUARD_SECRET_KEY before deployment.
app.secret_key = os.environ.get(
    "ROADGUARD_SECRET_KEY",
    "roadguard-local-development-secret-change-before-deployment"
)

CORS(
    app,
    supports_credentials=True
)


# ============================================================
# MODEL FILES
# ============================================================

IMAGE_MODEL_FINAL = os.path.join(
    AI_DIR,
    "roadguard_image_model_final.keras"
)

IMAGE_MODEL_BACKUP = os.path.join(
    AI_DIR,
    "roadguard_image_model.keras"
)

IMAGE_CLASS_NAMES_PATH = os.path.join(
    AI_DIR,
    "image_class_names.json"
)

RISK_MODEL_PATH = os.path.join(
    AI_DIR,
    "roadguard_model.pkl"
)

MODEL_FEATURES_PATH = os.path.join(
    AI_DIR,
    "model_features.pkl"
)


# ============================================================
# LOAD IMAGE CLASS NAMES
# ============================================================

image_class_names = [
    "accident",
    "broken_streetlight",
    "damaged_road",
    "flooding",
    "missing_sign",
    "normal_road",
    "pothole"
]


try:

    if os.path.exists(
        IMAGE_CLASS_NAMES_PATH
    ):

        with open(
            IMAGE_CLASS_NAMES_PATH,
            "r"
        ) as file:

            image_class_names = json.load(
                file
            )

        print(
            "Image classes loaded:"
        )

        print(
            image_class_names
        )

    else:

        print(
            "image_class_names.json not found."
        )

except Exception as e:

    print(
        "Could not load image class names:"
    )

    print(e)


# ============================================================
# LOAD IMAGE MODEL
# ============================================================

print(
    "\n========================================"
)

print(
    "ROADGUARD IMAGE MODEL LOADING"
)

print(
    "========================================"
)


image_model = None


image_model_paths = [

    IMAGE_MODEL_FINAL,

    IMAGE_MODEL_BACKUP

]


for model_path in image_model_paths:

    print(
        "\nTrying image model:"
    )

    print(
        model_path
    )


    if not os.path.exists(
        model_path
    ):

        print(
            "Model file does not exist."
        )

        continue


    try:

        # compile=False is important here.
        # We only need prediction, not training.
        image_model = load_model(
            model_path,
            compile=False
        )


        print(
            "\n========================================"
        )

        print(
            "IMAGE MODEL LOADED SUCCESSFULLY"
        )

        print(
            "Model:"
        )

        print(
            model_path
        )

        print(
            "========================================"
        )

        break


    except Exception as e:

        print(
            "\nFAILED TO LOAD IMAGE MODEL:"
        )

        print(
            str(e)
        )


if image_model is None:

    print(
        "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    )

    print(
        "IMAGE MODEL COULD NOT BE LOADED"
    )

    print(
        "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    )

    print(
        "Checked:"
    )

    for path in image_model_paths:

        print(
            path
        )


# ============================================================
# LOAD RISK MODEL
# ============================================================

print(
    "\n========================================"
)

print(
    "ROADGUARD RISK MODEL LOADING"
)

print(
    "========================================"
)


risk_model = None


try:

    risk_model = joblib.load(
        RISK_MODEL_PATH
    )

    print(
        "Risk model loaded successfully."
    )

    print(
        RISK_MODEL_PATH
    )


except Exception as e:

    print(
        "ERROR loading risk model:"
    )

    print(
        str(e)
    )


# ============================================================
# LOAD MODEL FEATURES
# ============================================================

model_features = None


try:

    model_features = joblib.load(
        MODEL_FEATURES_PATH
    )

    print(
        "Model features loaded successfully."
    )

    print(
        "Features:"
    )

    print(
        model_features
    )


except Exception as e:

    print(
        "Could not load model features:"
    )

    print(
        str(e)
    )


# ============================================================
# DATABASE
# ============================================================

def get_db_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def create_database():

    connection = get_db_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # CITIZENS
    # --------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citizens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE NOT NULL,
            phone_verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # OTP VERIFICATIONS
    # --------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otp_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            citizen_id INTEGER NOT NULL,
            otp_hash TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (citizen_id) REFERENCES citizens(id)
        )
    """)

    # --------------------------------------------------------
    # OFFICIALS
    # --------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS officials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # REPORTS
    # --------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT NOT NULL,
            description TEXT,
            hazard_type TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk TEXT NOT NULL,
            risk_probability REAL NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Existing databases were created before citizen accounts.
    # Add citizen_id only if it is not already present.
    cursor.execute("PRAGMA table_info(reports)")
    columns = [row["name"] for row in cursor.fetchall()]

    if "citizen_id" not in columns:
        cursor.execute(
            "ALTER TABLE reports ADD COLUMN citizen_id INTEGER"
        )
        print("Added citizen_id column to reports.")

    # --------------------------------------------------------
    # DEVELOPMENT OFFICIAL ACCOUNT
    # --------------------------------------------------------
    official_email = os.environ.get(
        "ROADGUARD_OFFICIAL_EMAIL",
        "admin@roadguard.com"
    )
    official_password = os.environ.get(
        "ROADGUARD_OFFICIAL_PASSWORD",
        "RoadGuard@123"
    )

    existing_official = cursor.execute(
        "SELECT id FROM officials WHERE lower(email) = ?",
        (official_email.lower(),)
    ).fetchone()

    if existing_official is None:
        cursor.execute("""
            INSERT INTO officials (
                name, email, password_hash
            ) VALUES (?, ?, ?)
        """, (
            "RoadGuard Official",
            official_email,
            generate_password_hash(official_password)
        ))

        print("\nDevelopment official account:")
        print("Email:", official_email)
        print("Password:", official_password)

    connection.commit()
    connection.close()

    print("\nDatabase ready:")
    print(DATABASE_PATH)


create_database()


# ============================================================
# IMAGE PREDICTION
# ============================================================

def predict_hazard(
    image_path
):

    if image_model is None:

        raise RuntimeError(
            "Image model is not loaded."
        )


    # Read image
    image = cv2.imread(
        image_path
    )


    if image is None:

        raise ValueError(
            "Could not read uploaded image."
        )


    # BGR -> RGB
    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )


    # MobileNetV2 input size
    image = cv2.resize(
        image,
        (224, 224)
    )


    # Normalize
    image = image.astype(
        np.float32
    ) / 255.0


    # Add batch dimension
    image = np.expand_dims(
        image,
        axis=0
    )


    # Predict
    predictions = image_model.predict(
        image,
        verbose=0
    )


    predictions = predictions[0]


    class_index = int(
        np.argmax(
            predictions
        )
    )


    confidence = float(
        predictions[class_index]
    )


    # Safety check
    if class_index >= len(
        image_class_names
    ):

        raise RuntimeError(
            "Predicted class index is outside class names."
        )


    hazard_type = image_class_names[
        class_index
    ]


    return (
        hazard_type,
        confidence
    )


# ============================================================
# RISK PREDICTION
# ============================================================

def predict_risk(
    hazard_type,
    latitude,
    longitude
):

    if risk_model is None:

        raise RuntimeError(
            "Risk model is not loaded."
        )


    now = datetime.now()


    month = now.month

    day = now.day

    hour = now.hour


    # --------------------------------------------------------
    # Create input
    # --------------------------------------------------------

    input_data = {

        "latitude":
            float(latitude),

        "longitude":
            float(longitude),

        "month":
            month,

        "day":
            day,

        "hour":
            hour

    }


    # --------------------------------------------------------
    # Hazard one-hot encoding
    # --------------------------------------------------------

    hazard_classes = [

        "accident",

        "broken_streetlight",

        "damaged_road",

        "flooding",

        "missing_sign",

        "pothole"

    ]


    for hazard in hazard_classes:

        input_data[
            f"hazard_type_{hazard}"
        ] = (

            1

            if hazard_type == hazard

            else 0

        )


    # --------------------------------------------------------
    # DataFrame
    # --------------------------------------------------------

    input_df = pd.DataFrame(
        [input_data]
    )


    # --------------------------------------------------------
    # Match training features
    # --------------------------------------------------------

    if model_features is not None:

        try:

            features = list(
                model_features
            )


            # Add missing columns
            for feature in features:

                if feature not in input_df.columns:

                    input_df[
                        feature
                    ] = 0


            # Keep exact order
            input_df = input_df[
                features
            ]


        except Exception as e:

            print(
                "Could not align model features:"
            )

            print(
                e
            )


    # --------------------------------------------------------
    # Risk prediction
    # --------------------------------------------------------

    prediction = risk_model.predict(
        input_df
    )[0]


    # --------------------------------------------------------
    # Probability
    # --------------------------------------------------------

    try:

        probabilities = (
            risk_model.predict_proba(
                input_df
            )[0]
        )


        risk_probability = float(
            probabilities[1]
        )


    except Exception:

        risk_probability = (

            1.0

            if int(prediction) == 1

            else 0.0

        )


    # --------------------------------------------------------
    # Risk label
    # --------------------------------------------------------

    if int(prediction) == 1:

        risk = "HIGH RISK"

    else:

        risk = "NORMAL RISK"


    return (
        risk,
        risk_probability
    )


# ============================================================
# CITIZEN AUTHENTICATION
# ============================================================

def normalize_phone_number(phone_number):
    phone_number = str(phone_number or "").strip()
    phone_number = (
        phone_number.replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    if len(phone_number) == 10 and phone_number.isdigit():
        return "+91" + phone_number

    if (
        len(phone_number) == 12
        and phone_number.startswith("91")
        and phone_number.isdigit()
    ):
        return "+" + phone_number

    return phone_number


def is_valid_phone_number(phone_number):
    if not phone_number.startswith("+91"):
        return False

    number = phone_number[3:]
    return (
        len(number) == 10
        and number.isdigit()
        and number[0] in "6789"
    )


def generate_otp():
    return f"{random.randint(0, 999999):06d}"


def hash_otp(otp):
    return hashlib.sha256(
        str(otp).encode("utf-8")
    ).hexdigest()


def citizen_required(view_function):
    @wraps(view_function)
    def wrapped(*args, **kwargs):
        if "citizen_id" not in session:
            return jsonify({
                "success": False,
                "authenticated": False,
                "error": "Citizen login required."
            }), 401

        return view_function(*args, **kwargs)

    return wrapped


@app.route("/citizen/send-otp", methods=["POST"])
def citizen_send_otp():
    try:
        data = request.get_json(silent=True) or {}
        phone_number = normalize_phone_number(
            data.get("phone_number", "")
        )

        if not is_valid_phone_number(phone_number):
            return jsonify({
                "success": False,
                "error": "Please enter a valid Indian mobile number."
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        citizen = cursor.execute("""
            SELECT id, phone_number, phone_verified
            FROM citizens
            WHERE phone_number = ?
        """, (phone_number,)).fetchone()

        if citizen is None:
            cursor.execute("""
                INSERT INTO citizens (phone_number, phone_verified)
                VALUES (?, 0)
            """, (phone_number,))
            citizen_id = cursor.lastrowid
        else:
            citizen_id = citizen["id"]

        # Invalidate older active OTPs.
        cursor.execute("""
            UPDATE otp_verifications
            SET verified = 1
            WHERE citizen_id = ? AND verified = 0
        """, (citizen_id,))

        otp = generate_otp()
        expires_at = datetime.now() + timedelta(minutes=5)

        cursor.execute("""
            INSERT INTO otp_verifications (
                citizen_id, otp_hash, expires_at, verified
            ) VALUES (?, ?, ?, 0)
        """, (
            citizen_id,
            hash_otp(otp),
            expires_at.strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()
        connection.close()

        # Local development only. Replace with SMS/Firebase later.
        print("\n========================================")
        print("ROADGUARD DEVELOPMENT OTP")
        print("========================================")
        print("Phone:", phone_number)
        print("OTP:", otp)
        print("Expires in: 5 minutes")
        print("========================================\n")

        return jsonify({
            "success": True,
            "message": "OTP generated successfully.",
            "phone_number": phone_number,
            "development_otp": otp,
            "expires_in": 300
        })

    except Exception as e:
        print("ERROR IN /citizen/send-otp:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/citizen/verify-otp", methods=["POST"])
def citizen_verify_otp():
    try:
        data = request.get_json(silent=True) or {}
        phone_number = normalize_phone_number(
            data.get("phone_number", "")
        )
        otp = str(data.get("otp", "")).strip()

        if not is_valid_phone_number(phone_number):
            return jsonify({
                "success": False,
                "error": "Invalid phone number."
            }), 400

        if len(otp) != 6 or not otp.isdigit():
            return jsonify({
                "success": False,
                "error": "OTP must contain 6 digits."
            }), 400

        connection = get_db_connection()
        citizen = connection.execute("""
            SELECT id, phone_number, phone_verified
            FROM citizens
            WHERE phone_number = ?
        """, (phone_number,)).fetchone()

        if citizen is None:
            connection.close()
            return jsonify({
                "success": False,
                "error": "Citizen account not found."
            }), 404

        otp_record = connection.execute("""
            SELECT id, otp_hash, expires_at
            FROM otp_verifications
            WHERE citizen_id = ? AND verified = 0
            ORDER BY id DESC
            LIMIT 1
        """, (citizen["id"],)).fetchone()

        if otp_record is None:
            connection.close()
            return jsonify({
                "success": False,
                "error": "No active OTP found. Please request a new OTP."
            }), 400

        expires_at = datetime.strptime(
            otp_record["expires_at"],
            "%Y-%m-%d %H:%M:%S"
        )

        if datetime.now() > expires_at:
            connection.execute("""
                UPDATE otp_verifications
                SET verified = 1
                WHERE id = ?
            """, (otp_record["id"],))
            connection.commit()
            connection.close()
            return jsonify({
                "success": False,
                "error": "OTP has expired. Please request a new OTP."
            }), 400

        if hash_otp(otp) != otp_record["otp_hash"]:
            connection.close()
            return jsonify({
                "success": False,
                "error": "Incorrect OTP."
            }), 401

        connection.execute("""
            UPDATE otp_verifications
            SET verified = 1
            WHERE id = ?
        """, (otp_record["id"],))

        connection.execute("""
            UPDATE citizens
            SET phone_verified = 1
            WHERE id = ?
        """, (citizen["id"],))

        connection.commit()
        connection.close()

        session.clear()
        session.permanent = True
        session["citizen_id"] = citizen["id"]
        session["citizen_phone"] = phone_number

        return jsonify({
            "success": True,
            "authenticated": True,
            "message": "Citizen login successful.",
            "citizen": {
                "id": citizen["id"],
                "phone_number": phone_number
            }
        })

    except Exception as e:
        print("ERROR IN /citizen/verify-otp:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/citizen/me", methods=["GET"])
@citizen_required
def citizen_me():
    try:
        connection = get_db_connection()
        citizen = connection.execute("""
            SELECT id, phone_number, phone_verified, created_at
            FROM citizens
            WHERE id = ?
        """, (session["citizen_id"],)).fetchone()
        connection.close()

        if citizen is None:
            session.clear()
            return jsonify({
                "success": False,
                "authenticated": False,
                "error": "Citizen account not found."
            }), 404

        return jsonify({
            "success": True,
            "authenticated": True,
            "citizen": dict(citizen)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/citizen/logout", methods=["POST"])
@citizen_required
def citizen_logout():
    session.clear()
    return jsonify({
        "success": True,
        "message": "Citizen logged out successfully."
    })


@app.route("/citizen/reports", methods=["GET"])
@citizen_required
def citizen_reports():
    try:
        connection = get_db_connection()
        rows = connection.execute("""
            SELECT
                id, image_filename, description, hazard_type,
                confidence, risk, risk_probability,
                latitude, longitude, status, created_at
            FROM reports
            WHERE citizen_id = ?
            ORDER BY id DESC
        """, (session["citizen_id"],)).fetchall()
        connection.close()

        reports = []
        for row in rows:
            report = dict(row)
            report["image"] = report["image_filename"]
            report["image_url"] = "/uploads/" + report["image_filename"]
            reports.append(report)

        return jsonify({
            "success": True,
            "reports": reports,
            "count": len(reports)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/citizen/reports/<int:report_id>", methods=["GET"])
@citizen_required
def citizen_single_report(report_id):
    try:
        connection = get_db_connection()
        row = connection.execute("""
            SELECT
                id, image_filename, description, hazard_type,
                confidence, risk, risk_probability,
                latitude, longitude, status, created_at
            FROM reports
            WHERE id = ? AND citizen_id = ?
        """, (report_id, session["citizen_id"])).fetchone()
        connection.close()

        if row is None:
            return jsonify({
                "success": False,
                "error": "Report not found."
            }), 404

        report = dict(row)
        report["image"] = report["image_filename"]
        report["image_url"] = "/uploads/" + report["image_filename"]

        return jsonify({
            "success": True,
            "report": report
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================
# OFFICIAL AUTHENTICATION
# ============================================================

def official_required(view_function):
    """
    Protect an API route so only logged-in officials can use it.
    """
    @wraps(view_function)
    def wrapped(*args, **kwargs):

        if "official_id" not in session:
            return jsonify({
                "success": False,
                "authenticated": False,
                "error": "Official login required."
            }), 401

        return view_function(*args, **kwargs)

    return wrapped


@app.route(
    "/official/login",
    methods=["POST"]
)
def official_login():

    try:

        data = request.get_json(silent=True) or {}

        email = str(
            data.get("email", "")
        ).strip().lower()

        password = str(
            data.get("password", "")
        )

        if not email or not password:

            return jsonify({
                "success": False,
                "error": "Email and password are required."
            }), 400

        connection = get_db_connection()

        official = connection.execute(
            """
            SELECT
                id,
                name,
                email,
                password_hash
            FROM officials
            WHERE lower(email) = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if (
            official is None
            or not check_password_hash(
                official["password_hash"],
                password
            )
        ):

            return jsonify({
                "success": False,
                "error": "Invalid official credentials."
            }), 401

        # Start a fresh official session.
        session.clear()

        session["official_id"] = official["id"]
        session["official_name"] = official["name"]
        session["official_email"] = official["email"]

        return jsonify({

            "success": True,

            "message":
                "Official login successful.",

            "official": {

                "id":
                    official["id"],

                "name":
                    official["name"],

                "email":
                    official["email"]

            }

        })

    except Exception as e:

        print(
            "\nERROR IN /official/login:"
        )

        print(str(e))

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


@app.route(
    "/official/me",
    methods=["GET"]
)
@official_required
def official_me():

    return jsonify({

        "success":
            True,

        "authenticated":
            True,

        "official": {

            "id":
                session["official_id"],

            "name":
                session["official_name"],

            "email":
                session["official_email"]

        }

    })


@app.route(
    "/official/logout",
    methods=["POST"]
)
@official_required
def official_logout():

    session.clear()

    return jsonify({

        "success":
            True,

        "message":
            "Official logged out successfully."

    })


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({

        "success":
            True,

        "message":
            "RoadGuard backend is running.",

        "endpoints": [

            "/",

            "/health",

            "/predict",

            "/citizen/send-otp",

            "/citizen/verify-otp",

            "/citizen/me",

            "/citizen/logout",

            "/citizen/reports",

            "/official/login",

            "/official/me",

            "/official/logout",

            "/reports",

            "/reports/<id>/status",

            "/uploads/<filename>"

        ]

    })


# ============================================================
# HEALTH
# ============================================================

@app.route(
    "/health"
)
def health():

    database_status = "connected"


    try:

        connection = get_db_connection()

        connection.execute(
            "SELECT 1"
        )

        connection.close()


    except Exception:

        database_status = "error"


    return jsonify({

        "success":
            True,

        "backend":
            "running",

        "database":
            database_status,

        "image_model":
            image_model is not None,

        "risk_model":
            risk_model is not None,

        "upload_folder":
            UPLOAD_FOLDER

    })


# ============================================================
# PREDICT + SAVE REPORT
# ============================================================

@app.route(
    "/predict",
    methods=["POST"]
)
@citizen_required
def predict():

    try:

        # ----------------------------------------------------
        # CHECK IMAGE
        # ----------------------------------------------------

        if "image" not in request.files:

            return jsonify({

                "success":
                    False,

                "error":
                    "No image uploaded."

            }), 400


        image_file = request.files[
            "image"
        ]


        if image_file.filename == "":

            return jsonify({

                "success":
                    False,

                "error":
                    "No image selected."

            }), 400


        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        latitude = request.form.get(
            "latitude"
        )

        longitude = request.form.get(
            "longitude"
        )


        if (
            latitude is None
            or longitude is None
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "Latitude and longitude are required."

            }), 400


        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )


        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        description = request.form.get(
            "description",
            ""
        ).strip()


        # ----------------------------------------------------
        # FILE EXTENSION
        # ----------------------------------------------------

        original_name = (
            image_file.filename
        )


        extension = os.path.splitext(
            original_name
        )[1].lower()


        if extension == "":

            extension = ".jpg"


        # ----------------------------------------------------
        # UNIQUE FILE NAME
        # ----------------------------------------------------

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )


        filename = (
            "roadguard_"
            + timestamp
            + extension
        )


        # ----------------------------------------------------
        # ABSOLUTE IMAGE PATH
        # ----------------------------------------------------

        image_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )


        # ----------------------------------------------------
        # SAVE IMAGE
        # ----------------------------------------------------

        image_file.save(
            image_path
        )


        print(
            "\n========================================"
        )

        print(
            "IMAGE SAVED"
        )

        print(
            "Filename:",
            filename
        )

        print(
            "Path:",
            image_path
        )

        print(
            "Exists:",
            os.path.exists(
                image_path
            )
        )

        print(
            "========================================"
        )


        # ----------------------------------------------------
        # IMAGE AI
        # ----------------------------------------------------

        hazard_type, confidence = (
            predict_hazard(
                image_path
            )
        )


        # ----------------------------------------------------
        # RISK AI
        # ----------------------------------------------------

        risk, risk_probability = (
            predict_risk(
                hazard_type,
                latitude,
                longitude
            )
        )


        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO reports (

                citizen_id,

                image_filename,

                description,

                hazard_type,

                confidence,

                risk,

                risk_probability,

                latitude,

                longitude,

                status

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,

            (

                session["citizen_id"],

                filename,

                description,

                hazard_type,

                round(
                    confidence * 100,
                    2
                ),

                risk,

                round(
                    risk_probability * 100,
                    2
                ),

                latitude,

                longitude,

                "Pending"

            )
        )


        report_id = cursor.lastrowid


        connection.commit()

        connection.close()


        # ----------------------------------------------------
        # TERMINAL
        # ----------------------------------------------------

        print(
            "\n========================================"
        )

        print(
            "ROADGUARD REPORT SAVED"
        )

        print(
            "Report ID:",
            report_id
        )

        print(
            "Image:",
            filename
        )

        print(
            "Hazard:",
            hazard_type
        )

        print(
            "Confidence:",
            round(
                confidence * 100,
                2
            ),
            "%"
        )

        print(
            "Risk:",
            risk
        )

        print(
            "Risk Probability:",
            round(
                risk_probability * 100,
                2
            ),
            "%"
        )

        print(
            "Description:",
            description
        )

        print(
            "Latitude:",
            latitude
        )

        print(
            "Longitude:",
            longitude
        )

        print(
            "Status:",
            "Pending"
        )

        print(
            "========================================\n"
        )


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return jsonify({

            "success":
                True,

            "report_id":
                report_id,

            "prediction": {

                "hazard_type":
                    hazard_type,

                "confidence":
                    round(
                        confidence * 100,
                        2
                    ),

                "risk":
                    risk,

                "risk_probability":
                    round(
                        risk_probability * 100,
                        2
                    )

            },

            "location": {

                "latitude":
                    latitude,

                "longitude":
                    longitude

            },

            "description":
                description,

            "image":
                filename,

            "status":
                "Pending"

        })


    except Exception as e:

        print(
            "\n========================================"
        )

        print(
            "ERROR IN /predict:"
        )

        print(
            str(e)
        )

        print(
            "========================================\n"
        )


        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# GET ALL REPORTS
# ============================================================

@app.route(
    "/reports",
    methods=["GET"]
)
@official_required
def get_reports():

    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            SELECT

                reports.id,

                reports.image_filename,

                reports.description,

                reports.hazard_type,

                reports.confidence,

                reports.risk,

                reports.risk_probability,

                reports.latitude,

                reports.longitude,

                reports.status,

                reports.created_at,

                reports.citizen_id,

                citizens.phone_number AS citizen_phone

            FROM reports

            LEFT JOIN citizens
                ON reports.citizen_id = citizens.id

            ORDER BY reports.id DESC
            """
        )


        rows = cursor.fetchall()


        connection.close()


        reports = []


        for row in rows:

            report = dict(
                row
            )


            # Frontend-friendly image field
            report["image"] = report[
                "image_filename"
            ]


            reports.append(
                report
            )


        return jsonify(
            reports
        )


    except Exception as e:

        print(
            "ERROR loading reports:"
        )

        print(
            str(e)
        )


        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# GET SINGLE REPORT STATUS
# ============================================================

@app.route(
    "/reports/<int:report_id>/status",
    methods=["GET"]
)
def get_report_status(
    report_id
):

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                hazard_type,
                confidence,
                risk,
                risk_probability,
                latitude,
                longitude,
                description,
                status,
                created_at
            FROM reports
            WHERE id = ?
            """,
            (report_id,)
        )

        row = cursor.fetchone()

        connection.close()

        if row is None:
            return jsonify({
                "success": False,
                "error": "Report not found."
            }), 404

        return jsonify({
            "success": True,
            "report": dict(row)
        })

    except Exception as e:

        print("ERROR getting report status:")
        print(str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================
# UPDATE REPORT STATUS
# ============================================================

@app.route(
    "/reports/<int:report_id>/status",
    methods=["PUT"]
)
@official_required
def update_status(
    report_id
):

    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "success":
                    False,

                "error":
                    "No JSON data received."

            }), 400


        new_status = data.get(
            "status"
        )


        allowed_statuses = [

            "Pending",

            "In Progress",

            "Resolved"

        ]


        if new_status not in allowed_statuses:

            return jsonify({

                "success":
                    False,

                "error":
                    "Invalid status.",

                "allowed":
                    allowed_statuses

            }), 400


        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            UPDATE reports

            SET status = ?

            WHERE id = ?
            """,

            (
                new_status,
                report_id
            )
        )


        if cursor.rowcount == 0:

            connection.close()


            return jsonify({

                "success":
                    False,

                "error":
                    "Report not found."

            }), 404


        connection.commit()

        connection.close()


        print(
            f"Report #{report_id} "
            f"updated to {new_status}"
        )


        return jsonify({

            "success":
                True,

            "report_id":
                report_id,

            "status":
                new_status

        })


    except Exception as e:

        print(
            "ERROR updating status:"
        )

        print(
            str(e)
        )


        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# SERVE UPLOADED ROAD IMAGES
# ============================================================

@app.route(
    "/uploads/<path:filename>",
    methods=["GET"]
)
def uploaded_file(
    filename
):

    # Always use backend/uploads
    upload_folder = os.path.join(
        BASE_DIR,
        "uploads"
    )


    # Prevent ../ path issues
    filename = os.path.basename(
        filename
    )


    file_path = os.path.join(
        upload_folder,
        filename
    )


    print(
        "\n----------------------------------------"
    )

    print(
        "IMAGE REQUESTED:",
        filename
    )

    print(
        "IMAGE PATH:",
        file_path
    )

    print(
        "IMAGE EXISTS:",
        os.path.exists(
            file_path
        )
    )

    print(
        "UPLOAD FOLDER:",
        upload_folder
    )

    print(
        "----------------------------------------"
    )


    if not os.path.isfile(
        file_path
    ):

        return jsonify({

            "success":
                False,

            "error":
                "Image not found.",

            "filename":
                filename,

            "expected_path":
                file_path

        }), 404


    return send_from_directory(
        upload_folder,
        filename
    )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        "ROADGUARD BACKEND"
    )

    print(
        "========================================"
    )

    print(
        "Backend:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print(
        "\nCitizen OTP Login:"
    )

    print(
        "POST http://127.0.0.1:5000/citizen/send-otp"
    )

    print(
        "POST http://127.0.0.1:5000/citizen/verify-otp"
    )

    print(
        "GET http://127.0.0.1:5000/citizen/reports"
    )

    print(
        "\nOfficial Login:"
    )

    print(
        "POST http://127.0.0.1:5000/official/login"
    )

    print(
        "\nReports (official login required):"
    )

    print(
        "http://127.0.0.1:5000/reports"
    )

    print(
        "\nHealth:"
    )

    print(
        "http://127.0.0.1:5000/health"
    )

    print(
        "\nUploads:"
    )

    print(
        "http://127.0.0.1:5000/uploads/<filename>"
    )

    print(
        "\nDatabase:"
    )

    print(
        DATABASE_PATH
    )

    print(
        "\nUpload folder:"
    )

    print(
        UPLOAD_FOLDER
    )

    print(
        "========================================\n"
    )


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )