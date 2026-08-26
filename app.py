import os
import socket
import uuid
import json
import base64
import qrcode

from datetime import datetime
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DEVICES_FILE = os.path.join(BASE_DIR, "devices.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()

    return ip


def load_devices():
    if not os.path.exists(DEVICES_FILE):
        return {}

    with open(DEVICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_devices(devices):
    with open(DEVICES_FILE, "w", encoding="utf-8") as f:
        json.dump(devices, f, indent=4)


def make_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


@app.route("/")
def home():
    ip = get_local_ip()

    register_url = f"http://{ip}:5000/register"
    qr_image = make_qr_code(register_url)

    devices = load_devices()

    return render_template(
        "index.html",
        qr_image=qr_image,
        register_url=register_url,
        devices=devices
    )


@app.route("/register")
def register():
    device_id = str(uuid.uuid4())[:8]

    devices = load_devices()

    devices[device_id] = {
        "name": f"Phone {len(devices) + 1}",
        "registered_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "last_upload": None
    }

    save_devices(devices)

    device_folder = os.path.join(
        UPLOAD_FOLDER,
        device_id
    )

    os.makedirs(
        device_folder,
        exist_ok=True
    )

    return redirect(
        url_for(
            "camera",
            device_id=device_id
        )
    )


@app.route("/camera/<device_id>")
def camera(device_id):
    devices = load_devices()

    if device_id not in devices:
        return "Unknown device", 404

    return render_template(
        "camera.html",
        device_id=device_id,
        device_name=devices[device_id]["name"]
    )


@app.route("/upload/<device_id>", methods=["POST"])
def upload(device_id):
    devices = load_devices()

    if device_id not in devices:
        return "Unknown device", 404

    if "image" not in request.files:
        return "No image received", 400

    image = request.files["image"]

    if image.filename == "":
        return "No image selected", 400

    device_folder = os.path.join(
        UPLOAD_FOLDER,
        device_id
    )

    os.makedirs(
        device_folder,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    extension = os.path.splitext(
        image.filename
    )[1]

    if not extension:
        extension = ".jpg"

    filename = f"{timestamp}{extension}"

    filepath = os.path.join(
        device_folder,
        filename
    )

    image.save(filepath)

    devices[device_id]["last_upload"] = (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    save_devices(devices)

    print(
        f"Photo received from {device_id}: {filepath}"
    )

    return render_template(
        "camera.html",
        device_id=device_id,
        device_name=devices[device_id]["name"],
        message="Photo uploaded successfully!"
    )


@app.route("/rename/<device_id>", methods=["POST"])
def rename_device(device_id):
    devices = load_devices()

    if device_id not in devices:
        return "Unknown device", 404

    new_name = request.form.get(
        "name",
        ""
    ).strip()

    if new_name:
        devices[device_id]["name"] = new_name
        save_devices(devices)

    return redirect(url_for("home"))


if __name__ == "__main__":
    print()
    print("================================")
    print(" Phone Camera Server")
    print("================================")
    print()
    print("Laptop:")
    print("http://localhost:5000")
    print()
    print("Phone:")
    print(
        f"http://{get_local_ip()}:5000"
    )
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )