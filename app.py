# -*- coding: utf-8 -*-
"""
교통 CCTV 뷰어 — Flask 웹서버
실행: python app.py
접속: http://127.0.0.1:5000
"""

import os
import sys
import signal
import logging
import logging.handlers

# Windows 한글 인코딩 강제 적용
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from flask import Flask, jsonify, render_template
import config
from cctv_api import fetch_cctv_list

# ─── 로그 설정 ───────────────────────────────────────────────────────────────
def setup_logging():
    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # 콘솔 (Vercel 포함 모든 환경)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # 파일 로그 (로컬 환경에서만, Vercel은 파일 쓰기 불가)
    if os.environ.get("VERCEL") is None:
        try:
            fh = logging.handlers.RotatingFileHandler(
                "cctv_viewer.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
            )
            fh.setFormatter(fmt)
            root.addHandler(fh)
        except Exception:
            pass


setup_logging()
logger = logging.getLogger(__name__)

# ─── Flask 앱 ────────────────────────────────────────────────────────────────
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html",
                           center_lat=config.CENTER_LAT,
                           center_lng=config.CENTER_LNG,
                           radius_km=config.SEARCH_RADIUS_KM)


@app.route("/api/cctv-list")
def api_cctv_list():
    """CCTV 목록 JSON 반환"""
    try:
        cctv_list = fetch_cctv_list()
        logger.info("CCTV 목록 반환: %d건", len(cctv_list))
        return jsonify({"ok": True, "count": len(cctv_list), "data": cctv_list})
    except RuntimeError as e:
        logger.error("CCTV 목록 조회 실패: %s", e)
        return jsonify({"ok": False, "error": str(e)}), 500


# ─── 정상 종료 (로컬 전용) ───────────────────────────────────────────────────
if os.environ.get("VERCEL") is None:
    def _shutdown(signum, frame):
        logger.info("종료 신호 수신 - 서버를 정상 종료합니다.")
        sys.exit(0)
    signal.signal(signal.SIGINT,  _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)


# ─── 로컬 실행 ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("CCTV 뷰어 시작 -> http://%s:%d", config.HOST, config.PORT)
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
