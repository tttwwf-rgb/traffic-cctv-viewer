# -*- coding: utf-8 -*-
"""
ITS 국가교통정보센터 CCTV API 연동 모듈
"""

import math
import logging
import requests
from config import ITS_API_KEY, ITS_API_URL, CENTER_LAT, CENTER_LNG, SEARCH_RADIUS_KM, MAX_CCTV_COUNT

logger = logging.getLogger(__name__)


def _haversine_km(lat1, lng1, lat2, lng2):
    """두 좌표 간 거리 계산 (km)"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def _km_to_degree(km):
    """km를 위경도 차이로 근사 변환"""
    return km / 111.0


def fetch_cctv_list():
    """
    중심 좌표 주변 CCTV 목록을 ITS API에서 가져온다.

    Returns:
        list[dict]: CCTV 정보 목록
            {
                "id": str,
                "name": str,
                "lat": float,
                "lng": float,
                "stream_url": str,    # HLS(.m3u8) 또는 RTSP URL
                "distance_km": float,
                "road_name": str,
            }
    Raises:
        RuntimeError: API 호출 실패 시
    """
    if ITS_API_KEY == "여기에_ITS_API_키_입력":
        raise RuntimeError("config.py 에서 ITS_API_KEY를 먼저 입력하세요.")

    margin = _km_to_degree(SEARCH_RADIUS_KM)
    min_x = CENTER_LNG - margin
    max_x = CENTER_LNG + margin
    min_y = CENTER_LAT - margin
    max_y = CENTER_LAT + margin

    # 국도(its) + 고속도로(ex) 두 번 호출해서 합산
    raw_list = []
    for road_type in ("its", "ex"):
        params = {
            "apiKey":   ITS_API_KEY,
            "type":     road_type,
            "cctvType": "1",            # 1=HLS 실시간 스트리밍
            "minX":     str(min_x),
            "maxX":     str(max_x),
            "minY":     str(min_y),
            "maxY":     str(max_y),
            "getType":  "json",
        }
        try:
            resp = requests.get(ITS_API_URL, params=params, timeout=10, verify=False)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("response", {}).get("data") or []
            raw_list.extend(items)
            logger.info("type=%s -> %d건", road_type, len(items))
        except requests.RequestException as e:
            logger.warning("ITS API 호출 실패 (type=%s): %s", road_type, e)
        except ValueError as e:
            logger.warning("ITS API 응답 파싱 실패 (type=%s): %s", road_type, e)

    if not raw_list:
        logger.warning("CCTV 데이터 없음 (반경 내 결과 0건)")
        return []

    result = []
    for item in raw_list:
        try:
            lat = float(item.get("coordy", 0))
            lng = float(item.get("coordx", 0))
            stream_url = item.get("cctvurl", "")

            if not stream_url:
                continue

            dist = _haversine_km(CENTER_LAT, CENTER_LNG, lat, lng)

            result.append({
                "id":          item.get("cctvid", ""),
                "name":        item.get("cctvname", "이름 없음"),
                "road_name":   item.get("roadsectionid", ""),
                "lat":         lat,
                "lng":         lng,
                "stream_url":  stream_url,
                "distance_km": round(dist, 2),
            })
        except (ValueError, TypeError) as e:
            logger.debug("항목 파싱 건너뜀: %s", e)
            continue

    # 거리순 정렬 후 개수 제한
    result.sort(key=lambda x: x["distance_km"])
    return result[:MAX_CCTV_COUNT]
