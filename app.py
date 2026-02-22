from flask import Flask, render_template, request, jsonify
from google import genai
import base64

app = Flask(__name__)

# ==========================
# GANTI API KEY KAMU
# ==========================
client = genai.Client(api_key="ISI API KEY KAMU DISINI")

# ==========================
# GLOBAL PRESERVE RULE
# ==========================
BASE_RULE = """
This is a strict image editing task.

DO NOT regenerate the entire image.
Preserve 100 percent of original background, lighting, pose, and camera angle.
Preserve the exact face without modification.

Only modify the clothing fabric and uniform design.
Keep body proportions identical.
Photorealistic.
"""

# ==========================
# PROFESI INDONESIA
# ==========================
PROMPT_OPTIONS = {
    "presiden": BASE_RULE + "Black suit, white shirt, red tie, Garuda pin.",
    "dokter": BASE_RULE + "White doctor coat, stethoscope, hospital ID.",
    "tentara": BASE_RULE + "TNI loreng uniform, red-white flag patch.",
    "polisi": BASE_RULE + "POLRI light brown uniform, rank badge.",
    "guru": BASE_RULE + "Formal batik teacher outfit.",
    "pilot": BASE_RULE + "Airline pilot white shirt, black tie, epaulette.",
    "pramugari": BASE_RULE + "Indonesian kebaya flight attendant uniform.",
    "pemadam": BASE_RULE + "Orange firefighter suit with reflective stripes.",
    "ojol": BASE_RULE + "Green Indonesian ojek online jacket and helmet.",
    "satpam": BASE_RULE + "Light blue Indonesian security uniform.",
    "hakim": BASE_RULE + "Black judge robe with white collar.",
    "jaksa": BASE_RULE + "Black prosecutor robe with badge.",
    "arsitek": BASE_RULE + "Semi formal architect outfit with helmet.",
    "chef": BASE_RULE + "White chef uniform with tall hat.",
    "wartawan": BASE_RULE + "Journalist attire with press ID.",
    "petani": BASE_RULE + "Traditional farmer outfit with caping.",
    "nelayan": BASE_RULE + "Indonesian fisherman outfit.",
    "montir": BASE_RULE + "Mechanic workshop uniform.",
    "perawat": BASE_RULE + "Nurse scrub medical attire.",
    "programmer": BASE_RULE + "Smart casual office outfit with lanyard."
}

# ==========================
# ROUTES
# ==========================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    file = request.files.get("image")
    styles = request.form.getlist("style")

    if not file or not styles:
        return jsonify({"error": "Invalid input"}), 400

    image_bytes = file.read()
    results = []

    for style in styles:
        if style not in PROMPT_OPTIONS:
            continue

        prompt = PROMPT_OPTIONS[style]

        try:
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": file.mimetype,
                                    "data": image_bytes
                                }
                            }
                        ]
                    }
                ]
            )

            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.inline_data:
                        img_base64 = base64.b64encode(part.inline_data.data).decode("utf-8")
                        results.append({
                            "style": style,
                            "image": img_base64
                        })
                        break

        except Exception as e:
            results.append({
                "style": style,
                "error": str(e)
            })

    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(debug=True)