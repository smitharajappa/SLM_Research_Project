"""
build_gold_set_uc7.py
Builds the pre-registered 100-item gold set for UC7: Legal Contract Clause Analysis
Saves to: data/gold_sets/uc7_legal_contract_analysis.csv

Gold set structure:
  25 HIGH_RISK clauses
  25 MEDIUM_RISK clauses
  25 LOW_RISK clauses
  25 STANDARD clauses
  Each item: id, text, label, category, subcategory, difficulty, source, notes

PRE-REGISTRATION DATE: March 2, 2026
DO NOT MODIFY after benchmark execution begins.
"""

import csv
import os
import json
from datetime import datetime

# ── Output path ────────────────────────────────────────────────
OUTPUT_DIR  = "data/gold_sets"
OUTPUT_FILE = "uc7_legal_contract_analysis.csv"
META_FILE   = "uc7_metadata.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Gold set items ─────────────────────────────────────────────
# Columns: id, text, label, category, subcategory, difficulty, source, notes
# difficulty: easy / medium / hard
# source: synthetic
# ──────────────────────────────────────────────────────────────

GOLD_SET = [

    # ══════════════════════════════════════════════════════════
    # HIGH_RISK — Indemnification (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_001", "label": "HIGH_RISK",
        "category": "Indemnification", "subcategory": "Unlimited Indemnity",
        "difficulty": "easy",
        "text": "The Receiving Party shall indemnify, defend, and hold harmless the Disclosing Party and its affiliates, officers, directors, employees, and agents from and against any and all claims, damages, losses, liabilities, costs, and expenses (including reasonable attorneys' fees) arising out of or in connection with this Agreement, without limitation as to amount or duration.",
        "source": "synthetic",
        "notes": "Classic unlimited indemnification — no cap, no carve-outs"
    },
    {
        "id": "UC7_002", "label": "HIGH_RISK",
        "category": "Indemnification", "subcategory": "Broad Scope Indemnity",
        "difficulty": "easy",
        "text": "Vendor shall indemnify and hold harmless Client against all losses, claims, damages, and expenses of any kind whatsoever, including but not limited to consequential, incidental, special, and punitive damages, arising from any act or omission of Vendor, its employees, subcontractors, or agents, whether or not such act or omission constitutes negligence.",
        "source": "synthetic",
        "notes": "Indemnification regardless of fault — extremely broad"
    },
    {
        "id": "UC7_003", "label": "HIGH_RISK",
        "category": "Indemnification", "subcategory": "Asymmetric Indemnity",
        "difficulty": "medium",
        "text": "Service Provider agrees to indemnify Client for any third-party claims related to the Services, including claims arising from Client's own specifications, instructions, or materials. Client shall have no reciprocal indemnification obligations under this Agreement.",
        "source": "synthetic",
        "notes": "One-sided indemnity covering Client's own actions — hidden asymmetry"
    },
    {
        "id": "UC7_004", "label": "HIGH_RISK",
        "category": "Indemnification", "subcategory": "IP Indemnity Unlimited",
        "difficulty": "medium",
        "text": "Licensor shall indemnify, defend, and hold Licensee harmless from any intellectual property infringement claim, including patent, copyright, trade secret, and trademark claims, and shall pay all damages, settlements, costs, and attorneys' fees without any aggregate cap on Licensor's indemnification obligations.",
        "source": "synthetic",
        "notes": "Uncapped IP indemnity — can be ruinous for licensor"
    },
    {
        "id": "UC7_005", "label": "HIGH_RISK",
        "category": "Indemnification", "subcategory": "Hidden Obligation",
        "difficulty": "hard",
        "text": "Each party shall indemnify the other for third-party claims arising from its breach. Notwithstanding the foregoing, Provider additionally agrees to indemnify Client for any regulatory fines, penalties, or enforcement actions imposed on Client that are in any way related to the Services, regardless of whether Provider was aware of the applicable regulatory requirements.",
        "source": "synthetic",
        "notes": "Appears mutual but buries asymmetric regulatory indemnity in second sentence"
    },

    # ══════════════════════════════════════════════════════════
    # HIGH_RISK — Liability (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_006", "label": "HIGH_RISK",
        "category": "Liability", "subcategory": "Unlimited Liability",
        "difficulty": "easy",
        "text": "Neither party's liability under this Agreement shall be limited in any way. Each party shall be liable for all direct, indirect, incidental, special, consequential, and punitive damages arising out of or related to this Agreement, regardless of the form of action or theory of liability.",
        "source": "synthetic",
        "notes": "Explicitly unlimited liability for all damage types"
    },
    {
        "id": "UC7_007", "label": "HIGH_RISK",
        "category": "Liability", "subcategory": "Uncapped Consequential",
        "difficulty": "medium",
        "text": "Notwithstanding any other provision of this Agreement, neither party excludes or limits its liability for indirect, consequential, or special damages, including but not limited to loss of profits, loss of revenue, loss of data, and loss of business opportunity. The limitations set forth in Section 9.1 shall not apply to claims under this Section.",
        "source": "synthetic",
        "notes": "Carves out consequential damages from any cap — high exposure"
    },
    {
        "id": "UC7_008", "label": "HIGH_RISK",
        "category": "Liability", "subcategory": "Asymmetric Liability",
        "difficulty": "hard",
        "text": "Supplier's aggregate liability for all claims under this Agreement shall not exceed the fees paid in the twelve (12) months preceding the claim. Client's liability shall not be subject to any limitation or exclusion, and Client acknowledges that Supplier's potential damages are not reasonably foreseeable and may substantially exceed the contract value.",
        "source": "synthetic",
        "notes": "Supplier capped but Client uncapped — asymmetry buried in reasonable-looking clause"
    },
    {
        "id": "UC7_009", "label": "HIGH_RISK",
        "category": "Liability", "subcategory": "Broad Liability Assumption",
        "difficulty": "hard",
        "text": "Contractor assumes full liability for any harm, loss, or damage arising in connection with the performance of the Work, including harm caused by the acts or omissions of Owner, Owner's employees, or third parties present at the worksite. Contractor waives any right of contribution or subrogation against Owner.",
        "source": "synthetic",
        "notes": "Assumes liability for counterparty's acts plus waives contribution rights"
    },
    {
        "id": "UC7_010", "label": "HIGH_RISK",
        "category": "Liability", "subcategory": "Consequential Damages Inclusion",
        "difficulty": "medium",
        "text": "In the event of breach, the non-breaching party shall be entitled to recover all damages, including consequential damages, lost profits, diminution in value, and cost of replacement services. The parties agree that such damages are foreseeable as of the Effective Date and are not speculative.",
        "source": "synthetic",
        "notes": "Pre-agrees consequential damages are foreseeable — eliminates key defense"
    },

    # ══════════════════════════════════════════════════════════
    # HIGH_RISK — Termination (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_011", "label": "HIGH_RISK",
        "category": "Termination", "subcategory": "Unilateral At-Will",
        "difficulty": "easy",
        "text": "Client may terminate this Agreement at any time, for any reason or no reason, upon written notice to Provider. Upon such termination, Provider shall immediately cease all work and shall not be entitled to any compensation for work in progress or any termination fee.",
        "source": "synthetic",
        "notes": "Unilateral termination with no compensation for work in progress"
    },
    {
        "id": "UC7_012", "label": "HIGH_RISK",
        "category": "Termination", "subcategory": "Termination for Convenience",
        "difficulty": "medium",
        "text": "Either party may terminate this Agreement for convenience upon thirty (30) days' written notice. Upon termination by Client, all prepaid fees are non-refundable and Provider shall invoice Client for the remaining balance of the minimum commitment period.",
        "source": "synthetic",
        "notes": "Appears mutual but accelerates full contract payment on Client termination"
    },
    {
        "id": "UC7_013", "label": "HIGH_RISK",
        "category": "Termination", "subcategory": "Auto-Renewal Lock-In",
        "difficulty": "hard",
        "text": "This Agreement shall automatically renew for successive one (1) year terms unless either party provides written notice of non-renewal at least one hundred eighty (180) days prior to the end of the then-current term. Upon any early termination, Client shall pay an early termination fee equal to one hundred percent (100%) of the fees remaining in the then-current term.",
        "source": "synthetic",
        "notes": "180-day notice with 100% remaining fees — effectively a lock-in"
    },
    {
        "id": "UC7_014", "label": "HIGH_RISK",
        "category": "Termination", "subcategory": "Broad Termination Trigger",
        "difficulty": "hard",
        "text": "Licensor may immediately terminate this Agreement if Licensee (a) undergoes a change of control, (b) assigns any rights hereunder, (c) experiences a material adverse change in its financial condition, or (d) in Licensor's sole and reasonable judgment, engages in conduct detrimental to Licensor's brand or reputation. Upon termination, all licenses granted herein shall immediately cease.",
        "source": "synthetic",
        "notes": "Subjective termination triggers — 'sole judgment' on brand detriment"
    },
    {
        "id": "UC7_015", "label": "HIGH_RISK",
        "category": "Termination", "subcategory": "Post-Termination Obligations",
        "difficulty": "medium",
        "text": "Upon termination for any reason, Vendor shall continue to provide transition services for up to twelve (12) months at no additional charge. Vendor shall transfer all work product, documentation, and data to Client or its designee within thirty (30) days of termination, at Vendor's sole expense.",
        "source": "synthetic",
        "notes": "12 months of free transition services post-termination"
    },

    # ══════════════════════════════════════════════════════════
    # HIGH_RISK — Non-Compete (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_016", "label": "HIGH_RISK",
        "category": "Non-Compete", "subcategory": "Unlimited Geographic Scope",
        "difficulty": "easy",
        "text": "During the term of this Agreement and for a period of three (3) years thereafter, Consultant shall not, directly or indirectly, engage in, own, manage, operate, or participate in any business that competes with Client's business anywhere in the world.",
        "source": "synthetic",
        "notes": "Worldwide non-compete for 3 years — likely unenforceable but still high risk"
    },
    {
        "id": "UC7_017", "label": "HIGH_RISK",
        "category": "Non-Compete", "subcategory": "Broad Activity Restriction",
        "difficulty": "medium",
        "text": "Employee agrees that for twenty-four (24) months following termination of employment, Employee shall not (a) provide services to any Competing Business, (b) solicit any customer or prospective customer of Employer, or (c) recruit or hire any employee or contractor of Employer. 'Competing Business' means any entity that offers products or services similar to any product or service offered by Employer at any time during Employee's employment.",
        "source": "synthetic",
        "notes": "Expansive definition of Competing Business — covers all historical products"
    },
    {
        "id": "UC7_018", "label": "HIGH_RISK",
        "category": "Non-Compete", "subcategory": "Non-Compete with Penalty",
        "difficulty": "hard",
        "text": "Provider covenants that it will not engage in Competing Activities during the Term and for eighteen (18) months thereafter within the Territory. The parties agree that in the event of breach, Provider shall pay liquidated damages of $500,000 per occurrence, and Client shall be entitled to injunctive relief without the need to post bond or prove irreparable harm.",
        "source": "synthetic",
        "notes": "Liquidated damages plus injunctive relief without bond — compounding penalties"
    },
    {
        "id": "UC7_019", "label": "HIGH_RISK",
        "category": "Non-Compete", "subcategory": "Broad Non-Solicitation",
        "difficulty": "hard",
        "text": "For a period of thirty-six (36) months following the expiration or termination of this Agreement, neither party shall directly or indirectly solicit, divert, or appropriate any business opportunity identified during the Term. Notwithstanding the mutual framing of this clause, Partner A acknowledges that Partner B's client relationships are proprietary, and Partner A's restriction extends to any client with whom Partner B has had contact in the preceding five (5) years.",
        "source": "synthetic",
        "notes": "Appears mutual but second sentence creates massive asymmetric restriction"
    },
    {
        "id": "UC7_020", "label": "HIGH_RISK",
        "category": "Non-Compete", "subcategory": "IP Non-Compete",
        "difficulty": "medium",
        "text": "During the Restricted Period, Licensee shall not develop, market, license, or sell any product or technology that incorporates functionality substantially similar to the Licensed Technology, even if such product or technology was independently developed by Licensee without use of Licensor's confidential information or trade secrets.",
        "source": "synthetic",
        "notes": "Prohibits independent development — extremely restrictive IP non-compete"
    },

    # ══════════════════════════════════════════════════════════
    # HIGH_RISK — Data Privacy (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_021", "label": "HIGH_RISK",
        "category": "Data Privacy", "subcategory": "Unlimited Data Rights",
        "difficulty": "easy",
        "text": "Client hereby grants Provider an irrevocable, perpetual, worldwide, royalty-free license to use, reproduce, modify, and create derivative works from all data provided by Client or generated through Client's use of the Services, for any purpose, including but not limited to Provider's own commercial purposes.",
        "source": "synthetic",
        "notes": "Irrevocable perpetual data license for all purposes — extreme data grab"
    },
    {
        "id": "UC7_022", "label": "HIGH_RISK",
        "category": "Data Privacy", "subcategory": "Broad Data Sharing",
        "difficulty": "medium",
        "text": "Provider may share Client Data with its affiliates, subcontractors, business partners, and other third parties as Provider deems necessary for the provision or improvement of its services. Provider shall use commercially reasonable efforts to ensure such third parties maintain appropriate safeguards, but shall not be liable for any unauthorized access, use, or disclosure by such third parties.",
        "source": "synthetic",
        "notes": "Unlimited third-party sharing with no liability for breaches"
    },
    {
        "id": "UC7_023", "label": "HIGH_RISK",
        "category": "Data Privacy", "subcategory": "Regulatory Non-Compliance",
        "difficulty": "hard",
        "text": "Processor shall process Personal Data in accordance with Controller's instructions. Controller acknowledges that Processor's standard infrastructure may involve the transfer and storage of Personal Data in jurisdictions that do not provide an adequate level of data protection, and Controller consents to such transfers. Processor shall implement technical and organizational measures consistent with industry practice, provided that Controller bears sole responsibility for ensuring compliance with applicable data protection laws.",
        "source": "synthetic",
        "notes": "Shifts all regulatory compliance responsibility to Controller while retaining transfer rights"
    },
    {
        "id": "UC7_024", "label": "HIGH_RISK",
        "category": "Data Privacy", "subcategory": "Data Retention Unlimited",
        "difficulty": "medium",
        "text": "Upon termination of this Agreement, Provider shall have the right to retain all Client Data, including personal data, for an indefinite period for archival, compliance, dispute resolution, and business analytics purposes. Client waives any right to request deletion of such data following termination.",
        "source": "synthetic",
        "notes": "Indefinite data retention with waiver of deletion rights — conflicts with GDPR/CCPA"
    },
    {
        "id": "UC7_025", "label": "HIGH_RISK",
        "category": "Data Privacy", "subcategory": "Breach Notification Waiver",
        "difficulty": "hard",
        "text": "In the event of a Security Incident affecting Client Data, Provider shall notify Client within a commercially reasonable time following Provider's determination that notification is warranted. Client agrees that Provider's determination of whether a Security Incident has occurred, and the appropriate timing of notification, shall be at Provider's sole discretion and shall not give rise to any claim by Client.",
        "source": "synthetic",
        "notes": "Subjective breach notification with no fixed timeline — undermines statutory requirements"
    },

    # ══════════════════════════════════════════════════════════
    # MEDIUM_RISK — Liability (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_026", "label": "MEDIUM_RISK",
        "category": "Liability", "subcategory": "Capped Liability",
        "difficulty": "easy",
        "text": "Each party's aggregate liability under this Agreement shall not exceed the total fees paid or payable by Client during the twelve (12) month period preceding the event giving rise to the claim. This limitation applies to all causes of action in the aggregate, including breach of contract, tort, and strict liability.",
        "source": "synthetic",
        "notes": "Standard 12-month cap — reasonable but not risk-free"
    },
    {
        "id": "UC7_027", "label": "MEDIUM_RISK",
        "category": "Liability", "subcategory": "Consequential Damages Exclusion",
        "difficulty": "easy",
        "text": "In no event shall either party be liable to the other for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenue, data, or business opportunity, arising out of or related to this Agreement, regardless of whether such damages are based on contract, tort, strict liability, or any other theory.",
        "source": "synthetic",
        "notes": "Mutual consequential damages exclusion — standard but creates medium risk"
    },
    {
        "id": "UC7_028", "label": "MEDIUM_RISK",
        "category": "Liability", "subcategory": "Tiered Liability Cap",
        "difficulty": "medium",
        "text": "Provider's aggregate liability shall not exceed two times (2x) the annual fees paid under this Agreement for direct damages. For data breach claims, Provider's liability shall be capped at five times (5x) annual fees. Notwithstanding the foregoing, these limitations shall not apply to Provider's indemnification obligations under Section 8.",
        "source": "synthetic",
        "notes": "Tiered cap with carve-out for indemnification — moderate risk"
    },
    {
        "id": "UC7_029", "label": "MEDIUM_RISK",
        "category": "Liability", "subcategory": "Limited Warranty",
        "difficulty": "medium",
        "text": "Provider warrants that the Services will conform in all material respects to the specifications set forth in the applicable Statement of Work for a period of ninety (90) days following delivery. Provider's sole obligation and Client's exclusive remedy for breach of this warranty shall be, at Provider's option, repair or replacement of the non-conforming Services or a refund of fees paid for such Services.",
        "source": "synthetic",
        "notes": "Limited warranty with exclusive remedy — caps exposure but restricts Client's options"
    },
    {
        "id": "UC7_030", "label": "MEDIUM_RISK",
        "category": "Liability", "subcategory": "Insurance Requirement",
        "difficulty": "hard",
        "text": "Contractor shall maintain commercial general liability insurance with limits of not less than $2,000,000 per occurrence and $5,000,000 in the aggregate, professional liability insurance of $3,000,000, and cyber liability insurance of $5,000,000. All policies shall name Client as an additional insured. Contractor's aggregate liability cap under this Agreement shall equal the applicable insurance limits.",
        "source": "synthetic",
        "notes": "Cap tied to insurance limits — seems protective but creates ambiguity if policy lapses"
    },

    # ══════════════════════════════════════════════════════════
    # MEDIUM_RISK — Non-Compete (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_031", "label": "MEDIUM_RISK",
        "category": "Non-Compete", "subcategory": "Geographically Limited",
        "difficulty": "easy",
        "text": "During the term of this Agreement and for twelve (12) months following its expiration, Consultant shall not engage in any Competing Business within a fifty (50) mile radius of Client's principal place of business. 'Competing Business' means any entity offering services substantially similar to those provided under this Agreement.",
        "source": "synthetic",
        "notes": "Geographically limited non-compete with reasonable duration"
    },
    {
        "id": "UC7_032", "label": "MEDIUM_RISK",
        "category": "Non-Compete", "subcategory": "Non-Solicitation Mutual",
        "difficulty": "easy",
        "text": "For a period of twelve (12) months following termination, neither party shall directly solicit for employment any employee of the other party who was involved in the performance of this Agreement. This restriction does not apply to general advertising or recruitment efforts not specifically targeted at the other party's employees.",
        "source": "synthetic",
        "notes": "Mutual non-solicitation with carve-out for general recruiting — balanced"
    },
    {
        "id": "UC7_033", "label": "MEDIUM_RISK",
        "category": "Non-Compete", "subcategory": "Customer Non-Solicitation",
        "difficulty": "medium",
        "text": "For eighteen (18) months following termination, Provider shall not directly or indirectly solicit or accept business from any customer of Client to whom Provider provided services during the final twenty-four (24) months of the Agreement. Provider may continue to serve such customers with respect to services unrelated to those provided under this Agreement.",
        "source": "synthetic",
        "notes": "Customer non-solicitation with reasonable scope and carve-out"
    },
    {
        "id": "UC7_034", "label": "MEDIUM_RISK",
        "category": "Non-Compete", "subcategory": "Industry Restriction",
        "difficulty": "hard",
        "text": "Employee agrees that for twelve (12) months following separation, Employee will not provide consulting, advisory, or employment services to any entity listed on Exhibit B (Restricted Competitors). The parties shall review and update Exhibit B annually. Employer may add up to five (5) new entities to Exhibit B per year, provided each addition is a bona fide competitor at the time of addition.",
        "source": "synthetic",
        "notes": "Named competitors with annual update right — seems reasonable but update mechanism creates drift risk"
    },
    {
        "id": "UC7_035", "label": "MEDIUM_RISK",
        "category": "Non-Compete", "subcategory": "Conditional Non-Compete",
        "difficulty": "hard",
        "text": "The non-compete restrictions set forth in Section 7.1 shall apply only if Employer provides Employee with garden leave compensation equal to fifty percent (50%) of Employee's base salary during the restricted period. If Employer elects not to provide such compensation, the non-compete shall be void and of no effect, but the non-solicitation obligations shall remain in full force.",
        "source": "synthetic",
        "notes": "Garden leave conditional non-compete — nuanced enforceability depends on election"
    },

    # ══════════════════════════════════════════════════════════
    # MEDIUM_RISK — Warranty (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_036", "label": "MEDIUM_RISK",
        "category": "Warranty", "subcategory": "Limited Warranty",
        "difficulty": "easy",
        "text": "Seller warrants that the Products shall be free from defects in materials and workmanship for a period of twelve (12) months from the date of delivery. This warranty does not cover damage resulting from misuse, unauthorized modification, or failure to follow Seller's instructions. Seller's liability under this warranty is limited to repair, replacement, or credit at Seller's option.",
        "source": "synthetic",
        "notes": "Standard limited product warranty with reasonable exclusions"
    },
    {
        "id": "UC7_037", "label": "MEDIUM_RISK",
        "category": "Warranty", "subcategory": "Warranty Disclaimer",
        "difficulty": "medium",
        "text": "EXCEPT AS EXPRESSLY SET FORTH IN SECTION 5.1, THE SERVICES ARE PROVIDED 'AS IS' AND PROVIDER DISCLAIMS ALL WARRANTIES, WHETHER EXPRESS, IMPLIED, OR STATUTORY, INCLUDING WITHOUT LIMITATION WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. Provider does not warrant that the Services will be uninterrupted or error-free.",
        "source": "synthetic",
        "notes": "Standard AS-IS disclaimer but leaves express warranty intact — common SaaS pattern"
    },
    {
        "id": "UC7_038", "label": "MEDIUM_RISK",
        "category": "Warranty", "subcategory": "SLA with Credits",
        "difficulty": "medium",
        "text": "Provider shall use commercially reasonable efforts to maintain 99.9% uptime for the Platform, measured monthly. In the event Provider fails to meet this commitment, Client shall receive a service credit equal to five percent (5%) of the monthly fees for each full hour of downtime exceeding the commitment, up to a maximum credit of twenty-five percent (25%) of monthly fees.",
        "source": "synthetic",
        "notes": "SLA with capped service credits — no direct damages for downtime"
    },
    {
        "id": "UC7_039", "label": "MEDIUM_RISK",
        "category": "Warranty", "subcategory": "Performance Warranty",
        "difficulty": "hard",
        "text": "Vendor warrants that the Software shall perform substantially in accordance with the Documentation. If Client reports a material non-conformity within sixty (60) days of acceptance, Vendor shall use reasonable efforts to correct the non-conformity. If Vendor cannot correct the non-conformity within ninety (90) days, Client may terminate the affected Order and receive a pro-rata refund of prepaid unused fees.",
        "source": "synthetic",
        "notes": "Short acceptance window plus 'reasonable efforts' standard — subtle limitation"
    },
    {
        "id": "UC7_040", "label": "MEDIUM_RISK",
        "category": "Warranty", "subcategory": "Liquidated Damages",
        "difficulty": "hard",
        "text": "In the event Contractor fails to achieve Substantial Completion by the Guaranteed Completion Date, Contractor shall pay Owner liquidated damages in the amount of $5,000 per calendar day of delay, up to a maximum of ten percent (10%) of the Contract Price. The parties agree that actual damages for delay are difficult to ascertain and that this amount represents a reasonable estimate of such damages.",
        "source": "synthetic",
        "notes": "Liquidated damages with cap — reasonable on face but daily accrual creates pressure"
    },

    # ══════════════════════════════════════════════════════════
    # MEDIUM_RISK — IP Rights (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_041", "label": "MEDIUM_RISK",
        "category": "IP Rights", "subcategory": "Work-for-Hire with License Back",
        "difficulty": "easy",
        "text": "All Work Product created by Contractor in the performance of the Services shall be considered work made for hire and shall be the exclusive property of Client. Contractor hereby assigns to Client all right, title, and interest in such Work Product. Client grants Contractor a non-exclusive, royalty-free license to use the general concepts, techniques, and know-how developed during the engagement.",
        "source": "synthetic",
        "notes": "Full IP assignment with limited license-back — standard consulting arrangement"
    },
    {
        "id": "UC7_042", "label": "MEDIUM_RISK",
        "category": "IP Rights", "subcategory": "Joint Ownership",
        "difficulty": "medium",
        "text": "Any intellectual property jointly developed by the parties during the performance of this Agreement shall be jointly owned. Each party shall have the right to use, license, and exploit such Joint IP without the consent of or accounting to the other party, subject to the confidentiality obligations herein.",
        "source": "synthetic",
        "notes": "Joint IP ownership without consent requirement — creates commercialization risk"
    },
    {
        "id": "UC7_043", "label": "MEDIUM_RISK",
        "category": "IP Rights", "subcategory": "Background IP Reservation",
        "difficulty": "medium",
        "text": "Provider retains all right, title, and interest in its pre-existing intellectual property and any improvements, modifications, or derivative works thereof ('Provider Technology'). Client is granted a non-exclusive, non-transferable, limited license to use Provider Technology solely as embedded in the Deliverables for Client's internal business purposes.",
        "source": "synthetic",
        "notes": "Provider retains background IP including improvements — could limit Client's flexibility"
    },
    {
        "id": "UC7_044", "label": "MEDIUM_RISK",
        "category": "IP Rights", "subcategory": "Moral Rights Waiver",
        "difficulty": "hard",
        "text": "To the extent permitted by applicable law, Contractor irrevocably waives all moral rights in the Work Product, including rights of attribution and integrity. Contractor acknowledges that Client may modify, adapt, or create derivative works from the Work Product without attribution to Contractor, and Contractor consents to any such modification.",
        "source": "synthetic",
        "notes": "Moral rights waiver — enforceable in US but problematic in EU jurisdictions"
    },
    {
        "id": "UC7_045", "label": "MEDIUM_RISK",
        "category": "IP Rights", "subcategory": "Escrow Provision",
        "difficulty": "hard",
        "text": "Licensor shall deposit the source code of the Licensed Software with a mutually agreed escrow agent. The source code shall be released to Licensee upon the occurrence of a Release Event, including (a) Licensor's insolvency or bankruptcy, (b) Licensor's material breach that remains uncured for sixty (60) days, or (c) Licensor's discontinuation of the Licensed Software. Upon release, Licensee shall have a limited license to use the source code solely for maintenance purposes.",
        "source": "synthetic",
        "notes": "Source code escrow with limited release triggers — protective but release conditions may be narrow"
    },

    # ══════════════════════════════════════════════════════════
    # MEDIUM_RISK — Force Majeure (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_046", "label": "MEDIUM_RISK",
        "category": "Force Majeure", "subcategory": "Broad Force Majeure",
        "difficulty": "easy",
        "text": "Neither party shall be liable for any failure or delay in performing its obligations where such failure or delay results from Force Majeure Events including, but not limited to, acts of God, war, terrorism, pandemic, government action, labor disputes, fire, flood, earthquake, or interruption of utility services. The affected party shall use reasonable efforts to mitigate the impact and resume performance.",
        "source": "synthetic",
        "notes": "Broad force majeure with mitigation requirement — standard but medium risk due to breadth"
    },
    {
        "id": "UC7_047", "label": "MEDIUM_RISK",
        "category": "Force Majeure", "subcategory": "Extended Force Majeure",
        "difficulty": "medium",
        "text": "If a Force Majeure Event continues for more than ninety (90) days, either party may terminate this Agreement upon thirty (30) days' written notice. Upon such termination, Client shall pay for all Services performed and expenses incurred prior to the Force Majeure Event, and Provider shall refund any prepaid fees for Services not yet performed.",
        "source": "synthetic",
        "notes": "Termination right after 90-day force majeure with equitable settlement — moderate risk"
    },
    {
        "id": "UC7_048", "label": "MEDIUM_RISK",
        "category": "Force Majeure", "subcategory": "Asymmetric Force Majeure",
        "difficulty": "hard",
        "text": "Provider shall be excused from performance during Force Majeure Events as defined herein. Client's payment obligations shall not be excused or deferred due to Force Majeure Events, and Client shall continue to pay all fees as they become due regardless of Provider's ability to perform. Provider shall use commercially reasonable efforts to resume performance as soon as practicable.",
        "source": "synthetic",
        "notes": "Force majeure excuses performance but not payment — asymmetric allocation"
    },
    {
        "id": "UC7_049", "label": "MEDIUM_RISK",
        "category": "Force Majeure", "subcategory": "Cyber Event Carve-Out",
        "difficulty": "hard",
        "text": "Force Majeure Events shall include the events described in Section 12.1, provided that cyber attacks, ransomware, distributed denial of service attacks, and other security incidents shall not constitute Force Majeure Events and shall remain the sole responsibility of the affected party. Each party shall maintain reasonable security measures as a condition of invoking force majeure protections.",
        "source": "synthetic",
        "notes": "Carves out cyber events from force majeure — allocates security risk regardless of fault"
    },
    {
        "id": "UC7_050", "label": "MEDIUM_RISK",
        "category": "Force Majeure", "subcategory": "Supply Chain Disruption",
        "difficulty": "medium",
        "text": "Supplier shall be excused from timely delivery in the event of supply chain disruptions beyond its reasonable control, including raw material shortages, shipping delays, and port closures. Supplier shall provide Buyer with prompt written notice and an estimated timeline for resumption. Buyer may cancel affected purchase orders without penalty if delivery is delayed by more than sixty (60) days.",
        "source": "synthetic",
        "notes": "Supply chain force majeure with cancellation right — balanced but leaves interim costs unaddressed"
    },

    # ══════════════════════════════════════════════════════════
    # LOW_RISK — Payment (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_051", "label": "LOW_RISK",
        "category": "Payment", "subcategory": "Standard Net Terms",
        "difficulty": "easy",
        "text": "Client shall pay all invoices within thirty (30) days of the invoice date. Invoices shall be submitted monthly in arrears for Services performed during the preceding calendar month. Late payments shall accrue interest at a rate of one and one-half percent (1.5%) per month or the maximum rate permitted by law, whichever is less.",
        "source": "synthetic",
        "notes": "Standard Net-30 with reasonable late interest — low risk"
    },
    {
        "id": "UC7_052", "label": "LOW_RISK",
        "category": "Payment", "subcategory": "Net-60 Terms",
        "difficulty": "easy",
        "text": "All amounts due under this Agreement shall be payable within sixty (60) days of receipt of a valid invoice. Each invoice shall include a detailed description of the Services performed, applicable hourly rates, and any approved expenses. Provider may not submit invoices more frequently than once per calendar month.",
        "source": "synthetic",
        "notes": "Net-60 with invoicing detail requirements — standard commercial terms"
    },
    {
        "id": "UC7_053", "label": "LOW_RISK",
        "category": "Payment", "subcategory": "Milestone Payments",
        "difficulty": "medium",
        "text": "Fees shall be invoiced upon completion and Client acceptance of each milestone as set forth in the Project Plan. Client shall have ten (10) business days to review each deliverable and provide acceptance or detailed written objection. Payment for accepted milestones shall be due within thirty (30) days of acceptance.",
        "source": "synthetic",
        "notes": "Milestone-based payments with acceptance period — low risk, standard project terms"
    },
    {
        "id": "UC7_054", "label": "LOW_RISK",
        "category": "Payment", "subcategory": "Expense Reimbursement",
        "difficulty": "medium",
        "text": "Client shall reimburse Contractor for pre-approved, reasonable, and documented out-of-pocket expenses incurred in the performance of the Services. All expenses exceeding $500 must receive prior written approval from Client. Expense reimbursement requests must be submitted within sixty (60) days of incurrence, accompanied by receipts.",
        "source": "synthetic",
        "notes": "Pre-approval expense policy with documentation requirements — low risk"
    },
    {
        "id": "UC7_055", "label": "LOW_RISK",
        "category": "Payment", "subcategory": "Disputed Invoice Process",
        "difficulty": "hard",
        "text": "If Client disputes any invoice in good faith, Client shall pay the undisputed portion and provide written notice of the disputed amount with reasonable supporting detail within fifteen (15) days of receipt. The parties shall negotiate in good faith to resolve the dispute within thirty (30) days. Undisputed amounts remain subject to late payment interest.",
        "source": "synthetic",
        "notes": "Dispute resolution process for invoices — seems protective on both sides"
    },

    # ══════════════════════════════════════════════════════════
    # LOW_RISK — Confidentiality (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_056", "label": "LOW_RISK",
        "category": "Confidentiality", "subcategory": "Standard NDA",
        "difficulty": "easy",
        "text": "Each party agrees to hold in confidence all Confidential Information received from the other party and to use such information solely for the purposes of this Agreement. Confidential Information shall not include information that is (a) publicly available, (b) rightfully known prior to disclosure, (c) independently developed, or (d) rightfully received from a third party without restriction.",
        "source": "synthetic",
        "notes": "Mutual NDA with standard carve-outs — low risk"
    },
    {
        "id": "UC7_057", "label": "LOW_RISK",
        "category": "Confidentiality", "subcategory": "Duration Limited",
        "difficulty": "easy",
        "text": "The obligations of confidentiality set forth in this Section shall survive for a period of three (3) years following the termination or expiration of this Agreement. Upon request, each party shall return or destroy all Confidential Information of the other party and certify such return or destruction in writing.",
        "source": "synthetic",
        "notes": "3-year confidentiality with return/destroy obligation — standard"
    },
    {
        "id": "UC7_058", "label": "LOW_RISK",
        "category": "Confidentiality", "subcategory": "Compelled Disclosure",
        "difficulty": "medium",
        "text": "If a Receiving Party is compelled by law, regulation, or legal process to disclose Confidential Information, the Receiving Party shall (a) provide prompt written notice to the Disclosing Party to the extent legally permitted, (b) cooperate with the Disclosing Party's efforts to obtain a protective order, and (c) disclose only that portion of the Confidential Information that is legally required.",
        "source": "synthetic",
        "notes": "Standard compelled disclosure carve-out with notice and cooperation — low risk"
    },
    {
        "id": "UC7_059", "label": "LOW_RISK",
        "category": "Confidentiality", "subcategory": "Employee Access",
        "difficulty": "medium",
        "text": "Each party shall restrict access to the other party's Confidential Information to those employees, contractors, and advisors who have a need to know such information for the purposes of this Agreement and who are bound by confidentiality obligations no less restrictive than those contained herein. Each party shall be responsible for any breach of this Section by its personnel.",
        "source": "synthetic",
        "notes": "Need-to-know access control with downstream binding — standard practice"
    },
    {
        "id": "UC7_060", "label": "LOW_RISK",
        "category": "Confidentiality", "subcategory": "Residuals Clause",
        "difficulty": "hard",
        "text": "Nothing in this Agreement shall restrict either party from using Residual Information for any purpose. 'Residual Information' means ideas, concepts, know-how, or techniques that are retained in the unaided memory of personnel who have had access to Confidential Information, provided that this right does not constitute a license under any patent, copyright, or other intellectual property right.",
        "source": "synthetic",
        "notes": "Residuals clause — appears benign but allows retention of concepts in memory"
    },

    # ══════════════════════════════════════════════════════════
    # LOW_RISK — Governing Law (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_061", "label": "LOW_RISK",
        "category": "Governing Law", "subcategory": "Choice of Law",
        "difficulty": "easy",
        "text": "This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflict of laws principles. The parties consent to the exclusive jurisdiction and venue of the state and federal courts located in Wilmington, Delaware.",
        "source": "synthetic",
        "notes": "Standard Delaware choice of law with exclusive jurisdiction — low risk"
    },
    {
        "id": "UC7_062", "label": "LOW_RISK",
        "category": "Governing Law", "subcategory": "Arbitration",
        "difficulty": "easy",
        "text": "Any dispute arising out of or relating to this Agreement shall be resolved by binding arbitration administered by the American Arbitration Association under its Commercial Arbitration Rules. The arbitration shall be conducted in New York, New York, before a single arbitrator. The arbitrator's decision shall be final and binding and may be entered as a judgment in any court of competent jurisdiction.",
        "source": "synthetic",
        "notes": "Standard AAA arbitration clause — low risk, common commercial provision"
    },
    {
        "id": "UC7_063", "label": "LOW_RISK",
        "category": "Governing Law", "subcategory": "Mediation First",
        "difficulty": "medium",
        "text": "Prior to initiating arbitration or litigation, the parties shall attempt to resolve any dispute through good faith mediation. Either party may initiate mediation by written notice, and the parties shall select a mutually agreeable mediator within fourteen (14) days. If the dispute is not resolved within forty-five (45) days of the mediation notice, either party may proceed to binding arbitration.",
        "source": "synthetic",
        "notes": "Tiered dispute resolution — mediation then arbitration — low risk"
    },
    {
        "id": "UC7_064", "label": "LOW_RISK",
        "category": "Governing Law", "subcategory": "Waiver of Jury Trial",
        "difficulty": "medium",
        "text": "EACH PARTY HEREBY IRREVOCABLY WAIVES ALL RIGHT TO A TRIAL BY JURY IN ANY ACTION, PROCEEDING, OR COUNTERCLAIM ARISING OUT OF OR RELATING TO THIS AGREEMENT OR THE TRANSACTIONS CONTEMPLATED HEREBY. Each party certifies that this waiver is made knowingly, voluntarily, and without duress.",
        "source": "synthetic",
        "notes": "Mutual jury trial waiver — standard in commercial contracts, low risk"
    },
    {
        "id": "UC7_065", "label": "LOW_RISK",
        "category": "Governing Law", "subcategory": "Attorneys' Fees",
        "difficulty": "hard",
        "text": "In the event of any legal proceeding arising under this Agreement, the prevailing party shall be entitled to recover its reasonable attorneys' fees, costs, and expenses from the non-prevailing party. For purposes of this provision, 'prevailing party' means the party that obtains substantially the relief sought, as determined by the arbitrator or court.",
        "source": "synthetic",
        "notes": "Prevailing party attorneys' fees — seems neutral but 'substantially' can be litigated"
    },

    # ══════════════════════════════════════════════════════════
    # LOW_RISK — Notice (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_066", "label": "LOW_RISK",
        "category": "General Provisions", "subcategory": "Notice Provisions",
        "difficulty": "easy",
        "text": "All notices under this Agreement shall be in writing and shall be deemed duly given when delivered personally, sent by nationally recognized overnight courier, or sent by certified mail, return receipt requested, to the addresses set forth on the signature page. Either party may change its notice address by written notice to the other party.",
        "source": "synthetic",
        "notes": "Standard notice provision — low risk"
    },
    {
        "id": "UC7_067", "label": "LOW_RISK",
        "category": "General Provisions", "subcategory": "Assignment",
        "difficulty": "easy",
        "text": "Neither party may assign this Agreement or any of its rights or obligations hereunder without the prior written consent of the other party, which consent shall not be unreasonably withheld. Notwithstanding the foregoing, either party may assign this Agreement to an affiliate or in connection with a merger, acquisition, or sale of substantially all of its assets.",
        "source": "synthetic",
        "notes": "Standard assignment clause with M&A carve-out — low risk"
    },
    {
        "id": "UC7_068", "label": "LOW_RISK",
        "category": "General Provisions", "subcategory": "Amendment",
        "difficulty": "medium",
        "text": "This Agreement may not be amended, modified, or supplemented except by a written instrument signed by authorized representatives of both parties. No waiver of any provision shall be effective unless in writing and signed by the waiving party. A waiver on one occasion shall not constitute a waiver on any subsequent occasion.",
        "source": "synthetic",
        "notes": "Standard amendment and waiver clause — protects against oral modifications"
    },
    {
        "id": "UC7_069", "label": "LOW_RISK",
        "category": "General Provisions", "subcategory": "Insurance",
        "difficulty": "hard",
        "text": "During the term and for two (2) years following termination, each party shall maintain commercially reasonable insurance coverage appropriate to its obligations under this Agreement, including commercial general liability and professional liability insurance. Each party shall provide certificates of insurance upon reasonable request by the other party.",
        "source": "synthetic",
        "notes": "Mutual insurance maintenance — 'commercially reasonable' is subjective but standard"
    },
    {
        "id": "UC7_070", "label": "LOW_RISK",
        "category": "General Provisions", "subcategory": "Compliance with Laws",
        "difficulty": "hard",
        "text": "Each party shall comply with all applicable federal, state, and local laws, regulations, and ordinances in the performance of its obligations under this Agreement. Each party shall promptly notify the other if it becomes aware of any regulatory change that may materially affect either party's obligations or rights hereunder.",
        "source": "synthetic",
        "notes": "Mutual compliance clause with notification — low risk, but 'materially affect' is subjective"
    },

    # ══════════════════════════════════════════════════════════
    # LOW_RISK — Data Privacy Standard (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_071", "label": "LOW_RISK",
        "category": "Data Privacy", "subcategory": "Standard DPA",
        "difficulty": "medium",
        "text": "Provider shall process Personal Data only on behalf of and in accordance with Client's documented instructions. Provider shall implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk, including encryption at rest and in transit, access controls, and regular security assessments.",
        "source": "synthetic",
        "notes": "Standard data processing agreement terms — GDPR-aligned, low risk"
    },
    {
        "id": "UC7_072", "label": "LOW_RISK",
        "category": "Data Privacy", "subcategory": "Breach Notification Standard",
        "difficulty": "medium",
        "text": "In the event of a Personal Data Breach, Processor shall notify Controller without undue delay and in any event within seventy-two (72) hours of becoming aware of the breach. Such notification shall include the nature of the breach, categories and approximate number of data subjects affected, likely consequences, and measures taken or proposed to address the breach.",
        "source": "synthetic",
        "notes": "72-hour breach notification aligned with GDPR Article 33 — standard compliance"
    },
    {
        "id": "UC7_073", "label": "LOW_RISK",
        "category": "Data Privacy", "subcategory": "Sub-Processor",
        "difficulty": "hard",
        "text": "Processor shall not engage any Sub-Processor without prior written authorization from Controller. Processor shall provide Controller with a current list of Sub-Processors and at least thirty (30) days' prior notice of any intended addition or replacement. Controller may object to any new Sub-Processor on reasonable grounds, and if the objection cannot be resolved, Controller may terminate the affected Services.",
        "source": "synthetic",
        "notes": "Sub-processor controls with objection rights — thorough but standard GDPR compliance"
    },

    # ══════════════════════════════════════════════════════════
    # LOW_RISK — Termination Standard (2 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_074", "label": "LOW_RISK",
        "category": "Termination", "subcategory": "Standard Notice",
        "difficulty": "easy",
        "text": "Either party may terminate this Agreement upon ninety (90) days' prior written notice to the other party. Upon termination, each party shall promptly return or destroy the other party's Confidential Information and pay all amounts due for Services performed through the effective date of termination.",
        "source": "synthetic",
        "notes": "Mutual termination with 90-day notice and equitable wind-down — low risk"
    },
    {
        "id": "UC7_075", "label": "LOW_RISK",
        "category": "Termination", "subcategory": "Cure Period",
        "difficulty": "hard",
        "text": "Either party may terminate this Agreement for material breach if the breaching party fails to cure such breach within thirty (30) days of receiving written notice specifying the breach in reasonable detail. Termination for cause shall not relieve the breaching party of liability for damages arising from the breach or affect any accrued rights or obligations.",
        "source": "synthetic",
        "notes": "Standard cure period termination — 30-day cure, preserves accrued rights"
    },

    # ══════════════════════════════════════════════════════════
    # STANDARD — Definitions (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_076", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Definitions",
        "difficulty": "easy",
        "text": "'Affiliate' means, with respect to a party, any entity that directly or indirectly controls, is controlled by, or is under common control with such party, where 'control' means ownership of fifty percent (50%) or more of the voting securities or equivalent ownership interest.",
        "source": "synthetic",
        "notes": "Standard definition of Affiliate — pure boilerplate"
    },
    {
        "id": "UC7_077", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Definitions",
        "difficulty": "easy",
        "text": "'Confidential Information' means all non-public information disclosed by one party to the other in connection with this Agreement, whether in written, oral, electronic, or other form, that is designated as confidential or that a reasonable person would understand to be confidential given the nature of the information and the circumstances of disclosure.",
        "source": "synthetic",
        "notes": "Standard Confidential Information definition — boilerplate"
    },
    {
        "id": "UC7_078", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Definitions",
        "difficulty": "easy",
        "text": "'Effective Date' means the date on which the last party signs this Agreement. 'Term' means the period commencing on the Effective Date and continuing for twelve (12) months, unless earlier terminated in accordance with Section 10.",
        "source": "synthetic",
        "notes": "Standard effective date and term definitions — boilerplate"
    },
    {
        "id": "UC7_079", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Definitions",
        "difficulty": "medium",
        "text": "'Intellectual Property Rights' means all patents, copyrights, trademarks, trade secrets, and other intellectual property rights, including all applications and registrations relating thereto, and all rights to sue for past, present, and future infringement, misappropriation, or dilution thereof.",
        "source": "synthetic",
        "notes": "Standard IP rights definition — comprehensive but neutral"
    },
    {
        "id": "UC7_080", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Definitions",
        "difficulty": "medium",
        "text": "'Services' means the professional consulting, development, and support services described in one or more Statements of Work executed by the parties from time to time. 'Deliverables' means the tangible work product identified in a Statement of Work to be delivered by Provider to Client.",
        "source": "synthetic",
        "notes": "Standard Services and Deliverables definitions — reference to SOW"
    },

    # ══════════════════════════════════════════════════════════
    # STANDARD — Recitals / Preamble (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_081", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Recitals",
        "difficulty": "easy",
        "text": "WHEREAS, Client desires to engage Provider to perform certain professional services as described herein; and WHEREAS, Provider represents that it has the requisite skills, experience, and resources to perform such services; NOW, THEREFORE, in consideration of the mutual covenants and agreements herein, the parties agree as follows.",
        "source": "synthetic",
        "notes": "Standard recital clause — boilerplate preamble"
    },
    {
        "id": "UC7_082", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Recitals",
        "difficulty": "easy",
        "text": "This Master Services Agreement ('Agreement') is entered into as of the Effective Date by and between Acme Corporation, a Delaware corporation ('Client'), and TechServices LLC, a California limited liability company ('Provider'). Each of Client and Provider may be referred to herein individually as a 'Party' and collectively as the 'Parties.'",
        "source": "synthetic",
        "notes": "Standard preamble identifying the parties — boilerplate"
    },
    {
        "id": "UC7_083", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Recitals",
        "difficulty": "medium",
        "text": "WHEREAS, the parties previously entered into that certain Non-Disclosure Agreement dated January 15, 2025 (the 'NDA'); and WHEREAS, the parties now wish to formalize their commercial relationship and set forth the terms under which Provider will deliver the Services; NOW, THEREFORE, the parties agree that this Agreement supersedes the NDA with respect to confidentiality obligations related to the Services.",
        "source": "synthetic",
        "notes": "Recital referencing prior NDA with supersession language — still standard"
    },
    {
        "id": "UC7_084", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Order of Precedence",
        "difficulty": "hard",
        "text": "In the event of a conflict between the terms of this Agreement and any Statement of Work, the terms of the Statement of Work shall control with respect to the specific services described therein, unless the Statement of Work expressly states that it intends to modify the terms of this Agreement. In all other cases, the terms of this Agreement shall prevail.",
        "source": "synthetic",
        "notes": "Order of precedence clause — standard but nuanced interaction between MSA and SOW"
    },
    {
        "id": "UC7_085", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Recitals",
        "difficulty": "medium",
        "text": "This Agreement, together with all Exhibits, Schedules, and Statements of Work attached hereto or incorporated by reference, constitutes the entire agreement between the parties with respect to the subject matter hereof and supersedes all prior and contemporaneous agreements, proposals, negotiations, representations, and communications, whether written or oral.",
        "source": "synthetic",
        "notes": "Entire agreement / integration clause — pure boilerplate"
    },

    # ══════════════════════════════════════════════════════════
    # STANDARD — Severability & Survival (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_086", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Severability",
        "difficulty": "easy",
        "text": "If any provision of this Agreement is held to be invalid, illegal, or unenforceable by a court of competent jurisdiction, such provision shall be modified to the minimum extent necessary to make it valid and enforceable, and the remaining provisions shall continue in full force and effect.",
        "source": "synthetic",
        "notes": "Standard severability with reformation — boilerplate"
    },
    {
        "id": "UC7_087", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Survival",
        "difficulty": "easy",
        "text": "The following provisions shall survive the expiration or termination of this Agreement: Sections 4 (Intellectual Property), 6 (Confidentiality), 7 (Limitation of Liability), 8 (Indemnification), and 12 (General Provisions). Any obligations that by their nature should survive termination shall also survive.",
        "source": "synthetic",
        "notes": "Standard survival clause enumerating surviving sections — boilerplate"
    },
    {
        "id": "UC7_088", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Severability",
        "difficulty": "medium",
        "text": "If any provision of this Agreement is determined to be unenforceable, the parties shall negotiate in good faith a substitute provision that most closely approximates the intent and economic effect of the original provision. If the parties cannot agree on a substitute within thirty (30) days, the provision shall be severed and the remainder of the Agreement shall continue in effect.",
        "source": "synthetic",
        "notes": "Severability with negotiation mechanism — slightly more involved but standard"
    },
    {
        "id": "UC7_089", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Survival",
        "difficulty": "hard",
        "text": "Upon expiration or termination of this Agreement, all rights and obligations shall cease except that (a) accrued payment obligations shall survive, (b) each party's confidentiality obligations shall survive for three (3) years, (c) indemnification obligations with respect to events occurring during the Term shall survive indefinitely, and (d) all provisions that by their nature are intended to survive shall survive.",
        "source": "synthetic",
        "notes": "Detailed survival with indefinite indemnification survival — standard but requires careful reading"
    },
    {
        "id": "UC7_090", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Severability",
        "difficulty": "hard",
        "text": "The invalidity or unenforceability of any provision in any particular jurisdiction shall not affect the validity or enforceability of such provision in any other jurisdiction or the validity or enforceability of any other provision of this Agreement. The parties intend that this Agreement be enforced to the fullest extent permitted by applicable law in each jurisdiction.",
        "source": "synthetic",
        "notes": "Multi-jurisdiction severability — standard but addresses cross-border enforceability"
    },

    # ══════════════════════════════════════════════════════════
    # STANDARD — Counterparts & Execution (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_091", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Counterparts",
        "difficulty": "easy",
        "text": "This Agreement may be executed in one or more counterparts, each of which shall be deemed an original, and all of which together shall constitute one and the same instrument. Execution and delivery of this Agreement by facsimile or electronic signature shall be deemed to be an original execution.",
        "source": "synthetic",
        "notes": "Standard counterparts clause — pure boilerplate"
    },
    {
        "id": "UC7_092", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Headings",
        "difficulty": "easy",
        "text": "The headings and captions in this Agreement are for convenience of reference only and shall not affect the interpretation or construction of any provision hereof. Unless the context otherwise requires, words importing the singular include the plural and vice versa, and references to Sections are to Sections of this Agreement.",
        "source": "synthetic",
        "notes": "Standard headings and interpretation clause — pure boilerplate"
    },
    {
        "id": "UC7_093", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "No Third-Party Beneficiaries",
        "difficulty": "easy",
        "text": "This Agreement is for the sole benefit of the parties hereto and their respective successors and permitted assigns. Nothing in this Agreement, express or implied, is intended to confer upon any third party any legal or equitable right, benefit, or remedy of any nature whatsoever under or by reason of this Agreement.",
        "source": "synthetic",
        "notes": "Standard no third-party beneficiaries clause — boilerplate"
    },
    {
        "id": "UC7_094", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Waiver",
        "difficulty": "medium",
        "text": "The failure of either party to enforce any provision of this Agreement shall not constitute a waiver of such party's right to enforce such provision or any other provision in the future. All waivers must be in writing and signed by the waiving party to be effective. A waiver on one occasion shall not be deemed a waiver on any subsequent occasion.",
        "source": "synthetic",
        "notes": "Standard waiver clause — requires written waiver, no implied waiver"
    },
    {
        "id": "UC7_095", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Relationship of Parties",
        "difficulty": "medium",
        "text": "The parties are independent contractors. Nothing in this Agreement shall be construed as creating a joint venture, partnership, agency, or employment relationship between the parties. Neither party shall have the authority to bind the other party or incur obligations on behalf of the other party without prior written consent.",
        "source": "synthetic",
        "notes": "Standard independent contractor / relationship clause — boilerplate"
    },

    # ══════════════════════════════════════════════════════════
    # STANDARD — Miscellaneous (5 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC7_096", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Governing Language",
        "difficulty": "medium",
        "text": "This Agreement has been prepared in the English language, and the English language version shall control in all respects. Any translation of this Agreement is provided for convenience only and shall not be used in the interpretation or construction of this Agreement.",
        "source": "synthetic",
        "notes": "Standard governing language clause — common in cross-border contracts"
    },
    {
        "id": "UC7_097", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Cumulative Remedies",
        "difficulty": "hard",
        "text": "Except as expressly set forth herein, all remedies provided under this Agreement are cumulative and not exclusive of any other remedies available at law or in equity. The exercise of any remedy shall not preclude the exercise of any other remedy, and the parties expressly reserve all rights and remedies available under applicable law.",
        "source": "synthetic",
        "notes": "Cumulative remedies clause — standard but can interact with limitation of liability"
    },
    {
        "id": "UC7_098", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Further Assurances",
        "difficulty": "hard",
        "text": "Each party agrees to execute and deliver such additional documents, instruments, and assurances and to take such further actions as may be reasonably required to carry out the provisions of this Agreement and to give effect to the transactions contemplated hereby.",
        "source": "synthetic",
        "notes": "Standard further assurances clause — boilerplate cooperation provision"
    },
    {
        "id": "UC7_099", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Publicity",
        "difficulty": "hard",
        "text": "Neither party shall issue any press release or public statement regarding this Agreement or the relationship between the parties without the prior written consent of the other party, except as required by applicable law or regulation. Notwithstanding the foregoing, Provider may include Client's name and logo in its client list for marketing purposes.",
        "source": "synthetic",
        "notes": "Publicity restriction with marketing carve-out — standard with minor asymmetry"
    },
    {
        "id": "UC7_100", "label": "STANDARD",
        "category": "General Provisions", "subcategory": "Electronic Records",
        "difficulty": "medium",
        "text": "The parties agree that this Agreement and any notices, consents, or other communications delivered pursuant hereto may be transmitted and stored electronically. Electronic records shall have the same legal effect, validity, and enforceability as paper records and shall satisfy any requirement that such records be in writing.",
        "source": "synthetic",
        "notes": "Standard electronic records and ESIGN compliance clause — boilerplate"
    },
]


