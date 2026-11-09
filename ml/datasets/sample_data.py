"""
DocuMind AI - Ground Truth Dataset & Document Corpus
Provides labeled text samples across 4 primary document categories:
- Invoice
- Receipt
- Resume
- Application Form
"""

DOCUMENT_SAMPLES = [
    # --- INVOICES ---
    {
        "text": "TAX INVOICE ABC Technologies Pvt Ltd Invoice Number: INV-1024 Date: 09/11/2026 Due Date: 24/11/2026 Bill To: Acme Corp GSTIN: 29ABCDE1234F1Z5 Item Description: Cloud Architecture Consulting Qty: 40 Rate: 250 Amount: 10000 Subtotal: 10000 SGST 9%: 900 CGST 9%: 900 Total Tax: 1800 Total Amount: 11800 Payment Terms: Net 15 days Bank Details: HDFC Bank",
        "label": "invoice"
    },
    {
        "text": "INVOICE Global Software Solutions Ltd Invoice No: INV-2026-894 Date of Issue: 01/10/2026 Client: Cyberdyne Systems Purchase Order: PO-9912 Description: Enterprise API Subscription Subtotal: $4,500.00 Sales Tax (8.25%): $371.25 Balance Due: $4,871.25 USD Wire Transfer Details routing number IBAN",
        "label": "invoice"
    },
    {
        "text": "COMMERCIAL INVOICE Supplier: Apex Hardware Supplies Invoice ID: 887211 Date: 15/08/2026 Customer Account: CUST-441 Server Rack Units x4 $800 Cat6 Cables x50 $200 Sub Total: $1,000.00 VAT 20%: $200.00 Total Due: $1,200.00 Remittance instructions enclosed",
        "label": "invoice"
    },
    {
        "text": "ORIGINAL FOR RECIPIENT TAX INVOICE TechNova Solutions Invoice: TN-5520 Date: 05/11/2026 Billed To: Starlight Media Services rendered: UI/UX Glassmorphism Design System Total Hours: 80 Rate: $75 Subtotal: $6,000.00 Tax 10%: $600.00 Grand Total: $6,600.00 Please pay within 30 days",
        "label": "invoice"
    },
    {
        "text": "FREELANCE INVOICE Johnathan Vance Design Studio Invoice #0045 Date: Nov 02, 2026 Bill to: Nexus Interactive Brand Identity System, Iconography, Responsive Mockups Subtotal: $3,200 Tax: $0.00 Total Amount Payable: $3,200 USD Payment via PayPal or Stripe",
        "label": "invoice"
    },
    {
        "text": "INVOICE Zenith Logistics Hub Inv #: ZL-9901 Date: 12/10/2026 Consignee: Metro Logistics Freight forwarding charges, customs clearance, dock demurrage Net Amount: 15,400.00 Service Tax 18%: 2,772.00 Total Amount: 18,172.00 Payment status: Unpaid",
        "label": "invoice"
    },

    # --- RECEIPTS ---
    {
        "text": "STARBUCKS COFFEE STORE #14092 104 MARKET ST SAN FRANCISCO CA DATE: 11/08/2026 08:42 AM REG 02 TRN 4910 Caffe Latte Grande $5.25 Blueberry Scone $3.95 Subtotal: $9.20 Tax: $0.78 TOTAL: $9.98 PAYMENT METHOD: VISA CONTACTLESS AUTH: 084920 THANKS FOR VISITING",
        "label": "receipt"
    },
    {
        "text": "WALMART SUPERCENTER Store 3211 Date: 11/04/2026 14:15 CASHIER: SARAH GROCERY Milk Whole 1GL $3.89 Bread Multi $2.49 Eggs 12pk $4.10 SUBTOTAL $10.48 TAX 1 6.5% $0.68 TOTAL $11.16 MASTER CARD TEND $11.16 CHANGE $0.00 ITEMS SOLD 3",
        "label": "receipt"
    },
    {
        "text": "SHELL FUEL STATION PUMP 04 REGULAR UNLEADED 10.412 GAL @ $3.799/GAL TOTAL FUEL: $39.56 SNACKS COCA COLA $2.19 TOTAL DUE: $41.75 PAID VIA AMEX DEBIT CHIP READ REF: 994012 PUMP RECEIPT THANK YOU",
        "label": "receipt"
    },
    {
        "text": "THE BISTRO RESTAURANT TABLE 14 GUESTS: 2 11/07/2026 20:30 SERVER: MARCUS 1 TRUFFLE PASTA 28.00 1 RIBEYE STEAK 45.00 2 SPARKLING WATER 12.00 FOOD TOTAL: 85.00 TAX: 7.65 GRATUITY 18%: 15.30 FINAL CHARGE: $107.95 CARD TYPE: APPLE PAY APPROVED",
        "label": "receipt"
    },
    {
        "text": "OFFICE DEPOT RECEIPT Store #0421 11/02/2026 11:20 Copy Paper Ream $8.99 Ballpoint Pens Black $4.50 Sticky Notes 4pk $5.20 SUBTOTAL: $18.69 SALES TAX: $1.49 TOTAL: $20.18 CASH TENDERED: $25.00 CHANGE DUE: $4.82 RETURN POLICY 14 DAYS",
        "label": "receipt"
    },

    # --- RESUMES ---
    {
        "text": "ALEXANDER CHEN Senior Full Stack & AI Engineer Email: alex.chen@example.com | Phone: +1-555-019-2834 | San Francisco, CA SUMMARY Experienced software engineer specializing in Next.js, Python, FastAPI, and machine learning document processing pipelines. SKILLS Languages: Python, TypeScript, SQL, Rust Frameworks: Next.js, React, FastAPI, PyTorch, Scikit-learn, TailwindCSS Databases & Tools: PostgreSQL, Redis, Docker, Celery, AWS EXPERIENCE Lead Machine Learning Engineer - DataStream Inc (2023 - Present) Architected end-to-end intelligent OCR pipeline processing 50k invoices daily using PyMuPDF and transformer models. Senior Software Engineer - CloudScale (2020 - 2023) EDUCATION B.S. in Computer Science - University of California, Berkeley (2016 - 2020)",
        "label": "resume"
    },
    {
        "text": "PRIYA SHARMA Data Scientist & NLP Specialist Bangalore, India | priya.sharma@example.in | +91 98765 43210 PROFESSIONAL PROFILE 5+ years of industry experience developing statistical NLP models, document classification, NER extractors, and LLM orchestration with LangChain and Gemini. TECHNICAL COMPETENCIES Machine Learning: scikit-learn, TensorFlow, SpaCy, HuggingFace Transformers Backend: FastAPI, Flask, SQLAlchemy, Docker EDUCATION M.Tech in Artificial Intelligence - Indian Institute of Science (IISc), 2019 WORK HISTORY Senior NLP Engineer at VeriText Solutions (2021-Present)",
        "label": "resume"
    },
    {
        "text": "DAVID R. MILLER Frontend Architect & UI Engineer portfolio: davidmiller.dev | email: contact@davidmiller.io | New York, NY OVERVIEW Passionate UI engineer specializing in high-performance web applications, Apple Liquid Glass aesthetics, design systems, and WebGL. CORE SKILLS React, Next.js App Router, TypeScript, Framer Motion, Tailwind CSS, Radix UI, Figma WORK EXPERIENCE Principal UI Architect - GlassUI Labs (2022 - Present) Senior Frontend Developer - Horizon SaaS (2018 - 2022) EDUCATION Bachelor of Fine Arts in Digital Design - RISD",
        "label": "resume"
    },
    {
        "text": "SARAH JENKINS Curriculum Vitae Education: Ph.D. in Computational Linguistics, Stanford University (2021). B.S. in Mathematics, MIT (2016). Research Interests: Information extraction from semi-structured texts, optical character recognition error correction. Publications: 8 peer-reviewed papers in ACL and EMNLP. Teaching Experience: Graduate Teaching Assistant for Natural Language Processing.",
        "label": "resume"
    },

    # --- APPLICATION FORMS ---
    {
        "text": "APPLICATION FOR EMPLOYMENT Confidential Candidate Application Form Position Applied For: Senior Backend Engineer Applicant Full Name: Robert Michael Taylor Date of Birth: 14/05/1992 Social Security Number / ID: XXX-XX-4819 Residential Address: 742 Evergreen Terrace, Springfield, OR Contact Phone: (555) 321-7654 Emergency Contact: Mary Taylor (Spouse) - (555) 321-7655 Are you legally authorized to work in the United States? [X] Yes [ ] No Have you ever been convicted of a felony? [ ] Yes [X] No Signature: R. Taylor Date: 09/11/2026",
        "label": "application_form"
    },
    {
        "text": "RESIDENTIAL LEASE APPLICATION Rental Property Address: Apt 4B, 120 Ocean View Ave Applicant Information: Full Name: Jessica Lynn Morales Drivers License No: DL-8891024-CA Current Address: 304 Pine St, Los Angeles, CA Current Landlord Name: Pacific Properties Monthly Income: $7,200 Current Employer: BioTech Innovations Position: Research Associate I hereby authorize credit check and employment verification. Applicant Signature: Jessica Morales Date: 02/11/2026",
        "label": "application_form"
    },
    {
        "text": "UNIVERSITY ADMISSION APPLICATION FORM Academic Year: 2027-2028 Program: Master of Science in Data Engineering 1. Personal Details: First Name: Marcus Last Name: Aurelius Date of Birth: 26/04/2000 Nationality: Canadian Passport Number: ZA991024 Email: marcus.a@domain.edu Permanent Mailing Address: 88 Maple Leaf Dr, Toronto, ON Highest Qualification: Bachelor of Engineering GPA: 3.85 / 4.0 Test Scores: GRE: 328, TOEFL: 110 Declaration: I certify that all particulars given above are true and complete.",
        "label": "application_form"
    },
    {
        "text": "LOAN APPLICATION FORM Financial Services Ltd Form Ref: LAF-2026-9901 Applicant Name: Emily Watson Govt ID / National ID: A9823412 Date of Birth: 1988-09-12 Marital Status: Married Gross Annual Income: $95,000 Requested Loan Amount: $35,000 Purpose of Loan: Home Renovation Existing Bank Account: Wells Fargo Checking Account # 99812401 I authorize credit bureau scoring and asset verification. Signature: Emily Watson",
        "label": "application_form"
    }
]
