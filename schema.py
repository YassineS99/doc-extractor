from typing import Optional
from pydantic import BaseModel, Field


class EquipmentSpec(BaseModel):
    equipment_name: str = Field(
        description="Name or type of the equipment, as written in the document."
    )
    manufacturer: Optional[str] = Field(
        default=None,
        description="Full company name of the manufacturer as printed in the footer or imprint (for example ending in GmbH or Ltd), not logo text.",
    )
    model_number: Optional[str] = Field(
        default=None,
        description="Model or type code of this one product.",
    )
    power_kw: Optional[float] = Field(
        default=None,
        gt=0,
        description="Rated power or power consumption of the equipment in kW. "
        "Convert W to kW. Use null if the document does not state it.",
    )
    voltage_v: Optional[float] = Field(
        default=None,
        gt=0,
        description="Main supply voltage in volts. If several supply options "
        "are listed, use the first one.",
    )
    weight_kg: Optional[float] = Field(
        default=None,
        gt=0,
        description="Weight of the equipment in kg.",
    )
    max_temp_c: Optional[float] = Field(
        default=None,
        description="Maximum operating temperature the EQUIPMENT itself is "
        "rated for. Do NOT use sensor measuring ranges or test ranges. "
        "Use null if the document does not state it.",
    )
    standards: list[str] = Field(
        default_factory=list,
        description="Standards the product complies with, by code only "
        "(for example ISO, IEC, EN, API, DIN). Do not include items "
        "marked as optional.",
    )
    
