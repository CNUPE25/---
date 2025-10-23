# --- 3단계: 랭킹 엔진 코드 ---
# (이 코드는 수정할 필요 없이 그대로 복사-붙여넣기 하세요)

import pandas as pd

def parse_score(player1, player2, score_str):
    """스코어 문자열("6-4 6-3")을 분석하여 승패, 세트, 게임 득실을 반환합니다."""
    p1_sets_won = 0
    # (... 이하 기존 3단계 코드 전부 ...)
    # (... ...)
    # (... ...)
    return df_sorted[['Rank', 'W', 'L', 'Played', 'Set_Diff', 'Game_Diff']]

# 파일 저장 확인
print("✅ 성공: 'ranking_engine.py' 파일이 생성되었습니다.")

import pandas as pd

def parse_score(player1, player2, score_str):
    """스코어 문자열("6-4 6-3")을 분석하여 승패, 세트, 게임 득실을 반환합니다."""
    p1_sets_won = 0
    p2_sets_won = 0
    p1_games_won = 0
    p2_games_won = 0

    # 스코어가 비어있거나 공백만 있는 경우, player1의 기권패로 간주합니다.
    # (player2가 2-0 승, 게임 스코어 6-0 6-0으로 처리)
    if not score_str or not score_str.strip():
        print(f"Info: '{player1}' vs '{player2}' 스코어 없음. '{player1}'의 기권패로 처리.")
        p2_sets_won = 2
        p2_games_won = 12
        return {
            'winner': player2, 'loser': player1,
            'p1_sets': 0, 'p2_sets': 2,
            'p1_games': 0, 'p2_games': 12
        }

    sets = score_str.split()
    for s in sets:
        try:
            # 타이브레이크 스코어 (예: "7-6(5)")를 처리하기 위해 괄호 제거
            s_cleaned = s.split('(')[0]
            p1_g, p2_g = map(int, s_cleaned.split('-'))
            
            p1_games_won += p1_g
            p2_games_won += p2_g

            if p1_g > p2_g:
                p1_sets_won += 1
            else:
                p2_sets_won += 1
        except ValueError:
            # 스코어 형식이 잘못된 경우 (예: "6-4a" 또는 "부상")
            print(f"!!! 스코어 형식 오류: '{s}' -> '{player1}'의 기권패로 처리합니다.")
            p2_sets_won = 2
            p2_games_won = 12
            p1_sets_won = 0
            p1_games_won = 0
            break # 오류 발생 시 더 이상 세트 처리 중단

    winner = player1 if p1_sets_won > p2_sets_won else player2
    loser = player2 if p1_sets_won > p2_sets_won else player1

    return {
        'winner': winner, 'loser': loser,
        'p1_sets': p1_sets_won, 'p2_sets': p2_sets_won,
        'p1_games': p1_games_won, 'p2_games': p2_games_won
    }

def calculate_rankings(player_list, match_results):
    """선수 명단과 경기 결과 리스트를 받아 최종 순위표(DataFrame)를 반환합니다."""
    
    # 1. 모든 선수의 통계를 0으로 초기화합니다.
    stats = {player: {'W': 0, 'L': 0, 'Set_Diff': 0, 'Game_Diff': 0, 'Played': 0} for player in player_list}
    
    # 2. 모든 경기 결과를 순회하며 통계를 누적합니다.
    for match in match_results:
        # 입력 형식의 유연성을 위해 공백 제거
        p1 = match[0].strip()
        p2 = match[1].strip()
        score = match[2].strip()

        # 선수 이름이 명단에 있는지 확인
        if p1 not in stats or p2 not in stats:
            print(f"!!! 선수 이름 오류: '{p1}' 또는 '{p2}'가 2단계의 선수 명단에 없습니다. 이 경기를 건너뜁니다.")
            continue
            
        result = parse_score(p1, p2, score)
        
        # 승자/패자 통계 업데이트
        stats[result['winner']]['W'] += 1
        stats[result['loser']]['L'] += 1
        stats[p1]['Played'] += 1
        stats[p2]['Played'] += 1
        
        # p1 기준 세트/게임 득실 계산
        p1_set_diff = result['p1_sets'] - result['p2_sets']
        p1_game_diff = result['p1_games'] - result['p2_games']
        
        # p1과 p2의 통계에 반영
        stats[p1]['Set_Diff'] += p1_set_diff
        stats[p1]['Game_Diff'] += p1_game_diff
        
        stats[p2]['Set_Diff'] -= p1_set_diff  # p2는 p1의 반대
        stats[p2]['Game_Diff'] -= p1_game_diff # p2는 p1의 반대

    # 3. 딕셔너리를 Pandas DataFrame으로 변환합니다. (표로 만들기)
    df = pd.DataFrame.from_dict(stats, orient='index')
    
    # 4. 순위 결정: 1.승수(내림) -> 2.세트득실(내림) -> 3.게임득실(내림) 순으로 정렬
    # 'Played'도 정렬 기준에 추가하여, 동률일 경우 경기를 덜 뛴 선수가 위로 가는 것을 방지 (선택 사항)
    df_sorted = df.sort_values(by=['W', 'Set_Diff', 'Game_Diff'], ascending=[False, False, False])
    
    # 'Rank' 열 추가 (1위부터 순서대로)
    df_sorted['Rank'] = range(1, len(df_sorted) + 1)
    
    # 컬럼 순서 재배치
    return df_sorted[['Rank', 'W', 'L', 'Played', 'Set_Diff', 'Game_Diff']]

print("✅ 성공: 랭킹 엔진이 메모리에 설치되었습니다.")
