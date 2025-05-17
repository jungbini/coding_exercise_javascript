import pandas as pd
from git_analyzer import analyze_commits_in_directory
from html_parser import save_dataframe_as_html

def analyze_multiple_users(account_file, branch="main"):
    with open(account_file, "r") as f:
        lines = f.readlines()

    all_results = []

    for line in lines:
        if not line.strip():
            continue
        try:
            github_url, token, username = line.strip().split(",")
            print(f"\n🔍 분석 중: {username} ({github_url})")
            df = analyze_commits_in_directory(github_url, token, username, directory="lib/")
            if not df.empty:
                all_results.append(df)
            else:
                print(f"⚠️  {username} 에 대한 커밋 데이터 없음.")
        except Exception as e:
            print(f"❌ 오류 발생 (줄 내용: {line.strip()}): {e}")

    if all_results:
        combined = pd.concat(all_results, ignore_index=True)
        combined.to_csv("all_users_summary.csv", index=False)
        print("\n📦 전체 요약 파일: all_users_summary.csv 저장 완료.")
        return combined
    else:
        print("\n❗ 모든 사용자 분석에 실패하거나 커밋 없음.")
        return pd.DataFrame()


result_df = analyze_multiple_users("users_account.txt")
if not result_df.empty:
    save_dataframe_as_html(result_df)