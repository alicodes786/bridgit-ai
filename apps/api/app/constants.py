JOB_STATUSES = (
    "queued",
    "processing",
    "needs_input",
    "ready_for_review",
    "approved",
)

STORAGE_BUCKET = "ai-documents"

VAT_CODES = ("SR", "ZR", "EX", "NV", "OS")

# Year-end workbooks and bank PDFs; reject anything larger.
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