def build_csv():
    """Write gold set to CSV with all metadata columns."""
    filepath = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    fieldnames = [
        "id", "text", "label", "category", "subcategory",
        "difficulty", "source", "notes",
        "split"  # train or test
    ]

    # Assign 70/30 train/test split preserving label balance
    # Within each label group: first ~17-18 train, last ~7-8 test (25 per label)
    for label in ["HIGH_RISK", "MEDIUM_RISK", "LOW_RISK", "STANDARD"]:
        items = [x for x in GOLD_SET if x["label"] == label]
        # 25 items per label: 17 or 18 train, 7 or 8 test
        # 17 train + 8 test = 25  (4 labels x 17 = 68, need 70 total train)
        # HIGH_RISK: 18 train, 7 test
        # MEDIUM_RISK: 18 train, 7 test
        # LOW_RISK: 17 train, 8 test
        # STANDARD: 17 train, 8 test
        # Total: 70 train, 30 test
        if label in ["HIGH_RISK", "MEDIUM_RISK"]:
            train_count = 18
        else:
            train_count = 17
        for i, item in enumerate(items):
            item["split"] = "train" if i < train_count else "test"

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(GOLD_SET)

    return filepath


def build_metadata():
    """Write metadata JSON for paper appendix reference."""
    labels = ["HIGH_RISK", "MEDIUM_RISK", "LOW_RISK", "STANDARD"]

    meta = {
        "use_case": "UC7",
        "name": "Legal Contract Clause Analysis",
        "task": "4-way risk classification of legal contract clauses",
        "pre_registration_date": "2026-03-02",
        "version": "1.0",
        "total_items": len(GOLD_SET),
        "label_distribution": {
            label: len([x for x in GOLD_SET if x["label"] == label])
            for label in labels
        },
        "categories": {
            cat: len([x for x in GOLD_SET if x["category"] == cat])
            for cat in sorted(set(x["category"] for x in GOLD_SET))
        },
        "difficulty_distribution": {
            "easy":   len([x for x in GOLD_SET if x["difficulty"] == "easy"]),
            "medium": len([x for x in GOLD_SET if x["difficulty"] == "medium"]),
            "hard":   len([x for x in GOLD_SET if x["difficulty"] == "hard"]),
        },
        "train_test_split": {
            "train": len([x for x in GOLD_SET if x.get("split") == "train"]),
            "test":  len([x for x in GOLD_SET if x.get("split") == "test"]),
        },
        "s3_score": {
            "overall": 3.60,
            "tier": "Hybrid",
            "flag_rule": "SK>=4 enforces minimum Hybrid tier",
            "dimensions": {
                "task_complexity": {"value": 4, "weight": 3, "rationale": "Reasoning about legal implications and obligations"},
                "output_structure": {"value": 4, "weight": 2, "rationale": "Strict classification from closed 4-class vocabulary"},
                "stakes": {"value": 4, "weight": 4, "rationale": "Legal consequences of wrong analysis — contracts are binding"},
                "data_sensitivity": {"value": 4, "weight": 2, "rationale": "Privileged legal documents, regulated"},
                "latency_requirement": {"value": 3, "weight": 3, "rationale": "Interactive, lawyer workflow"},
                "volume": {"value": 1, "weight": 1, "rationale": "Dozens per day"},
            },
            "formula": "54/75 x 5 = 3.60 -> Hybrid (formula) + Flag Rule (SK=4)",
        },
        "evaluation_metrics": [
            "Exact Match Rate (Accuracy)",
            "Macro F1 Score",
            "Per-Class Precision / Recall / F1",
            "Confusion Matrix",
            "Latency P50/P95 (ms)",
            "Cost Per Successful Task (CPS)",
            "Hallucination Rate",
        ],
        "pre_registered_hypotheses": [
            "H7.1: Best SLM achieves >= 80% of LLM accuracy on legal clause risk classification",
            "H7.2: Best SLM P95 latency < 4000ms",
            "H7.3: UC7 validates as Hybrid tier — SK=4 Flag Rule correctly enforces minimum Hybrid tier",
            "H7.4: HIGH_RISK class will have highest SLM-LLM gap (requires nuanced legal reasoning)",
        ],
        "label_definitions": {
            "HIGH_RISK": "Unlimited liability, broad indemnification, unilateral termination rights, non-compete without geographic limit, uncapped damages",
            "MEDIUM_RISK": "Capped liability (reasonable caps), mutual non-compete with limits, limited warranty disclaimers, liquidated damages clauses",
            "LOW_RISK": "Standard payment terms (net-30/60), standard notice periods, choice of law/venue, standard confidentiality with reasonable duration",
            "STANDARD": "Boilerplate definitions, recitals, entire agreement, severability, counterparts, headings clause",
        },
        "created_at": datetime.now().isoformat(),
    }

    meta_path = os.path.join(OUTPUT_DIR, META_FILE)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return meta_path


