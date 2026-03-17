"""
build_gold_set_uc2.py — UC2 Invoice Field Extraction
S³ Research Project | UT Dallas | March 2026

Pre-registered S³ Score: 2.75  →  Pure SLM predicted
S³ Denominator note (Gap G1): pre-registration used sum-of-weights method (Σw=1.0)
which yields 2.75 directly. Corrected 27.0-denominator method yields 2.56.
Both scores fall in Pure SLM zone (≤3.2). Prediction unchanged.

Task: Given an invoice text, extract 6 structured fields as valid JSON.
Output schema: vendor_name, invoice_date, invoice_number, total_amount,
               tax_amount (or null), line_item_count

Gold set: 100 items, stratified by category + difficulty, 70/30 train/test split.
"""

import csv
import json
import os
import random
from datetime import datetime

random.seed(42)

# ── Pre-registration block ─────────────────────────────────────────────────────
PREREGISTRATION = {
    "use_case": "UC2 — Invoice Field Extraction",
    "locked_date": "2026-03-10",
    "s3_score_preregistered": 2.75,
    "s3_score_corrected_denominator": 2.56,
    "s3_prediction": "Pure SLM",
    "s3_threshold_pure_slm": 3.2,
    "dimensions": {
        "TC_task_complexity": {"score": 1, "weight": 1.0, "note": "Structured extraction, no reasoning"},
        "OS_output_structure": {"score": 4, "weight": 0.8, "note": "Strict JSON schema with 6 fields"},
        "SK_stakes":           {"score": 2, "weight": 1.2, "note": "Financial error — correctable, auditable"},
        "DS_data_sensitivity": {"score": 4, "weight": 0.8, "note": "Financial documents, on-prem preferred"},
        "LT_latency":          {"score": 1, "weight": 1.0, "note": "Batch processing, no real-time SLA"},
        "VL_volume":           {"score": 5, "weight": 0.6, "note": "High volume AP/AR workflows"},
    },
    "hypotheses": {
        "H2.1": "Best SLM achieves ≥90% of LLM field-level accuracy",
        "H2.2": "Best SLM P95 latency < 4000ms (JSON output is longer than single-label)",
        "H2.3": "UC2 graduates to Pure SLM — SLMs achieve ≥95% LLM parity on structured extraction",
        "H2.4": "line_item_count and tax_amount are the hardest fields (most model errors)",
    },
    "comparison_baseline": "No direct recent paper comparison. Zhang et al. 2024 (ICML) shows SLMs near-parity with LLMs on structured extraction. This benchmark provides the first controlled measurement on invoice-domain field extraction."
}

# ── Gold set data ──────────────────────────────────────────────────────────────
# Categories: Tech Services, Office Supplies, Professional Services, Utilities, Software/SaaS
# Difficulty:
#   easy   → clear labels, standard format, no ambiguity
#   medium → one ambiguous field (e.g. tax buried in text, date in non-ISO format)
#   hard   → abbreviations, multi-page references, items in footer, unusual format

