from app.services.normalization_service import NormalizationService
from app.domain.enums import BusinessStatus
from datetime import date

def test_normalize_tax_code():
    assert NormalizationService.normalize_tax_code("010 123 4567") == "0101234567"
    assert NormalizationService.normalize_tax_code("invalid") is None

def test_normalize_business_name():
    assert NormalizationService.normalize_business_name("  CÔNG   TY  ABC  ") == "CÔNG TY ABC"

def test_parse_date():
    assert NormalizationService.parse_date("28/05/2026") == date(2026, 5, 28)
    assert NormalizationService.parse_date("2026-05-28") == date(2026, 5, 28)

def test_normalize_status():
    assert NormalizationService.normalize_status("Đang hoạt động (đã được cấp GCN ĐKT)") == BusinessStatus.ACTIVE
    assert NormalizationService.normalize_status("Tạm ngừng kinh doanh") == BusinessStatus.SUSPENDED
