from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024  # 限制最大 2GB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_video_info(file_path):
    """使用 ffprobe 获取视频信息"""
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        file_path,
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, encoding="utf-8"
        )
        data = json.loads(result.stdout)

        video_stream = None
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                video_stream = stream
                break

        if not video_stream:
            return None

        codec_name = video_stream.get("codec_name", "unknown")
        codec_map = {
            "h264": "H.264",
            "h265": "H.265",
            "hevc": "H.265",
            "vp8": "VP8",
            "vp9": "VP9",
            "av1": "AV1",
            "mpeg4": "MPEG-4",
            "mpeg2video": "MPEG-2",
        }

        codec_display = codec_map.get(codec_name.lower(), codec_name.upper())

        return {
            "codec": codec_display,
            "codec_name": codec_name,
            "width": video_stream.get("width", 0),
            "height": video_stream.get("height", 0),
            "duration": float(data.get("format", {}).get("duration", 0)),
            "bit_rate": data.get("format", {}).get("bit_rate", "0"),
        }
    except Exception as e:
        print(f"获取视频信息失败：{e}")
        return None


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "没有文件"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "文件名为空"}), 400

    if not file.filename.lower().endswith(".mp4"):
        return jsonify({"error": "只支持 MP4 格式"}), 400

    original_filename = file.filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_filename = f"{timestamp}_{original_filename}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_filename)

    file.save(file_path)

    file_size = os.path.getsize(file_path)
    upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    video_info = get_video_info(file_path)

    if video_info:
        return jsonify(
            {
                "success": True,
                "filename": original_filename,
                "size": file_size,
                "upload_time": upload_time,
                "codec": video_info["codec"],
                "resolution": f"{video_info['width']}x{video_info['height']}",
                "duration": video_info["duration"],
            }
        )
    else:
        return jsonify(
            {
                "success": True,
                "filename": original_filename,
                "size": file_size,
                "upload_time": upload_time,
                "codec": "未知",
                "resolution": "未知",
                "duration": 0,
            }
        )


@app.route("/convert", methods=["POST"])
def convert_file():
    if "file" not in request.files:
        return jsonify({"error": "没有文件"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "文件名为空"}), 400

    if not file.filename.lower().endswith(".mp4"):
        return jsonify({"error": "只支持 MP4 格式"}), 400

    original_filename = file.filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    input_filename = f"{timestamp}_input.mp4"
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], input_filename)
    output_filename = f"{timestamp}_h264_converted.mp4"
    output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_filename)

    file.save(input_path)
    print(f"文件已保存到：{input_path}")

    abs_input_path = os.path.abspath(input_path)
    abs_output_path = os.path.abspath(output_path)

    cmd = [
        "ffmpeg",
        "-i",
        abs_input_path,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-y",
        abs_output_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        print(f"转换完成：{output_path}")

        os.remove(input_path)

        file_size = os.path.getsize(output_path)
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        video_info = get_video_info(output_path)

        return jsonify(
            {
                "success": True,
                "filename": original_filename,
                "size": file_size,
                "upload_time": upload_time,
                "codec": video_info["codec"] if video_info else "H.264",
                "resolution": f"{video_info['width']}x{video_info['height']}"
                if video_info
                else "未知",
                "duration": video_info["duration"] if video_info else 0,
            }
        )
    except subprocess.CalledProcessError as e:
        print(f"转换失败：{e}")
        print(f"stderr: {e.stderr}")
        if os.path.exists(input_path):
            os.remove(input_path)
        return jsonify(
            {"error": f"转换失败：{e.stderr[:200] if e.stderr else str(e)}"}
        ), 500
    except Exception as e:
        print(f"转换异常：{e}")
        if os.path.exists(input_path):
            os.remove(input_path)
        return jsonify({"error": f"转换异常：{str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
