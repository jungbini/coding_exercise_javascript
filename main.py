import pandas as pd
import sys, os
from git_analyzer import analyze_commits, get_week_options, load_week_range
from html_parser import save_dataframe_as_html


def load_token(file_path="token.txt"):
    """
    파일에서 GitHub 토큰을 읽어옵니다.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"❌ 오류: '{file_path}' 파일을 찾을 수 없습니다. 토큰 파일을 생성해주세요.")
        sys.exit(1)


def analyze_repositories_for_week(account_file, token, selected_week, branch="main"):
    """
    학생 이메일 목록 파일을 읽어와서, 전달받은 토큰으로 저장소를 분석합니다.
    """
    try:
        with open(account_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ 오류: '{account_file}' 파일을 찾을 수 없습니다. 학생 이메일 목록 파일이 있는지 확인하세요.")
        sys.exit(1)

    all_results = []

    # account_file에서 이메일 목록을 한 줄씩 읽어옵니다.
    for line in lines:
        email = line.strip()
        if not email:
            continue
        try:
            # 이메일에서 사용자 ID와 표시할 이름을 추출합니다.
            user_id = email.split('@')[0]
            username = user_id

            # 추출된 user_id로 GitHub 저장소 이름을 생성합니다.
            repo_name = f"homework-{selected_week}-{user_id}"
            github_url = f"https://github.com/computer-sunmoon/{repo_name}"

            print(f"🔍 분석 중: {username} ({github_url})")
            
            # analyze_commits 호출 시, 미리 읽어둔 토큰을 사용합니다.
            df = analyze_commits(
                github_url=github_url,
                token=token,                    # 미리 읽어온 교사 토큰
                username=username,              # 보고서 표시용 이름
                author_email=email,             # 커밋 필터링용 이메일
                selected_week=selected_week,
                directory=f"lib/{selected_week}/",
                exclude_first_commit=True
            )
            
            if not df.empty:
                all_results.append(df)
            else:
                print(f"⚠️  {username} 에 대한 커밋 데이터가 없습니다.")
        except Exception as e:
            print(f"❌ 오류 발생 (사용자: {email}): {e}")

    if all_results:
        combined = pd.concat(all_results, ignore_index=True)
        return combined
    else:
        print("\n❗ 모든 사용자에 대한 분석에 실패했거나 유효한 커밋이 없습니다.")
        return pd.DataFrame()


# --- 스크립트 실행 부분 ---
if __name__ == "__main__":
    TOKEN_FILE = "token.txt"
    ACCOUNT_FILE = "users_account.txt"
    WEEK_INFO_FILE = "week_information.txt"

    try:
        # 1. 스크립트 시작 시 토큰을 먼저 로드합니다.
        teacher_token = load_token(TOKEN_FILE)
        
        # 2. week_information.txt에서 선택 가능한 주차 목록 가져오기
        week_options = get_week_options(WEEK_INFO_FILE)
        
        # 3. 사용자에게 주차 선택 요청
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

        # 4. 선택된 주차에 대한 분석 실행 (로드한 토큰을 전달)
        result_df = analyze_repositories_for_week(ACCOUNT_FILE, teacher_token, selected_week_label)

        # 5. 분석 결과가 있으면 HTML 파일로 저장
        if not result_df.empty:
            week_info = load_week_range(WEEK_INFO_FILE, selected_week_label)
            output_html_filename = f"{selected_week_label}_summary.html"
            report_title = f"{selected_week_label} 주차 커밋 통계"
            save_dataframe_as_html(result_df, week_info, output_path=output_html_filename, title=report_title)

    except FileNotFoundError:
        print(f"❌ 오류: '{WEEK_INFO_FILE}' 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 예상치 못한 오류 발생: {e}")