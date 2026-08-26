import os
import socket
import uuid
from datetime import datetime

import qrcode
import base64

from flask import Flask, render_template, request
from io import BytesIO


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

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

    img.save(
        buffer,
        format="PNG"
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


@app.route("/")
def home():

    ip = get_local_ip()

    register_url = f"http://{ip}:5000/register"

    qr_image = make_qr_code(register_url)

    return render_template(
        "index.html",
        qr_image=qr_image,
        register_url=register_url
    )


@app.route("/register")
def register():

    device_id = str(uuid.uuid4())[:8]

    device_folder = os.path.join(
        UPLOAD_FOLDER,
        device_id
    )

    os.makedirs(
        device_folder,
        exist_ok=True
    )

    return render_template(
        "camera.html",
        device_id=device_id
    )


@app.route("/upload/<device_id>", methods=["POST"])
def upload(device_id):

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

    print(
        f"Photo received from {device_id}: "
        f"{filepath}"
    )

    return render_template(
        "camera.html",
        device_id=device_id,
        message="Photo uploaded successfully!"
    )


if __name__ == "__main__":

    print()
    print("================================")
    print(" Phone Camera Server")
    print("================================")
    print()

    print(
        f"Open laptop browser:"
        f" http://localhost:5000"
    )

    print(
        f"Phone URL:"
        f" http://{get_local_ip()}:5000"
    )

    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )