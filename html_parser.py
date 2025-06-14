import pandas as pd
import os

def save_dataframe_as_html(df, week_info, output_path="commit_summary.html", title="파일별 커밋 통계"):
    """
    DataFrame을 HTML 파일로 저장합니다. week_info 튜플(라벨, 시작일, 종료일)을 직접 받습니다.
    """
    week_label, start_date, end_date = week_info

    # 평가 결과에 따른 배경색 설정
    df["result_color"] = df["평가"].map({
        "fail": "background-color: #ffdddd;",
        "warning": "background-color: #fffacc;",
        "success": "background-color: #ddffdd;"
    })

    # git_analyzer에서 추가된 week_label을 그대로 사용하므로, 여기서는 별도 계산이 필요 없습니다.
    # 단지 그룹화를 위해 컬럼을 유지합니다.

    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }}
        table {{ border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
        th {{ background-color: #f2f2f2; }}
        td.filename-col {{ text-align: left; }}
        h2 {{ color: #333; }}
    </style>
    </head>
    <body>
    <h2>{title}</h2>
    <table>
    <thead>
    <tr>
        <th>주차</th>
        <th>User</th>
        <th>파일명 (총 커밋 수)</th>
        <th>최근 커밋일시</th>
        <th>상태</th>
        <th>평균 수정 라인 수 (+/-)</th>
        <th>코드 유사도 (%)</th>
        <th>코딩 시간</th>
        <th>평가</th>
    </tr>
    </thead>
    <tbody>
    """
    # 주차와 사용자로 그룹화하여 테이블 생성
    grouped = df.groupby(["week_label", "user"])
    for (week, user), group in grouped:
        rowspan = len(group)
        # 그룹 내에서 최근 커밋일시 순으로 정렬
        sorted_group = group.sort_values(by="최근 커밋일시", ascending=False)
        for idx, row in sorted_group.iterrows():
            html += "<tr>"
            # 그룹의 첫 번째 행일 때만 주차와 사용자 셀을 병합하여 표시
            if idx == sorted_group.index[0]:
                html += f"<td rowspan='{rowspan}'>{week}</td>"
                html += f"<td rowspan='{rowspan}'>{user}</td>"
            
            # 나머지 데이터 셀 추가
            html += f"<td class='filename-col'>{row['파일명 (총 커밋 수)']}</td>"
            html += f"<td>{row['최근 커밋일시']}</td>"
            html += f"<td>{row['상태']}</td>"
            html += f"<td>{row['평균 수정 라인 수 (+/-)']}</td>"
            # 코드 유사도 값이 있는 경우에만 표시
            similarity = f"{row['코드 유사도']:.2f}" if pd.notnull(row['코드 유사도']) else "N/A"
            html += f"<td>{similarity}</td>"
            html += f"<td>{row['코딩 시간']}</td>"
            html += f"<td style='{row['result_color']}'>{row['평가']}</td>"
            html += "</tr>"

    html += "</tbody></table></body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML 리포트 저장 완료: {output_path}")