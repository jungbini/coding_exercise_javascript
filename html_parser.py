from git_analyzer import load_week_range
import pandas as pd
import os

def save_dataframe_as_html(df, output_path="commit_summary.html", title="파일별 커밋 통계"):
    week_label, start_date, end_date = load_week_range()
    
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
        <th>파일명 (총 커밋 수)</th>
        <th>최근 커밋일시</th>
        <th>상태</th>
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
            html += f"<td class='filename-col'>{row['파일명 (총 커밋 수)']}</td>"
            html += f"<td>{row['최근 커밋일시']}</td>"
            html += f"<td>{row['상태']}</td>"
            html += f"<td>{row['평균 수정 라인 수 (+/-)']}</td>"
            html += f"<td>{row['코드 유사도']}</td>"
            html += f"<td>{row['코딩 시간']}</td>"
            html += f"<td style='{row['result_color']}'>{row['평가']}</td>"
            html += "</tr>"

    html += "</tbody></table></body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML 파일 저장 완료: {output_path}")