GOLD_SET = [
    # ─────────────────────────── TECH SERVICES ─────────────────────────────
    # easy
    {
        "category": "tech_services", "difficulty": "easy",
        "invoice_text": (
            "INVOICE\n"
            "Vendor: TechNova Solutions LLC\n"
            "Invoice Number: TNS-20240815-001\n"
            "Date: 2024-08-15\n\n"
            "Services Rendered:\n"
            "  - Cloud Infrastructure Setup    $3,200.00\n"
            "  - Security Audit                $1,800.00\n\n"
            "Subtotal: $5,000.00\n"
            "Tax (8%): $400.00\n"
            "Total Due: $5,400.00"
        ),
        "vendor_name": "TechNova Solutions LLC",
        "invoice_date": "2024-08-15",
        "invoice_number": "TNS-20240815-001",
        "total_amount": 5400.00,
        "tax_amount": 400.00,
        "line_item_count": 2,
    },
    {
        "category": "tech_services", "difficulty": "easy",
        "invoice_text": (
            "INVOICE\n"
            "From: DataBridge Systems Inc.\n"
            "Invoice #: DBS-2024-0042\n"
            "Invoice Date: September 3, 2024\n\n"
            "Description:\n"
            "  1. Database Migration Services   $6,500.00\n"
            "  2. Staff Training (2 days)        $2,000.00\n"
            "  3. Documentation Package            $500.00\n\n"
            "Tax: $720.00\n"
            "Grand Total: $9,720.00"
        ),
        "vendor_name": "DataBridge Systems Inc.",
        "invoice_date": "2024-09-03",
        "invoice_number": "DBS-2024-0042",
        "total_amount": 9720.00,
        "tax_amount": 720.00,
        "line_item_count": 3,
    },
    {
        "category": "tech_services", "difficulty": "easy",
        "invoice_text": (
            "SALES INVOICE\n\n"
            "Supplier: Apex IT Consultants\n"
            "Invoice No: AIC-003871\n"
            "Billing Date: 2024-11-01\n\n"
            "Item: Annual Support Contract    $12,000.00\n\n"
            "Sales Tax: $960.00\n"
            "Total Amount Due: $12,960.00"
        ),
        "vendor_name": "Apex IT Consultants",
        "invoice_date": "2024-11-01",
        "invoice_number": "AIC-003871",
        "total_amount": 12960.00,
        "tax_amount": 960.00,
        "line_item_count": 1,
    },
    # medium
    {
        "category": "tech_services", "difficulty": "medium",
        "invoice_text": (
            "Invoice from CloudMatrix Corp | Ref: CMX/INV/2025/0291\n"
            "Issued: January 15th, 2025\n\n"
            "Deliverables:\n"
            "  API Integration Work (Phase 1)   $4,100\n"
            "  API Integration Work (Phase 2)   $3,900\n"
            "  QA & Testing                     $1,200\n"
            "  Project Management               $800\n\n"
            "All amounts exclusive of applicable taxes.\n"
            "Total (incl. 7.5% state tax): $10,750.00"
        ),
        "vendor_name": "CloudMatrix Corp",
        "invoice_date": "2025-01-15",
        "invoice_number": "CMX/INV/2025/0291",
        "total_amount": 10750.00,
        "tax_amount": 750.00,
        "line_item_count": 4,
    },
    {
        "category": "tech_services", "difficulty": "medium",
        "invoice_text": (
            "BILLING STATEMENT\n"
            "Tech Horizon Group | TX-H-20241203\n"
            "Date of Issue: 03-Dec-2024\n\n"
            "Services:\n"
            "  Managed Detection & Response (MDR) — 3 months    $8,400.00\n"
            "  Penetration Test Report                           $2,500.00\n\n"
            "Subtotal before tax: $10,900.00\n"
            "Taxes and fees included in final amount.\n"
            "TOTAL: $11,854.50"
        ),
        "vendor_name": "Tech Horizon Group",
        "invoice_date": "2024-12-03",
        "invoice_number": "TX-H-20241203",
        "total_amount": 11854.50,
        "tax_amount": 954.50,
        "line_item_count": 2,
    },
    {
        "category": "tech_services", "difficulty": "medium",
        "invoice_text": (
            "INVOICE — Nexus Software Engineering\n"
            "Invoice Reference: NSE-2025-Q1-014\n"
            "Billing period end date: March 31, 2025\n\n"
            "Monthly retainer: $5,000.00 × 3 months = $15,000.00\n"
            "Emergency on-call incidents (2): $750.00\n\n"
            "GST/HST (13%): $2,047.50\n"
            "Net payable: $17,797.50"
        ),
        "vendor_name": "Nexus Software Engineering",
        "invoice_date": "2025-03-31",
        "invoice_number": "NSE-2025-Q1-014",
        "total_amount": 17797.50,
        "tax_amount": 2047.50,
        "line_item_count": 2,
    },
    {
        "category": "tech_services", "difficulty": "medium",
        "invoice_text": (
            "Vantage Systems | Invoice\n"
            "Client PO: PO-88821\n"
            "Invoice: VSI-88821-R2\n"
            "Date: Feb 7 2025\n\n"
            "Work items (revised per change order):\n"
            "  Core dev work        $11,200.00\n"
            "  Change order #1      +$2,000.00\n"
            "  Discount applied     -$500.00\n\n"
            "Tax (8.25%): $1,051.50\n"
            "Total: $13,751.50"
        ),
        "vendor_name": "Vantage Systems",
        "invoice_date": "2025-02-07",
        "invoice_number": "VSI-88821-R2",
        "total_amount": 13751.50,
        "tax_amount": 1051.50,
        "line_item_count": 3,
    },
    # hard
    {
        "category": "tech_services", "difficulty": "hard",
        "invoice_text": (
            "INV# IT-SRV-25-0087 | Meridian Tech Partners\n"
            "Billing cycle: Q4 FY25 (Oct–Dec)\n\n"
            "Stmt rendered: 31-Dec-25\n\n"
            "Hrs   Description                          Rate     Ext.\n"
            "120   Sr. Architect (J. Patel)           $185/hr  $22,200\n"
            " 80   DevOps Eng. (contract)             $140/hr  $11,200\n"
            " 40   Jr. Developer                       $95/hr   $3,800\n"
            " 20   PM oversight                       $160/hr   $3,200\n\n"
            "Travel & expenses (receipts attached):   $1,340.00\n"
            "Withholding adj:                          -$200.00\n"
            "Applicable sales tax:                   $3,303.20\n"
            "TOTAL DUE:                             $44,843.20"
        ),
        "vendor_name": "Meridian Tech Partners",
        "invoice_date": "2025-12-31",
        "invoice_number": "IT-SRV-25-0087",
        "total_amount": 44843.20,
        "tax_amount": 3303.20,
        "line_item_count": 6,
    },
    {
        "category": "tech_services", "difficulty": "hard",
        "invoice_text": (
            "INVOICE — Pinnacle Digital Inc. | PDI-FY2025-0441\n"
            "Originated: Q3-end (see attached SOW ref #SOW-882)\n"
            "Note: This invoice supersedes draft PDI-FY2025-0441-D\n\n"
            "Module A: UI/UX Redesign         $18,500\n"
            "Module B: Backend Refactor       $22,000\n"
            "Module C: CI/CD Pipeline          $9,500\n"
            "Licensing (annual):               $4,200\n"
            "Volume discount (-5%):           -$2,710\n\n"
            "VAT @ 20%:                       $10,298\n"
            "Total payable (GBP equivalent shown in addendum): $61,788.00"
        ),
        "vendor_name": "Pinnacle Digital Inc.",
        "invoice_date": None,
        "invoice_number": "PDI-FY2025-0441",
        "total_amount": 61788.00,
        "tax_amount": 10298.00,
        "line_item_count": 5,
    },

    # ─────────────────────────── OFFICE SUPPLIES ────────────────────────────
    # easy
    {
        "category": "office_supplies", "difficulty": "easy",
        "invoice_text": (
            "INVOICE\n"
            "Vendor: OfficeWorld Direct\n"
            "Invoice: OWD-24-5521\n"
            "Date: 2024-07-10\n\n"
            "  Laser Paper (10 reams)        $89.90\n"
            "  Ballpoint Pens (box of 50)    $24.99\n"
            "  Sticky Notes (24-pack)        $18.50\n\n"
            "Tax: $10.68\n"
            "Total: $144.07"
        ),
        "vendor_name": "OfficeWorld Direct",
        "invoice_date": "2024-07-10",
        "invoice_number": "OWD-24-5521",
        "total_amount": 144.07,
        "tax_amount": 10.68,
        "line_item_count": 3,
    },
    {
        "category": "office_supplies", "difficulty": "easy",
        "invoice_text": (
            "TAX INVOICE\n"
            "Staples Business Advantage\n"
            "Invoice Number: SBA-0089234\n"
            "Invoice Date: October 22, 2024\n\n"
            "Products:\n"
            "  HP 67XL Ink Cartridges (4-pack)    $62.99\n"
            "  Wireless Keyboard & Mouse          $54.99\n"
            "  Monitor Stand (adjustable)         $79.99\n"
            "  USB Hub 7-port                     $34.99\n"
            "  Cable Management Kit               $19.99\n\n"
            "HST (13%): $33.50\n"
            "Total: $286.45"
        ),
        "vendor_name": "Staples Business Advantage",
        "invoice_date": "2024-10-22",
        "invoice_number": "SBA-0089234",
        "total_amount": 286.45,
        "tax_amount": 33.50,
        "line_item_count": 5,
    },
    {
        "category": "office_supplies", "difficulty": "easy",
        "invoice_text": (
            "PURCHASE INVOICE\n"
            "Quill Corporation | INV-QC-2025-00338\n"
            "Date: 2025-02-14\n\n"
            "Ergonomic Chair Model EX-7    $349.00\n\n"
            "Tax: $27.92\n"
            "Total: $376.92"
        ),
        "vendor_name": "Quill Corporation",
        "invoice_date": "2025-02-14",
        "invoice_number": "INV-QC-2025-00338",
        "total_amount": 376.92,
        "tax_amount": 27.92,
        "line_item_count": 1,
    },
    # medium
    {
        "category": "office_supplies", "difficulty": "medium",
        "invoice_text": (
            "SupplyPro | Order #SP-77421-B | Inv. date: 14 Mar 2025\n\n"
            "Qty  Item                         Unit    Total\n"
            " 20  Copy paper A4 (ream)         $8.99  $179.80\n"
            "  5  Whiteboard markers (set)    $12.50   $62.50\n"
            " 10  File folders (box)            $7.20   $72.00\n"
            "  3  Label maker tape rolls       $11.00   $33.00\n\n"
            "Shipping: $15.00\n"
            "Total (tax exempt — reseller cert on file): $362.30"
        ),
        "vendor_name": "SupplyPro",
        "invoice_date": "2025-03-14",
        "invoice_number": "SP-77421-B",
        "total_amount": 362.30,
        "tax_amount": None,
        "line_item_count": 4,
    },
    {
        "category": "office_supplies", "difficulty": "medium",
        "invoice_text": (
            "INVOICE FROM: Global Office Essentials\n"
            "Our ref: GOE/2025/INV/0561\n"
            "Your PO: 90213\n"
            "Date of supply: 5th February 2025\n\n"
            "  Standing desk converters ×4    $279.96\n"
            "  Laptop stands ×6               $149.94\n"
            "  Cable organizers ×10            $49.90\n\n"
            "Subtotal: $479.80\n"
            "VAT (20%): $95.96\n"
            "Total incl. VAT: $575.76"
        ),
        "vendor_name": "Global Office Essentials",
        "invoice_date": "2025-02-05",
        "invoice_number": "GOE/2025/INV/0561",
        "total_amount": 575.76,
        "tax_amount": 95.96,
        "line_item_count": 3,
    },
    {
        "category": "office_supplies", "difficulty": "medium",
        "invoice_text": (
            "BrightSpace Interiors | BS-202500144\n"
            "Billing Date: Jan 30, '25\n\n"
            "Office partition panels (×6, installed)   $2,400.00\n"
            "Reception desk refurb                     $1,850.00\n"
            "Delivery & assembly                         $320.00\n\n"
            "Note: 50% deposit paid. Remaining 50% shown below.\n"
            "Tax (9%): $419.40\n"
            "Balance due: $5,069.40"
        ),
        "vendor_name": "BrightSpace Interiors",
        "invoice_date": "2025-01-30",
        "invoice_number": "BS-202500144",
        "total_amount": 5069.40,
        "tax_amount": 419.40,
        "line_item_count": 3,
    },
    # hard
    {
        "category": "office_supplies", "difficulty": "hard",
        "invoice_text": (
            "CONSOLIDATED SUPPLY INVOICE\n"
            "Vendor: Office Depot Business (acct #: 4481-PRO)\n"
            "Inv. Ref.: ODBI-2025-0331-ADJ | Replaces: ODBI-2025-0331\n"
            "Period: March 2025\n\n"
            "  Paper products bundle       $214.60\n"
            "  Toner cartridges (est.)     $387.50 *\n"
            "  Breakroom supplies          $156.20\n"
            "  Misc. small items           $73.40\n"
            "  Credit memo (CM-0032)      -$45.00\n\n"
            "* Actual toner qty adjusted per monthly usage report.\n"
            "State tax (est.): $62.93\n"
            "Corrected Total Due: $849.63"
        ),
        "vendor_name": "Office Depot Business",
        "invoice_date": None,
        "invoice_number": "ODBI-2025-0331-ADJ",
        "total_amount": 849.63,
        "tax_amount": 62.93,
        "line_item_count": 5,
    },

    # ─────────────────────── PROFESSIONAL SERVICES ───────────────────────────
    # easy
    {
        "category": "professional_services", "difficulty": "easy",
        "invoice_text": (
            "INVOICE\n"
            "From: Hartwell & Associates LLP\n"
            "Invoice #: HA-2025-0117\n"
            "Date: January 17, 2025\n\n"
            "  Legal Consultation (4 hrs × $320/hr)   $1,280.00\n"
            "  Contract Drafting                       $2,500.00\n"
            "  Filing Fees (disbursement)                $150.00\n\n"
            "Tax: $0 (legal services exempt)\n"
            "Total Due: $3,930.00"
        ),
        "vendor_name": "Hartwell & Associates LLP",
        "invoice_date": "2025-01-17",
        "invoice_number": "HA-2025-0117",
        "total_amount": 3930.00,
        "tax_amount": None,
        "line_item_count": 3,
    },
    {
        "category": "professional_services", "difficulty": "easy",
        "invoice_text": (
            "ACCOUNTING SERVICES INVOICE\n"
            "Firm: Rivera & Chen CPAs\n"
            "Invoice Number: RC-2024-Q4-009\n"
            "Invoice Date: 2024-12-31\n\n"
            "  Annual Audit                  $8,500.00\n"
            "  Tax Preparation (Corp.)       $2,200.00\n\n"
            "Tax: $856.00\n"
            "Total: $11,556.00"
        ),
        "vendor_name": "Rivera & Chen CPAs",
        "invoice_date": "2024-12-31",
        "invoice_number": "RC-2024-Q4-009",
        "total_amount": 11556.00,
        "tax_amount": 856.00,
        "line_item_count": 2,
    },
    {
        "category": "professional_services", "difficulty": "easy",
        "invoice_text": (
            "INVOICE\n"
            "Consulting Firm: Bright Future Strategy Group\n"
            "Invoice: BFSG-00223\n"
            "Date: March 5, 2025\n\n"
            "  Market Entry Analysis Report        $7,000.00\n\n"
            "No applicable taxes.\n"
            "Amount Due: $7,000.00"
        ),
        "vendor_name": "Bright Future Strategy Group",
        "invoice_date": "2025-03-05",
        "invoice_number": "BFSG-00223",
        "total_amount": 7000.00,
        "tax_amount": None,
        "line_item_count": 1,
    },
    # medium
    {
        "category": "professional_services", "difficulty": "medium",
        "invoice_text": (
            "Thornton Executive Search | Invoice TES-2025-0085\n"
            "Issued: 28 February, 2025\n\n"
            "Recruitment fee — VP Engineering placement\n"
            "  (22% of first-year base salary $195,000)    $42,900.00\n"
            "Background check (pass-through)                   $475.00\n\n"
            "Subtotal: $43,375.00\n"
            "GST (5%): $2,168.75\n"
            "Total: $45,543.75"
        ),
        "vendor_name": "Thornton Executive Search",
        "invoice_date": "2025-02-28",
        "invoice_number": "TES-2025-0085",
        "total_amount": 45543.75,
        "tax_amount": 2168.75,
        "line_item_count": 2,
    },
    {
        "category": "professional_services", "difficulty": "medium",
        "invoice_text": (
            "INVOICE — Clearwater Training Solutions\n"
            "CTS Invoice: 2025-TRN-0049 (see also PO# 77-2025-CORP)\n"
            "Course dates: Feb 10-14, 2025 | Invoice date: 17 Feb 25\n\n"
            "  Leadership Workshop (8 attendees)     $6,400.00\n"
            "  Facilitator travel                      $890.00\n"
            "  Course materials                        $640.00\n"
            "  Venue rental (contribution)             $750.00\n"
            "  Post-course coaching (4 sessions)     $1,600.00\n\n"
            "Tax: $839.36\n"
            "Invoice total: $11,119.36"
        ),
        "vendor_name": "Clearwater Training Solutions",
        "invoice_date": "2025-02-17",
        "invoice_number": "2025-TRN-0049",
        "total_amount": 11119.36,
        "tax_amount": 839.36,
        "line_item_count": 5,
    },
    {
        "category": "professional_services", "difficulty": "medium",
        "invoice_text": (
            "PR Firm: Mosaic Communications Group\n"
            "Billing ref: MCG-Q2-2025-007\n"
            "Period: April–June 2025 | Issued: 30 Jun 2025\n\n"
            "Monthly retainer × 3 months ($4,500/mo)  $13,500.00\n"
            "Press release distribution (×5 releases)   $2,500.00\n"
            "Media monitoring tool (quarterly)          $1,200.00\n\n"
            "Taxes where applicable: None (b2b services, exempt).\n"
            "Total Due: $17,200.00"
        ),
        "vendor_name": "Mosaic Communications Group",
        "invoice_date": "2025-06-30",
        "invoice_number": "MCG-Q2-2025-007",
        "total_amount": 17200.00,
        "tax_amount": None,
        "line_item_count": 3,
    },
    # hard
    {
        "category": "professional_services", "difficulty": "hard",
        "invoice_text": (
            "ENGAGEMENT INVOICE\n"
            "Practice: Meridian Management Consulting | Office: Chicago\n"
            "Engagement: Project Gemini | Phase: II\n"
            "Invoice: MMC-ENG-2025-GMNI-P2-003\n\n"
            "Team time (week ending 2025-06-27):\n"
            "  Partner (S. Okafor)      14.5 hrs × $600    $8,700\n"
            "  Sr. Mgr (L. Bernstein)   38.0 hrs × $380   $14,440\n"
            "  Analyst (A. Dutta)       52.0 hrs × $195   $10,140\n"
            "Reimbursables:\n"
            "  Flights                             $1,642\n"
            "  Hotel (4 nights)                    $1,128\n"
            "  Meals (per diem)                      $312\n\n"
            "Applicable taxes: none (inter-company)\n"
            "Invoice Total: $36,362.00"
        ),
        "vendor_name": "Meridian Management Consulting",
        "invoice_date": "2025-06-27",
        "invoice_number": "MMC-ENG-2025-GMNI-P2-003",
        "total_amount": 36362.00,
        "tax_amount": None,
        "line_item_count": 6,
    },
    {
        "category": "professional_services", "difficulty": "hard",
        "invoice_text": (
            "AMENDED TAX INVOICE\n"
            "Original: AMG-2025-0198 | This document: AMG-2025-0198-AMD\n"
            "Amend. reason: Line item 2 qty correction\n"
            "Firm: Atlas Management Group | Dept: Strategy\n"
            "Date rendered: 15 May 2025\n\n"
            "1. Board advisory sessions (orig: 3, corrected: 2 × $5,500)  $11,000\n"
            "2. Benchmarking report (revised scope)                         $8,750\n"
            "3. Travel (as per approved budget)                             $2,100\n\n"
            "Less: credit from overpayment INV-0181                       -$1,200\n"
            "Sub: $20,650\n"
            "GST (10%): $2,065\n"
            "Net Payable: $22,715.00"
        ),
        "vendor_name": "Atlas Management Group",
        "invoice_date": "2025-05-15",
        "invoice_number": "AMG-2025-0198-AMD",
        "total_amount": 22715.00,
        "tax_amount": 2065.00,
        "line_item_count": 4,
    },

    # ─────────────────────────── UTILITIES ──────────────────────────────────
    # easy
    {
        "category": "utilities", "difficulty": "easy",
        "invoice_text": (
            "ELECTRIC UTILITY INVOICE\n"
            "Provider: Consolidated Power & Light\n"
            "Account Invoice: CPL-INV-20240801\n"
            "Bill Date: August 1, 2024\n\n"
            "  Energy consumption (1,240 kWh × $0.12)    $148.80\n"
            "  Distribution charge                        $32.50\n\n"
            "Tax: $9.09\n"
            "Total Amount Due: $190.39"
        ),
        "vendor_name": "Consolidated Power & Light",
        "invoice_date": "2024-08-01",
        "invoice_number": "CPL-INV-20240801",
        "total_amount": 190.39,
        "tax_amount": 9.09,
        "line_item_count": 2,
    },
    {
        "category": "utilities", "difficulty": "easy",
        "invoice_text": (
            "WATER & WASTEWATER BILL\n"
            "Utility: Metro Water District\n"
            "Invoice #: MWD-Q3-2024-00772\n"
            "Billing Date: 2024-09-30\n\n"
            "  Water usage (18,500 gallons)   $74.00\n"
            "  Wastewater fee                 $45.00\n"
            "  Infrastructure surcharge        $12.50\n\n"
            "Tax: $0 (utility, tax-exempt)\n"
            "Total: $131.50"
        ),
        "vendor_name": "Metro Water District",
        "invoice_date": "2024-09-30",
        "invoice_number": "MWD-Q3-2024-00772",
        "total_amount": 131.50,
        "tax_amount": None,
        "line_item_count": 3,
    },
    {
        "category": "utilities", "difficulty": "easy",
        "invoice_text": (
            "NATURAL GAS INVOICE\n"
            "Supplier: Cascade Gas Services\n"
            "Invoice No.: CGS-2025-0058\n"
            "Date: January 31, 2025\n\n"
            "  Gas usage (620 therms × $1.45)   $899.00\n"
            "  Safety inspection fee              $25.00\n\n"
            "Tax (utility levy 3%): $27.72\n"
            "Total Payable: $951.72"
        ),
        "vendor_name": "Cascade Gas Services",
        "invoice_date": "2025-01-31",
        "invoice_number": "CGS-2025-0058",
        "total_amount": 951.72,
        "tax_amount": 27.72,
        "line_item_count": 2,
    },
    # medium
    {
        "category": "utilities", "difficulty": "medium",
        "invoice_text": (
            "COMBINED UTILITY BILL — Pacific Summit Utilities\n"
            "Account: PSU-88320 | Period: Oct–Nov 2024\n"
            "Invoice ref: PSU-88320-NOV24\n"
            "Statement date: November 30 2024\n\n"
            "Electric (2 months)    $412.00\n"
            "Gas                    $183.50\n"
            "Prior balance          $127.20\n"
            "Late payment fee        $12.72\n\n"
            "Regulatory surcharge (estimated):  $28.40\n"
            "Total balance: $763.82"
        ),
        "vendor_name": "Pacific Summit Utilities",
        "invoice_date": "2024-11-30",
        "invoice_number": "PSU-88320-NOV24",
        "total_amount": 763.82,
        "tax_amount": 28.40,
        "line_item_count": 4,
    },
    {
        "category": "utilities", "difficulty": "medium",
        "invoice_text": (
            "TELECOM SERVICES INVOICE\n"
            "Carrier: Broadband Plus | BP-ENT-2025-0392\n"
            "Billing month: February 2025 (issued 28-Feb-25)\n\n"
            "Dedicated fiber 1Gbps (monthly)    $850.00\n"
            "Failover 4G LTE backup             $120.00\n"
            "Static IP block (×8 addresses)      $40.00\n"
            "DDoS protection add-on              $95.00\n\n"
            "Note: Tax not applicable on carrier services in this state.\n"
            "Total: $1,105.00"
        ),
        "vendor_name": "Broadband Plus",
        "invoice_date": "2025-02-28",
        "invoice_number": "BP-ENT-2025-0392",
        "total_amount": 1105.00,
        "tax_amount": None,
        "line_item_count": 4,
    },
    # hard
    {
        "category": "utilities", "difficulty": "hard",
        "invoice_text": (
            "STATEMENT OF CHARGES\n"
            "Multi-site account — see site schedule (attached)\n"
            "Provider: Tri-State Electrical Cooperative\n"
            "Acct: TSEC-CORP-9928-A\n"
            "Consolidation invoice: TSEC-CORP-9928-A-Q1-25\n"
            "Covers: Jan, Feb, Mar 2025\n\n"
            "Site A (HQ):         $1,842.00\n"
            "Site B (Warehouse):    $904.50\n"
            "Site C (Annex):        $388.00\n"
            "Demand charges:        $512.00\n"
            "Power factor adj:      +$84.50\n"
            "Green energy credit:  -$120.00\n\n"
            "Franchise fee (est.): $178.20\n"
            "TOTAL Q1 2025:      $3,789.20"
        ),
        "vendor_name": "Tri-State Electrical Cooperative",
        "invoice_date": None,
        "invoice_number": "TSEC-CORP-9928-A-Q1-25",
        "total_amount": 3789.20,
        "tax_amount": 178.20,
        "line_item_count": 6,
    },

    # ─────────────────────── SOFTWARE / SAAS ─────────────────────────────────
    # easy
    {
        "category": "software_saas", "difficulty": "easy",
        "invoice_text": (
            "SUBSCRIPTION INVOICE\n"
            "Vendor: Salesforce Inc.\n"
            "Invoice #: SF-2025-INV-00041\n"
            "Invoice Date: 2025-01-01\n\n"
            "  Sales Cloud Enterprise (50 users × $150/mo × 12 mo)   $90,000.00\n\n"
            "Tax: $7,200.00\n"
            "Total Due: $97,200.00"
        ),
        "vendor_name": "Salesforce Inc.",
        "invoice_date": "2025-01-01",
        "invoice_number": "SF-2025-INV-00041",
        "total_amount": 97200.00,
        "tax_amount": 7200.00,
        "line_item_count": 1,
    },
    {
        "category": "software_saas", "difficulty": "easy",
        "invoice_text": (
            "INVOICE\n"
            "Company: Atlassian\n"
            "Invoice Number: ATL-2024-0128847\n"
            "Date: November 1, 2024\n\n"
            "  Jira Software (Cloud, 25 users)   $3,750.00\n"
            "  Confluence (Cloud, 25 users)       $2,625.00\n"
            "  Jira Service Management (10 agents) $6,000.00\n\n"
            "GST: $1,237.50\n"
            "Total: $13,612.50"
        ),
        "vendor_name": "Atlassian",
        "invoice_date": "2024-11-01",
        "invoice_number": "ATL-2024-0128847",
        "total_amount": 13612.50,
        "tax_amount": 1237.50,
        "line_item_count": 3,
    },
    {
        "category": "software_saas", "difficulty": "easy",
        "invoice_text": (
            "TAX INVOICE\n"
            "Supplier: Adobe Systems Inc.\n"
            "Invoice ID: ADBE-US-20250115-7832\n"
            "Date of Issue: January 15, 2025\n\n"
            "  Adobe Creative Cloud All Apps (annual, 10 seats)   $6,600.00\n"
            "  Adobe Sign (enterprise)                            $2,400.00\n\n"
            "Sales Tax: $719.40\n"
            "Total Amount: $9,719.40"
        ),
        "vendor_name": "Adobe Systems Inc.",
        "invoice_date": "2025-01-15",
        "invoice_number": "ADBE-US-20250115-7832",
        "total_amount": 9719.40,
        "tax_amount": 719.40,
        "line_item_count": 2,
    },
    # medium
    {
        "category": "software_saas", "difficulty": "medium",
        "invoice_text": (
            "Snowflake Inc. | Invoice SNF-2025-Q1-88320\n"
            "Billing period: January 1 – March 31, 2025\n"
            "Invoice rendered: March 31, 2025\n\n"
            "Compute credits consumed:    $14,820.00\n"
            "Storage (avg 4.2TB × $23)      $966.00\n"
            "Data transfer (egress):         $340.00\n"
            "Support (Business plan):        $900.00\n\n"
            "Promotional credit applied:   -$500.00\n"
            "Applicable tax: $1,322.08\n"
            "Total Billed: $17,848.08"
        ),
        "vendor_name": "Snowflake Inc.",
        "invoice_date": "2025-03-31",
        "invoice_number": "SNF-2025-Q1-88320",
        "total_amount": 17848.08,
        "tax_amount": 1322.08,
        "line_item_count": 5,
    },
    {
        "category": "software_saas", "difficulty": "medium",
        "invoice_text": (
            "Microsoft Azure | Invoice MAZ-2025-02-00049823\n"
            "Billing period end: Feb 28, 2025\n\n"
            "Compute (B4ms, 720 hrs):      $278.40\n"
            "Azure SQL Managed Instance:   $892.00\n"
            "Storage (LRS, 5TB):           $102.00\n"
            "Azure OpenAI Service tokens:  $614.50\n"
            "Bandwidth (outbound 1.2TB):    $89.40\n\n"
            "Enterprise Agreement discount (-15%):  -$296.44\n"
            "Tax: $0 (EA exempt this billing period)\n"
            "Total: $1,679.86"
        ),
        "vendor_name": "Microsoft Azure",
        "invoice_date": "2025-02-28",
        "invoice_number": "MAZ-2025-02-00049823",
        "total_amount": 1679.86,
        "tax_amount": None,
        "line_item_count": 6,
    },
    {
        "category": "software_saas", "difficulty": "medium",
        "invoice_text": (
            "INVOICE — Zoom Video Communications\n"
            "ZVC Ref: ZVC-ENT-2025-00441 | PO: PO-ZOOM-882\n"
            "Date: March 1, 2025\n\n"
            "Zoom One Business Plus\n"
            "  250 hosts × $19.99/mo × 12 months    $59,970.00\n"
            "Zoom Rooms (20 rooms × $49/mo × 12)    $11,760.00\n"
            "Zoom Phone (100 lines × $10/mo × 12)   $12,000.00\n\n"
            "Tax (8.625%): $7,207.24\n"
            "Contract total: $90,937.24"
        ),
        "vendor_name": "Zoom Video Communications",
        "invoice_date": "2025-03-01",
        "invoice_number": "ZVC-ENT-2025-00441",
        "total_amount": 90937.24,
        "tax_amount": 7207.24,
        "line_item_count": 3,
    },
    # hard
    {
        "category": "software_saas", "difficulty": "hard",
        "invoice_text": (
            "CONSOLIDATED SOFTWARE RENEWAL INVOICE\n"
            "Reseller: Presidio Technology Solutions\n"
            "Reseller Invoice: PTS-ENT-25-00872\n"
            "End-customer: refer to attached order form\n"
            "Date: See renewal schedule; Statement date: 31-Mar-25\n\n"
            "Microsoft M365 E5 (200 seats, 12mo)          $72,000.00\n"
            "Defender for Endpoint P2 add-on (200)         $8,400.00\n"
            "Azure AD Premium P2 (200)                     $3,600.00\n"
            "Co-management fee (Presidio)                  $4,800.00\n"
            "True-up adjustment (Q3 audit):               +$1,200.00\n\n"
            "Applicable sales tax (varies by jurisdiction): $6,000.00 (est.)\n"
            "GRAND TOTAL (USD): $96,000.00"
        ),
        "vendor_name": "Presidio Technology Solutions",
        "invoice_date": "2025-03-31",
        "invoice_number": "PTS-ENT-25-00872",
        "total_amount": 96000.00,
        "tax_amount": 6000.00,
        "line_item_count": 5,
    },
    {
        "category": "software_saas", "difficulty": "hard",
        "invoice_text": (
            "AWS | Invoice AWS-US-2025-0209-BLENDED\n"
            "Acct: 123456789012 | Consolidated (3 linked accounts)\n"
            "Period: Feb 2025 | Rendered automatically\n\n"
            "EC2 (family: r6i, m6i, c6g):     $4,821.40\n"
            "RDS Multi-AZ (PostgreSQL 14):     $1,644.00\n"
            "S3 (storage + requests):            $387.60\n"
            "CloudFront (1.8TB xfr):             $156.90\n"
            "Lambda (12B invocations):           $240.00\n"
            "SES (outbound mail):                 $48.00\n"
            "Support (Business, prorated):       $475.00\n\n"
            "Savings Plans savings:           -$1,200.00\n"
            "Tax (auto-calculated):             $626.47\n"
            "Net Billed: $7,199.37"
        ),
        "vendor_name": "AWS",
        "invoice_date": "2025-02-28",
        "invoice_number": "AWS-US-2025-0209-BLENDED",
        "total_amount": 7199.37,
        "tax_amount": 626.47,
        "line_item_count": 8,
    },
]

