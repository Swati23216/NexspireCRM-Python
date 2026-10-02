from pydantic import BaseModel


class LeadReport(BaseModel):
    total_leads: int
    new_leads: int
    contacted_leads: int
    qualified_leads: int
    converted_leads: int
    lost_leads: int


class OpportunityReport(BaseModel):
    total_opportunities: int
    total_pipeline: float
    won_opportunities: int
    won_revenue: float
    lost_opportunities: int
    lost_value: float


class ActivityReport(BaseModel):
    total_activities: int
    pending_activities: int
    completed_activities: int
    overdue_activities: int


class TicketReport(BaseModel):
    total_tickets: int
    open_tickets: int
    pending_tickets: int
    resolved_tickets: int
    closed_tickets: int


class SalesReport(BaseModel):
    total_pipeline: float
    won_revenue: float
    lost_value: float
    win_rate: float


class PerformanceReport(BaseModel):
    total_leads: int
    total_opportunities: int
    total_activities: int
    total_tickets: int
    won_revenue: float