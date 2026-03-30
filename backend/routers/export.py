"""
Export Router - Generate downloadable reports
"""
import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
logger = logging.getLogger(__name__)


class ExportRequest(BaseModel):
    document_id: Optional[str] = None
    analysis_data: Optional[dict] = None
    format: str = "json"


@router.post("/export")
async def export_report(request: ExportRequest):
    """Export analysis report as JSON."""
    try:
        if request.analysis_data:
            data = request.analysis_data
        else:
            raise HTTPException(400, "No analysis data provided.")

        if request.format == "json":
            json_str = json.dumps(data, indent=2, default=str)
            return Response(
                content=json_str,
                media_type="application/json",
                headers={"Content-Disposition": "attachment; filename=legalcopilot-report.json"}
            )

        # Text report format
        lines = []
        lines.append("=" * 60)
        lines.append("LEGALCOPILOT - RISK ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append("")

        summary = data.get("summary", {})
        lines.append(f"Overall Risk Score: {data.get('overall_risk_score', 'N/A')}/100")
        lines.append(f"Risk Level: {summary.get('risk_level', 'N/A')}")
        lines.append(f"Total Clauses Analyzed: {summary.get('total_clauses', 'N/A')}")
        lines.append(f"Red Flags Found: {summary.get('red_flag_count', 0)}")
        lines.append("")
        lines.append("VERDICT:")
        lines.append(summary.get('verdict', 'N/A'))
        lines.append("")

        lines.append("KEY RISKS:")
        for risk in summary.get('key_risks', []):
            lines.append(f"  - {risk}")
        lines.append("")

        lines.append("RISK DISTRIBUTION:")
        dist = data.get('risk_distribution', {})
        lines.append(f"  Critical: {dist.get('critical', 0)}")
        lines.append(f"  High: {dist.get('high', 0)}")
        lines.append(f"  Medium: {dist.get('medium', 0)}")
        lines.append(f"  Low: {dist.get('low', 0)}")
        lines.append("")

        lines.append("CLAUSE ANALYSIS:")
        for clause in data.get('clauses', [])[:20]:
            lines.append("-" * 40)
            lines.append(f"Category: {clause.get('category', 'N/A')}")
            lines.append(f"Risk Level: {clause.get('risk_level', 'N/A')} ({clause.get('risk_score', 0)}/100)")
            lines.append(f"Impact: {clause.get('user_impact', 'N/A')}")
            lines.append(f"Explanation: {clause.get('explanation', 'N/A')}")
            lines.append("")

        report_text = "\n".join(lines)
        return Response(
            content=report_text,
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=legalcopilot-report.txt"}
        )

    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(500, f"Export failed: {str(e)}")
