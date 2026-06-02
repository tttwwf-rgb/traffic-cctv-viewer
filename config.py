# -*- coding: utf-8 -*-
"""
설정값 모음 — 운영 환경에 맞게 수정하세요.
"""

# ─── ITS 국가교통정보센터 API ────────────────────────────────────────────────
# 발급처: https://www.its.go.kr/opendata/opendataList?service=cctv
# (무료 회원가입 후 API 키 발급, 즉시 사용 가능)
ITS_API_KEY = "여기에_ITS_API_키_입력"

ITS_API_URL = "https://openapi.its.go.kr:9443/cctvInfo"

# ─── 검색 중심 좌표 (대구 달서구 조암남로32길 13) ──────────────────────────
CENTER_LAT = 35.8329    # 위도
CENTER_LNG = 128.5372   # 경도

# 검색 반경 (km) — 숫자를 높이면 더 넓은 범위 검색
SEARCH_RADIUS_KM = 3.0

# ─── CCTV 표시 개수 제한 ────────────────────────────────────────────────────
MAX_CCTV_COUNT = 12

# ─── Flask 서버 ─────────────────────────────────────────────────────────────
HOST = "127.0.0.1"
PORT = 5000
DEBUG = False