def print_summary():
    """Print verification summary to confirm gold set is correct."""
    labels = ["HIGH_RISK", "MEDIUM_RISK", "LOW_RISK", "STANDARD"]

    print()
    print("=" * 62)
    print("  UC7 GOLD SET — Build Complete")
    print("  Legal Contract Clause Analysis — Pre-Registration v1.0")
    print("=" * 62)
    print()
    print(f"  Total items  : {len(GOLD_SET)}")
    for label in labels:
        n = len([x for x in GOLD_SET if x["label"] == label])
        print(f"  {label:<14} : {n} items (25%)")
    print()
    print("  Category breakdown:")
    for cat in sorted(set(x["category"] for x in GOLD_SET)):
        n = len([x for x in GOLD_SET if x["category"] == cat])
        print(f"    {cat:<25} {n} items")

    print()
    print("  Difficulty distribution:")
    for diff in ["easy", "medium", "hard"]:
        n = len([x for x in GOLD_SET if x["difficulty"] == diff])
        bar = "█" * n
        print(f"    {diff:<8} {bar:<50} {n}")

    train_n = len([x for x in GOLD_SET if x.get("split") == "train"])
    test_n  = len([x for x in GOLD_SET if x.get("split") == "test"])
    print()
    print(f"  Train / Test split : {train_n} train / {test_n} test (70/30)")
    print()
    print("  S³ Score: 3.60 → Hybrid tier")
    print("  Flag Rule: SK=4 → minimum Hybrid tier enforced")
    print()
    print("  Files saved:")
    print(f"    data/gold_sets/{OUTPUT_FILE}")
    print(f"    data/gold_sets/{META_FILE}")
    print()
    print("  ✅  Gold set locked — DO NOT MODIFY after this point")
    print("      This is your pre-registered ground truth.")
    print()
    print("  NEXT STEP:")
    print("  → python3 scripts/run_benchmark_uc7.py")
    print("  → Runs all models against UC7 test set (30 items × N models × 3 runs)")
    print("=" * 62)
    print()


if __name__ == "__main__":
    print()
    print("Building UC7 Gold Set — Legal Contract Clause Analysis...")
    csv_path  = build_csv()
    meta_path = build_metadata()
    print_summary()
