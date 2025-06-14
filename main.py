import pandas as pd
# 필요한 함수들을 git_analyzer에서 가져옵니다.
from git_analyzer import analyze_commits, get_week_options, load_week_range
from html_parser import save_dataframe_as_html
import sys # 오류 발생 시 종료를 위해 추가

def analyze_repositories_for_week(account_file, selected_week, branch="main"):
    """
    선택된 주차에 대해 여러 사용자의 저장소를 분석합니다.
    users_account.txt는 '사용자ID,토큰,사용자이름' 형식을 따라야 합니다.
    """
    try:
        with open(account_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ 오류: '{account_file}' 파일을 찾을 수 없습니다. 파일이 정확한 위치에 있는지 확인하세요.")
        sys.exit(1)


    all_results = []

    for line in lines:
        if not line.strip():
            continue
        try:
            # 변경된 users_account.txt 형식에 맞게 파싱
            user_id, token, username = line.strip().split(",")

            # XXX와 YYY를 채워 동적으로 GitHub URL 생성
            repo_name = f"homework-{selected_week}-{user_id}"
            github_url = f"https://github.com/computer-sunmoon/{repo_name}.git"

            print(f"🔍 분석 중: {username} ({github_url})")
            
            # analyze_commits 호출 시 selected_week 전달
            df = analyze_commits(
                github_url=github_url,
                token=token,
                username=username,
                selected_week=selected_week, # 주차 정보 전달
                directory="lib/",
                exclude_first_commit=True
            )
            
            if not df.empty:
                all_results.append(df)
            else:
                print(f"⚠️  {username} 에 대한 커밋 데이터가 없습니다.")
        except ValueError:
            print(f"❌ 오류: '{line.strip()}' 라인이 '사용자ID,토큰,사용자이름' 형식이 아닙니다. 확인해주세요.")
        except Exception as e:
            print(f"❌ 오류 발생 (사용자: {line.strip().split(',')[0]}): {e}")

    if all_results:
        combined = pd.concat(all_results, ignore_index=True)
        # 결과 파일명을 동적으로 생성
        output_csv_filename = f"{selected_week}_summary.csv"
        combined.to_csv(output_csv_filename, index=False)
        print(f"\n📦 전체 요약 파일: {output_csv_filename} 저장 완료.")
        return combined
    else:
        print("\n❗ 모든 사용자에 대한 분석에 실패했거나 유효한 커밋이 없습니다.")
        return pd.DataFrame()

# 스크립트 실행 부분
if __name__ == "__main__":
    ACCOUNT_FILE = "users_account.txt"
    WEEK_INFO_FILE = "week_information.txt"

    try:
        # 1. week_information.txt에서 선택 가능한 주차 목록 가져오기
        week_options = get_week_options(WEEK_INFO_FILE)
        
        # 2. 사용자에게 주차 선택 요청
        print("──────────────────────────────────")
        print("분석할 주차를 선택하세요:")
        for i, option in enumerate(week_options):
            print(f"  {i+1}. {option}")
        print("──────────────────────────────────")

        selected_index = -1
        while selected_index < 0 or selected_index >= len(week_options):
            try:
                choice = input(f"👉 번호를 입력하세요 (1-{len(week_options)}): ")
                selected_index = int(choice) - 1
                if not (0 <= selected_index < len(week_options)):
                    print("⚠️ 잘못된 번호입니다. 다시 입력해주세요.")
            except ValueError:
                print("⚠️ 숫자로 입력해야 합니다.")

        selected_week_label = week_options[selected_index]
        print(f"\n🚀 '{selected_week_label}' 주차 분석을 시작합니다...\n")

        # 3. 선택된 주차에 대한 분석 실행
        result_df = analyze_repositories_for_week(ACCOUNT_FILE, selected_week_label)

        # 4. 분석 결과가 있으면 HTML 파일로 저장
        if not result_df.empty:
            # HTML 파서에 전달할 주차 정보(라벨, 시작일, 종료일) 로드
            week_info = load_week_range(WEEK_INFO_FILE, selected_week_label)
            output_html_filename = f"{selected_week_label}_summary.html"
            report_title = f"{selected_week_label} 주차 커밋 통계"
            save_dataframe_as_html(result_df, week_info, output_path=output_html_filename, title=report_title)

    except FileNotFoundError:
        print(f"❌ 오류: '{WEEK_INFO_FILE}' 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 예상치 못한 오류 발생: {e}")