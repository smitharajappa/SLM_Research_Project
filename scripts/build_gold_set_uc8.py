# -*- coding: utf-8 -*-
"""
build_gold_set_uc8.py
=====================
S3 Research Project -- UC8 Gold Set Builder
Use Case  : Financial Report Drafting
Task      : Given structured quarterly financial data, generate a professional
            2-3 paragraph performance summary suitable for an earnings report.
S3 Score  : 3.80  (Hybrid tier predicted)
Category  : Cat 3 -- Multi-step Reasoning / Generation
Evaluation: LLM-as-Judge (Accuracy, Depth, Tone, Completeness -- 1-5 each)

Gold set  : 100 items
  - 5 sectors x 20 items each
  - Difficulty: easy (35%), medium (35%), hard (30%)
  - Split: 70 train / 30 test  (stratified by sector x difficulty)
  - Test : 6 items per sector (2 easy + 2 medium + 2 hard) = 30 items
  - Train: 14 items per sector                              = 70 items

Output    : data/gold_sets/uc8_financial_report_drafting.csv
Pre-reg   : 2026-03-11
Author    : S3 Research Team
"""

import csv
import json
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# GOLD SET ITEMS
# Each item:
#   item_id        -- UC8_001 ... UC8_100
#   company_name   -- fictional company
#   period         -- e.g. "Q3 2025"
#   sector         -- Technology / Retail / Healthcare / Manufacturing / Financial
#   difficulty     -- easy / medium / hard
#   split          -- train / test
#   financial_data -- JSON string with all figures given to the model
#   prompt_text    -- full prompt sent to the model (filled from financial_data)
#   gold_criteria  -- pipe-separated key points judge checks for (not shown to model)
# ---------------------------------------------------------------------------

