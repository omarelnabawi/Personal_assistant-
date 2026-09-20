
def deep_merge_personal_info(old: dict, new: dict) -> dict:
    merged = old.copy()
    for key, value in new.items():
        if value is None:
            continue   # الموديل رجّع الحقل ده فاضي، سيب القديم زي ما هو
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = {**merged[key], **value}   # دمج الحقول المتداخلة (زي languages)
        else:
            merged[key] = value   # قيمة جديدة أو محدّثة، خدها
    return merged