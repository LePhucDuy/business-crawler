from typing import List, Optional
from rapidfuzz import fuzz
from app.domain.schemas import ProviderResult, BusinessMergeResult
from app.domain.normalized import BusinessProfileNormalized
from app.services.data_quality_service import DataQualityService
import structlog

logger = structlog.get_logger(__name__)

class BusinessMergeService:
    def __init__(self):
        self.data_quality_service = DataQualityService()

    def merge_results(self, results: List[ProviderResult]) -> BusinessMergeResult:
        successful_results = [r for r in results if r.success and r.profile]
        
        if not successful_results:
            return BusinessMergeResult(
                final_profile=BusinessProfileNormalized(source_name="system"),
                provider_results=results,
                needs_manual_review=True
            )

        for r in successful_results:
            if r.profile.confidence_score is None:
                r.profile.confidence_score = self.data_quality_service.calculate_confidence(r.profile)

        successful_results.sort(key=lambda r: r.profile.confidence_score or 0, reverse=True)
        
        best_profile = successful_results[0].profile
        final_profile = best_profile.model_copy()
        conflicts = []
        needs_manual_review = False

        for other_result in successful_results[1:]:
            other_profile = other_result.profile
            
            if final_profile.normalized_business_name and other_profile.normalized_business_name:
                similarity = fuzz.ratio(final_profile.normalized_business_name, other_profile.normalized_business_name)
                if similarity < 85:
                    conflicts.append({
                        "field": "business_name",
                        "value_1": final_profile.business_name,
                        "value_2": other_profile.business_name,
                        "source_1": final_profile.source_name,
                        "source_2": other_profile.source_name
                    })
                    needs_manual_review = True
                    
            if final_profile.normalized_legal_representative and other_profile.normalized_legal_representative:
                similarity = fuzz.ratio(final_profile.normalized_legal_representative, other_profile.normalized_legal_representative)
                if similarity < 80:
                    conflicts.append({
                        "field": "legal_representative",
                        "value_1": final_profile.legal_representative,
                        "value_2": other_profile.legal_representative,
                        "source_1": final_profile.source_name,
                        "source_2": other_profile.source_name
                    })

            for field in final_profile.model_fields.keys():
                if getattr(final_profile, field) is None and getattr(other_profile, field) is not None:
                    setattr(final_profile, field, getattr(other_profile, field))

        final_profile.confidence_score = self.data_quality_service.calculate_confidence(final_profile)

        for r in results:
            if r.status == "manual_required":
                needs_manual_review = True

        return BusinessMergeResult(
            final_profile=final_profile,
            provider_results=results,
            conflicts=conflicts,
            needs_manual_review=needs_manual_review,
            confidence_score=final_profile.confidence_score
        )