RAW_ITEMS = [

    # =========================================================
    # SECTOR: Technology   (items 001-020)
    # =========================================================

    # --- easy (items 001-007, 2 in test: 001-002) ---
    {
        "item_id": "UC8_001", "sector": "Technology", "difficulty": "easy", "split": "test",
        "company_name": "NovaSoft Inc.", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 142.3, "revenue_growth_yoy_pct": 22.1,
            "gross_margin_pct": 74.5, "operating_income_m": 38.4,
            "operating_margin_pct": 27.0, "net_income_m": 31.2,
            "eps": 1.84, "arr_m": 540.0, "arr_growth_yoy_pct": 28.0,
            "net_revenue_retention_pct": 118, "customer_count": 4120,
            "free_cash_flow_m": 44.1, "cash_and_equivalents_m": 210.0
        },
        "gold_criteria": "Revenue $142.3M up 22.1% YoY|Gross margin 74.5%|Operating income $38.4M margin 27%|ARR $540M up 28%|NRR 118%|FCF $44.1M|4120 customers"
    },
    {
        "item_id": "UC8_002", "sector": "Technology", "difficulty": "easy", "split": "test",
        "company_name": "CloudPeak Systems", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 89.6, "revenue_growth_yoy_pct": 31.4,
            "gross_margin_pct": 71.2, "operating_income_m": 19.8,
            "operating_margin_pct": 22.1, "net_income_m": 16.5,
            "eps": 0.97, "arr_m": 348.0, "arr_growth_yoy_pct": 34.0,
            "net_revenue_retention_pct": 121, "customer_count": 2870,
            "free_cash_flow_m": 22.4, "cash_and_equivalents_m": 145.0
        },
        "gold_criteria": "Revenue $89.6M up 31.4% YoY|Gross margin 71.2%|Operating income $19.8M margin 22.1%|ARR $348M up 34%|NRR 121%|FCF $22.4M|2870 customers"
    },
    {
        "item_id": "UC8_003", "sector": "Technology", "difficulty": "easy", "split": "train",
        "company_name": "DataBridge Corp", "period": "Q3 2025",
        "financial_data": {
            "revenue_m": 205.1, "revenue_growth_yoy_pct": 18.7,
            "gross_margin_pct": 78.3, "operating_income_m": 62.0,
            "operating_margin_pct": 30.2, "net_income_m": 51.8,
            "eps": 2.41, "arr_m": 790.0, "arr_growth_yoy_pct": 21.0,
            "net_revenue_retention_pct": 115, "customer_count": 6500,
            "free_cash_flow_m": 70.2, "cash_and_equivalents_m": 380.0
        },
        "gold_criteria": "Revenue $205.1M up 18.7%|Gross margin 78.3%|Operating income $62M 30.2% margin|ARR $790M up 21%|NRR 115%|FCF $70.2M"
    },
    {
        "item_id": "UC8_004", "sector": "Technology", "difficulty": "easy", "split": "train",
        "company_name": "Aperio Analytics", "period": "Q4 2024",
        "financial_data": {
            "revenue_m": 178.4, "revenue_growth_yoy_pct": 25.6,
            "gross_margin_pct": 72.9, "operating_income_m": 44.7,
            "operating_margin_pct": 25.1, "net_income_m": 37.3,
            "eps": 2.10, "arr_m": 680.0, "arr_growth_yoy_pct": 27.0,
            "net_revenue_retention_pct": 119, "customer_count": 5100,
            "free_cash_flow_m": 55.6, "cash_and_equivalents_m": 270.0
        },
        "gold_criteria": "Revenue $178.4M up 25.6%|Gross margin 72.9%|Operating income $44.7M 25.1% margin|ARR $680M up 27%|NRR 119%|FCF $55.6M"
    },
    {
        "item_id": "UC8_005", "sector": "Technology", "difficulty": "easy", "split": "train",
        "company_name": "Meridian SaaS", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 67.2, "revenue_growth_yoy_pct": 29.8,
            "gross_margin_pct": 76.1, "operating_income_m": 15.4,
            "operating_margin_pct": 22.9, "net_income_m": 13.0,
            "eps": 0.78, "arr_m": 258.0, "arr_growth_yoy_pct": 32.0,
            "net_revenue_retention_pct": 116, "customer_count": 1980,
            "free_cash_flow_m": 17.8, "cash_and_equivalents_m": 98.0
        },
        "gold_criteria": "Revenue $67.2M up 29.8%|Gross margin 76.1%|Operating income $15.4M|ARR $258M up 32%|NRR 116%|1980 customers"
    },
    {
        "item_id": "UC8_006", "sector": "Technology", "difficulty": "easy", "split": "train",
        "company_name": "Vektor Cloud", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 113.0, "revenue_growth_yoy_pct": 20.5,
            "gross_margin_pct": 73.8, "operating_income_m": 27.1,
            "operating_margin_pct": 24.0, "net_income_m": 22.7,
            "eps": 1.35, "arr_m": 435.0, "arr_growth_yoy_pct": 22.0,
            "net_revenue_retention_pct": 114, "customer_count": 3450,
            "free_cash_flow_m": 31.5, "cash_and_equivalents_m": 162.0
        },
        "gold_criteria": "Revenue $113M up 20.5%|Gross margin 73.8%|Operating income $27.1M|ARR $435M up 22%|NRR 114%|FCF $31.5M"
    },
    {
        "item_id": "UC8_007", "sector": "Technology", "difficulty": "easy", "split": "train",
        "company_name": "Nimbix Solutions", "period": "Q3 2024",
        "financial_data": {
            "revenue_m": 55.9, "revenue_growth_yoy_pct": 27.3,
            "gross_margin_pct": 70.4, "operating_income_m": 11.3,
            "operating_margin_pct": 20.2, "net_income_m": 9.4,
            "eps": 0.56, "arr_m": 210.0, "arr_growth_yoy_pct": 30.0,
            "net_revenue_retention_pct": 113, "customer_count": 1560,
            "free_cash_flow_m": 13.2, "cash_and_equivalents_m": 77.0
        },
        "gold_criteria": "Revenue $55.9M up 27.3%|Gross margin 70.4%|Operating income $11.3M|ARR $210M up 30%|NRR 113%"
    },

    # --- medium (items 008-014, 2 in test: 008-009) ---
    {
        "item_id": "UC8_008", "sector": "Technology", "difficulty": "medium", "split": "test",
        "company_name": "Stratix Platform", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 121.7, "revenue_growth_yoy_pct": 9.4,
            "gross_margin_pct": 68.2, "gross_margin_prev_qtr_pct": 71.5,
            "operating_income_m": 14.6, "operating_margin_pct": 12.0,
            "net_income_m": 11.3, "eps": 0.67,
            "arr_m": 465.0, "arr_growth_yoy_pct": 11.0,
            "net_revenue_retention_pct": 104, "customer_count": 3820,
            "customer_churn_pct": 4.2, "free_cash_flow_m": 18.9,
            "cash_and_equivalents_m": 92.0,
            "restructuring_charge_m": 8.5,
            "note": "Gross margin compression due to increased cloud hosting costs; restructuring charge of $8.5M related to workforce rebalancing"
        },
        "gold_criteria": "Revenue $121.7M up 9.4% (growth deceleration)|Gross margin 68.2% down from 71.5% -- compression noted|Operating margin 12% impacted by $8.5M restructuring|ARR $465M up 11%|NRR 104% -- retention pressure|4.2% churn elevated|restructuring context required"
    },
    {
        "item_id": "UC8_009", "sector": "Technology", "difficulty": "medium", "split": "test",
        "company_name": "Axon Digital", "period": "Q4 2024",
        "financial_data": {
            "revenue_m": 98.3, "revenue_growth_yoy_pct": 14.8,
            "gross_margin_pct": 65.7, "operating_income_m": 8.9,
            "operating_margin_pct": 9.1, "net_income_m": 6.2,
            "eps": 0.37, "arr_m": 372.0, "arr_growth_yoy_pct": 16.0,
            "net_revenue_retention_pct": 107, "customer_count": 2960,
            "free_cash_flow_m": 12.4, "cash_and_equivalents_m": 68.0,
            "r_and_d_expense_m": 31.5, "r_and_d_as_pct_revenue": 32.0,
            "new_product_launches": 2,
            "note": "Heavy R&D investment in next-generation AI features; two new product modules launched in quarter"
        },
        "gold_criteria": "Revenue $98.3M up 14.8%|Gross margin 65.7% -- R&D investment context|Operating income $8.9M 9.1% margin|R&D $31.5M (32% of revenue)|ARR $372M up 16%|NRR 107%|two new product launches"
    },
    {
        "item_id": "UC8_010", "sector": "Technology", "difficulty": "medium", "split": "train",
        "company_name": "Optera Systems", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 145.2, "revenue_growth_yoy_pct": 7.1,
            "gross_margin_pct": 67.4, "operating_income_m": 12.3,
            "operating_margin_pct": 8.5, "net_income_m": 9.8,
            "eps": 0.58, "arr_m": 558.0, "arr_growth_yoy_pct": 8.0,
            "net_revenue_retention_pct": 103, "customer_count": 4320,
            "free_cash_flow_m": 16.1, "cash_and_equivalents_m": 105.0,
            "sales_and_marketing_m": 52.0, "note": "Increased S&M spend to re-accelerate growth after two quarters of deceleration"
        },
        "gold_criteria": "Revenue $145.2M up 7.1%|Gross margin 67.4%|Operating income $12.3M 8.5% margin|ARR $558M up 8%|NRR 103%|Elevated S&M spend $52M growth re-acceleration noted"
    },
    {
        "item_id": "UC8_011", "sector": "Technology", "difficulty": "medium", "split": "train",
        "company_name": "Parallax Software", "period": "Q3 2024",
        "financial_data": {
            "revenue_m": 77.8, "revenue_growth_yoy_pct": 11.2,
            "gross_margin_pct": 69.0, "operating_income_m": 7.0,
            "operating_margin_pct": 9.0, "net_income_m": 5.6,
            "eps": 0.33, "arr_m": 298.0, "arr_growth_yoy_pct": 12.5,
            "net_revenue_retention_pct": 105, "customer_count": 2340,
            "free_cash_flow_m": 9.5, "cash_and_equivalents_m": 55.0,
            "customer_acquisition_cost_m": 18.2, "note": "CAC increased 15% sequentially due to competitive market dynamics"
        },
        "gold_criteria": "Revenue $77.8M up 11.2%|Gross margin 69%|Operating income $7M 9% margin|ARR $298M up 12.5%|NRR 105%|CAC increase competitive environment"
    },
    {
        "item_id": "UC8_012", "sector": "Technology", "difficulty": "medium", "split": "train",
        "company_name": "Quorum Technologies", "period": "Q2 2024",
        "financial_data": {
            "revenue_m": 161.0, "revenue_growth_yoy_pct": 13.0,
            "gross_margin_pct": 70.8, "operating_income_m": 21.7,
            "operating_margin_pct": 13.5, "net_income_m": 18.0,
            "eps": 1.06, "arr_m": 615.0, "arr_growth_yoy_pct": 14.0,
            "net_revenue_retention_pct": 109, "customer_count": 4890,
            "free_cash_flow_m": 26.3, "cash_and_equivalents_m": 148.0,
            "international_revenue_pct": 38, "note": "International revenue grew 22% YoY outpacing domestic growth of 8%"
        },
        "gold_criteria": "Revenue $161M up 13%|Gross margin 70.8%|Operating income $21.7M 13.5% margin|ARR $615M up 14%|NRR 109%|International 38% of revenue up 22%"
    },
    {
        "item_id": "UC8_013", "sector": "Technology", "difficulty": "medium", "split": "train",
        "company_name": "Flux Analytics", "period": "Q4 2025",
        "financial_data": {
            "revenue_m": 89.1, "revenue_growth_yoy_pct": 10.8,
            "gross_margin_pct": 66.5, "operating_income_m": 8.0,
            "operating_margin_pct": 9.0, "net_income_m": 6.5,
            "eps": 0.39, "arr_m": 340.0, "arr_growth_yoy_pct": 11.5,
            "net_revenue_retention_pct": 106, "customer_count": 2680,
            "free_cash_flow_m": 10.4, "cash_and_equivalents_m": 61.0,
            "note": "Professional services revenue declined 8% as company shifts to product-led growth model"
        },
        "gold_criteria": "Revenue $89.1M up 10.8%|Gross margin 66.5%|Operating income $8M 9% margin|ARR $340M up 11.5%|NRR 106%|Professional services decline product-led growth transition"
    },
    {
        "item_id": "UC8_014", "sector": "Technology", "difficulty": "medium", "split": "train",
        "company_name": "Helix Data Corp", "period": "Q1 2024",
        "financial_data": {
            "revenue_m": 54.3, "revenue_growth_yoy_pct": 16.4,
            "gross_margin_pct": 68.8, "operating_income_m": 5.4,
            "operating_margin_pct": 10.0, "net_income_m": 4.3,
            "eps": 0.26, "arr_m": 208.0, "arr_growth_yoy_pct": 18.0,
            "net_revenue_retention_pct": 110, "customer_count": 1740,
            "free_cash_flow_m": 7.1, "cash_and_equivalents_m": 43.0,
            "note": "Land-and-expand motion driving NRR; average contract value grew 12% YoY"
        },
        "gold_criteria": "Revenue $54.3M up 16.4%|Gross margin 68.8%|Operating income $5.4M 10% margin|ARR $208M up 18%|NRR 110%|ACV grew 12% land-and-expand"
    },

    # --- hard (items 015-020, 2 in test: 015-016) ---
    {
        "item_id": "UC8_015", "sector": "Technology", "difficulty": "hard", "split": "test",
        "company_name": "Corvis Technologies", "period": "Q3 2025",
        "financial_data": {
            "revenue_m": 134.2, "revenue_growth_yoy_pct": -3.1,
            "gross_margin_pct": 61.4, "gross_margin_prev_year_pct": 70.8,
            "operating_income_m": -8.7, "operating_margin_pct": -6.5,
            "net_income_m": -11.4, "eps": -0.67,
            "arr_m": 510.0, "arr_growth_yoy_pct": -1.5,
            "net_revenue_retention_pct": 92, "customer_count": 3890,
            "customer_churn_pct": 8.9, "free_cash_flow_m": -15.2,
            "cash_and_equivalents_m": 48.0,
            "impairment_charge_m": 22.0,
            "restructuring_charge_m": 14.5,
            "debt_m": 180.0,
            "note": "Goodwill impairment $22M related to underperforming acquisition from 2023; net revenue decline driven by enterprise segment downturn; $14.5M restructuring charge for 12% workforce reduction; 8.9% churn highest in company history"
        },
        "gold_criteria": "Revenue $134.2M DOWN 3.1% YoY -- revenue decline|Gross margin 61.4% down sharply from 70.8%|Operating loss -$8.7M margin -6.5%|Net loss -$11.4M|ARR $510M down 1.5%|NRR 92% -- below 100 means contraction|Churn 8.9% highest on record|$22M goodwill impairment|$14.5M restructuring 12% workforce cut|FCF -$15.2M cash burn|$48M cash limited runway with $180M debt|All negative signals must be clearly reported"
    },
    {
        "item_id": "UC8_016", "sector": "Technology", "difficulty": "hard", "split": "test",
        "company_name": "Specter AI", "period": "Q2 2024",
        "financial_data": {
            "revenue_m": 47.8, "revenue_growth_yoy_pct": 62.3,
            "gross_margin_pct": 41.2,
            "operating_income_m": -28.4, "operating_margin_pct": -59.4,
            "net_income_m": -31.0, "eps": -1.83,
            "arr_m": 180.0, "arr_growth_yoy_pct": 78.0,
            "net_revenue_retention_pct": 138, "customer_count": 890,
            "free_cash_flow_m": -33.1,
            "cash_and_equivalents_m": 124.0,
            "r_and_d_expense_m": 28.5, "sales_and_marketing_m": 32.1,
            "headcount": 620, "headcount_growth_yoy_pct": 89,
            "note": "Hyper-growth phase -- company deliberately investing ahead of revenue; gross margin suppressed by compute costs for AI model training and inference; management expects gross margins to expand to 65%+ at scale"
        },
        "gold_criteria": "Revenue $47.8M up 62.3% hyper-growth|Gross margin 41.2% suppressed by AI compute -- scale expectation 65%+|Operating loss -$28.4M -59.4% margin -- deliberate investment phase|Net loss -$31M|ARR $180M up 78%|NRR 138% -- exceptional retention|R&D $28.5M and S&M $32.1M investment ahead of revenue|FCF -$33.1M burn rate|$124M cash runway context|Headcount +89% YoY|Both growth story and cash burn risk must be addressed"
    },
    {
        "item_id": "UC8_017", "sector": "Technology", "difficulty": "hard", "split": "train",
        "company_name": "Meridian AI", "period": "Q1 2024",
        "financial_data": {
            "revenue_m": 88.5, "revenue_growth_yoy_pct": -8.2,
            "gross_margin_pct": 58.3, "operating_income_m": -19.2,
            "operating_margin_pct": -21.7, "net_income_m": -22.8, "eps": -1.35,
            "arr_m": 337.0, "arr_decline_qoq_m": -12.0,
            "net_revenue_retention_pct": 88, "customer_count": 2940,
            "free_cash_flow_m": -24.5, "cash_and_equivalents_m": 62.0,
            "note": "ARR contraction driven by enterprise downgrades; NRR below 100 for third consecutive quarter"
        },
        "gold_criteria": "Revenue $88.5M down 8.2%|Gross margin 58.3%|Operating loss -$19.2M|ARR $337M contracting QoQ by $12M|NRR 88% below 100 third consecutive quarter|FCF -$24.5M|$62M cash limited runway"
    },
    {
        "item_id": "UC8_018", "sector": "Technology", "difficulty": "hard", "split": "train",
        "company_name": "Conduit SaaS", "period": "Q4 2024",
        "financial_data": {
            "revenue_m": 201.0, "revenue_growth_yoy_pct": 4.2,
            "gross_margin_pct": 72.1, "operating_income_m": 30.1,
            "operating_margin_pct": 15.0, "net_income_m": 24.8,
            "eps": 1.47, "arr_m": 780.0, "arr_growth_yoy_pct": 5.5,
            "net_revenue_retention_pct": 101, "customer_count": 6200,
            "free_cash_flow_m": 41.2, "cash_and_equivalents_m": 290.0,
            "share_repurchase_m": 60.0,
            "note": "Company returned $60M to shareholders via buyback; management commented growth deceleration reflects market saturation in core segment; expanding into adjacent markets"
        },
        "gold_criteria": "Revenue $201M up 4.2% -- significant deceleration|Gross margin 72.1% healthy|Operating income $30.1M 15% margin|ARR $780M up 5.5%|NRR 101% barely positive|$60M share buyback capital return|Growth deceleration and adjacent market expansion"
    },
    {
        "item_id": "UC8_019", "sector": "Technology", "difficulty": "hard", "split": "train",
        "company_name": "Phalanx Cloud", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 156.4, "revenue_growth_yoy_pct": 38.1,
            "gross_margin_pct": 55.8,
            "operating_income_m": -42.0, "operating_margin_pct": -26.8,
            "net_income_m": -46.3, "eps": -2.74,
            "arr_m": 590.0, "arr_growth_yoy_pct": 44.0,
            "net_revenue_retention_pct": 129, "customer_count": 3210,
            "free_cash_flow_m": -48.5, "cash_and_equivalents_m": 198.0,
            "note": "Infrastructure-heavy business model suppresses gross margins; company pursuing GPU capacity build-out worth $120M over next 18 months"
        },
        "gold_criteria": "Revenue $156.4M up 38.1%|Gross margin 55.8% infrastructure costs|Operating loss -$42M -26.8% margin -- investment phase|Net loss -$46.3M|ARR $590M up 44%|NRR 129%|FCF -$48.5M|$198M cash|$120M GPU build-out capex context"
    },
    {
        "item_id": "UC8_020", "sector": "Technology", "difficulty": "hard", "split": "train",
        "company_name": "Virtex Platform", "period": "Q3 2024",
        "financial_data": {
            "revenue_m": 112.7, "revenue_growth_yoy_pct": 2.1,
            "gross_margin_pct": 63.9, "operating_income_m": 4.5,
            "operating_margin_pct": 4.0, "net_income_m": 2.8,
            "eps": 0.17, "arr_m": 432.0, "arr_growth_yoy_pct": 3.0,
            "net_revenue_retention_pct": 99, "customer_count": 3780,
            "free_cash_flow_m": 6.2, "cash_and_equivalents_m": 80.0,
            "note": "Legacy product revenue declining; new product transition underway; large deal delays pushed $18M of ARR to Q4"
        },
        "gold_criteria": "Revenue $112.7M up 2.1% near-stagnant|Gross margin 63.9%|Operating income $4.5M 4% margin|ARR $432M up 3% NRR 99% slightly below 100|Legacy product decline transition risk|$18M ARR deal slippage to Q4"
    },

    # =========================================================
    # SECTOR: Retail / E-commerce   (items 021-040)
    # =========================================================

    # --- easy (items 021-027, 2 in test: 021-022) ---
    {
        "item_id": "UC8_021", "sector": "Retail", "difficulty": "easy", "split": "test",
        "company_name": "Velora Commerce", "period": "Q4 2024",
        "financial_data": {
            "revenue_m": 892.4, "revenue_growth_yoy_pct": 14.3,
            "gross_margin_pct": 38.2, "operating_income_m": 98.7,
            "operating_margin_pct": 11.1, "net_income_m": 76.3,
            "eps": 3.82, "comparable_store_sales_growth_pct": 9.8,
            "e_commerce_revenue_m": 312.0, "e_commerce_growth_pct": 28.4,
            "store_count": 415, "new_stores_opened": 12,
            "inventory_turnover": 6.4, "free_cash_flow_m": 112.0
        },
        "gold_criteria": "Revenue $892.4M up 14.3%|Gross margin 38.2%|Operating income $98.7M 11.1% margin|Comp sales +9.8%|E-commerce $312M up 28.4%|415 stores 12 new openings|Inventory turnover 6.4x|FCF $112M"
    },
    {
        "item_id": "UC8_022", "sector": "Retail", "difficulty": "easy", "split": "test",
        "company_name": "Stratum Retail Group", "period": "Q3 2024",
        "financial_data": {
            "revenue_m": 621.8, "revenue_growth_yoy_pct": 11.7,
            "gross_margin_pct": 41.5, "operating_income_m": 74.6,
            "operating_margin_pct": 12.0, "net_income_m": 58.4,
            "eps": 2.92, "comparable_store_sales_growth_pct": 7.4,
            "e_commerce_revenue_m": 186.5, "e_commerce_growth_pct": 22.0,
            "store_count": 289, "free_cash_flow_m": 83.2
        },
        "gold_criteria": "Revenue $621.8M up 11.7%|Gross margin 41.5%|Operating income $74.6M 12% margin|Comp sales +7.4%|E-commerce $186.5M up 22%|289 stores|FCF $83.2M"
    },
    {
        "item_id": "UC8_023", "sector": "Retail", "difficulty": "easy", "split": "train",
        "company_name": "Harmon Lifestyle", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 445.0, "revenue_growth_yoy_pct": 10.2,
            "gross_margin_pct": 39.8, "operating_income_m": 49.0,
            "operating_margin_pct": 11.0, "net_income_m": 38.2,
            "eps": 1.91, "comparable_store_sales_growth_pct": 6.1,
            "e_commerce_revenue_m": 133.5, "e_commerce_growth_pct": 19.5,
            "store_count": 218, "free_cash_flow_m": 58.3
        },
        "gold_criteria": "Revenue $445M up 10.2%|Gross margin 39.8%|Operating income $49M 11% margin|Comp sales +6.1%|E-commerce $133.5M up 19.5%|218 stores|FCF $58.3M"
    },
    {
        "item_id": "UC8_024", "sector": "Retail", "difficulty": "easy", "split": "train",
        "company_name": "Crestview Brands", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 337.4, "revenue_growth_yoy_pct": 13.0,
            "gross_margin_pct": 43.2, "operating_income_m": 44.1,
            "operating_margin_pct": 13.1, "net_income_m": 34.7,
            "eps": 1.73, "comparable_store_sales_growth_pct": 8.5,
            "e_commerce_revenue_m": 101.2, "e_commerce_growth_pct": 25.3,
            "store_count": 162, "free_cash_flow_m": 51.4
        },
        "gold_criteria": "Revenue $337.4M up 13%|Gross margin 43.2%|Operating income $44.1M 13.1% margin|Comp sales +8.5%|E-commerce $101.2M up 25.3%|162 stores"
    },
    {
        "item_id": "UC8_025", "sector": "Retail", "difficulty": "easy", "split": "train",
        "company_name": "Luxora Home", "period": "Q4 2025",
        "financial_data": {
            "revenue_m": 758.1, "revenue_growth_yoy_pct": 12.5,
            "gross_margin_pct": 37.6, "operating_income_m": 82.5,
            "operating_margin_pct": 10.9, "net_income_m": 64.3,
            "eps": 3.21, "comparable_store_sales_growth_pct": 8.0,
            "e_commerce_revenue_m": 265.3, "e_commerce_growth_pct": 21.0,
            "store_count": 368, "free_cash_flow_m": 97.4
        },
        "gold_criteria": "Revenue $758.1M up 12.5%|Gross margin 37.6%|Operating income $82.5M 10.9% margin|Comp sales +8%|E-commerce $265.3M up 21%|368 stores"
    },
    {
        "item_id": "UC8_026", "sector": "Retail", "difficulty": "easy", "split": "train",
        "company_name": "Pinnacle Goods", "period": "Q3 2025",
        "financial_data": {
            "revenue_m": 512.0, "revenue_growth_yoy_pct": 9.8,
            "gross_margin_pct": 40.1, "operating_income_m": 56.3,
            "operating_margin_pct": 11.0, "net_income_m": 43.9,
            "eps": 2.19, "comparable_store_sales_growth_pct": 5.9,
            "e_commerce_revenue_m": 153.6, "e_commerce_growth_pct": 17.8,
            "store_count": 248, "free_cash_flow_m": 66.8
        },
        "gold_criteria": "Revenue $512M up 9.8%|Gross margin 40.1%|Operating income $56.3M 11% margin|Comp sales +5.9%|E-commerce $153.6M up 17.8%|248 stores"
    },
    {
        "item_id": "UC8_027", "sector": "Retail", "difficulty": "easy", "split": "train",
        "company_name": "Denmore Retail", "period": "Q2 2024",
        "financial_data": {
            "revenue_m": 289.6, "revenue_growth_yoy_pct": 11.4,
            "gross_margin_pct": 42.7, "operating_income_m": 34.8,
            "operating_margin_pct": 12.0, "net_income_m": 27.2,
            "eps": 1.36, "comparable_store_sales_growth_pct": 7.0,
            "e_commerce_revenue_m": 86.9, "e_commerce_growth_pct": 20.8,
            "store_count": 143, "free_cash_flow_m": 41.5
        },
        "gold_criteria": "Revenue $289.6M up 11.4%|Gross margin 42.7%|Operating income $34.8M 12% margin|Comp sales +7%|E-commerce $86.9M up 20.8%|143 stores"
    },

    # --- medium (items 028-034, 2 in test: 028-029) ---
    {
        "item_id": "UC8_028", "sector": "Retail", "difficulty": "medium", "split": "test",
        "company_name": "Vantage Apparel", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 478.3, "revenue_growth_yoy_pct": 3.8,
            "gross_margin_pct": 34.1, "gross_margin_prev_year_pct": 39.2,
            "operating_income_m": 28.7, "operating_margin_pct": 6.0,
            "net_income_m": 21.5, "eps": 1.07,
            "comparable_store_sales_growth_pct": 1.2,
            "e_commerce_revenue_m": 143.5, "e_commerce_growth_pct": 12.0,
            "store_count": 231, "stores_closed": 8,
            "inventory_excess_m": 42.0, "markdown_impact_m": 18.5,
            "free_cash_flow_m": 34.1,
            "note": "Gross margin pressure from inventory markdown of $18.5M; 8 underperforming stores closed; tariff headwinds impacting COGS"
        },
        "gold_criteria": "Revenue $478.3M up 3.8% growth slowdown|Gross margin 34.1% down from 39.2%|$18.5M markdown impact|Operating income $28.7M 6% margin|Comp sales +1.2% decelerated|E-commerce $143.5M up 12%|8 store closures rationalisation|Inventory excess $42M tariff headwinds"
    },
    {
        "item_id": "UC8_029", "sector": "Retail", "difficulty": "medium", "split": "test",
        "company_name": "Eastbrook Home Goods", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 394.7, "revenue_growth_yoy_pct": 6.1,
            "gross_margin_pct": 36.8, "operating_income_m": 35.5,
            "operating_margin_pct": 9.0, "net_income_m": 27.3,
            "eps": 1.37, "comparable_store_sales_growth_pct": 3.5,
            "e_commerce_revenue_m": 118.4, "e_commerce_growth_pct": 18.5,
            "store_count": 196, "new_stores_opened": 5,
            "loyalty_members_m": 2.4, "loyalty_revenue_pct": 68,
            "free_cash_flow_m": 43.2,
            "note": "Loyalty programme driving 68% of revenue; new loyalty tier launched driving 14% increase in average order value"
        },
        "gold_criteria": "Revenue $394.7M up 6.1%|Gross margin 36.8%|Operating income $35.5M 9% margin|Comp sales +3.5%|E-commerce $118.4M up 18.5%|Loyalty 68% of revenue 2.4M members|AOV up 14%|5 new stores"
    },
    {
        "item_id": "UC8_030", "sector": "Retail", "difficulty": "medium", "split": "train",
        "company_name": "Radleigh Fashion", "period": "Q3 2025",
        "financial_data": {
            "revenue_m": 567.1, "revenue_growth_yoy_pct": 5.3,
            "gross_margin_pct": 35.7, "operating_income_m": 45.4,
            "operating_margin_pct": 8.0, "net_income_m": 35.2,
            "eps": 1.76, "comparable_store_sales_growth_pct": 2.8,
            "e_commerce_revenue_m": 170.1, "e_commerce_growth_pct": 15.0,
            "store_count": 275, "free_cash_flow_m": 52.8,
            "note": "Promotional activity increased to clear seasonal inventory; freight costs elevated 12% YoY"
        },
        "gold_criteria": "Revenue $567.1M up 5.3%|Gross margin 35.7% pressure from promotions|Operating income $45.4M 8% margin|Comp sales +2.8%|E-commerce $170.1M up 15%|Freight costs elevated 12%"
    },
    {
        "item_id": "UC8_031", "sector": "Retail", "difficulty": "medium", "split": "train",
        "company_name": "Summit Outdoors", "period": "Q1 2024",
        "financial_data": {
            "revenue_m": 312.4, "revenue_growth_yoy_pct": 4.6,
            "gross_margin_pct": 38.1, "operating_income_m": 28.1,
            "operating_margin_pct": 9.0, "net_income_m": 21.7,
            "eps": 1.09, "comparable_store_sales_growth_pct": 2.0,
            "e_commerce_revenue_m": 93.7, "e_commerce_growth_pct": 14.2,
            "store_count": 152, "free_cash_flow_m": 33.5,
            "note": "Consumer discretionary spending softening in core demographic; average transaction value flat"
        },
        "gold_criteria": "Revenue $312.4M up 4.6%|Gross margin 38.1%|Operating income $28.1M 9% margin|Comp sales +2% slowdown|Consumer spending softening|E-commerce $93.7M up 14.2%|152 stores"
    },
    {
        "item_id": "UC8_032", "sector": "Retail", "difficulty": "medium", "split": "train",
        "company_name": "Tressbridge Grocers", "period": "Q4 2024",
        "financial_data": {
            "revenue_m": 1240.0, "revenue_growth_yoy_pct": 7.5,
            "gross_margin_pct": 26.3, "operating_income_m": 62.0,
            "operating_margin_pct": 5.0, "net_income_m": 48.4,
            "eps": 2.42, "comparable_store_sales_growth_pct": 5.1,
            "e_commerce_delivery_revenue_m": 148.8, "e_commerce_growth_pct": 31.0,
            "store_count": 512, "own_brand_revenue_pct": 34,
            "free_cash_flow_m": 78.0,
            "note": "Own-brand penetration reached 34%; delivery orders up 31%; fuel price deflation aided gross margin"
        },
        "gold_criteria": "Revenue $1.24B up 7.5%|Gross margin 26.3%|Operating income $62M 5% margin|Comp sales +5.1%|Own-brand 34% penetration|Delivery revenue $148.8M up 31%|512 stores|FCF $78M"
    },
    {
        "item_id": "UC8_033", "sector": "Retail", "difficulty": "medium", "split": "train",
        "company_name": "Holbrook Electronics", "period": "Q3 2024",
        "financial_data": {
            "revenue_m": 687.2, "revenue_growth_yoy_pct": 4.0,
            "gross_margin_pct": 31.8, "operating_income_m": 41.2,
            "operating_margin_pct": 6.0, "net_income_m": 31.6,
            "eps": 1.58, "comparable_store_sales_growth_pct": 1.9,
            "e_commerce_revenue_m": 206.2, "e_commerce_growth_pct": 16.0,
            "store_count": 334, "free_cash_flow_m": 49.5,
            "note": "Services (warranty, installation) revenue grew 22%; device revenue soft due to elongated upgrade cycles"
        },
        "gold_criteria": "Revenue $687.2M up 4%|Gross margin 31.8%|Operating income $41.2M 6% margin|Comp sales +1.9%|E-commerce $206.2M up 16%|Services revenue grew 22%|Device revenue soft upgrade cycle elongation"
    },
    {
        "item_id": "UC8_034", "sector": "Retail", "difficulty": "medium", "split": "train",
        "company_name": "Alderton Sports", "period": "Q2 2024",
        "financial_data": {
            "revenue_m": 421.6, "revenue_growth_yoy_pct": 5.8,
            "gross_margin_pct": 37.4, "operating_income_m": 38.0,
            "operating_margin_pct": 9.0, "net_income_m": 29.4,
            "eps": 1.47, "comparable_store_sales_growth_pct": 3.2,
            "e_commerce_revenue_m": 126.5, "e_commerce_growth_pct": 15.8,
            "store_count": 207, "free_cash_flow_m": 44.7,
            "note": "Private label margin uplift partially offset by promotional pricing in team sports category"
        },
        "gold_criteria": "Revenue $421.6M up 5.8%|Gross margin 37.4%|Operating income $38M 9% margin|Comp sales +3.2%|E-commerce $126.5M up 15.8%|207 stores|Private label uplift vs promotions trade-off"
    },

    # --- hard (items 035-040, 2 in test: 035-036) ---
    {
        "item_id": "UC8_035", "sector": "Retail", "difficulty": "hard", "split": "test",
        "company_name": "Ashford Department Stores", "period": "Q3 2025",
        "financial_data": {
            "revenue_m": 1820.0, "revenue_growth_yoy_pct": -6.3,
            "gross_margin_pct": 28.4, "gross_margin_prev_year_pct": 33.8,
            "operating_income_m": -45.2, "operating_margin_pct": -2.5,
            "net_income_m": -68.4, "eps": -3.42,
            "comparable_store_sales_growth_pct": -8.1,
            "e_commerce_revenue_m": 273.0, "e_commerce_growth_pct": 5.2,
            "store_count": 289, "stores_closed": 22,
            "inventory_writedown_m": 65.0, "debt_m": 1240.0,
            "interest_expense_m": 41.0, "free_cash_flow_m": -82.0,
            "note": "Accelerated store rationalisation; $65M inventory writedown on clearance; debt service burden constraining investment; management pursuing strategic alternatives including potential partial brand sale"
        },
        "gold_criteria": "Revenue $1.82B down 6.3%|Gross margin 28.4% down from 33.8%|Operating loss -$45.2M -2.5% margin|Net loss -$68.4M|Comp sales -8.1% sustained decline|E-commerce $273M up 5.2% insufficient to offset store decline|22 store closures rationalisation|$65M inventory writedown|$1.24B debt interest burden $41M|FCF -$82M|Strategic alternatives including brand sale -- multiple severe signals must all be reported"
    },
    {
        "item_id": "UC8_036", "sector": "Retail", "difficulty": "hard", "split": "test",
        "company_name": "Meridian Marketplaces", "period": "Q4 2025",
        "financial_data": {
            "revenue_m": 2340.0, "revenue_growth_yoy_pct": 18.6,
            "gross_margin_pct": 22.1, "operating_income_m": 93.6,
            "operating_margin_pct": 4.0, "net_income_m": 68.2,
            "eps": 3.41, "gmv_b": 8.4, "gmv_growth_pct": 31.0,
            "take_rate_pct": 27.9,
            "active_sellers": 142000, "active_buyers_m": 18.2,
            "fulfillment_expense_m": 420.0, "fulfillment_pct_revenue": 17.9,
            "advertising_revenue_m": 280.8, "advertising_growth_pct": 44.0,
            "free_cash_flow_m": 187.0,
            "note": "Marketplace model: product revenue mix shifting; advertising becoming material segment (12% of revenue); GMV growth substantially exceeds revenue growth due to mix shift toward lower take-rate categories; fulfillment cost improvement programme on track"
        },
        "gold_criteria": "Revenue $2.34B up 18.6%|GMV $8.4B up 31% exceeds revenue growth -- mix shift|Take rate 27.9%|Gross margin 22.1% marketplace model|Operating income $93.6M 4% margin|Advertising $280.8M up 44% 12% of revenue material segment|Active buyers 18.2M sellers 142K|Fulfillment $420M 17.9% of revenue|FCF $187M strong|GMV vs revenue divergence must be explained"
    },
    {
        "item_id": "UC8_037", "sector": "Retail", "difficulty": "hard", "split": "train",
        "company_name": "Prism Fashion Group", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 643.8, "revenue_growth_yoy_pct": -4.8,
            "gross_margin_pct": 30.2, "operating_income_m": -32.1,
            "operating_margin_pct": -5.0, "net_income_m": -41.5, "eps": -2.07,
            "comparable_store_sales_growth_pct": -7.2,
            "e_commerce_revenue_m": 96.6, "e_commerce_growth_pct": 8.5,
            "store_count": 312, "stores_closed": 18, "free_cash_flow_m": -38.4,
            "note": "Brand refresh underway; spring collection underperformed; inventory aged at 14 weeks vs target of 9 weeks"
        },
        "gold_criteria": "Revenue $643.8M down 4.8%|Gross margin 30.2%|Operating loss -$32.1M|Comp sales -7.2%|E-commerce only bright spot up 8.5%|18 store closures|Aged inventory 14 weeks vs 9 target|Brand refresh underway"
    },
    {
        "item_id": "UC8_038", "sector": "Retail", "difficulty": "hard", "split": "train",
        "company_name": "Veritas Luxury", "period": "Q2 2024",
        "financial_data": {
            "revenue_m": 189.4, "revenue_growth_yoy_pct": 9.3,
            "gross_margin_pct": 62.8, "operating_income_m": 44.2,
            "operating_margin_pct": 23.4, "net_income_m": 35.7,
            "eps": 5.96, "comparable_store_sales_growth_pct": 6.1,
            "china_revenue_pct": 28, "china_revenue_growth_pct": -11.0,
            "europe_revenue_growth_pct": 18.5, "us_revenue_growth_pct": 12.1,
            "store_count": 84, "free_cash_flow_m": 52.0,
            "note": "China slowdown notable given prior-year double-digit growth; European and US demand remain robust; FX headwind of 3pp on reported revenue"
        },
        "gold_criteria": "Revenue $189.4M up 9.3%|Gross margin 62.8% luxury premium|Operating income $44.2M 23.4% margin|Comp sales +6.1%|China 28% of revenue DOWN 11% -- significant|Europe +18.5% US +12.1% offsetting|FX 3pp headwind|84 stores"
    },
    {
        "item_id": "UC8_039", "sector": "Retail", "difficulty": "hard", "split": "train",
        "company_name": "Vortex Grocery Chain", "period": "Q3 2024",
        "financial_data": {
            "revenue_m": 3120.0, "revenue_growth_yoy_pct": 3.2,
            "gross_margin_pct": 24.8, "operating_income_m": 93.6,
            "operating_margin_pct": 3.0, "net_income_m": 71.8,
            "eps": 3.59, "comparable_store_sales_growth_pct": 1.8,
            "food_inflation_impact_pct": 2.5, "volume_growth_pct": -0.7,
            "store_count": 718, "new_stores_opened": 14, "stores_closed": 6,
            "own_brand_pct": 31, "free_cash_flow_m": 112.0,
            "note": "Volume declined 0.7% -- consumers trading down; food inflation of 2.5% masking underlying demand weakness; own-brand outperforming national brands"
        },
        "gold_criteria": "Revenue $3.12B up 3.2%|Gross margin 24.8%|Operating income $93.6M 3% margin|Comp sales +1.8% driven by inflation 2.5% not volume|Volume -0.7% trade-down pressure|Own-brand 31% outperforming|718 stores net 8 new|FCF $112M"
    },
    {
        "item_id": "UC8_040", "sector": "Retail", "difficulty": "hard", "split": "train",
        "company_name": "Kestrel Direct", "period": "Q1 2024",
        "financial_data": {
            "revenue_m": 1128.0, "revenue_growth_yoy_pct": 21.4,
            "gross_margin_pct": 19.8, "operating_income_m": -33.8,
            "operating_margin_pct": -3.0, "net_income_m": -42.6, "eps": -2.13,
            "return_rate_pct": 24.8, "return_cost_m": 88.0,
            "customer_acquisition_cost": 48, "ltv_cac_ratio": 2.1,
            "active_customers_m": 6.8, "free_cash_flow_m": -55.0,
            "note": "High return rate eating into margins; LTV:CAC improving; management expects path to profitability by Q4 2025; $55M FCF burn rate"
        },
        "gold_criteria": "Revenue $1.13B up 21.4%|Gross margin 19.8%|Operating loss -$33.8M -3% margin|Return rate 24.8% -- major margin headwind $88M cost|LTV:CAC 2.1 improving|FCF -$55M burn|Path to profitability Q4 2025 guidance"
    },

    # =========================================================
    # SECTOR: Healthcare   (items 041-060)
    # =========================================================

    # --- easy (items 041-047, 2 in test: 041-042) ---
    {
        "item_id": "UC8_041", "sector": "Healthcare", "difficulty": "easy", "split": "test",
        "company_name": "Meridian Health Systems", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 1840.0, "revenue_growth_yoy_pct": 8.4,
            "patient_service_revenue_m": 1656.0, "other_revenue_m": 184.0,
            "operating_income_m": 184.0, "operating_margin_pct": 10.0,
            "net_income_m": 138.0, "eps": 6.90,
            "adjusted_ebitda_m": 294.4, "adjusted_ebitda_margin_pct": 16.0,
            "patient_volume_growth_pct": 5.2, "same_facility_revenue_growth_pct": 7.1,
            "beds": 4280, "admissions": 68400, "new_facilities": 2,
            "free_cash_flow_m": 221.0
        },
        "gold_criteria": "Revenue $1.84B up 8.4%|Patient service revenue $1.656B|Operating income $184M 10% margin|Adjusted EBITDA $294.4M 16% margin|Patient volume +5.2%|Same-facility +7.1%|68400 admissions 4280 beds|2 new facilities|FCF $221M"
    },
    {
        "item_id": "UC8_042", "sector": "Healthcare", "difficulty": "easy", "split": "test",
        "company_name": "Clearpath Medical Group", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 924.0, "revenue_growth_yoy_pct": 9.6,
            "patient_service_revenue_m": 831.6, "other_revenue_m": 92.4,
            "operating_income_m": 102.7, "operating_margin_pct": 11.1,
            "net_income_m": 78.5, "eps": 3.92,
            "adjusted_ebitda_m": 157.1, "adjusted_ebitda_margin_pct": 17.0,
            "patient_volume_growth_pct": 6.3, "same_facility_revenue_growth_pct": 8.4,
            "beds": 2190, "admissions": 34200,
            "free_cash_flow_m": 119.0
        },
        "gold_criteria": "Revenue $924M up 9.6%|Patient service revenue $831.6M|Operating income $102.7M 11.1% margin|Adjusted EBITDA $157.1M 17% margin|Patient volume +6.3%|Same-facility +8.4%|34200 admissions|FCF $119M"
    },
    {
        "item_id": "UC8_043", "sector": "Healthcare", "difficulty": "easy", "split": "train",
        "company_name": "Talbot Physician Network", "period": "Q3 2024",
        "financial_data": {
            "revenue_m": 618.0, "revenue_growth_yoy_pct": 7.2,
            "patient_service_revenue_m": 556.2, "operating_income_m": 61.8,
            "operating_margin_pct": 10.0, "net_income_m": 47.4, "eps": 2.37,
            "adjusted_ebitda_m": 98.9, "adjusted_ebitda_margin_pct": 16.0,
            "patient_volume_growth_pct": 4.8, "same_facility_revenue_growth_pct": 6.1,
            "free_cash_flow_m": 78.2
        },
        "gold_criteria": "Revenue $618M up 7.2%|Operating income $61.8M 10% margin|Adjusted EBITDA $98.9M 16%|Patient volume +4.8%|Same-facility +6.1%|FCF $78.2M"
    },
    {
        "item_id": "UC8_044", "sector": "Healthcare", "difficulty": "easy", "split": "train",
        "company_name": "Elara Health Partners", "period": "Q4 2024",
        "financial_data": {
            "revenue_m": 1120.0, "revenue_growth_yoy_pct": 10.1,
            "operating_income_m": 123.2, "operating_margin_pct": 11.0,
            "net_income_m": 94.1, "eps": 4.71,
            "adjusted_ebitda_m": 179.2, "adjusted_ebitda_margin_pct": 16.0,
            "patient_volume_growth_pct": 6.5, "same_facility_revenue_growth_pct": 8.8,
            "free_cash_flow_m": 148.0
        },
        "gold_criteria": "Revenue $1.12B up 10.1%|Operating income $123.2M 11% margin|EBITDA $179.2M 16%|Patient volume +6.5%|Same-facility +8.8%|FCF $148M"
    },
    {
        "item_id": "UC8_045", "sector": "Healthcare", "difficulty": "easy", "split": "train",
        "company_name": "Novus Diagnostics", "period": "Q2 2024",
        "financial_data": {
            "revenue_m": 412.0, "revenue_growth_yoy_pct": 8.9,
            "operating_income_m": 49.4, "operating_margin_pct": 12.0,
            "net_income_m": 38.3, "eps": 1.91,
            "test_volume_growth_pct": 7.4, "revenue_per_test_growth_pct": 1.4,
            "free_cash_flow_m": 58.0
        },
        "gold_criteria": "Revenue $412M up 8.9%|Operating income $49.4M 12% margin|Test volume +7.4%|Revenue per test +1.4%|FCF $58M"
    },
    {
        "item_id": "UC8_046", "sector": "Healthcare", "difficulty": "easy", "split": "train",
        "company_name": "Cascade Wellness Group", "period": "Q3 2025",
        "financial_data": {
            "revenue_m": 782.0, "revenue_growth_yoy_pct": 7.8,
            "operating_income_m": 86.0, "operating_margin_pct": 11.0,
            "net_income_m": 66.0, "eps": 3.30,
            "adjusted_ebitda_m": 125.1, "adjusted_ebitda_margin_pct": 16.0,
            "patient_volume_growth_pct": 5.0, "free_cash_flow_m": 102.0
        },
        "gold_criteria": "Revenue $782M up 7.8%|Operating income $86M 11% margin|EBITDA $125.1M 16%|Patient volume +5%|FCF $102M"
    },
    {
        "item_id": "UC8_047", "sector": "Healthcare", "difficulty": "easy", "split": "train",
        "company_name": "Keystone Medical Centers", "period": "Q1 2024",
        "financial_data": {
            "revenue_m": 534.0, "revenue_growth_yoy_pct": 6.4,
            "operating_income_m": 58.7, "operating_margin_pct": 11.0,
            "net_income_m": 44.8, "eps": 2.24,
            "adjusted_ebitda_m": 85.4, "adjusted_ebitda_margin_pct": 16.0,
            "patient_volume_growth_pct": 4.1, "free_cash_flow_m": 69.8
        },
        "gold_criteria": "Revenue $534M up 6.4%|Operating income $58.7M 11% margin|EBITDA $85.4M 16%|Patient volume +4.1%|FCF $69.8M"
    },

    # --- medium (items 048-054, 2 in test: 048-049) ---
    {
        "item_id": "UC8_048", "sector": "Healthcare", "difficulty": "medium", "split": "test",
        "company_name": "Apex Health Network", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 2140.0, "revenue_growth_yoy_pct": 5.1,
            "operating_income_m": 149.8, "operating_margin_pct": 7.0,
            "net_income_m": 107.0, "eps": 5.35,
            "adjusted_ebitda_m": 278.2, "adjusted_ebitda_margin_pct": 13.0,
            "patient_volume_growth_pct": 2.8, "same_facility_revenue_growth_pct": 4.6,
            "nursing_vacancy_rate_pct": 14.2, "agency_staffing_spend_m": 142.0,
            "agency_pct_revenue": 6.6,
            "free_cash_flow_m": 178.0,
            "note": "Agency staffing costs elevated at 6.6% of revenue due to nursing vacancy rate of 14.2%; management targeting 10% vacancy rate by year-end through recruitment programme"
        },
        "gold_criteria": "Revenue $2.14B up 5.1%|Operating income $149.8M 7% margin -- compressed|EBITDA $278.2M 13% margin|Patient volume +2.8%|Agency staffing $142M 6.6% revenue headwind|Nursing vacancy 14.2%|Recruitment programme targeting 10%|FCF $178M"
    },
    {
        "item_id": "UC8_049", "sector": "Healthcare", "difficulty": "medium", "split": "test",
        "company_name": "Sunridge Medical", "period": "Q3 2025",
        "financial_data": {
            "revenue_m": 876.0, "revenue_growth_yoy_pct": 6.8,
            "operating_income_m": 70.1, "operating_margin_pct": 8.0,
            "net_income_m": 51.7, "eps": 2.58,
            "adjusted_ebitda_m": 131.4, "adjusted_ebitda_margin_pct": 15.0,
            "patient_volume_growth_pct": 4.2,
            "malpractice_settlement_m": 28.0, "insurance_recoverable_m": 16.0,
            "government_reimbursement_rate_change_pct": -1.8,
            "free_cash_flow_m": 92.0,
            "note": "Malpractice settlement of $28M ($16M covered by insurance, $12M net charge); government reimbursement rates reduced 1.8% effective Q2"
        },
        "gold_criteria": "Revenue $876M up 6.8%|Operating income $70.1M 8% margin impacted by settlement|EBITDA $131.4M 15%|Patient volume +4.2%|$28M malpractice settlement net $12M after $16M insurance|Government reimbursement -1.8% headwind|FCF $92M"
    },
    {
        "item_id": "UC8_050", "sector": "Healthcare", "difficulty": "medium", "split": "train",
        "company_name": "Holloway Hospital Group", "period": "Q4 2024",
        "financial_data": {
            "revenue_m": 1580.0, "revenue_growth_yoy_pct": 4.3,
            "operating_income_m": 110.6, "operating_margin_pct": 7.0,
            "net_income_m": 79.0, "eps": 3.95,
            "adjusted_ebitda_m": 205.4, "adjusted_ebitda_margin_pct": 13.0,
            "patient_volume_growth_pct": 2.1, "payer_mix_government_pct": 62,
            "payer_mix_private_pct": 38,
            "free_cash_flow_m": 130.0,
            "note": "Government payer mix at 62% constraining revenue per visit; private payer volumes grew 8% offsetting government reimbursement pressure"
        },
        "gold_criteria": "Revenue $1.58B up 4.3%|Operating income $110.6M 7% margin|EBITDA $205.4M 13%|Patient volume +2.1%|Government payer 62% constraining revenue|Private payer volume +8%|FCF $130M"
    },
    {
        "item_id": "UC8_051", "sector": "Healthcare", "difficulty": "medium", "split": "train",
        "company_name": "Vertex Pharma Services", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 354.0, "revenue_growth_yoy_pct": 11.4,
            "operating_income_m": 42.5, "operating_margin_pct": 12.0,
            "net_income_m": 32.7, "eps": 1.64,
            "backlog_m": 1240.0, "backlog_growth_pct": 18.0,
            "book_to_bill_ratio": 1.24, "free_cash_flow_m": 47.2,
            "note": "Contract research organisation; backlog grew 18% to $1.24B; book-to-bill of 1.24 signals continued pipeline growth"
        },
        "gold_criteria": "Revenue $354M up 11.4%|Operating income $42.5M 12% margin|Backlog $1.24B up 18%|Book-to-bill 1.24 strong pipeline signal|FCF $47.2M"
    },
    {
        "item_id": "UC8_052", "sector": "Healthcare", "difficulty": "medium", "split": "train",
        "company_name": "Brightway Behavioral Health", "period": "Q1 2024",
        "financial_data": {
            "revenue_m": 228.0, "revenue_growth_yoy_pct": 14.2,
            "operating_income_m": 27.4, "operating_margin_pct": 12.0,
            "net_income_m": 20.8, "eps": 1.04,
            "patient_volume_growth_pct": 11.5, "occupancy_rate_pct": 82.4,
            "new_facilities_opened": 4, "free_cash_flow_m": 31.4,
            "note": "Expansion into telehealth driving volume growth; occupancy at 82.4% with target of 88%; four new facilities increased capacity by 340 beds"
        },
        "gold_criteria": "Revenue $228M up 14.2%|Operating income $27.4M 12% margin|Patient volume +11.5%|Occupancy 82.4% target 88%|4 new facilities 340 beds|Telehealth expansion driver|FCF $31.4M"
    },
    {
        "item_id": "UC8_053", "sector": "Healthcare", "difficulty": "medium", "split": "train",
        "company_name": "Indus Medical Devices", "period": "Q3 2024",
        "financial_data": {
            "revenue_m": 612.0, "revenue_growth_yoy_pct": 9.1,
            "gross_margin_pct": 58.4, "operating_income_m": 79.6,
            "operating_margin_pct": 13.0, "net_income_m": 62.0, "eps": 3.10,
            "r_and_d_m": 67.3, "r_and_d_pct_revenue": 11.0,
            "pipeline_products_phase_3": 3, "free_cash_flow_m": 88.4,
            "note": "Three products in Phase 3 trials; R&D spend elevated at 11% of revenue; gross margin expansion driven by premium product mix"
        },
        "gold_criteria": "Revenue $612M up 9.1%|Gross margin 58.4%|Operating income $79.6M 13% margin|R&D $67.3M 11% revenue|3 Phase 3 pipeline products|FCF $88.4M"
    },
    {
        "item_id": "UC8_054", "sector": "Healthcare", "difficulty": "medium", "split": "train",
        "company_name": "Solara Health IT", "period": "Q4 2025",
        "financial_data": {
            "revenue_m": 198.0, "revenue_growth_yoy_pct": 12.7,
            "gross_margin_pct": 67.2, "operating_income_m": 29.7,
            "operating_margin_pct": 15.0, "net_income_m": 22.8, "eps": 1.14,
            "arr_m": 762.0, "arr_growth_pct": 14.0,
            "net_revenue_retention_pct": 112, "free_cash_flow_m": 34.7,
            "note": "Health IT software; hospital system consolidation creating larger deal sizes"
        },
        "gold_criteria": "Revenue $198M up 12.7%|Gross margin 67.2%|Operating income $29.7M 15% margin|ARR $762M up 14%|NRR 112%|FCF $34.7M|Consolidation tailwind"
    },

    # --- hard (items 055-060, 2 in test: 055-056) ---
    {
        "item_id": "UC8_055", "sector": "Healthcare", "difficulty": "hard", "split": "test",
        "company_name": "Talbot Health Corporation", "period": "Q2 2024",
        "financial_data": {
            "revenue_m": 3420.0, "revenue_growth_yoy_pct": 1.8,
            "operating_income_m": -68.4, "operating_margin_pct": -2.0,
            "net_income_m": -112.0, "eps": -5.60,
            "adjusted_ebitda_m": 171.0, "adjusted_ebitda_margin_pct": 5.0,
            "patient_volume_growth_pct": -1.2,
            "labor_cost_pct_revenue": 58.4, "labor_cost_prev_year_pct": 54.1,
            "cpi_adjustment_shortfall_m": 82.0,
            "impairment_charges_m": 148.0, "goodwill_impairment_m": 104.0,
            "debt_m": 2840.0, "interest_expense_m": 91.0,
            "free_cash_flow_m": 42.0,
            "note": "Operating loss driven by $148M impairment charges ($104M goodwill); labor cost inflation 4.3pp exceeding government reimbursement CPI adjustment by $82M; patient volume decline reflects community health centre competition; debt covenants under review"
        },
        "gold_criteria": "Revenue $3.42B up 1.8% near-flat|Operating loss -$68.4M -2% margin|Net loss -$112M|$148M impairment $104M goodwill|EBITDA $171M 5% excluding impairment|Labor cost 58.4% up from 54.1% -- major margin headwind|Government CPI shortfall $82M|Patient volume -1.2%|Debt $2.84B covenants review|Interest $91M|FCF $42M positive despite net loss -- must explain gap|Multiple compounding pressures all required"
    },
    {
        "item_id": "UC8_056", "sector": "Healthcare", "difficulty": "hard", "split": "test",
        "company_name": "Pharos Genomics", "period": "Q3 2025",
        "financial_data": {
            "revenue_m": 84.2, "revenue_growth_yoy_pct": 48.6,
            "gross_margin_pct": 71.4, "operating_income_m": -62.1,
            "operating_margin_pct": -73.8, "net_income_m": -68.4, "eps": -3.42,
            "r_and_d_m": 95.6, "r_and_d_pct_revenue": 113.5,
            "clinical_trials_active": 7, "fda_pdu_applications": 2,
            "cash_and_equivalents_m": 312.0, "cash_runway_quarters": 5.8,
            "partnership_milestone_revenue_m": 38.0,
            "product_revenue_m": 46.2,
            "note": "Genomics company with two FDA applications pending; R&D exceeds revenue at 113.5%; $38M of revenue from partnership milestone payments (one-time in nature); product revenue of $46.2M growing at 68% organically; cash runway of ~5.8 quarters requiring capital raise or partnership monetisation"
        },
        "gold_criteria": "Revenue $84.2M up 48.6% -- include milestone vs product split|Product revenue $46.2M up 68% organic growth|Partnership milestones $38M one-time|Gross margin 71.4%|Operating loss -$62.1M -73.8% margin|R&D $95.6M 113.5% of revenue|Net loss -$68.4M|7 active trials 2 FDA applications|Cash $312M runway 5.8 quarters -- capital raise risk|Distinction between one-time and recurring revenue essential"
    },
    {
        "item_id": "UC8_057", "sector": "Healthcare", "difficulty": "hard", "split": "train",
        "company_name": "Caduceus Hospital Group", "period": "Q4 2025",
        "financial_data": {
            "revenue_m": 4180.0, "revenue_growth_yoy_pct": -2.1,
            "operating_income_m": -125.4, "operating_margin_pct": -3.0,
            "net_income_m": -196.0, "eps": -9.80,
            "adjusted_ebitda_m": 209.0, "adjusted_ebitda_margin_pct": 5.0,
            "divestiture_proceeds_m": 340.0, "divestiture_facilities": 8,
            "debt_m": 3620.0, "free_cash_flow_m": 125.0,
            "note": "Divested 8 underperforming facilities for $340M proceeds; restructuring ongoing; management targeting positive GAAP income by Q3 2026"
        },
        "gold_criteria": "Revenue $4.18B down 2.1%|Operating loss -$125.4M -3% margin|Net loss -$196M|EBITDA $209M 5% margin -- positive on adjusted basis|Divested 8 facilities $340M proceeds|Debt $3.62B|FCF +$125M despite net loss|Restructuring Q3 2026 profitability target"
    },
    {
        "item_id": "UC8_058", "sector": "Healthcare", "difficulty": "hard", "split": "train",
        "company_name": "Ardent Biosciences", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 128.0, "revenue_growth_yoy_pct": -18.4,
            "gross_margin_pct": 78.1, "operating_income_m": -44.8,
            "operating_margin_pct": -35.0, "net_income_m": -51.2, "eps": -2.56,
            "key_product_revenue_decline_pct": -32,
            "generic_competition_products": 2,
            "pipeline_nda_submissions": 1, "cash_m": 285.0,
            "free_cash_flow_m": -48.0,
            "note": "Revenue decline driven by generic competition on two legacy products; new NDA submission for next-generation compound; cash runway ~6 quarters"
        },
        "gold_criteria": "Revenue $128M down 18.4%|Gross margin 78.1%|Operating loss -$44.8M -35% margin|Generic competition on 2 products|1 NDA submission pipeline|Cash $285M runway 6 quarters|FCF -$48M|Revenue decline must be contextualised with pipeline"
    },
    {
        "item_id": "UC8_059", "sector": "Healthcare", "difficulty": "hard", "split": "train",
        "company_name": "Vitalis Care Network", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 1920.0, "revenue_growth_yoy_pct": 14.8,
            "organic_growth_pct": 6.2, "acquisition_contribution_pct": 8.6,
            "operating_income_m": 134.4, "operating_margin_pct": 7.0,
            "net_income_m": 76.8, "eps": 3.84,
            "debt_from_acquisitions_m": 680.0, "leverage_ratio": 3.4,
            "free_cash_flow_m": 153.0,
            "note": "Growth includes 8.6pp from recent acquisition; organic growth 6.2%; leverage ratio of 3.4x elevated following acquisition financing"
        },
        "gold_criteria": "Revenue $1.92B up 14.8%|Organic growth 6.2% acquisition 8.6%|Operating income $134.4M 7% margin|Net income $76.8M|Leverage 3.4x elevated acquisition debt $680M|FCF $153M|Must distinguish organic vs inorganic growth"
    },
    {
        "item_id": "UC8_060", "sector": "Healthcare", "difficulty": "hard", "split": "train",
        "company_name": "Pinnacle Payer Solutions", "period": "Q3 2025",
        "financial_data": {
            "premium_revenue_m": 6840.0, "premium_growth_pct": 12.3,
            "medical_loss_ratio_pct": 87.4, "mlr_prev_year_pct": 83.2,
            "admin_expense_ratio_pct": 7.8, "operating_income_m": 335.2,
            "operating_margin_pct": 4.9, "net_income_m": 261.4, "eps": 13.07,
            "members_m": 4.8, "member_growth_pct": 8.2,
            "free_cash_flow_m": 412.0,
            "note": "Medical loss ratio deterioration of 4.2pp due to elevated utilisation in Medicare Advantage segment; admin efficiency improving; prior year benefited from favourable claims development of $95M not repeated"
        },
        "gold_criteria": "Revenue $6.84B up 12.3%|MLR 87.4% up from 83.2% -- 4.2pp deterioration Medicare Advantage utilisation|Admin ratio 7.8% efficient|Operating income $335.2M 4.9% margin|Net income $261.4M|4.8M members +8.2%|Prior year $95M favourable development not repeated|FCF $412M|MLR deterioration is primary concern"
    },

    # =========================================================
    # SECTOR: Manufacturing   (items 061-080)
    # =========================================================

    # --- easy (items 061-067, 2 in test: 061-062) ---
    {
        "item_id": "UC8_061", "sector": "Manufacturing", "difficulty": "easy", "split": "test",
        "company_name": "Fortis Industrial", "period": "Q3 2025",
        "financial_data": {
            "revenue_m": 2840.0, "revenue_growth_yoy_pct": 9.2,
            "gross_margin_pct": 32.4, "operating_income_m": 312.4,
            "operating_margin_pct": 11.0, "net_income_m": 240.0, "eps": 12.00,
            "organic_growth_pct": 9.2, "volume_growth_pct": 6.8, "price_mix_pct": 2.4,
            "backlog_b": 14.2, "backlog_growth_pct": 14.5,
            "capacity_utilisation_pct": 84, "free_cash_flow_m": 354.0
        },
        "gold_criteria": "Revenue $2.84B up 9.2%|Gross margin 32.4%|Operating income $312.4M 11% margin|Volume +6.8% price/mix +2.4%|Backlog $14.2B up 14.5%|Capacity utilisation 84%|FCF $354M"
    },
    {
        "item_id": "UC8_062", "sector": "Manufacturing", "difficulty": "easy", "split": "test",
        "company_name": "Vantage Precision Parts", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 1120.0, "revenue_growth_yoy_pct": 11.8,
            "gross_margin_pct": 29.6, "operating_income_m": 112.0,
            "operating_margin_pct": 10.0, "net_income_m": 84.0, "eps": 4.20,
            "organic_growth_pct": 11.8, "volume_growth_pct": 8.4, "price_mix_pct": 3.4,
            "backlog_m": 4200.0, "capacity_utilisation_pct": 81,
            "free_cash_flow_m": 138.0
        },
        "gold_criteria": "Revenue $1.12B up 11.8%|Gross margin 29.6%|Operating income $112M 10% margin|Volume +8.4% price/mix +3.4%|Backlog $4.2B|Capacity 81%|FCF $138M"
    },
    {
        "item_id": "UC8_063", "sector": "Manufacturing", "difficulty": "easy", "split": "train",
        "company_name": "Apex Composites", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 780.0, "revenue_growth_yoy_pct": 8.5,
            "gross_margin_pct": 31.0, "operating_income_m": 85.8,
            "operating_margin_pct": 11.0, "net_income_m": 64.4, "eps": 3.22,
            "volume_growth_pct": 6.2, "price_mix_pct": 2.3,
            "backlog_m": 2900.0, "free_cash_flow_m": 104.0
        },
        "gold_criteria": "Revenue $780M up 8.5%|Gross margin 31%|Operating income $85.8M 11% margin|Volume +6.2% price/mix +2.3%|Backlog $2.9B|FCF $104M"
    },
    {
        "item_id": "UC8_064", "sector": "Manufacturing", "difficulty": "easy", "split": "train",
        "company_name": "Delta Engineering Works", "period": "Q4 2024",
        "financial_data": {
            "revenue_m": 1560.0, "revenue_growth_yoy_pct": 10.3,
            "gross_margin_pct": 33.1, "operating_income_m": 171.6,
            "operating_margin_pct": 11.0, "net_income_m": 128.7, "eps": 6.44,
            "volume_growth_pct": 7.5, "price_mix_pct": 2.8, "backlog_b": 6.8,
            "free_cash_flow_m": 196.0
        },
        "gold_criteria": "Revenue $1.56B up 10.3%|Gross margin 33.1%|Operating income $171.6M 11% margin|Volume +7.5% price +2.8%|Backlog $6.8B|FCF $196M"
    },
    {
        "item_id": "UC8_065", "sector": "Manufacturing", "difficulty": "easy", "split": "train",
        "company_name": "Ironclad Systems", "period": "Q3 2024",
        "financial_data": {
            "revenue_m": 956.0, "revenue_growth_yoy_pct": 9.8,
            "gross_margin_pct": 28.4, "operating_income_m": 95.6,
            "operating_margin_pct": 10.0, "net_income_m": 71.7, "eps": 3.59,
            "volume_growth_pct": 7.0, "price_mix_pct": 2.8, "backlog_m": 3800.0,
            "free_cash_flow_m": 117.0
        },
        "gold_criteria": "Revenue $956M up 9.8%|Gross margin 28.4%|Operating income $95.6M 10% margin|Volume +7% price +2.8%|Backlog $3.8B|FCF $117M"
    },
    {
        "item_id": "UC8_066", "sector": "Manufacturing", "difficulty": "easy", "split": "train",
        "company_name": "Thorngate Pumps", "period": "Q2 2024",
        "financial_data": {
            "revenue_m": 642.0, "revenue_growth_yoy_pct": 7.4,
            "gross_margin_pct": 30.2, "operating_income_m": 64.2,
            "operating_margin_pct": 10.0, "net_income_m": 48.2, "eps": 2.41,
            "volume_growth_pct": 5.1, "price_mix_pct": 2.3, "backlog_m": 2400.0,
            "free_cash_flow_m": 79.0
        },
        "gold_criteria": "Revenue $642M up 7.4%|Gross margin 30.2%|Operating income $64.2M 10% margin|Volume +5.1% price +2.3%|Backlog $2.4B|FCF $79M"
    },
    {
        "item_id": "UC8_067", "sector": "Manufacturing", "difficulty": "easy", "split": "train",
        "company_name": "Keystone Metals", "period": "Q1 2024",
        "financial_data": {
            "revenue_m": 492.0, "revenue_growth_yoy_pct": 8.1,
            "gross_margin_pct": 29.8, "operating_income_m": 49.2,
            "operating_margin_pct": 10.0, "net_income_m": 36.9, "eps": 1.85,
            "volume_growth_pct": 5.8, "price_mix_pct": 2.3, "backlog_m": 1840.0,
            "free_cash_flow_m": 60.4
        },
        "gold_criteria": "Revenue $492M up 8.1%|Gross margin 29.8%|Operating income $49.2M 10% margin|Volume +5.8% price +2.3%|Backlog $1.84B|FCF $60.4M"
    },

    # --- medium (items 068-074, 2 in test: 068-069) ---
    {
        "item_id": "UC8_068", "sector": "Manufacturing", "difficulty": "medium", "split": "test",
        "company_name": "Regulus Aerospace", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 4820.0, "revenue_growth_yoy_pct": 7.3,
            "gross_margin_pct": 14.8, "gross_margin_prev_year_pct": 18.2,
            "operating_income_m": 193.0, "operating_margin_pct": 4.0,
            "net_income_m": 134.0, "eps": 6.70,
            "backlog_b": 64.0, "backlog_growth_pct": 11.0,
            "supply_chain_premium_costs_m": 182.0,
            "capacity_utilisation_pct": 92,
            "deliveries": 124, "delivery_target": 135,
            "free_cash_flow_m": -210.0,
            "note": "Production ramp constrained by titanium and engine supply shortages; $182M in supply chain premium costs absorbed; 11 aircraft deliveries below target; FCF negative due to inventory build; backlog at record $64B provides long-term visibility"
        },
        "gold_criteria": "Revenue $4.82B up 7.3%|Gross margin 14.8% down from 18.2% -- supply chain $182M premium cost|Operating income $193M 4% margin|Deliveries 124 vs 135 target -- supply shortfall|Backlog $64B up 11% record|Capacity 92%|FCF -$210M inventory build|Supply constraints primary theme must be addressed"
    },
    {
        "item_id": "UC8_069", "sector": "Manufacturing", "difficulty": "medium", "split": "test",
        "company_name": "Harmon Heavy Industries", "period": "Q1 2024",
        "financial_data": {
            "revenue_m": 3120.0, "revenue_growth_yoy_pct": 5.8,
            "gross_margin_pct": 22.4, "operating_income_m": 218.4,
            "operating_margin_pct": 7.0, "net_income_m": 156.0, "eps": 7.80,
            "steel_input_cost_change_pct": 14.2, "price_realization_pct": 6.8,
            "volume_growth_pct": -1.0, "backlog_b": 18.4,
            "free_cash_flow_m": 265.0,
            "note": "Steel input costs increased 14.2% YoY; company captured only 6.8% through pricing, resulting in margin compression; volume declined 1% due to delayed infrastructure project starts"
        },
        "gold_criteria": "Revenue $3.12B up 5.8%|Gross margin 22.4% compressed|Steel costs +14.2% price recovery 6.8% -- margin headwind|Operating income $218.4M 7% margin|Volume -1% project delays|Backlog $18.4B|FCF $265M|Input cost vs pricing gap is key finding"
    },
    {
        "item_id": "UC8_070", "sector": "Manufacturing", "difficulty": "medium", "split": "train",
        "company_name": "Pinnacle Defense Systems", "period": "Q3 2025",
        "financial_data": {
            "revenue_m": 5640.0, "revenue_growth_yoy_pct": 8.1,
            "gross_margin_pct": 16.2, "operating_income_m": 394.8,
            "operating_margin_pct": 7.0, "net_income_m": 282.0, "eps": 14.10,
            "funded_backlog_b": 28.4, "total_backlog_b": 48.6,
            "cost_growth_contracts_pct_portfolio": 18,
            "free_cash_flow_m": 412.0,
            "note": "18% of contract portfolio experiencing cost growth; mix of firm fixed-price and cost-reimbursable contracts; cost growth on two major fixed-price programmes impacting margins"
        },
        "gold_criteria": "Revenue $5.64B up 8.1%|Gross margin 16.2%|Operating income $394.8M 7% margin|Funded backlog $28.4B total $48.6B|18% portfolio cost growth fixed-price risk|FCF $412M"
    },
    {
        "item_id": "UC8_071", "sector": "Manufacturing", "difficulty": "medium", "split": "train",
        "company_name": "Arcum Automotive", "period": "Q2 2024",
        "financial_data": {
            "revenue_m": 6840.0, "revenue_growth_yoy_pct": 4.2,
            "gross_margin_pct": 18.8, "operating_income_m": 479.0,
            "operating_margin_pct": 7.0, "net_income_m": 342.0, "eps": 17.10,
            "ev_revenue_pct": 18, "ev_revenue_growth_pct": 42,
            "ice_revenue_growth_pct": -2, "warranty_provision_m": 84.0,
            "free_cash_flow_m": 521.0,
            "note": "EV segment now 18% of revenue growing 42%; ICE revenue declining 2%; $84M warranty provision for software recall on model year 2023 vehicles"
        },
        "gold_criteria": "Revenue $6.84B up 4.2%|Gross margin 18.8%|Operating income $479M 7% margin|EV 18% of revenue up 42%|ICE down 2%|$84M warranty provision software recall|FCF $521M|EV transition and ICE decline dynamic required"
    },
    {
        "item_id": "UC8_072", "sector": "Manufacturing", "difficulty": "medium", "split": "train",
        "company_name": "Stratford Chemical Corp", "period": "Q4 2024",
        "financial_data": {
            "revenue_m": 2240.0, "revenue_growth_yoy_pct": 3.1,
            "gross_margin_pct": 26.8, "operating_income_m": 179.2,
            "operating_margin_pct": 8.0, "net_income_m": 134.4, "eps": 6.72,
            "volume_growth_pct": 5.4, "price_pct": -2.3,
            "raw_material_cost_change_pct": -8.0,
            "capacity_utilisation_pct": 76,
            "free_cash_flow_m": 212.0,
            "note": "Selling price declined 2.3% reflecting feedstock cost pass-through in contract structures; raw materials 8% lower YoY benefiting margins; capacity at 76% below target of 85%"
        },
        "gold_criteria": "Revenue $2.24B up 3.1%|Gross margin 26.8%|Operating income $179.2M 8% margin|Volume +5.4% price -2.3%|Raw materials -8% tailwind|Capacity 76% below 85% target|FCF $212M"
    },
    {
        "item_id": "UC8_073", "sector": "Manufacturing", "difficulty": "medium", "split": "train",
        "company_name": "Axion Power Systems", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 1840.0, "revenue_growth_yoy_pct": 12.2,
            "gross_margin_pct": 24.5, "operating_income_m": 184.0,
            "operating_margin_pct": 10.0, "net_income_m": 138.0, "eps": 6.90,
            "renewable_segment_growth_pct": 38, "traditional_segment_growth_pct": 2,
            "order_intake_m": 2640.0, "backlog_b": 9.2,
            "free_cash_flow_m": 218.0,
            "note": "Renewable energy segment growing 38% now 32% of revenue; order intake of $2.64B book-to-bill of 1.43"
        },
        "gold_criteria": "Revenue $1.84B up 12.2%|Gross margin 24.5%|Operating income $184M 10% margin|Renewable 38% growth 32% of revenue|Traditional +2%|Order intake $2.64B book-to-bill 1.43|Backlog $9.2B|FCF $218M"
    },
    {
        "item_id": "UC8_074", "sector": "Manufacturing", "difficulty": "medium", "split": "train",
        "company_name": "Crestwood Packaging", "period": "Q3 2024",
        "financial_data": {
            "revenue_m": 1124.0, "revenue_growth_yoy_pct": 2.8,
            "gross_margin_pct": 22.1, "operating_income_m": 90.0,
            "operating_margin_pct": 8.0, "net_income_m": 67.4, "eps": 3.37,
            "volume_growth_pct": 4.2, "price_pct": -1.4,
            "sustainability_packaging_pct": 42, "free_cash_flow_m": 106.0,
            "note": "Sustainable packaging now 42% of product portfolio; price pressure from overcapacity in conventional segment"
        },
        "gold_criteria": "Revenue $1.12B up 2.8%|Gross margin 22.1%|Operating income $90M 8% margin|Volume +4.2% price -1.4%|Sustainable packaging 42% portfolio|FCF $106M"
    },

    # --- hard (items 075-080, 2 in test: 075-076) ---
    {
        "item_id": "UC8_075", "sector": "Manufacturing", "difficulty": "hard", "split": "test",
        "company_name": "Quorum Semiconductors", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 3480.0, "revenue_growth_yoy_pct": -12.4,
            "gross_margin_pct": 38.2, "gross_margin_prev_year_pct": 52.1,
            "operating_income_m": -124.0, "operating_margin_pct": -3.6,
            "net_income_m": -168.0, "eps": -8.40,
            "inventory_m": 2840.0, "inventory_weeks": 38,
            "channel_inventory_overhang_m": 640.0,
            "capex_m": 980.0, "depreciation_m": 620.0,
            "revenue_ai_segment_growth_pct": 84,
            "revenue_pc_segment_decline_pct": -38,
            "free_cash_flow_m": -820.0,
            "note": "PC segment in severe downturn; AI chip segment growing 84% but insufficient to offset; 38 weeks of inventory on hand; channel destocking ongoing; $980M capex commitment for advanced process node ramp; management expects revenue trough in Q2"
        },
        "gold_criteria": "Revenue $3.48B down 12.4%|Gross margin 38.2% down sharply from 52.1%|Operating loss -$124M -3.6% margin|Net loss -$168M|Inventory 38 weeks vs normal 12 channel overhang $640M|AI segment +84% offset by PC -38%|Capex $980M node ramp commitment|FCF -$820M severe cash burn|Revenue trough Q2 guidance|Cyclical downturn context vs structural AI growth required"
    },
    {
        "item_id": "UC8_076", "sector": "Manufacturing", "difficulty": "hard", "split": "test",
        "company_name": "Albion Automotive Group", "period": "Q4 2025",
        "financial_data": {
            "revenue_m": 38400.0, "revenue_growth_yoy_pct": 1.4,
            "gross_margin_pct": 12.8, "operating_income_m": 768.0,
            "operating_margin_pct": 2.0, "net_income_m": 384.0, "eps": 19.20,
            "ev_unit_sales": 142000, "ice_unit_sales": 1184000, "total_units": 1326000,
            "ev_unit_growth_pct": 28, "ice_unit_growth_pct": -4,
            "ev_gross_margin_pct": -8.4,
            "ice_gross_margin_pct": 16.2,
            "ev_investment_ytd_m": 3840.0,
            "uaw_wage_increase_m": 620.0,
            "free_cash_flow_m": 1140.0,
            "note": "EV segment gross margin at -8.4% dragging blended margin; legacy ICE profitability subsidising EV ramp; UAW wage settlement adding $620M annually; EV unit sales growing but pricing pressure from Chinese OEMs; management reaffirmed path to EV profitability at 400K units annually"
        },
        "gold_criteria": "Revenue $38.4B up 1.4%|Gross margin 12.8%|Operating income $768M 2% margin|EV 142K units up 28% gross margin -8.4% -- loss-making|ICE 1.184M units down 4% gross margin 16.2% profitable|EV investment $3.84B YTD|UAW settlement $620M annual cost|FCF $1.14B|Cross-subsidy dynamic -- ICE profits funding EV losses -- is key insight required|Path to EV profitability 400K unit threshold"
    },
    {
        "item_id": "UC8_077", "sector": "Manufacturing", "difficulty": "hard", "split": "train",
        "company_name": "Nova Shipbuilding", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 2140.0, "revenue_growth_yoy_pct": 8.4,
            "gross_margin_pct": 8.2, "operating_income_m": 64.2,
            "operating_margin_pct": 3.0, "net_income_m": 38.5, "eps": 1.93,
            "backlog_b": 22.4, "cost_overrun_programmes_m": 284.0,
            "cost_overrun_charges_m": 148.0, "free_cash_flow_m": 87.0,
            "note": "Two fixed-price naval contracts experienced $284M cost overruns; $148M charges taken in quarter; backlog of $22.4B provides long-term visibility"
        },
        "gold_criteria": "Revenue $2.14B up 8.4%|Gross margin 8.2% compressed by overruns|Operating income $64.2M 3% margin|$284M cost overruns $148M charges|Backlog $22.4B visibility|FCF $87M|Fixed-price contract risk highlighted"
    },
    {
        "item_id": "UC8_078", "sector": "Manufacturing", "difficulty": "hard", "split": "train",
        "company_name": "Trident Industrials", "period": "Q3 2024",
        "financial_data": {
            "revenue_m": 8420.0, "revenue_growth_yoy_pct": -6.8,
            "gross_margin_pct": 20.4, "operating_income_m": 252.6,
            "operating_margin_pct": 3.0, "net_income_m": 168.4, "eps": 8.42,
            "china_exposure_pct": 34, "tariff_impact_m": 312.0,
            "restructuring_m": 185.0, "free_cash_flow_m": 302.0,
            "note": "Revenue decline driven by tariff impact of $312M on China-exposed segments (34% of sales); restructuring charge of $185M for supply chain relocalisation programme"
        },
        "gold_criteria": "Revenue $8.42B down 6.8%|Gross margin 20.4%|Operating income $252.6M 3% margin|China 34% revenue exposure|Tariff impact $312M|Restructuring $185M supply chain relocalisation|FCF $302M|Trade policy risk central finding"
    },
    {
        "item_id": "UC8_079", "sector": "Manufacturing", "difficulty": "hard", "split": "train",
        "company_name": "Paragon Heavy Equipment", "period": "Q1 2024",
        "financial_data": {
            "revenue_m": 5640.0, "revenue_growth_yoy_pct": -3.2,
            "gross_margin_pct": 24.6, "operating_income_m": 282.0,
            "operating_margin_pct": 5.0, "net_income_m": 197.4, "eps": 9.87,
            "mining_segment_decline_pct": -18, "construction_segment_growth_pct": 7,
            "infrastructure_segment_growth_pct": 14,
            "dealer_inventory_overhang_weeks": 22,
            "free_cash_flow_m": 338.0,
            "note": "Mining segment decline of 18% driven by weak commodity prices; construction and infrastructure offsetting; dealer inventory elevated at 22 weeks requiring production cuts"
        },
        "gold_criteria": "Revenue $5.64B down 3.2%|Gross margin 24.6%|Operating income $282M 5% margin|Mining -18% commodity price weakness|Construction +7% infrastructure +14%|Dealer inventory 22 weeks production cuts|FCF $338M|Segment mix analysis essential"
    },
    {
        "item_id": "UC8_080", "sector": "Manufacturing", "difficulty": "hard", "split": "train",
        "company_name": "Colossus Energy Equipment", "period": "Q4 2024",
        "financial_data": {
            "revenue_m": 3820.0, "revenue_growth_yoy_pct": 21.4,
            "gross_margin_pct": 18.4, "operating_income_m": 229.2,
            "operating_margin_pct": 6.0, "net_income_m": 152.8, "eps": 7.64,
            "backlog_b": 16.8, "book_to_bill": 1.38,
            "renewable_order_intake_pct_total": 58,
            "working_capital_build_m": 420.0,
            "free_cash_flow_m": -180.0,
            "note": "Strong orders but FCF negative due to $420M working capital build supporting ramp; 58% of new orders renewable energy; book-to-bill 1.38 signals continued growth"
        },
        "gold_criteria": "Revenue $3.82B up 21.4%|Gross margin 18.4%|Operating income $229.2M 6% margin|Backlog $16.8B book-to-bill 1.38|Renewable 58% of new orders|FCF -$180M working capital build $420M|Strong earnings vs negative FCF divergence must be explained"
    },

    # =========================================================
    # SECTOR: Financial Services   (items 081-100)
    # =========================================================

    # --- easy (items 081-087, 2 in test: 081-082) ---
    {
        "item_id": "UC8_081", "sector": "Financial", "difficulty": "easy", "split": "test",
        "company_name": "Meridian Capital Bank", "period": "Q2 2025",
        "financial_data": {
            "net_interest_income_m": 842.0, "net_interest_margin_pct": 3.42,
            "non_interest_income_m": 284.0, "total_revenue_m": 1126.0,
            "revenue_growth_yoy_pct": 9.8, "provision_for_credit_losses_m": 112.6,
            "operating_income_m": 450.4, "operating_margin_pct": 40.0,
            "net_income_m": 348.0, "eps": 5.80,
            "roa_pct": 1.18, "roe_pct": 14.2,
            "npl_ratio_pct": 0.82, "cet1_capital_ratio_pct": 13.4,
            "loan_growth_yoy_pct": 8.2, "deposit_growth_yoy_pct": 6.8,
            "efficiency_ratio_pct": 52.4, "free_cash_flow_m": 412.0
        },
        "gold_criteria": "Revenue $1.126B up 9.8%|NII $842M NIM 3.42%|Non-interest income $284M|Provision $112.6M|Operating income $450.4M 40% margin|ROA 1.18% ROE 14.2%|NPL ratio 0.82% healthy|CET1 13.4% well-capitalised|Loans +8.2% deposits +6.8%|Efficiency ratio 52.4%"
    },
    {
        "item_id": "UC8_082", "sector": "Financial", "difficulty": "easy", "split": "test",
        "company_name": "Harborne Asset Management", "period": "Q1 2025",
        "financial_data": {
            "aum_b": 284.0, "aum_growth_yoy_pct": 18.4,
            "net_flows_b": 12.4, "market_appreciation_b": 31.2,
            "management_fee_revenue_m": 568.0, "revenue_growth_yoy_pct": 16.8,
            "operating_income_m": 227.2, "operating_margin_pct": 40.0,
            "net_income_m": 181.8, "eps": 9.09,
            "avg_fee_rate_bps": 42, "equity_pct_aum": 64,
            "fixed_income_pct_aum": 28, "alternatives_pct_aum": 8,
            "free_cash_flow_m": 198.0
        },
        "gold_criteria": "AUM $284B up 18.4%|Net flows $12.4B market appreciation $31.2B|Revenue $568M up 16.8%|Operating income $227.2M 40% margin|Net income $181.8M|Avg fee 42bps|Equity 64% fixed income 28% alternatives 8%|FCF $198M"
    },
    {
        "item_id": "UC8_083", "sector": "Financial", "difficulty": "easy", "split": "train",
        "company_name": "Axon Regional Bank", "period": "Q3 2025",
        "financial_data": {
            "net_interest_income_m": 412.0, "net_interest_margin_pct": 3.28,
            "total_revenue_m": 548.0, "revenue_growth_yoy_pct": 7.4,
            "net_income_m": 162.0, "eps": 2.70,
            "roa_pct": 1.12, "roe_pct": 12.8, "cet1_capital_ratio_pct": 12.9,
            "loan_growth_yoy_pct": 7.0, "efficiency_ratio_pct": 54.2
        },
        "gold_criteria": "Revenue $548M up 7.4%|NII $412M NIM 3.28%|Net income $162M|ROA 1.12% ROE 12.8%|CET1 12.9%|Loans +7%|Efficiency 54.2%"
    },
    {
        "item_id": "UC8_084", "sector": "Financial", "difficulty": "easy", "split": "train",
        "company_name": "Prism Insurance Group", "period": "Q2 2024",
        "financial_data": {
            "premium_revenue_m": 3420.0, "premium_growth_pct": 11.2,
            "combined_ratio_pct": 91.4, "underwriting_income_m": 294.0,
            "investment_income_m": 184.0, "net_income_m": 352.0, "eps": 17.60,
            "loss_ratio_pct": 62.8, "expense_ratio_pct": 28.6,
            "return_on_equity_pct": 15.4
        },
        "gold_criteria": "Premium $3.42B up 11.2%|Combined ratio 91.4% profitable|Loss ratio 62.8% expense ratio 28.6%|Underwriting income $294M|Investment income $184M|Net income $352M|ROE 15.4%"
    },
    {
        "item_id": "UC8_085", "sector": "Financial", "difficulty": "easy", "split": "train",
        "company_name": "Clarity Wealth Management", "period": "Q4 2024",
        "financial_data": {
            "aum_b": 128.0, "aum_growth_yoy_pct": 14.8,
            "net_flows_b": 6.4, "revenue_m": 256.0, "revenue_growth_pct": 13.2,
            "operating_income_m": 102.4, "operating_margin_pct": 40.0,
            "net_income_m": 81.9, "eps": 4.10
        },
        "gold_criteria": "AUM $128B up 14.8%|Net flows $6.4B|Revenue $256M up 13.2%|Operating income $102.4M 40% margin|Net income $81.9M"
    },
    {
        "item_id": "UC8_086", "sector": "Financial", "difficulty": "easy", "split": "train",
        "company_name": "Westgate Savings Bank", "period": "Q1 2024",
        "financial_data": {
            "net_interest_income_m": 284.0, "net_interest_margin_pct": 3.15,
            "total_revenue_m": 368.0, "revenue_growth_yoy_pct": 6.8,
            "net_income_m": 110.4, "eps": 1.84,
            "roa_pct": 1.08, "roe_pct": 11.6, "cet1_capital_ratio_pct": 12.4,
            "loan_growth_yoy_pct": 6.2, "efficiency_ratio_pct": 56.8
        },
        "gold_criteria": "Revenue $368M up 6.8%|NII $284M NIM 3.15%|Net income $110.4M|ROA 1.08% ROE 11.6%|CET1 12.4%|Loans +6.2%|Efficiency 56.8%"
    },
    {
        "item_id": "UC8_087", "sector": "Financial", "difficulty": "easy", "split": "train",
        "company_name": "Northland Insurance Co", "period": "Q3 2024",
        "financial_data": {
            "premium_revenue_m": 1840.0, "premium_growth_pct": 9.4,
            "combined_ratio_pct": 93.2, "net_income_m": 184.0, "eps": 9.20,
            "loss_ratio_pct": 64.8, "expense_ratio_pct": 28.4, "roe_pct": 13.4
        },
        "gold_criteria": "Premium $1.84B up 9.4%|Combined ratio 93.2% profitable|Loss ratio 64.8% expense 28.4%|Net income $184M|ROE 13.4%"
    },

    # --- medium (items 088-094, 2 in test: 088-089) ---
    {
        "item_id": "UC8_088", "sector": "Financial", "difficulty": "medium", "split": "test",
        "company_name": "Oaktree Commercial Bank", "period": "Q3 2025",
        "financial_data": {
            "net_interest_income_m": 1124.0, "net_interest_margin_pct": 2.84,
            "nim_prev_year_pct": 3.41,
            "non_interest_income_m": 384.0, "total_revenue_m": 1508.0,
            "revenue_growth_yoy_pct": 2.4,
            "provision_for_credit_losses_m": 302.0, "provision_prev_year_m": 148.0,
            "net_income_m": 420.0, "eps": 7.00,
            "npl_ratio_pct": 2.14, "cet1_capital_ratio_pct": 12.1,
            "cre_exposure_pct_tier1": 284,
            "office_cre_npl_pct": 8.4,
            "deposit_beta_pct": 62,
            "free_cash_flow_m": 387.0,
            "note": "NIM compressed 57bps from peak due to deposit repricing; provisions doubled YoY; office CRE NPL ratio at 8.4% -- elevated; commercial real estate exposure at 284% of Tier 1 capital above regulatory comfort threshold"
        },
        "gold_criteria": "Revenue $1.508B up 2.4% weak growth|NII $1.124B NIM 2.84% down from 3.41%|Provision $302M doubled from $148M -- credit quality deterioration|Office CRE NPL 8.4% elevated|CRE exposure 284% Tier 1 above threshold|CET1 12.1% manageable|Deposit beta 62%|Net income $420M|FCF $387M|NIM compression and credit quality are key findings"
    },
    {
        "item_id": "UC8_089", "sector": "Financial", "difficulty": "medium", "split": "test",
        "company_name": "Meridian Investment Bank", "period": "Q2 2024",
        "financial_data": {
            "total_revenue_m": 2840.0, "revenue_growth_yoy_pct": 7.2,
            "advisory_revenue_m": 624.0, "advisory_growth_pct": -18.0,
            "ecm_revenue_m": 412.0, "ecm_growth_pct": 42.0,
            "dcm_revenue_m": 684.0, "dcm_growth_pct": 28.0,
            "trading_revenue_m": 980.0, "trading_growth_pct": 4.2,
            "operating_income_m": 568.0, "operating_margin_pct": 20.0,
            "net_income_m": 440.0, "eps": 22.00, "rote_pct": 12.8,
            "vwap_normalized_var_m": 84.0,
            "free_cash_flow_m": 512.0,
            "note": "Advisory down 18% on M&A drought; ECM up 42% as IPO market reopens; DCM strong on refinancing wave; trading steady"
        },
        "gold_criteria": "Revenue $2.84B up 7.2%|Advisory $624M down 18% M&A drought|ECM $412M up 42% IPO recovery|DCM $684M up 28% refinancing wave|Trading $980M up 4.2%|Operating income $568M 20% margin|ROTE 12.8%|Mix shift must be explained not just total revenue"
    },
    {
        "item_id": "UC8_090", "sector": "Financial", "difficulty": "medium", "split": "train",
        "company_name": "Beacon Fintech Corp", "period": "Q1 2025",
        "financial_data": {
            "revenue_m": 482.0, "revenue_growth_yoy_pct": 24.8,
            "gross_margin_pct": 58.4, "operating_income_m": 86.8,
            "operating_margin_pct": 18.0, "net_income_m": 67.5, "eps": 3.37,
            "payment_volume_b": 28.4, "payment_volume_growth_pct": 32.0,
            "take_rate_bps": 17, "user_growth_pct": 18.4,
            "chargeback_rate_pct": 0.08,
            "note": "Payment volume growing faster than revenue due to take rate compression from enterprise client negotiations"
        },
        "gold_criteria": "Revenue $482M up 24.8%|Payment volume $28.4B up 32% -- exceeds revenue growth|Take rate 17bps compression|Gross margin 58.4%|Operating income $86.8M 18% margin|Users +18.4%|Chargeback 0.08% low fraud|FCF implied"
    },
    {
        "item_id": "UC8_091", "sector": "Financial", "difficulty": "medium", "split": "train",
        "company_name": "Solent Insurance Group", "period": "Q3 2024",
        "financial_data": {
            "premium_revenue_m": 5840.0, "premium_growth_pct": 14.2,
            "combined_ratio_pct": 98.4, "underwriting_income_m": 93.4,
            "investment_income_m": 380.6, "net_income_m": 354.0, "eps": 17.70,
            "catastrophe_losses_m": 284.0, "cat_loss_impact_combined_pct": 4.9,
            "ex_cat_combined_ratio_pct": 93.5,
            "note": "Cat losses of $284M added 4.9pp to combined ratio; ex-cat combined ratio of 93.5% demonstrates underlying profitability"
        },
        "gold_criteria": "Premium $5.84B up 14.2%|Combined ratio 98.4% near 100%|Cat losses $284M 4.9pp impact|Ex-cat combined ratio 93.5% strong underlying|Underwriting income $93.4M|Investment income $380.6M|Net income $354M|Cat impact must be distinguished from underlying"
    },
    {
        "item_id": "UC8_092", "sector": "Financial", "difficulty": "medium", "split": "train",
        "company_name": "Stratus Capital Partners", "period": "Q2 2025",
        "financial_data": {
            "fee_revenue_m": 284.0, "fee_revenue_growth_pct": 18.2,
            "carried_interest_m": 148.0, "total_revenue_m": 432.0,
            "operating_income_m": 173.0, "operating_margin_pct": 40.0,
            "net_income_m": 138.4, "eps": 6.92,
            "aum_b": 42.4, "aum_growth_pct": 22.0,
            "dry_powder_b": 8.2, "deals_closed": 4,
            "realizations_m": 620.0
        },
        "gold_criteria": "Fee revenue $284M up 18.2% recurring|Carried interest $148M performance|Total revenue $432M|Operating income $173M 40% margin|AUM $42.4B up 22%|Dry powder $8.2B deployable|4 deals closed|Realisations $620M|Fee vs carry distinction important"
    },
    {
        "item_id": "UC8_093", "sector": "Financial", "difficulty": "medium", "split": "train",
        "company_name": "Aldgate Leasing Corp", "period": "Q4 2024",
        "financial_data": {
            "revenue_m": 684.0, "revenue_growth_yoy_pct": 9.1,
            "net_interest_margin_pct": 4.82, "operating_income_m": 154.0,
            "operating_margin_pct": 22.5, "net_income_m": 116.0, "eps": 5.80,
            "portfolio_size_b": 14.2, "delinquency_90plus_pct": 1.84,
            "net_charge_off_rate_pct": 0.64, "allowance_coverage_ratio_pct": 284,
            "note": "Delinquency rate elevated vs prior year 1.42%; management increased allowance coverage to 284%"
        },
        "gold_criteria": "Revenue $684M up 9.1%|NIM 4.82%|Operating income $154M 22.5% margin|Portfolio $14.2B|Delinquency 1.84% up from 1.42%|Net charge-off 0.64%|Allowance coverage 284% conservative|Credit quality trend important"
    },
    {
        "item_id": "UC8_094", "sector": "Financial", "difficulty": "medium", "split": "train",
        "company_name": "Pinnacle Exchange Corp", "period": "Q1 2024",
        "financial_data": {
            "trading_revenue_m": 284.0, "trading_revenue_growth_pct": 14.8,
            "data_revenue_m": 124.0, "data_revenue_growth_pct": 9.2,
            "total_revenue_m": 408.0, "revenue_growth_yoy_pct": 12.8,
            "operating_income_m": 204.0, "operating_margin_pct": 50.0,
            "net_income_m": 163.2, "eps": 8.16,
            "adv_contracts_m": 8.4, "adv_growth_pct": 12.1,
            "market_share_pct": 24.8, "free_cash_flow_m": 188.0
        },
        "gold_criteria": "Revenue $408M up 12.8%|Trading $284M up 14.8% data $124M up 9.2%|Operating income $204M 50% margin -- exchange economics|ADV 8.4M up 12.1%|Market share 24.8%|FCF $188M"
    },

    # --- hard (items 095-100, 2 in test: 095-096) ---
    {
        "item_id": "UC8_095", "sector": "Financial", "difficulty": "hard", "split": "test",
        "company_name": "Cormorant Bank plc", "period": "Q1 2025",
        "financial_data": {
            "net_interest_income_m": 2840.0, "net_interest_margin_pct": 1.84,
            "nim_prev_peak_pct": 2.42,
            "non_interest_income_m": 984.0, "total_revenue_m": 3824.0,
            "revenue_growth_yoy_pct": -4.2,
            "provision_for_credit_losses_m": 764.0, "provision_prev_year_m": 384.0,
            "net_income_m": 812.0, "eps": 40.60,
            "cet1_capital_ratio_pct": 13.8, "target_cet1_pct": 13.0,
            "npl_ratio_pct": 3.42, "stage_3_loans_pct": 4.18,
            "rote_pct": 9.8, "rote_target_pct": 12.0,
            "dividend_per_share": 1.82, "buyback_programme_m": 1200.0,
            "fca_investigation_provision_m": 280.0,
            "cost_of_risk_bps": 62, "free_cash_flow_m": 1420.0,
            "note": "NIM compressed 58bps from cycle peak; provisions nearly doubled on SME sector deterioration; FCA investigation provision $280M related to historical product sales practices; ROTE 9.8% below 12% target; $1.2B buyback programme announced offsetting negative sentiment; CET1 above target providing capital flexibility"
        },
        "gold_criteria": "Revenue $3.824B down 4.2%|NII $2.84B NIM 1.84% down 58bps from 2.42%|Provision $764M nearly doubled from $384M|FCA investigation $280M provision|NPL 3.42% Stage 3 4.18%|ROTE 9.8% below 12% target|CET1 13.8% above 13% target -- buffer|$1.2B buyback capital return|Dividend $1.82|FCF $1.42B|NIM compression credit deterioration FCA provision -- three compounding pressures must all be addressed"
    },
    {
        "item_id": "UC8_096", "sector": "Financial", "difficulty": "hard", "split": "test",
        "company_name": "Nexus Digital Bank", "period": "Q2 2025",
        "financial_data": {
            "revenue_m": 284.0, "revenue_growth_yoy_pct": 62.4,
            "net_interest_margin_pct": 6.84,
            "customer_deposits_b": 4.2, "deposit_growth_pct": 84.0,
            "loan_book_b": 2.8, "loan_growth_pct": 112.0,
            "net_income_m": -48.4, "eps": -2.42,
            "cet1_capital_ratio_pct": 14.8,
            "npl_ratio_pct": 1.84,
            "customer_acquisition_cost": 48,
            "monthly_active_users_m": 3.8, "mau_growth_pct": 94.0,
            "nps_score": 72,
            "cost_income_ratio_pct": 118,
            "free_cash_flow_m": -62.0,
            "note": "Digital challenger bank investing aggressively in growth; cost-income ratio of 118% as fixed cost base not yet leveraged against revenue; strong unit economics expected at scale (NIM 6.84% on unsecured personal lending, NPS 72); management targeting profitability at 5M MAU (currently 3.8M)"
        },
        "gold_criteria": "Revenue $284M up 62.4%|NIM 6.84% -- premium on personal lending|Deposits $4.2B up 84% loans $2.8B up 112%|Net loss -$48.4M|Cost-income 118% not yet leveraged|CET1 14.8% well-capitalised|MAU 3.8M up 94%|NPS 72 high|FCF -$62M|Profitability at 5M MAU 1.2M users away|Both growth potential and current losses required"
    },
    {
        "item_id": "UC8_097", "sector": "Financial", "difficulty": "hard", "split": "train",
        "company_name": "Fortis Bancorp", "period": "Q4 2025",
        "financial_data": {
            "total_revenue_m": 5840.0, "revenue_growth_yoy_pct": -8.4,
            "net_interest_income_m": 3840.0, "nim_pct": 2.14,
            "provision_m": 1168.0, "net_income_m": 812.0, "eps": 4.06,
            "cet1_pct": 11.4, "npl_pct": 4.82,
            "exposure_commercial_property_b": 84.0,
            "commercial_property_impairment_m": 420.0,
            "doj_settlement_m": 280.0,
            "free_cash_flow_m": 924.0,
            "note": "Commercial property impairment $420M on office portfolio; DOJ settlement $280M on historical lending practices; NIM under pressure; capital ratio above minimum but below peer median"
        },
        "gold_criteria": "Revenue $5.84B down 8.4%|NII $3.84B NIM 2.14%|Provision $1.168B elevated|$420M commercial property impairment|$280M DOJ settlement|NPL 4.82% elevated|CET1 11.4% above minimum but below peers|Net income $812M|FCF $924M"
    },
    {
        "item_id": "UC8_098", "sector": "Financial", "difficulty": "hard", "split": "train",
        "company_name": "Solaris Asset Management", "period": "Q3 2025",
        "financial_data": {
            "aum_b": 184.0, "aum_decline_pct": -12.8,
            "net_outflows_b": -18.4, "market_appreciation_b": 4.8,
            "revenue_m": 312.0, "revenue_decline_pct": -14.2,
            "operating_income_m": 87.4, "operating_margin_pct": 28.0,
            "net_income_m": 68.2, "eps": 3.41,
            "flagship_fund_performance_pct": -4.8,
            "benchmark_return_pct": 6.2,
            "redemption_notices_b": 8.4,
            "note": "Flagship fund down 4.8% vs benchmark +6.2%; net outflows of $18.4B driven by institutional redemptions; $8.4B in redemption notices for Q3 settlement"
        },
        "gold_criteria": "AUM $184B down 12.8%|Outflows $18.4B market appreciation $4.8B|Revenue $312M down 14.2%|Operating income $87.4M 28% margin|Flagship fund -4.8% vs benchmark +6.2% -- performance drag|$8.4B pending redemptions|Revenue and AUM decline context with performance underperformance as driver"
    },
    {
        "item_id": "UC8_099", "sector": "Financial", "difficulty": "hard", "split": "train",
        "company_name": "Pinnacle Reinsurance", "period": "Q2 2024",
        "financial_data": {
            "premium_revenue_m": 2840.0, "premium_growth_pct": 22.4,
            "combined_ratio_pct": 107.4, "underwriting_loss_m": -210.1,
            "investment_income_m": 284.0, "net_income_m": 52.4, "eps": 2.62,
            "catastrophe_losses_m": 684.0, "nat_cat_event": "North Atlantic hurricane season",
            "prior_year_reserve_release_m": 48.0,
            "rate_change_pct": 18.4,
            "note": "Hurricane season cat losses $684M driving combined above 100%; reserve release of $48M from prior years partially offsetting; rate hardening of 18.4% improving prospective economics; investment income provides earnings floor"
        },
        "gold_criteria": "Premium $2.84B up 22.4%|Combined ratio 107.4% -- underwriting loss|Cat losses $684M hurricane season|Prior year reserve release $48M|Underwriting loss -$210.1M|Investment income $284M provides floor|Net income $52.4M barely positive|Rate hardening 18.4% prospective improvement|Must distinguish cat impact from underlying rate cycle"
    },
    {
        "item_id": "UC8_100", "sector": "Financial", "difficulty": "hard", "split": "train",
        "company_name": "Vantage Crypto Exchange", "period": "Q1 2025",
        "financial_data": {
            "trading_revenue_m": 684.0, "trading_revenue_growth_pct": 184.0,
            "staking_revenue_m": 84.0, "other_revenue_m": 48.0,
            "total_revenue_m": 816.0, "total_growth_pct": 162.0,
            "operating_income_m": 326.4, "operating_margin_pct": 40.0,
            "net_income_m": 244.8, "eps": 12.24,
            "transaction_volume_b": 284.0, "volume_growth_pct": 224.0,
            "retail_volume_pct": 72, "institutional_volume_pct": 28,
            "take_rate_bps": 24, "take_rate_decline_bps": -6,
            "regulatory_reserve_requirement_m": 180.0,
            "note": "Revenue highly volatile -- correlates with crypto market cycles; Q1 2025 benefited from bull market conditions; trading volume growing faster than revenue due to take rate compression from institutional clients; regulatory reserve of $180M maintained for customer asset protection"
        },
        "gold_criteria": "Revenue $816M up 162%|Trading $684M up 184%|Operating income $326.4M 40% margin|Volume $284B up 224% -- exceeds revenue growth|Take rate 24bps down 6bps institutional compression|Staking $84M|Regulatory reserve $180M|Revenue volatility and crypto market cycle dependency essential -- not sustainable at this growth rate without cycle context"
    },
]


