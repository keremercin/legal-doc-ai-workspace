from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def build_pdf(path: Path, lines: list[str]) -> None:
    c = canvas.Canvas(str(path), pagesize=letter)
    text = c.beginText(50, 750)
    for line in lines:
        text.textLine(line)
    c.drawText(text)
    c.save()


def main() -> None:
    base = Path("data/demo_docs")
    base.mkdir(parents=True, exist_ok=True)

    docs = {
        "sample-service-agreement.pdf": [
            "SERVICE AGREEMENT",
            "This Service Agreement is entered into on March 12, 2026.",
            "Between Northwind Analytics LLC and Blue Harbor Operations Inc.",
            "Northwind Analytics LLC shall provide document automation and reporting services.",
            "Blue Harbor Operations Inc. must pay all invoices within 15 days of receipt.",
            "Both parties agree to protect confidential information.",
            "The agreement term begins on March 12, 2026 and ends on September 12, 2026.",
        ],
        "sample-amendment.pdf": [
            "FIRST AMENDMENT TO SERVICE AGREEMENT",
            "This Amendment is effective as of April 4, 2026.",
            "Between Northwind Analytics LLC and Blue Harbor Operations Inc.",
            "The payment term is amended from 15 days to 30 days from invoice receipt.",
            "Northwind Analytics LLC shall also provide audit trail reporting.",
            "All other obligations remain in effect unless modified by this amendment.",
        ],
        "sample-nda.pdf": [
            "NON-DISCLOSURE AGREEMENT",
            "This Non-Disclosure Agreement is made on February 2, 2026.",
            "Between Blue Harbor Operations Inc. and Harbor Peak Legal Group LLC.",
            "Each party must protect confidential information and shall not disclose it to third parties.",
            "Confidential materials must be returned within 10 business days upon request.",
            "The confidentiality obligations survive for 24 months after termination.",
        ],
    }

    for filename, lines in docs.items():
        path = base / filename
        build_pdf(path, lines)
        print(path.resolve())


if __name__ == "__main__":
    main()
