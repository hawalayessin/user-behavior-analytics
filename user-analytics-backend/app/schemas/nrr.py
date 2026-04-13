from pydantic import BaseModel


class NRRResponse(BaseModel):
    nrr_percent: float
    revenue_start: float
    revenue_renewed: float
    revenue_churned: float
    revenue_expansion: float
    period_label: str
    calculated_at: str