def format_financial_data(fd: dict, sector: str) -> str:
    """Format financial data block for model prompt based on sector."""
    lines = []
    for key, value in fd.items():
        if key == "note":
            continue  # note is analyst context, not given to model
        label = key.replace("_", " ").replace(" pct", " (%)").replace(" m", " ($M)").replace(" b", " ($B)")
        label = label.title()
        if isinstance(value, float):
            lines.append(f"  {label}: {value:,.1f}")
        elif isinstance(value, int):
            lines.append(f"  {label}: {value:,}")
        else:
            lines.append(f"  {label}: {value}")
    return "\n".join(lines)


def build_prompt(item: dict) -> str:
    """Build the full prompt text for a given item."""
    fd = json.loads(item["financial_data_json"])
    financial_block = format_financial_data(fd, item["sector"])
    prompt = (
        f"You are a financial analyst preparing a quarterly earnings summary for internal reporting.\n\n"
        f"Based on the quarterly financial data below, write a professional financial performance summary "
        f"(2-3 paragraphs) suitable for inclusion in an earnings report. Your summary should:\n"
        f"  1. Report revenue performance with year-over-year context\n"
        f"  2. Address profitability (gross margin, operating income, net income where available)\n"
        f"  3. Highlight key business drivers, segment performance, or notable items\n"
        f"  4. Maintain a neutral, professional financial reporting tone\n\n"
        f"Do not add information not present in the data. Report figures accurately.\n\n"
        f"Company  : {item['company_name']}\n"
        f"Period   : {item['period']}\n"
        f"Sector   : {item['sector']}\n\n"
        f"Financial Data:\n"
        f"{financial_block}\n\n"
        f"Write the financial performance summary now:"
    )
    return prompt


