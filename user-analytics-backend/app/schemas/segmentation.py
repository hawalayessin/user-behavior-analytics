from pydantic import BaseModel
from typing import List, Optional


class ClusterPoint(BaseModel):
    """Single point in 2D clustering space"""
    x: float
    y: float
    segment: str


class SegmentDistribution(BaseModel):
    """Distribution of users across segments"""
    name: str
    percentage: float
    count: Optional[int] = None


class SegmentProfile(BaseModel):
    """Detailed profile of a segment"""
    segment: str
    avg_duration: str
    arpu: float
    churn_rate: float


class KPIResponse(BaseModel):
    """KPI metrics for segmentation"""
    total_segments: int
    dominant_segment: str
    dominant_pct: float
    high_value_segment: str
    arpu_premium: float
    risk_segment: str
    risk_churn_rate: float


class ClustersResponse(BaseModel):
    """Clustering data response"""
    clusters: List[ClusterPoint]
    distribution: List[SegmentDistribution]


class ProfilesResponse(BaseModel):
    """Segment profiles response"""
    profiles: List[SegmentProfile]


class TrainResponse(BaseModel):
    """Model training response"""
    status: str
    message: str