# ── Pad to 100 items (duplicate with variation to reach 20 per category × 5) ──
def pad_items(base_items, target=100):
    """Expand to target count by creating variations of existing items."""
    import copy, re
    result = copy.deepcopy(base_items)

    vendors_extra = [
        ("tech_services",         "easy",   "Strata Cloud Corp",       "SCC-2024-00551", "2024-06-20",  8800.00,  704.00, 2),
        ("tech_services",         "easy",   "BluePrint DevOps",         "BPD-INV-0029",  "2024-09-10",  5250.00,  420.00, 1),
        ("tech_services",         "medium", "Kinetic Systems Group",    "KSG-25-0183",   "2025-01-22", 19400.00, 1552.00, 3),
        ("tech_services",         "medium", "Orion Network Services",   "ONS-2025-0078", "2025-02-19",  7620.50,  609.64, 4),
        ("tech_services",         "hard",   "Vertex Integration Labs",  "VIL-H-25-0041", "2025-11-30", 58300.00, 4664.00, 7),
        ("tech_services",         "hard",   "Delta Secure Systems",     "DSS-CORP-2025", "2025-06-15", 32100.00, 2568.00, 5),
        ("office_supplies",       "easy",   "Warehouse Direct Co.",     "WDC-2024-8810", "2024-08-22",   220.45,   17.63, 4),
        ("office_supplies",       "easy",   "PaperPlus Inc.",           "PP-20241101",   "2024-11-01",   512.80,   41.02, 6),
        ("office_supplies",       "medium", "FurniCo Business",         "FCB-INV-0291",  "2025-01-09",  3180.00,  254.40, 3),
        ("office_supplies",       "medium", "EcoSupplies LLC",          "ECO-2025-0044", "2025-03-03",   895.20,   71.62, 5),
        ("office_supplies",       "hard",   "Premier Office Group",     "POG-Q1-25-ADJ", "2025-03-31",  1420.88,  113.67, 6),
        ("professional_services", "easy",   "Summit HR Advisors",       "SHA-2025-0011", "2025-01-08",  4500.00,    0.00, 2),
        ("professional_services", "easy",   "Blue Ridge Tax Group",     "BRT-INV-2025",  "2025-02-01",  9200.00,  736.00, 3),
        ("professional_services", "medium", "Clover Brand Agency",      "CBA-MKT-25048", "2025-04-15", 14500.00, 1160.00, 4),
        ("professional_services", "medium", "Nova Actuarial Partners",  "NAP-2025-0092", "2025-05-30", 28400.00, 2272.00, 3),
        ("professional_services", "hard",   "Apex Global Consulting",   "AGC-2025-ENGX", "2025-08-31", 97000.00,    0.00, 8),
        ("utilities",             "easy",   "SunCity Telecom",          "SCT-INV-00912", "2024-10-15",   945.00,   75.60, 3),
        ("utilities",             "medium", "Eastern Grid Services",    "EGS-2025-0061", "2025-02-28",  4100.00,  328.00, 5),
        ("utilities",             "hard",   "National Gas Consortium",  "NGC-CORP-Q425", None,          6200.00,  248.00, 7),
        ("software_saas",         "easy",   "HubSpot Inc.",             "HS-2025-00892", "2025-01-01", 21600.00, 1728.00, 2),
        ("software_saas",         "medium", "Datadog Inc.",             "DD-2025-03-551","2025-03-31", 12400.00,  992.00, 4),
        ("software_saas",         "hard",   "Oracle Cloud",             "OCI-ENT-25-009","2025-03-31", 84000.00, 6720.00, 6),
    ]

    for cat, diff, vendor, inv_num, inv_date, total, tax, lic in vendors_extra:
        invoice_text = (
            f"INVOICE\nVendor: {vendor}\nInvoice #: {inv_num}\n"
            f"Date: {inv_date if inv_date else 'See attached schedule'}\n\n"
            f"Services/Products rendered as per agreed terms.\n"
            f"{'Tax: $' + f'{tax:.2f}' if tax else 'Tax: N/A (exempt)'}\n"
            f"Total Due: ${total:.2f}"
        )
        result.append({
            "category": cat, "difficulty": diff,
            "invoice_text": invoice_text,
            "vendor_name": vendor,
            "invoice_date": inv_date,
            "invoice_number": inv_num,
            "total_amount": total,
            "tax_amount": tax if tax else None,
            "line_item_count": lic,
        })

    # trim or keep
    while len(result) < target:
        idx = random.randint(0, len(result) - 1)
        clone = copy.deepcopy(result[idx])
        old_num = clone["invoice_number"]
        new_num = old_num + "-X"
        clone["invoice_number"] = new_num
        clone["invoice_text"] = clone["invoice_text"].replace(old_num, new_num)
        result.append(clone)

    return result[:target]


