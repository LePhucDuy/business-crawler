from bs4 import BeautifulSoup
from app.crawlers.parsers.base_parser import BaseBusinessParser
from app.crawlers.parsers.html_utils import find_label_value
from app.domain.normalized import BusinessProfileNormalized
from app.services.normalization_service import NormalizationService
from datetime import datetime

class MasothueParser(BaseBusinessParser):
    provider_name = "masothue"

    def parse_detail_page(self, html: str, source_url: str) -> BusinessProfileNormalized:
        soup = BeautifulSoup(html, "lxml")
        
        # Defensive parsing
        tax_code = find_label_value(soup, ["Mã số thuế"])
        
        # If we couldn't find a tax code, we might have been redirected to the home page or a search list
        if not tax_code:
            # Return an empty profile; the service will handle this as a 'not found'
            return BusinessProfileNormalized(
                source_name=self.provider_name,
                source_url=source_url,
                crawled_at=datetime.utcnow()
            )
            
        business_name = find_label_value(soup, ["Tên công ty", "Tên doanh nghiệp", "Tên giao dịch"])
        if not business_name:
            th = soup.find("th", itemprop="name")
            if th:
                business_name = self.normalize_whitespace(th.get_text())
            elif soup.find("h1"):
                business_name = self.normalize_whitespace(soup.find("h1").get_text())
                
        address = find_label_value(soup, ["Địa chỉ"])
        representative = find_label_value(soup, ["Đại diện pháp luật", "Người đại diện"])
        status = find_label_value(soup, ["Tình trạng", "Trạng thái"])
        issued_date_str = find_label_value(soup, ["Ngày cấp", "Ngày hoạt động"])
        
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
            issued_date=issued_date,
            source_name=self.provider_name,
            source_url=source_url,
            crawled_at=datetime.utcnow()
        )
        return profile
