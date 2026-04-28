"""Chart data API routes for ECharts visualization."""

from fastapi import APIRouter, HTTPException

from models.chart import (
    ConsistencyRadar,
    HitPointHeatmap,
    IssueStatistics,
    ServeHeightData,
)
from services.chart_service import (
    get_consistency_radar,
    get_hit_point_heatmap,
    get_issue_statistics,
    get_serve_height_data,
)

router = APIRouter()


@router.get("/charts/{video_id}/serve-height", response_model=ServeHeightData)
async def serve_height_chart(video_id: str) -> ServeHeightData:
    """Get serve height data for line chart.

    Returns body.y_pct values for serve frames over time.
    Lower y_pct = higher serve height.

    Args:
        video_id: Unique video identifier

    Returns:
        ServeHeightData with frame_number, time_seconds, height_pct
    """
    try:
        return get_serve_height_data(video_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Video analysis not found: {video_id}")


@router.get("/charts/{video_id}/hit-points", response_model=HitPointHeatmap)
async def hit_points_chart(video_id: str) -> HitPointHeatmap:
    """Get hit point positions for scatter/heatmap visualization.

    Returns hand_l (racket hand) positions with issue markers.

    Args:
        video_id: Unique video identifier

    Returns:
        HitPointHeatmap with x_pct, y_pct, issue_type per frame
    """
    try:
        return get_hit_point_heatmap(video_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Video analysis not found: {video_id}")


@router.get("/charts/{video_id}/radar", response_model=ConsistencyRadar)
async def radar_chart(video_id: str) -> ConsistencyRadar:
    """Get 6-dimension consistency radar chart data.

    Dimensions: 击球技术, 步法移动, 身体旋转, 击球节奏, 体能分配, 战术执行

    Args:
        video_id: Unique video identifier

    Returns:
        ConsistencyRadar with dimension scores (0-10) and overall_score
    """
    try:
        return get_consistency_radar(video_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Video analysis not found: {video_id}")


@router.get("/charts/{video_id}/issues", response_model=IssueStatistics)
async def issue_stats_chart(video_id: str) -> IssueStatistics:
    """Get issue type statistics for bar chart.

    Counts occurrences of each issue_type with severity classification.

    Args:
        video_id: Unique video identifier

    Returns:
        IssueStatistics with stats, total_issues, total_frames
    """
    try:
        return get_issue_statistics(video_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Video analysis not found: {video_id}")