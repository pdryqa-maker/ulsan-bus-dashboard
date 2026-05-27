
import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="513번 버스 실시간 도착정보", page_icon="🚌", layout="centered")

API_KEY = urllib.parse.unquote(st.secrets["ULSAN_BIS_API_KEY"])
BASE_URL = "http://openapi.its.ulsan.kr/UlsanAPI"
USTEC_STOP_ID = "196040234"
ULSAN_ST_BACK_ID = "196015414"

def get_bus_arrival(stop_id, route_no_filter, api_key, num_of_rows=20):
    url = f"{BASE_URL}/getBusArrivalInfo.xo"
    params = {"serviceKey": api_key, "stopid": stop_id, "pageNo": 1, "numOfRows": num_of_rows}
    try:
        resp = requests.get(url, params=params, timeout=5)
        root = ET.fromstring(resp.content)
        results = []
        for row in root.iter("row"):
            route_nm      = row.findtext("ROUTENM", "").strip()
            arrival_sec   = row.findtext("ARRIVALTIME", "").strip()
            prev_stop_cnt = row.findtext("PREVSTOPCNT", "").strip()
            present_stop  = row.findtext("PRESENTSTOPNM", "").strip()
            stop_nm       = row.findtext("STOPNM", "").strip()
            if route_no_filter in route_nm:
                arrival_min = round(int(arrival_sec) / 60, 1) if arrival_sec.isdigit() else "?"
                results.append({
                    "조회정류장명": stop_nm,
                    "노선번호":     route_nm,
                    "도착까지(분)": f"{arrival_min}분 후",
                    "도착까지(초)": f"{arrival_sec}초",
                    "현재정류장":   present_stop,
                    "남은정류장수": f"{prev_stop_cnt}정류장",
                })
        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"API 호출 오류: {e}")
        return pd.DataFrame()

st.title("🚌 513번 버스 실시간 도착정보")
st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

tab1, tab2 = st.tabs(["울산과학기술원 → 울산역", "울산역 → 울산과학기술원"])

with tab1:
    st.subheader("➡️ 울산과학기술원 출발 (울산역 방향)")
    st.caption(f"정류장 ID: {USTEC_STOP_ID}")
    df1 = get_bus_arrival(USTEC_STOP_ID, "513", API_KEY)
    if df1.empty:
        st.warning("현재 울산과학기술원 정류장에 513번 도착 예정 없음")
    else:
        st.dataframe(df1.head(10), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("➡️ 울산역(시내방면) 출발 (캠퍼스 방향)")
    st.caption(f"정류장 ID: {ULSAN_ST_BACK_ID}")
    df3 = get_bus_arrival(ULSAN_ST_BACK_ID, "513", API_KEY)
    if df3.empty:
        st.warning("현재 울산역(시내방면) 정류장에 513번 도착 예정 없음")
    else:
        st.dataframe(df3.head(10), use_container_width=True, hide_index=True)

st.divider()
if st.button("🔄 새로고침"):
    st.rerun()

st_autorefresh_code = """
<script>
setTimeout(function(){{ window.location.reload(); }}, 30000);
</script>
"""
st.components.v1.html(st_autorefresh_code, height=0)
