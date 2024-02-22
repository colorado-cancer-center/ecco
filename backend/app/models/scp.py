"""
Models derived from scraped data from statecancerprofiles.cancer.gov
"""
from typing import Optional

from sqlmodel import Field, SQLModel

class COIncidenceData(SQLModel):
    id: Optional[int] = Field(default=None, nullable=False, primary_key=True)
    
    county : str = Field()
    fips : str = Field(index=True)
    in_co : bool = Field()
    age_adjusted_incidence_raterate_note___cases_per_100_000 : float = Field()
    lower_95pct_confidence_interval : str = Field()
    upper_95pct_confidence_interval : str = Field()
    ci_rankrank_note : Optional[str] = Field(nullable=True)
    lower_ci_ci_rank : int = Field()
    upper_ci_ci_rank : int = Field()
    average_annual_count : int = Field()
    recent_trend : Optional[str] = Field(nullable=True)
    recent_5_year_trend_trend_note_in_incidence_rates : Optional[float] = Field(nullable=True)
    lower_95pct_confidence_interval_1 : Optional[str] = Field(nullable=True)
    upper_95pct_confidence_interval_1 : Optional[str] = Field(nullable=True)
    year : str = Field()
    sex : str = Field(index=True)
    stage : str = Field(index=True)
    race : str = Field(index=True)
    cancer : str = Field(index=True)
    areatype : str = Field(index=True)
    age : str = Field(index=True)
    state_fips : str = Field(index=True)
    _extracted_at : float = Field()
    url : str = Field()
    percent_of_cases_with_late_stage : Optional[float] = Field(nullable=True)
