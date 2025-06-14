import requests
import pandas as pd
import time
import re
import difflib
import os
from datetime import datetime, timedelta

def extract_repo_info(url):
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)", url)
    if match:
        return match.group(1), match.group(2)
    else:
        raise ValueError("잘못된 GitHub 저장소 주소입니다. 예: https://github.com/owner/repo")

def calculate_result(count):
    if count == 1:
        return "fail"
    elif 2 <= count < 5:
        return "warning"
    else:
        return "success"

def fetch_loc(repo_owner, repo_name, branch, filename, headers):
    raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/{filename}"
    try:
        resp = requests.get(raw_url, headers=headers)
        if resp.status_code == 200:
            return resp.text.count("\n") + 1
        else:
            return None
    except:
        return None

def calculate_similarity(local_code: str, remote_code: str) -> float:
    matcher = difflib.SequenceMatcher(None, local_code, remote_code)
    return round(matcher.ratio() * 100, 2)

def fetch_similarity(repo_owner, repo_name, branch, filename, headers, local_base_dir="lib"):
    local_path = os.path.join(local_base_dir, filename[len("lib/"):])
    if not os.path.exists(local_path):
        return None
    try:
        with open(local_path, "r", encoding="utf-8") as f:
            local_code = f.read()
        raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/{filename}"
        resp = requests.get(raw_url, headers=headers)
        if resp.status_code == 200:
            remote_code = resp.text
            return calculate_similarity(local_code, remote_code)
        else:
            return None
    except:
        return None

def calculate_duration(start_time, end_time):
    duration = end_time - start_time
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours)}시간 {int(minutes)}분"

def load_week_range(file_path="week_information.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        line = f.readline().strip()
        label, start_str, end_str = line.split(",")
        start = datetime.strptime(start_str.strip(), "%Y-%m-%d")
        end = datetime.strptime(end_str.strip(), "%Y-%m-%d")
        return label, start, end

def analyze_commits(github_url, token, username, directory="lib/", branch="main", start_date=None, end_date=None, exclude_first_commit=False):
    repo_owner, repo_name = extract_repo_info(github_url)
    week_label, start_filter, end_filter = load_week_range()

    base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    params = {
        "per_page": 100,
        "author": username
    }

    raw_data = []
    page = 1

    while True:
        params["page"] = page
        res = requests.get(base_url, headers=headers, params=params)
        commits = res.json()
        if not commits:
            break

        for commit in commits:
            sha = commit["sha"]
            detail_url = f"{base_url}/{sha}"
            detail_res = requests.get(detail_url, headers=headers)
            if detail_res.status_code != 200:
                continue

            detail = detail_res.json()
            date_raw = detail["commit"]["author"]["date"]
            utc_date = datetime.strptime(date_raw, "%Y-%m-%dT%H:%M:%SZ")
            date = utc_date + timedelta(hours=9)

            if not (start_filter <= date <= end_filter):
                continue

            html_url = detail.get("html_url")

            for f in detail.get("files", []):
                filepath = f["filename"]
                status = f.get("status", "")
                if filepath.startswith(directory) and status != "removed":
                    raw_data.append({
                        "user": username,
                        "date": date,
                        "filename": filepath,
                        "total_changes": f.get("changes", 0),
                        "additions": f.get("additions", 0),
                        "deletions": f.get("deletions", 0),
                        "status": status,
                        "url": html_url
                    })

            time.sleep(0.2)
        page += 1

    if not raw_data:
        print(f"⚠️ No commits found in directory '{directory}' for user '{username}' in selected week.")
        return pd.DataFrame()

    df = pd.DataFrame(raw_data)

    if exclude_first_commit:
        df["rank"] = df.groupby("filename")["date"].rank(method="first")
        df = df[~((df["rank"] == 1) & (df.groupby("filename")["filename"].transform("count") > 1))]
        df.drop(columns=["rank"], inplace=True)

    grouped_time = df.groupby("filename").agg(
        first_date=("date", "min"),
        last_date=("date", "max")
    ).reset_index()
    grouped_time["코딩 시간"] = grouped_time.apply(lambda row: calculate_duration(row["first_date"], row["last_date"]), axis=1)

    latest_info = df.sort_values("date").groupby("filename").last().reset_index()

    summary = df.groupby("filename").agg(
        user=("user", "first"),
        date=("date", "max"),
        total_changes_mean=("total_changes", "mean"),
        additions_mean=("additions", "mean"),
        deletions_mean=("deletions", "mean"),
        commit_count=("filename", "count")
    ).reset_index()

    summary = summary.merge(latest_info[["filename", "status", "url"]], on="filename", how="left")
    summary = summary.merge(grouped_time[["filename", "코딩 시간"]], on="filename", how="left")

    summary["loc"] = summary["filename"].apply(lambda f: fetch_loc(repo_owner, repo_name, branch, f, headers))
    summary = summary[summary["loc"].notnull()]
    summary["loc"] = summary["loc"].astype(int)

    summary["code_similarity"] = summary["filename"].apply(lambda f: fetch_similarity(repo_owner, repo_name, branch, f, headers))
    summary["date"] = pd.to_datetime(summary["date"]).dt.strftime("%Y-%m-%d %H:%M")
    summary["result"] = summary["commit_count"].apply(calculate_result)

    summary["파일명 (총 커밋 수)"] = summary.apply(
        lambda row: f'<a href="{row["url"]}" target="_blank">{row["filename"]} ({row["commit_count"]})</a>', axis=1)

    summary = summary.round({
        "total_changes_mean": 2,
        "additions_mean": 2,
        "deletions_mean": 2,
        "code_similarity": 2
    })

    summary["평균 수정 라인 수 (+/-)"] = summary.apply(
        lambda row: f'{row["total_changes_mean"]} ({row["additions_mean"]}/{row["deletions_mean"]})', axis=1
    )

    summary.drop(columns=["filename", "url", "commit_count", "total_changes_mean", "additions_mean", "deletions_mean"], inplace=True)

    summary.rename(columns={
        "date": "최근 커밋일시",
        "status": "상태",
        "code_similarity": "코드 유사도",
        "result": "평가"
    }, inplace=True)

    summary = summary[[
        "user", "파일명 (총 커밋 수)", "최근 커밋일시", "상태",
        "평균 수정 라인 수 (+/-)", "코드 유사도", "코딩 시간", "평가"
    ]]

    return summary