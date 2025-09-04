from flask import Flask, render_template, request, session, redirect, url_for, flash
import secrets
import os
from gtts import gTTS
from config import Config
from fallback_products import get_fallback_products
from video_generator import generate_video_from_products  # full video generator

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
Config.load_env()

# Categories
CATEGORIES = [
    {"key": "kitchen", "label": "Kitchen"},
    {"key": "beauty", "label": "Beauty"},
    {"key": "tech", "label": "Tech"},
    {"key": "household", "label": "Household"},
    {"key": "outdoors", "label": "Outdoors"},
]

MAX_FULL = 10
VIDEO_DIR = "static/videos"
AUDIO_DIR = "static/audio"
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# -------------------
# Login (choose Demo or Full)
# -------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        mode = request.form.get("mode")

        if mode == "demo":
            session["user_type"] = "demo"
            flash("Demo mode activated! Browse products, but video generation is disabled.", "info")
            return redirect(url_for("dashboard"))

        elif mode == "full":
            password = request.form.get("password")
            if password == os.getenv("FULL_MODE_PASSWORD"):  # stored in .env
                return redirect(url_for("activate"))
            else:
                flash("Invalid password for full mode.", "error")

    return render_template("login.html")


# -------------------
# Full Mode Activation
# -------------------
@app.route("/activate", methods=["GET", "POST"])
def activate():
    if request.method == "POST":
        session["amazon_tag"] = request.form.get("amazon_tag")
        session["youtube_key"] = request.form.get("youtube_key")
        session["license_key"] = request.form.get("license_key")
        session["user_type"] = "full"
        session["full_uses"] = 0
        flash("Full mode activated! You can now generate custom TTS videos.", "success")
        return redirect(url_for("dashboard"))
    return render_template("activation.html")


# -------------------
# Dashboard
# -------------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user_type = session.get("user_type")

    if not user_type:
        return redirect(url_for("login"))

    category = request.form.get("category") if request.method == "POST" else None
    products = []

    if category:
        products = get_fallback_products(category)
        for p in products:
            p["default_text"] = p.get("description", "")
            p["video"] = None
            if session.get("amazon_tag") and p.get("link"):
                p["amazon_link"] = f"{p['link']}&tag={session['amazon_tag']}"
            else:
                p["amazon_link"] = p.get("link")

    return render_template(
        "dashboard.html",
        categories=CATEGORIES,
        category=category,
        products=products,
        user_type=user_type,
        full_limit_reached=session.get("full_uses", 0) >= MAX_FULL if user_type == "full" else True,
        max_full=MAX_FULL
    )


# -------------------
# Generate Video per Product (Full mode only)
# -------------------
@app.route("/generate_video", methods=["POST"])
def generate_video():
    if session.get("user_type") != "full":
        flash("Video generation available for full users only. You are in demo mode.", "error")
        return redirect(url_for("dashboard"))

    if session.get("full_uses", 0) >= MAX_FULL:
        flash("Maximum full mode video generation reached.", "error")
        return redirect(url_for("dashboard"))

    product_index = int(request.form.get("product_index"))
    category = request.form.get("category")
    tts_text = request.form.get("tts_text")

    # Get product info
    products = get_fallback_products(category)
    product = products[product_index]

    # Generate TTS audio
    audio_file = f"full_audio_{secrets.token_hex(4)}.mp3"
    audio_path = os.path.join(AUDIO_DIR, audio_file)
    tts = gTTS(text=tts_text or product.get("description", ""))
    tts.save(audio_path)

    # Generate video using the full pipeline
    video_paths = generate_video_from_products(
        products=[{"title": product["title"], "description": tts_text or product.get("description", "")}],
        audio_path=audio_path,
        output_dir=VIDEO_DIR
    )

    product["video"] = url_for("static", filename=f"videos/{os.path.basename(video_paths['landscape'])}")
    session["full_uses"] += 1

    flash("Custom TTS video generated successfully!", "success")
    return redirect(url_for("dashboard"))


# -------------------
# Logout
# -------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