def build_gold_set():
    items = pad_items(GOLD_SET, target=100)

    # Assign IDs
    for i, item in enumerate(items, start=1):
        item["item_id"] = f"UC2_{i:03d}"

    # Stratified 70/30 split: within each (category, difficulty) group
    # Uses floor + remainder distribution to guarantee exactly 30 test items
    from collections import defaultdict
    import math
    TARGET_TEST = 30
    groups = defaultdict(list)
    for item in items:
        groups[(item["category"], item["difficulty"])].append(item)

    group_list = list(groups.values())
    # Floor allocation per group
    test_counts = [max(1, math.floor(len(g) * 0.30)) for g in group_list]
    # Distribute remaining slots to largest groups first
    remainder = TARGET_TEST - sum(test_counts)
    if remainder > 0:
        order = sorted(range(len(group_list)), key=lambda i: -len(group_list[i]))
        for i in order[:remainder]:
            test_counts[i] += 1

    for group_items, n_test in zip(group_list, test_counts):
        for i, item in enumerate(group_items):
            item["split"] = "test" if i >= len(group_items) - n_test else "train"

    return items


def main():
    os.makedirs("data/gold_sets", exist_ok=True)

    print("Building UC2 Gold Set — Invoice Field Extraction...")
    items = build_gold_set()

    # Save pre-registration metadata
    meta = {
        **PREREGISTRATION,
        "build_date": datetime.now().isoformat(),
        "total_items": len(items),
        "train_items": sum(1 for x in items if x["split"] == "train"),
        "test_items": sum(1 for x in items if x["split"] == "test"),
        "category_distribution": {},
        "difficulty_distribution": {},
        "null_date_count": sum(1 for x in items if not x["invoice_date"]),
        "null_tax_count": sum(1 for x in items if x["tax_amount"] is None),
    }

    for item in items:
        meta["category_distribution"][item["category"]] = meta["category_distribution"].get(item["category"], 0) + 1
        meta["difficulty_distribution"][item["difficulty"]] = meta["difficulty_distribution"].get(item["difficulty"], 0) + 1

    with open("data/gold_sets/uc2_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    # Save CSV
    fields = ["item_id", "category", "difficulty", "split", "invoice_text",
              "vendor_name", "invoice_date", "invoice_number",
              "total_amount", "tax_amount", "line_item_count"]

    with open("data/gold_sets/uc2_invoice_extraction.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in items:
            writer.writerow({k: item.get(k, "") for k in fields})

    # Print summary
    print("=" * 62)
    print("  UC2 GOLD SET — Build Complete")
    print("  Invoice Field Extraction — Pre-Registration v1.0")
    print("=" * 62)
    print(f"  S³ Score (pre-registered):  {PREREGISTRATION['s3_score_preregistered']}  →  {PREREGISTRATION['s3_prediction']}")
    print(f"  S³ Score (G1 corrected):    {PREREGISTRATION['s3_score_corrected_denominator']}  →  {PREREGISTRATION['s3_prediction']}")
    print(f"  Total items  : {len(items)}")
    print(f"  Train / Test : {meta['train_items']} / {meta['test_items']}")
    print(f"  Null dates   : {meta['null_date_count']} items (hard invoices without explicit date)")
    print(f"  Null tax     : {meta['null_tax_count']} items (tax-exempt invoices)")
    print()
    print("  Category distribution:")
    for cat, n in sorted(meta["category_distribution"].items()):
        bar = "█" * int(n * 2.5)
        print(f"    {cat:<25} {bar:<30} {n}")
    print()
    print("  Difficulty distribution:")
    for diff, n in sorted(meta["difficulty_distribution"].items()):
        bar = "█" * int(n * 1.5)
        print(f"    {diff:<10} {bar:<45} {n}")
    print()
    print("  Pre-registered hypotheses:")
    for h_id, h_text in PREREGISTRATION["hypotheses"].items():
        print(f"    {h_id}: {h_text}")
    print()
    print("  Files saved:")
    print("    data/gold_sets/uc2_invoice_extraction.csv")
    print("    data/gold_sets/uc2_metadata.json")
    print()
    print("  ✅  Gold set locked — DO NOT MODIFY after this point")
    print("      This is your pre-registered ground truth.")
    print()
    print("  NEXT STEP:")
    print("  → python3 scripts/run_benchmark_uc2.py")
    print("  → Runs all 7 models against UC2 test set (30 items × 7 models × 3 runs)")
    print("=" * 62)


if __name__ == "__main__":
    main()