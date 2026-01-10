"""PDF Service for generating reports with Korean language support."""
import io
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from src.app.schemas.report import ExpertReportData, SystemReportData


class PDFService:
    """Service for generating PDF reports.

    Uses Jinja2 templates for HTML generation and WeasyPrint for PDF conversion.
    Supports Korean text rendering with appropriate fonts.
    """

    # Template directory
    TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

    # Report storage directory (can be configured via environment)
    REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "/tmp/reports"))

    @classmethod
    def _get_jinja_env(cls) -> Environment:
        """Get Jinja2 environment with template directory."""
        # Create templates directory if not exists
        cls.TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        return Environment(
            loader=FileSystemLoader(str(cls.TEMPLATE_DIR)),
            autoescape=True,
        )

    @classmethod
    def _ensure_reports_dir(cls) -> Path:
        """Ensure reports directory exists."""
        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        return cls.REPORTS_DIR

    @classmethod
    def _get_expert_report_html(cls, data: ExpertReportData) -> str:
        """Generate HTML for expert evaluation report."""
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: 'Nanum Gothic', 'Malgun Gothic', sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 11pt;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #1e40af;
            margin: 0;
            font-size: 24pt;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 12pt;
            margin-top: 8px;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section-title {{
            font-size: 14pt;
            color: #1e40af;
            border-bottom: 1px solid #ddd;
            padding-bottom: 8px;
            margin-bottom: 15px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        .info-item {{
            padding: 8px 0;
        }}
        .info-label {{
            font-weight: bold;
            color: #555;
        }}
        .score-box {{
            background: linear-gradient(135deg, #2563eb, #1e40af);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        }}
        .score-main {{
            font-size: 36pt;
            font-weight: bold;
        }}
        .score-detail {{
            font-size: 12pt;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background: #f3f4f6;
            font-weight: bold;
            color: #374151;
        }}
        .progress-bar {{
            background: #e5e7eb;
            border-radius: 4px;
            height: 8px;
            overflow: hidden;
        }}
        .progress-fill {{
            background: #2563eb;
            height: 100%;
            transition: width 0.3s;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            font-size: 10pt;
            color: #666;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 10pt;
            font-weight: bold;
        }}
        .badge-success {{
            background: #dcfce7;
            color: #166534;
        }}
        .badge-warning {{
            background: #fef3c7;
            color: #92400e;
        }}
        .badge-info {{
            background: #dbeafe;
            color: #1e40af;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>전문가 평가 보고서</h1>
        <div class="subtitle">AX 코칭단 평가 시스템</div>
    </div>

    <div class="section">
        <h2 class="section-title">전문가 정보</h2>
        <div class="info-grid">
            <div class="info-item">
                <span class="info-label">이름:</span> {data.expert_name}
            </div>
            <div class="info-item">
                <span class="info-label">이메일:</span> {data.email}
            </div>
            <div class="info-item">
                <span class="info-label">연락처:</span> {data.phone or '-'}
            </div>
            <div class="info-item">
                <span class="info-label">전문분야:</span> {data.specialty or '-'}
            </div>
            <div class="info-item">
                <span class="info-label">소속:</span> {data.organization or '-'}
            </div>
        </div>
    </div>

    <div class="section">
        <h2 class="section-title">종합 점수</h2>
        <div class="score-box">
            <div class="score-main">{data.score_summary.percentage:.1f}%</div>
            <div class="score-detail">
                {data.score_summary.total_score:.1f} / {data.score_summary.max_possible_score:.1f}점
            </div>
            {f'<div class="score-detail">전체 {data.score_summary.rank}위 (상위 {data.score_summary.percentile:.1f}%)</div>' if data.score_summary.rank else ''}
        </div>
    </div>

    <div class="section">
        <h2 class="section-title">카테고리별 점수</h2>
        <table>
            <thead>
                <tr>
                    <th>카테고리</th>
                    <th>점수</th>
                    <th>비율</th>
                    <th>진행률</th>
                </tr>
            </thead>
            <tbody>
                {''.join(f'''
                <tr>
                    <td>{cat.category_name}</td>
                    <td>{cat.score:.1f} / {cat.max_score:.1f}</td>
                    <td>{cat.percentage:.1f}%</td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {cat.percentage}%"></div>
                        </div>
                    </td>
                </tr>
                ''' for cat in data.category_scores)}
            </tbody>
        </table>
    </div>

    {'<div class="section"><h2 class="section-title">상세 답변</h2><table><thead><tr><th>문항</th><th>유형</th><th>점수</th><th>코멘트</th></tr></thead><tbody>' + ''.join(f"<tr><td>{ans.question_content[:50]}...</td><td>{ans.question_type}</td><td>{ans.score or '-'} / {ans.max_score}</td><td>{ans.grader_comment or '-'}</td></tr>" for ans in data.answer_details[:20]) + '</tbody></table></div>' if data.answer_details else ''}

    <div class="footer">
        <p>보고서 생성일: {data.generated_at.strftime('%Y년 %m월 %d일 %H:%M')}</p>
        <p>AX 코칭단 평가 시스템</p>
    </div>
</body>
</html>
"""
        return html

    @classmethod
    def _get_system_report_html(cls, data: SystemReportData) -> str:
        """Generate HTML for system summary report."""
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: 'Nanum Gothic', 'Malgun Gothic', sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 11pt;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #1e40af;
            margin: 0;
            font-size: 24pt;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section-title {{
            font-size: 14pt;
            color: #1e40af;
            border-bottom: 1px solid #ddd;
            padding-bottom: 8px;
            margin-bottom: 15px;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
        }}
        .stat-box {{
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }}
        .stat-value {{
            font-size: 24pt;
            font-weight: bold;
            color: #1e40af;
        }}
        .stat-label {{
            font-size: 10pt;
            color: #64748b;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background: #f3f4f6;
            font-weight: bold;
        }}
        .progress-bar {{
            background: #e5e7eb;
            border-radius: 4px;
            height: 8px;
        }}
        .progress-fill {{
            background: #2563eb;
            height: 100%;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            font-size: 10pt;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>평가 시스템 종합 보고서</h1>
    </div>

    <div class="section">
        <h2 class="section-title">전문가 현황</h2>
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-value">{data.total_experts}</div>
                <div class="stat-label">전체 전문가</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{data.experts_with_submissions}</div>
                <div class="stat-label">제출 완료</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{data.fully_graded_experts}</div>
                <div class="stat-label">채점 완료</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{data.average_expert_score:.1f}%</div>
                <div class="stat-label">평균 점수</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2 class="section-title">답변 현황</h2>
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-value">{data.total_questions}</div>
                <div class="stat-label">전체 문항</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{data.total_answers}</div>
                <div class="stat-label">전체 답변</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{data.graded_answers}</div>
                <div class="stat-label">채점 완료</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{data.pending_answers}</div>
                <div class="stat-label">채점 대기</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2 class="section-title">카테고리별 현황</h2>
        <table>
            <thead>
                <tr>
                    <th>카테고리</th>
                    <th>문항 수</th>
                    <th>답변 수</th>
                    <th>채점 완료</th>
                    <th>평균 점수</th>
                </tr>
            </thead>
            <tbody>
                {''.join(f'''
                <tr>
                    <td>{cat.category_name}</td>
                    <td>{cat.total_questions}</td>
                    <td>{cat.total_answers}</td>
                    <td>{cat.graded_answers}</td>
                    <td>{cat.average_score:.1f}%</td>
                </tr>
                ''' for cat in data.category_summaries)}
            </tbody>
        </table>
    </div>

    {'''<div class="section">
        <h2 class="section-title">점수 분포</h2>
        <table>
            <thead>
                <tr>
                    <th>점수 구간</th>
                    <th>인원</th>
                    <th>비율</th>
                </tr>
            </thead>
            <tbody>''' + ''.join(f"<tr><td>{d.range_start:.0f}% ~ {d.range_end:.0f}%</td><td>{d.count}명</td><td>{d.percentage:.1f}%</td></tr>" for d in data.score_distribution) + '''
            </tbody>
        </table>
    </div>''' if data.score_distribution else ''}

    <div class="footer">
        <p>보고서 생성일: {data.generated_at.strftime('%Y년 %m월 %d일 %H:%M')}</p>
        <p>AX 코칭단 평가 시스템</p>
    </div>
</body>
</html>
"""
        return html

    @classmethod
    async def generate_expert_report(
        cls,
        data: ExpertReportData,
    ) -> bytes:
        """Generate PDF for an expert evaluation report.

        Args:
            data: Expert report data

        Returns:
            PDF content as bytes
        """
        try:
            from weasyprint import HTML
        except ImportError:
            # Fallback: return HTML as bytes if WeasyPrint is not available
            html_content = cls._get_expert_report_html(data)
            return html_content.encode("utf-8")

        html_content = cls._get_expert_report_html(data)
        pdf_buffer = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer.read()

    @classmethod
    async def generate_summary_report(
        cls,
        data: SystemReportData,
    ) -> bytes:
        """Generate PDF for a system summary report.

        Args:
            data: System report data

        Returns:
            PDF content as bytes
        """
        try:
            from weasyprint import HTML
        except ImportError:
            html_content = cls._get_system_report_html(data)
            return html_content.encode("utf-8")

        html_content = cls._get_system_report_html(data)
        pdf_buffer = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer.read()

    @classmethod
    async def save_report_file(
        cls,
        content: bytes,
        filename: str,
    ) -> str:
        """Save report content to file and return the file path.

        Args:
            content: PDF or report content
            filename: Filename to save as

        Returns:
            Full file path
        """
        reports_dir = cls._ensure_reports_dir()
        file_path = reports_dir / filename

        with open(file_path, "wb") as f:
            f.write(content)

        return str(file_path)
