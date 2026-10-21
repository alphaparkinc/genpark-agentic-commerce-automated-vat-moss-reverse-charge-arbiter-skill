# -*- coding: utf-8 -*-
"""EU VAT MOSS Reverse Charge Arbiter for GenPark Agentic Commerce."""
import json
from typing import Dict, Any

class EUVATMOSSReverseChargeArbiter:
    VAT_RATES = {"DE": 19.0, "FR": 20.0, "IT": 22.0, "ES": 21.0, "NL": 21.0, "IE": 23.0, "SE": 25.0}

    @staticmethod
    def audit_eu_vat_reverse_charge(buyer_country_code: str, seller_country_code: str, is_b2b_verified: bool, buyer_vies_vat_number: str = "") -> Dict[str, Any]:
        buyer = buyer_country_code.upper()
        seller = seller_country_code.upper()
        if buyer == seller:
            verdict = "DOMESTIC_VAT_APPLIES"; reverse = False; rate = EUVATMOSSReverseChargeArbiter.VAT_RATES.get(buyer, 20.0)
        elif is_b2b_verified and buyer_vies_vat_number:
            verdict = "ARTICLE_196_REVERSE_CHARGE_ZERO_VAT"; reverse = True; rate = 0.0
        else:
            verdict = "B2C_DESTINATION_VAT_APPLIES"; reverse = False; rate = EUVATMOSSReverseChargeArbiter.VAT_RATES.get(buyer, 20.0)
        return {"buyer_country": buyer, "seller_country": seller, "qualifies_reverse_charge": reverse, "applicable_vat_rate_pct": rate, "tax_ruling": verdict}

    @staticmethod
    def lookup_eu_member_state_vat_rate(member_state_code: str) -> Dict[str, Any]:
        code = member_state_code.upper()
        rate = EUVATMOSSReverseChargeArbiter.VAT_RATES.get(code, 20.0)
        return {"member_state": code, "standard_digital_vat_rate_pct": rate}
