from input.pdf_ocr import (
    extract_text_from_pdf,
    parse_medical_fields,
    compute_data_quality
)

text = extract_text_from_pdf("sample_report.pdf")
data = parse_medical_fields(text) or {}
quality = compute_data_quality(data)

print(data)
print("Data quality:", quality)
