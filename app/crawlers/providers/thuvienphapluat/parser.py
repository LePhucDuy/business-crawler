from bs4 import BeautifulSoup
from app.crawlers.parsers.base_parser import BaseBusinessParser
from app.crawlers.parsers.html_utils import find_label_value
from app.domain.normalized import BusinessProfileNormalized
from app.services.normalization_service import NormalizationService
from datetime import datetime

class ThuvienphapluatParser(BaseBusinessParser):
    provider_name = "thuvienphapluat"

    def parse_detail_page(self, html: str, source_url: str) -> BusinessProfileNormalized:
        soup = BeautifulSoup(html, "lxml")
        
        tax_code = find_label_value(soup, ["Mã số thuế", "MST"])
        
        if not tax_code:
            return BusinessProfileNormalized(
                source_name=self.provider_name,
                source_url=source_url,
                crawled_at=datetime.utcnow()
            )
            
        business_name = find_label_value(soup, ["Tên doanh nghiệp", "Tên công ty"])
        if not business_name:
            h1 = soup.find("h1")
            if h1:
                business_name = self.normalize_whitespace(h1.get_text())
                
        address = find_label_value(soup, ["Địa chỉ", "Trụ sở"])
        representative = find_label_value(soup, ["Người đại diện", "Đại diện pháp luật"])
        status = find_label_value(soup, ["Tình trạng", "Trạng thái", "Tình trạng hoạt động"])
        issued_date_str = find_label_value(soup, ["Ngày cấp", "Ngày hoạt động", "Ngày thành lập"])
        
        tax_authority = find_label_value(soup, ["Cơ quan thuế quản lý", "Nơi đăng ký quản lý"])
        business_type = find_label_value(soup, ["Loại hình doanh nghiệp", "Loại hình"])
        industry = find_label_value(soup, ["Ngành nghề kinh doanh", "Ngành nghề chính"])
        
        issued_date = NormalizationService.parse_date(issued_date_str) if issued_date_str else None

        profile = BusinessProfileNormalized(
            tax_code=NormalizationService.normalize_tax_code(tax_code),
            business_name=business_name,
            normalized_business_name=NormalizationService.normalize_business_name(business_name),
            address=address,
            normalized_address=NormalizationService.normalize_address(address),
            legal_representative=representative,
            normalized_legal_representative=NormalizationService.normalize_legal_representative(representative),
            status=NormalizationService.normalize_status(status),
            tax_authority=tax_authority,
            business_type=business_type,
            industry=industry,
            issued_date=issued_date,
            source_name=self.provider_name,
            source_url=source_url,
            crawled_at=datetime.utcnow()
        )
        return profile