def main():
    output_dir = "data/gold_sets"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "uc8_financial_report_drafting.csv")

    fieldnames = [
        "item_id", "sector", "difficulty", "split",
        "company_name", "period",
        "financial_data_json", "prompt_text", "gold_criteria"
    ]

    rows = []
    for raw in RAW_ITEMS:
        fd_json = json.dumps(raw["financial_data"])
        row = {
            "item_id": raw["item_id"],
            "sector": raw["sector"],
            "difficulty": raw["difficulty"],
            "split": raw["split"],
            "company_name": raw["company_name"],
            "period": raw["period"],
            "financial_data_json": fd_json,
            "gold_criteria": raw["gold_criteria"],
        }
        # Build prompt (temporarily store fd_json in row before prompt build)
        row["financial_data_json"] = fd_json
        row["prompt_text"] = build_prompt(row)
        rows.append(row)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Verification report
    total = len(rows)
    train = sum(1 for r in rows if r["split"] == "train")
    test  = sum(1 for r in rows if r["split"] == "test")
    print("=" * 68)
    print("  UC8 Gold Set Builder — Financial Report Drafting")
    print(f"  Pre-registered : 2026-03-11  |  S3 Score: 3.80  |  Tier: Hybrid")
    print("=" * 68)
    print(f"  Total items     : {total}")
    print(f"  Train split     : {train}")
    print(f"  Test split      : {test}")
    print()
    print("  Distribution by sector:")
    sectors = {}
    for r in rows:
        sectors.setdefault(r["sector"], {"easy": 0, "medium": 0, "hard": 0, "train": 0, "test": 0})
        sectors[r["sector"]][r["difficulty"]] += 1
        sectors[r["sector"]][r["split"]] += 1
    for sector, counts in sorted(sectors.items()):
        print(f"    {sector:<14} easy={counts['easy']:2d}  medium={counts['medium']:2d}  "
              f"hard={counts['hard']:2d}  train={counts['train']:2d}  test={counts['test']:2d}")
    print()
    test_items = [r for r in rows if r["split"] == "test"]
    print("  Test items by sector x difficulty:")
    for sector in sorted(sectors.keys()):
        for diff in ["easy", "medium", "hard"]:
            n = sum(1 for r in test_items if r["sector"] == sector and r["difficulty"] == diff)
            print(f"    {sector:<14} {diff:<8} : {n}")
    print()
    print(f"  Output file: {output_path}")
    print("=" * 68)
    print("  GOLD SET LOCKED. Do not modify after this point.")
    print(f"  Lock timestamp: {datetime.now().isoformat()}")
    print("=" * 68)


if __name__ == "__main__":
    main()