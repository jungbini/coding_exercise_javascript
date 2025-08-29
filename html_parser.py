from git_analyzer import load_week_range
import pandas as pd
import os
import re


def _split_filename_and_count(cell: str):
    """
    '<a href="...">path/to/file.py (3)</a>' 형태나 'path/to/file.py (3)' 형태에서
    파일명(anchor 유지)과 정수 커밋 수를 분리합니다.
    """
    if pd.isna(cell):
        return cell, None

    s = str(cell)
    href = None
    # href 추출 (있을 경우)
    m_href = re.search(r'href="([^"]+)"', s)
    if m_href:
        href = m_href.group(1)

    # 앵커 안에 '파일명 (숫자)' 형태
    m = re.search(r'>(.*?)\s*\((\d+)\)\s*</a>\s*$', s)
    if m:
        filename_text = m.group(1).strip()
        count = int(m.group(2))
        anchor = f'<a href="{href}" target="_blank">{filename_text}</a>' if href else filename_text
        return anchor, count

    # 일반 텍스트 '파일명 (숫자)' 형태
    m2 = re.search(r'^(.*?)\s*\((\d+)\)\s*$', s)
    if m2:
        filename_text = m2.group(1).strip()
        count = int(m2.group(2))
        anchor = f'<a href="{href}" target="_blank">{filename_text}</a>' if href else filename_text
        return anchor, count

    # 숫자를 못 찾으면 앵커 안의 텍스트만 파일명으로
    m3 = re.search(r'>(.*?)</a>', s)
    if m3:
        filename_text = m3.group(1).strip()
        anchor = f'<a href="{href}" target="_blank">{filename_text}</a>' if href else filename_text
        return anchor, None

    return s, None


def save_dataframe_as_html(df, output_path="commit_summary.html", title="파일별 커밋 통계"):
    week_label, start_date, end_date = load_week_range()

    # ✅ 입력 df에 '파일명 (총 커밋 수)'가 있다면 '파일명', '총 커밋 수'로 분리
    if "파일명 (총 커밋 수)" in df.columns:
        filenames = []
        counts = []
        for val in df["파일명 (총 커밋 수)"]:
            name_anchor, cnt = _split_filename_and_count(val)
            filenames.append(name_anchor)
            counts.append(cnt if cnt is not None else 0)
        df["파일명"] = filenames
        df["총 커밋 수"] = pd.Series(counts, index=df.index).astype(int)
        df.drop(columns=["파일명 (총 커밋 수)"], inplace=True)
    else:
        # '파일명'은 있는데 '총 커밋 수'가 없다면 0으로 초기화(안전망)
        if "파일명" in df.columns and "총 커밋 수" not in df.columns:
            df["총 커밋 수"] = 0

    df["result_color"] = df["평가"].map({
        "fail": "background-color: #ffdddd;",
        "warning": "background-color: #fffacc;",
        "success": "background-color: #ddffdd;"
    })

    df["최근 커밋일시(dt)"] = pd.to_datetime(df["최근 커밋일시"])
    df["week_label"] = df["최근 커밋일시(dt)"].apply(lambda d: week_label if start_date <= d <= end_date else "")
    df.drop(columns=["최근 커밋일시(dt)"], inplace=True)

    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        table {{
            border-collapse: collapse;
            width: 100%;
            font-family: Arial, sans-serif;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 8px;
            text-align: center;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        td.filename-col {{
            text-align: left;
        }}
    </style>
    </head>
    <body>
    <h2>{title}</h2>
    <table>
    <thead>
    <tr>
        <th>주차</th>
        <th>user</th>
        <th>파일명</th>
        <th>최근 커밋일시</th>
        <th>상태</th>
        <th>총 커밋 수</th>
        <th>평균 수정 라인 수 (+/-)</th>
        <th>코드 유사도</th>
        <th>코딩 시간</th>
        <th>평가</th>
    </tr>
    </thead>
    <tbody>
    """

    grouped = df.groupby(["week_label", "user"])
    for (week, user), group in grouped:
        rowspan = len(group)
        for idx, row in group.iterrows():
            html += "<tr>"
            if idx == group.index[0]:
                html += f"<td rowspan='{rowspan}'>{week}</td>"
                html += f"<td rowspan='{rowspan}'>{user}</td>"
            html += f"<td class='filename-col'>{row['파일명']}</td>"
            html += f"<td>{row['최근 커밋일시']}</td>"
            html += f"<td>{row['상태']}</td>"
            html += f"<td>{row['총 커밋 수']}</td>"
            html += f"<td>{row['평균 수정 라인 수 (+/-)']}</td>"
            html += f"<td>{row['코드 유사도']}</td>"
            html += f"<td>{row['코딩 시간']}</td>"
            html += f"<td style='{row['result_color']}'>{row['평가']}</td>"
            html += "</tr>"

    html += "</tbody></table></body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML 파일 저장 완료: {output_path}")
