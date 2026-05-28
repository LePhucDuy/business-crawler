def mask_tax_code(tax_code: str | None) -> str | None:
    if not tax_code:
        return None
    if len(tax_code) <= 6:
        return "***"
    return f"{tax_code[:3]}***{tax_code[-3:]}"

def mask_name(name: str | None) -> str | None:
    if not name:
        return None
    parts = name.split()
    if len(parts) <= 1:
        return "***"
    return f"{' '.join(parts[:-1])} ***"
