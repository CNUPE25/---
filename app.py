# --- app.py: Streamlit 웹 앱 코드 ---

import streamlit as st
import pandas as pd
import ranking_engine # 1단계에서 만든 랭킹 엔진을 import

# --- Streamlit 웹페이지 설정 ---
st.set_page_config(layout="wide", page_title="테니스 리그 실시간 순위표")
st.title("🎾 학교 테니스 리그 실시간 순위표")
st.markdown("데이터는 **Google Sheets**에서 실시간으로 불러옵니다. 경기 결과는 관리자만 입력합니다.")

# ----------------------------------------------------
# 1. Google Sheets에서 데이터 불러오기 (Streamlit의 캐싱 기능 사용)
# ----------------------------------------------------

# @st.cache_data: 데이터가 변하지 않았으면 웹 앱을 새로고침해도 sheets에서 다시 읽지 않습니다. (효율성 UP)
@st.cache_data(ttl=600) # 10분(600초)마다 Sheets에서 데이터 새로고침
def load_data(sheet_url):
    try:
        # Google Sheets URL에서 워크시트 ID를 추출합니다.
        sheet_id = sheet_url.split("/d/")[1].split("/edit")[0]
        
        # Players 시트 불러오기 (ID = 0)
        players_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid=0"
        df_players = pd.read_csv(players_url)
        PLAYERS = df_players['Name'].dropna().tolist() # 선수 명단 추출 (비어있는 셀 제거)
        
        # Matches 시트 불러오기 (ID = 1010101010과 같은 gid를 수동으로 찾아서 넣는 것이 정확하지만,
        # 편의를 위해 일단 두 번째 시트(index=1)로 가정합니다.
        # 실제 gid를 알고 있다면 해당 숫자로 바꿔야 합니다.
        matches_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid=0&sheet=Matches"
        
        # Sheets의 'Matches' 시트에서 데이터를 읽어와 (Player_A, Player_B, Score) 튜플 리스트로 변환
        df_matches = pd.read_csv(matches_url, encoding='utf-8')
        df_matches = df_matches.dropna(subset=['Player_A', 'Player_B']) # 선수 이름 없는 행 제거
        
        MATCH_DATA = [
            (row['Player_A'].strip(), row['Player_B'].strip(), str(row['Score']).strip())
            for index, row in df_matches.iterrows()
        ]
        
        return PLAYERS, MATCH_DATA
        
    except Exception as e:
        st.error(f"Google Sheets에서 데이터를 불러오는 중 오류 발생: {e}")
        st.info("💡 1단계에서 복사한 **Google Sheets의 '공유 링크'**가 정확한지 확인해 주세요. 시트 이름이 'Players', 'Matches' 인지도 확인해 주세요.")
        return [], []


# ----------------------------------------------------
# 2. 순위표 표시 (네이버 스타일)
# ----------------------------------------------------

def display_rankings(final_rankings):
    # 컬럼 이름을 한글로 바꾸고, 순서 재배치 (5단계 업그레이드 코드의 로직)
    df_display = final_rankings.reset_index().rename(columns={'index': '선수명'})
    df_display = df_display.rename(columns={
        'Rank': '순위', 'W': '승', 'L': '패', 'Played': '경기수',
        'Set_Diff': '세트득실', 'Game_Diff': '게임득실'
    })
    df_display = df_display[['순위', '선수명', '경기수', '승', '패', '세트득실', '게임득실']]

    # 네이버 스포츠 스타일(CSS) 정의
    styles = [
        dict(selector="th", props=[
            ("background-color", "#f5f5f7"), ("color", "#333"),
            ("font-weight", "bold"), ("border-bottom", "1px solid #ddd"),
            ("text-align", "center"), ("padding", "10px")
        ]),
        dict(selector="td", props=[
            ("border-bottom", "1px solid #f0f0f0"), ("padding", "8px")
        ]),
        dict(selector="tr:hover", props=[
            ("background-color", "#f9f9f9")
        ]),
        dict(selector="tbody tr:nth-child(even)", props=[
            ("background-color", "#fafafa")
        ])
    ]

    # 스타일 적용 및 출력
    styled_df = df_display.style.set_table_styles(styles).set_properties(
        subset=['선수명'], **{'text-align': 'left'}
    ).set_properties(
        subset=['순위', '경기수', '승', '패', '세트득실', '게임득실'], **{'text-align': 'center'}
    ).hide(axis='index')
    
    # Streamlit에 순위표 출력
    st.markdown("### 🏆 현재 리그 순위")
    st.dataframe(styled_df, use_container_width=True, height=len(df_display) * 35 + 50)


# ----------------------------------------------------
# 3. 메인 실행 함수 (앱 시작 지점)
# ----------------------------------------------------

# TODO: 여기에 1단계에서 복사한 'Google Sheets 공유 링크'를 붙여넣으세요!
SHEETS_URL = "https://docs.google.com/spreadsheets/d/1uHmFEsvELqVAXnJ7f6vG5pg9AetxRXQJucCUTndpU30/edit?usp=sharing"


if __name__ == "__main__":
    PLAYERS, MATCH_DATA = load_data(SHEETS_URL)
    
    if PLAYERS and MATCH_DATA:
        # 랭킹 계산
        final_rankings = ranking_engine.calculate_rankings(PLAYERS, MATCH_DATA)
        
        # 순위표 표시
        display_rankings(final_rankings)
        
        # 데이터 업데이트 시간 표시
        st.caption(f"최종 업데이트 시간: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption(f"총 {len(PLAYERS)}명 참가, {len(MATCH_DATA)}경기 반영")
