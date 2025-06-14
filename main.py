# main.py

def analyze_repositories_for_week(account_file, selected_week, branch="main"):
    """
    선택된 주차에 대해 여러 사용자의 저장소를 분석합니다.
    users_account.txt는 '이메일,토큰' 형식을 따라야 합니다.
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
            # 1. 변경된 형식에 맞게 '이메일'과 '토큰'만 읽어옵니다.
            email, token = line.strip().split(",")

            # 2. 이메일에서 사용자 ID와 표시할 이름을 추출합니다. (예: 'jungbini@...' -> 'jungbini')
            user_id = email.split('@')[0]
            username = user_id  # 보고서에 표시될 이름으로 사용자 ID를 사용합니다.

            # 3. 추출된 user_id로 GitHub 저장소 이름을 생성합니다.
            repo_name = f"homework-{selected_week}-{user_id}"
            github_url = f"https://github.com/computer-sunmoon/{repo_name}" # .git은 제거하는 것이 좋습니다.

            print(f"🔍 분석 중: {username} ({github_url})")
            
            # 4. analyze_commits 호출 시, username과 email을 명확히 전달합니다.
            df = analyze_commits(
                github_url=github_url,
                token=token,
                username=username,              # 보고서 표시용 이름 (예: 'jungbini')
                author_email=email,             # 커밋 필터링용 이메일 주소
                selected_week=selected_week,
                directory=f"{selected_week}/",
                exclude_first_commit=True
            )
            
            if not df.empty:
                all_results.append(df)
            else:
                print(f"⚠️  {username} 에 대한 커밋 데이터가 없습니다.")
        except ValueError:
            print(f"❌ 오류: '{line.strip()}' 라인이 '이메일,토큰' 형식이 아닙니다. 확인해주세요.")
        except Exception as e:
            print(f"❌ 오류 발생 (사용자: {line.strip().split(',')[0]}): {e}")

    if all_results:
        combined = pd.concat(all_results, ignore_index=True)
        output_csv_filename = f"{selected_week}_summary.csv"
        combined.to_csv(output_csv_filename, index=False)
        print(f"\n📦 전체 요약 파일: {output_csv_filename} 저장 완료.")
        return combined
    else:
        print("\n❗ 모든 사용자에 대한 분석에 실패했거나 유효한 커밋이 없습니다.")
        return pd.DataFrame()