"""
build_gold_set_uc3.py
Builds the pre-registered 100-item gold set for UC3: Support Ticket Routing
Saves to: data/gold_sets/uc3_support_ticket_routing.csv
          data/gold_sets/uc3_metadata.json

Gold set structure:
  100 support tickets across 6 routing categories
  BILLING / TECHNICAL / ACCOUNT / SHIPPING / RETURNS / GENERAL
  17 items each for BILLING, TECHNICAL, ACCOUNT, SHIPPING
  16 items each for RETURNS, GENERAL
  Train/test split: 70 train / 30 test (5 per category in test)

S³ Dimension Scores (pre-registered 2026-03-02):
  Task Complexity     (w=1.0) = 2  → Simple intent classification
  Output Structure    (w=0.8) = 3  → Single label from 6 fixed categories
  Stakes              (w=1.2) = 2  → Misrouting delays response, easily correctable
  Data Sensitivity    (w=0.8) = 2  → Standard business customer data
  Latency Requirement (w=1.0) = 3  → Near-real-time preferred, not millisecond-critical
  Volume              (w=0.6) = 5  → Enterprise: thousands of tickets daily

  Weighted sum = 2(1.0)+3(0.8)+2(1.2)+2(0.8)+3(1.0)+5(0.6) = 14.4
  S³ = 14.4 / 27.0 × 5 = 2.67  →  Pure SLM predicted

PRE-REGISTRATION DATE: March 2, 2026
DO NOT MODIFY after benchmark execution begins.
"""

import csv
import os
import json

OUTPUT_DIR  = "data/gold_sets"
OUTPUT_FILE = "uc3_support_ticket_routing.csv"
META_FILE   = "uc3_metadata.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────
# GOLD SET — 100 items
# Columns: id, text, label, category, subcategory, difficulty, source, notes
# Last 5 items of each category block = test split
# ─────────────────────────────────────────────────────────────────

GOLD_SET = [

    # ══════════════════════════════════════════════════════════
    # BILLING — 17 items (UC3_001 – UC3_017)
    # Test items: UC3_013 – UC3_017
    # ══════════════════════════════════════════════════════════

    {
        "id": "UC3_001", "label": "BILLING",
        "category": "BILLING", "subcategory": "Overcharge",
        "difficulty": "easy",
        "text": "I was charged twice for the same order. Please refund the duplicate charge.",
        "source": "synthetic",
        "notes": "Clear double-charge complaint — strong billing signal"
    },
    {
        "id": "UC3_002", "label": "BILLING",
        "category": "BILLING", "subcategory": "Invoice",
        "difficulty": "easy",
        "text": "My invoice shows the wrong tax amount. The rate applied does not match my state.",
        "source": "synthetic",
        "notes": "Invoice error — clear billing keyword"
    },
    {
        "id": "UC3_003", "label": "BILLING",
        "category": "BILLING", "subcategory": "Invoice",
        "difficulty": "easy",
        "text": "I need a copy of last month's invoice for my expense report.",
        "source": "synthetic",
        "notes": "Invoice request — unambiguous"
    },
    {
        "id": "UC3_004", "label": "BILLING",
        "category": "BILLING", "subcategory": "Subscription",
        "difficulty": "medium",
        "text": "I upgraded my plan two weeks ago but I am still being charged the old price.",
        "source": "synthetic",
        "notes": "Plan upgrade billing issue — medium, mentions plan change"
    },
    {
        "id": "UC3_005", "label": "BILLING",
        "category": "BILLING", "subcategory": "Subscription",
        "difficulty": "medium",
        "text": "I cancelled my subscription last month but was still charged this billing cycle.",
        "source": "synthetic",
        "notes": "Post-cancellation charge — subscription keyword present"
    },
    {
        "id": "UC3_006", "label": "BILLING",
        "category": "BILLING", "subcategory": "Discount",
        "difficulty": "medium",
        "text": "The discount code I applied at checkout did not appear on my final invoice.",
        "source": "synthetic",
        "notes": "Discount not reflected — billing + discount keywords"
    },
    {
        "id": "UC3_007", "label": "BILLING",
        "category": "BILLING", "subcategory": "Subscription",
        "difficulty": "medium",
        "text": "I signed up for monthly billing but I was charged the full annual price upfront.",
        "source": "synthetic",
        "notes": "Billing cycle mismatch — clear billing intent"
    },
    {
        "id": "UC3_008", "label": "BILLING",
        "category": "BILLING", "subcategory": "Payment_Method",
        "difficulty": "medium",
        "text": "I need to update my credit card before the next billing cycle on the 15th.",
        "source": "synthetic",
        "notes": "Payment method update — medium, could seem like ACCOUNT"
    },
    {
        "id": "UC3_009", "label": "BILLING",
        "category": "BILLING", "subcategory": "Invoice",
        "difficulty": "easy",
        "text": "My company needs an official receipt with our tax ID number for reimbursement purposes.",
        "source": "synthetic",
        "notes": "Receipt/invoice request — clear billing need"
    },
    {
        "id": "UC3_010", "label": "BILLING",
        "category": "BILLING", "subcategory": "Subscription",
        "difficulty": "medium",
        "text": "I would like to switch from monthly to annual billing to take advantage of the discount.",
        "source": "synthetic",
        "notes": "Billing frequency change — subscription + billing keywords"
    },
    {
        "id": "UC3_011", "label": "BILLING",
        "category": "BILLING", "subcategory": "Invoice",
        "difficulty": "easy",
        "text": "The invoice I received has the wrong company name and address. It needs to be corrected.",
        "source": "synthetic",
        "notes": "Invoice correction — clear billing"
    },
    {
        "id": "UC3_012", "label": "BILLING",
        "category": "BILLING", "subcategory": "Overcharge",
        "difficulty": "easy",
        "text": "I was overcharged for an item that was marked as on sale on your website.",
        "source": "synthetic",
        "notes": "Overcharge on sale item — clear billing"
    },
    # ── BILLING TEST ITEMS (013–017) ───────────────────────────
    {
        "id": "UC3_013", "label": "BILLING",
        "category": "BILLING", "subcategory": "Overcharge",
        "difficulty": "easy",
        "text": "I see an unrecognized charge of $29.99 on my account this month.",
        "source": "synthetic",
        "notes": "TEST — unrecognized charge — clear billing signal"
    },
    {
        "id": "UC3_014", "label": "BILLING",
        "category": "BILLING", "subcategory": "Payment_Method",
        "difficulty": "easy",
        "text": "I need to set up automatic payments so I never miss my monthly due date.",
        "source": "synthetic",
        "notes": "TEST — auto-pay setup — easy billing"
    },
    {
        "id": "UC3_015", "label": "BILLING",
        "category": "BILLING", "subcategory": "Discount",
        "difficulty": "medium",
        "text": "The promotional coupon I received by email is not being accepted at checkout.",
        "source": "synthetic",
        "notes": "TEST — coupon not working — medium, discount + checkout"
    },
    {
        "id": "UC3_016", "label": "BILLING",
        "category": "BILLING", "subcategory": "Payment_Method",
        "difficulty": "medium",
        "text": "My payment failed but the charge still appears on my bank statement.",
        "source": "synthetic",
        "notes": "TEST — payment failure with bank charge — medium billing"
    },
    {
        "id": "UC3_017", "label": "BILLING",
        "category": "BILLING", "subcategory": "Subscription",
        "difficulty": "hard",
        "text": "I upgraded mid-month. How is the prorated charge calculated and when will I see it?",
        "source": "synthetic",
        "notes": "TEST — prorated billing inquiry — hard, requires billing domain knowledge"
    },

    # ══════════════════════════════════════════════════════════
    # TECHNICAL — 17 items (UC3_018 – UC3_034)
    # Test items: UC3_030 – UC3_034
    # ══════════════════════════════════════════════════════════

    {
        "id": "UC3_018", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "App_Crash",
        "difficulty": "easy",
        "text": "The app crashes every time I try to upload a file larger than 10MB.",
        "source": "synthetic",
        "notes": "App crash — clear technical bug"
    },
    {
        "id": "UC3_019", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Feature_Bug",
        "difficulty": "easy",
        "text": "The search function is returning no results even when I type exact matches.",
        "source": "synthetic",
        "notes": "Feature not working — clear technical"
    },
    {
        "id": "UC3_020", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Feature_Bug",
        "difficulty": "easy",
        "text": "My data export keeps failing. I get error code 500 every time I try.",
        "source": "synthetic",
        "notes": "Error code failure — clear technical"
    },
    {
        "id": "UC3_021", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Sync_Issue",
        "difficulty": "medium",
        "text": "The mobile app is not syncing properly with the desktop version. My changes are not showing up.",
        "source": "synthetic",
        "notes": "Sync failure — technical, medium complexity"
    },
    {
        "id": "UC3_022", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Feature_Bug",
        "difficulty": "medium",
        "text": "I am getting an SSL certificate error when I try to access the dashboard.",
        "source": "synthetic",
        "notes": "SSL error — technical, medium"
    },
    {
        "id": "UC3_023", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Feature_Bug",
        "difficulty": "easy",
        "text": "Videos will not play on my account. I just see a spinning loading icon.",
        "source": "synthetic",
        "notes": "Playback failure — clear technical"
    },
    {
        "id": "UC3_024", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Performance",
        "difficulty": "easy",
        "text": "The platform is running extremely slowly today. Every page takes over 30 seconds to load.",
        "source": "synthetic",
        "notes": "Performance issue — clear technical"
    },
    {
        "id": "UC3_025", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Feature_Bug",
        "difficulty": "medium",
        "text": "After installing your latest update, all my saved preferences and settings were reset.",
        "source": "synthetic",
        "notes": "Post-update data loss — technical, medium"
    },
    {
        "id": "UC3_026", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "App_Crash",
        "difficulty": "medium",
        "text": "I keep getting logged out of the app automatically every few minutes.",
        "source": "synthetic",
        "notes": "Auto-logout bug — medium, could seem like ACCOUNT but is a bug"
    },
    {
        "id": "UC3_027", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Feature_Bug",
        "difficulty": "medium",
        "text": "The PDF export is cutting off the last page of every document I try to download.",
        "source": "synthetic",
        "notes": "Export bug — clear technical"
    },
    {
        "id": "UC3_028", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Feature_Bug",
        "difficulty": "easy",
        "text": "The dashboard is not updating in real time. The data appears to be frozen.",
        "source": "synthetic",
        "notes": "Real-time update failure — clear technical"
    },
    {
        "id": "UC3_029", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Feature_Bug",
        "difficulty": "easy",
        "text": "Dark mode is broken. The text is invisible in several areas of the interface.",
        "source": "synthetic",
        "notes": "UI rendering bug — clear technical"
    },
    # ── TECHNICAL TEST ITEMS (030–034) ─────────────────────────
    {
        "id": "UC3_030", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Feature_Bug",
        "difficulty": "easy",
        "text": "The screen shows a blank white page for every member of my team since this morning.",
        "source": "synthetic",
        "notes": "TEST — blank screen bug — clear technical"
    },
    {
        "id": "UC3_031", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Feature_Bug",
        "difficulty": "easy",
        "text": "I keep getting a permission denied error when I try to open a shared folder.",
        "source": "synthetic",
        "notes": "TEST — permission error — easy technical, not ACCOUNT"
    },
    {
        "id": "UC3_032", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Integration",
        "difficulty": "medium",
        "text": "The integration with Slack stopped sending notifications yesterday after working fine for months.",
        "source": "synthetic",
        "notes": "TEST — integration failure — medium technical"
    },
    {
        "id": "UC3_033", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Feature_Bug",
        "difficulty": "medium",
        "text": "I am unable to install the software on Windows 11. The installer fails at the last step.",
        "source": "synthetic",
        "notes": "TEST — install failure — medium technical"
    },
    {
        "id": "UC3_034", "label": "TECHNICAL",
        "category": "TECHNICAL", "subcategory": "Integration",
        "difficulty": "hard",
        "text": "The API endpoint we rely on stopped returning data after your deployment last night.",
        "source": "synthetic",
        "notes": "TEST — API breakage — hard, developer-facing technical issue"
    },

    # ══════════════════════════════════════════════════════════
    # ACCOUNT — 17 items (UC3_035 – UC3_051)
    # Test items: UC3_047 – UC3_051
    # ══════════════════════════════════════════════════════════

    {
        "id": "UC3_035", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Password_Reset",
        "difficulty": "easy",
        "text": "I forgot my password and the password reset email is not arriving in my inbox.",
        "source": "synthetic",
        "notes": "Password reset — clear account"
    },
    {
        "id": "UC3_036", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Profile_Update",
        "difficulty": "easy",
        "text": "I need to update the email address on my account to a new one.",
        "source": "synthetic",
        "notes": "Email update — clear account"
    },
    {
        "id": "UC3_037", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Access_Control",
        "difficulty": "easy",
        "text": "My account has been locked after several failed login attempts. Please unlock it.",
        "source": "synthetic",
        "notes": "Account locked — clear account"
    },
    {
        "id": "UC3_038", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Team_Management",
        "difficulty": "medium",
        "text": "I need to add three new team members to my organization account.",
        "source": "synthetic",
        "notes": "Team member addition — account management"
    },
    {
        "id": "UC3_039", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Profile_Update",
        "difficulty": "medium",
        "text": "I would like to permanently delete my account and remove all my data.",
        "source": "synthetic",
        "notes": "Account deletion — clear account action"
    },
    {
        "id": "UC3_040", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Access_Control",
        "difficulty": "medium",
        "text": "My two-factor authentication is not working. I am not receiving the SMS verification codes.",
        "source": "synthetic",
        "notes": "2FA issue — account security"
    },
    {
        "id": "UC3_041", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Profile_Update",
        "difficulty": "medium",
        "text": "I need to update my company name and registered address on the account.",
        "source": "synthetic",
        "notes": "Account profile update — medium, has billing overlap"
    },
    {
        "id": "UC3_042", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Access_Control",
        "difficulty": "medium",
        "text": "I was removed from my team's workspace but I should still have access as an admin.",
        "source": "synthetic",
        "notes": "Permission/role issue — account management"
    },
    {
        "id": "UC3_043", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Profile_Update",
        "difficulty": "easy",
        "text": "The name on my account is misspelled. I need it corrected to match my legal name.",
        "source": "synthetic",
        "notes": "Name correction — clear account"
    },
    {
        "id": "UC3_044", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Profile_Update",
        "difficulty": "medium",
        "text": "I want to remove my saved payment details from the account for security reasons.",
        "source": "synthetic",
        "notes": "Remove payment from account — medium, billing/account overlap"
    },
    {
        "id": "UC3_045", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Profile_Update",
        "difficulty": "easy",
        "text": "My profile picture will not update. It keeps reverting to the old photo.",
        "source": "synthetic",
        "notes": "Profile picture — account settings"
    },
    {
        "id": "UC3_046", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Password_Reset",
        "difficulty": "easy",
        "text": "I need to reset my password because I suspect someone else accessed my account.",
        "source": "synthetic",
        "notes": "Security password reset — clear account"
    },
    # ── ACCOUNT TEST ITEMS (047–051) ───────────────────────────
    {
        "id": "UC3_047", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Access_Control",
        "difficulty": "easy",
        "text": "I cannot access my account. I think I may have used a different email address when I signed up.",
        "source": "synthetic",
        "notes": "TEST — account access issue — clear account"
    },
    {
        "id": "UC3_048", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Access_Control",
        "difficulty": "easy",
        "text": "I want to enable two-factor authentication on my account for added security.",
        "source": "synthetic",
        "notes": "TEST — 2FA setup — clear account security"
    },
    {
        "id": "UC3_049", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Profile_Update",
        "difficulty": "medium",
        "text": "I accidentally created two accounts using different email addresses. Can they be merged into one?",
        "source": "synthetic",
        "notes": "TEST — account merge — medium account management"
    },
    {
        "id": "UC3_050", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "SSO",
        "difficulty": "medium",
        "text": "I need to set up single sign-on for my organization so employees can log in with company credentials.",
        "source": "synthetic",
        "notes": "TEST — SSO setup — medium, enterprise account"
    },
    {
        "id": "UC3_051", "label": "ACCOUNT",
        "category": "ACCOUNT", "subcategory": "Team_Management",
        "difficulty": "hard",
        "text": "I am taking over a former employee's responsibilities and need ownership of their account transferred to me.",
        "source": "synthetic",
        "notes": "TEST — account ownership transfer — hard, requires careful account action"
    },

    # ══════════════════════════════════════════════════════════
    # SHIPPING — 17 items (UC3_052 – UC3_068)
    # Test items: UC3_064 – UC3_068
    # ══════════════════════════════════════════════════════════

    {
        "id": "UC3_052", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Delivery_Status",
        "difficulty": "easy",
        "text": "Where is my order? It is now three days past the expected delivery date.",
        "source": "synthetic",
        "notes": "Late delivery — clear shipping"
    },
    {
        "id": "UC3_053", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Address_Change",
        "difficulty": "easy",
        "text": "I need to change the delivery address for an order I placed this morning.",
        "source": "synthetic",
        "notes": "Address change — clear shipping"
    },
    {
        "id": "UC3_054", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Delivery_Status",
        "difficulty": "easy",
        "text": "The tracking number I received is not showing any results on the carrier website.",
        "source": "synthetic",
        "notes": "Tracking not working — clear shipping"
    },
    {
        "id": "UC3_055", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Delivery_Status",
        "difficulty": "medium",
        "text": "Is it possible to upgrade to expedited shipping on an order I placed yesterday?",
        "source": "synthetic",
        "notes": "Shipping upgrade request — medium"
    },
    {
        "id": "UC3_056", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Missing_Package",
        "difficulty": "medium",
        "text": "My order was split into two shipments but I have only received one of them so far.",
        "source": "synthetic",
        "notes": "Partial shipment — clear shipping"
    },
    {
        "id": "UC3_057", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Carrier_Issue",
        "difficulty": "medium",
        "text": "I received someone else's package. My order seems to have been delivered to a different address.",
        "source": "synthetic",
        "notes": "Wrong delivery — shipping issue"
    },
    {
        "id": "UC3_058", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Carrier_Issue",
        "difficulty": "easy",
        "text": "The courier attempted delivery but I was not home. How do I reschedule the delivery?",
        "source": "synthetic",
        "notes": "Missed delivery — clear shipping"
    },
    {
        "id": "UC3_059", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Delivery_Status",
        "difficulty": "medium",
        "text": "My tracking shows the package has been in transit for 10 days with no new updates.",
        "source": "synthetic",
        "notes": "Stalled tracking — shipping"
    },
    {
        "id": "UC3_060", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Carrier_Issue",
        "difficulty": "medium",
        "text": "I would prefer to collect my order from a local pickup location instead of home delivery.",
        "source": "synthetic",
        "notes": "Pickup request — shipping logistics"
    },
    {
        "id": "UC3_061", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Carrier_Issue",
        "difficulty": "medium",
        "text": "Can I add a signature-required instruction to my upcoming delivery?",
        "source": "synthetic",
        "notes": "Delivery instruction — shipping"
    },
    {
        "id": "UC3_062", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Delivery_Status",
        "difficulty": "easy",
        "text": "I need an official proof-of-delivery document for my company's records.",
        "source": "synthetic",
        "notes": "Delivery confirmation — clear shipping"
    },
    {
        "id": "UC3_063", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Carrier_Issue",
        "difficulty": "hard",
        "text": "My order tracking says it was returned to sender, but I never requested a return.",
        "source": "synthetic",
        "notes": "Unexpected return-to-sender — hard, shipping vs returns ambiguity"
    },
    # ── SHIPPING TEST ITEMS (064–068) ──────────────────────────
    {
        "id": "UC3_064", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Missing_Package",
        "difficulty": "easy",
        "text": "My package is marked as delivered but I never received it. No one left it at the door.",
        "source": "synthetic",
        "notes": "TEST — missing delivered package — clear shipping"
    },
    {
        "id": "UC3_065", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Delivery_Status",
        "difficulty": "easy",
        "text": "How many days does standard shipping usually take to the Pacific Northwest region?",
        "source": "synthetic",
        "notes": "TEST — shipping time inquiry — easy, could seem GENERAL but is shipping-specific"
    },
    {
        "id": "UC3_066", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Missing_Package",
        "difficulty": "medium",
        "text": "My order arrived but one of the items listed on the packing slip is missing from the box.",
        "source": "synthetic",
        "notes": "TEST — partial shipment / missing item — medium shipping"
    },
    {
        "id": "UC3_067", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Address_Change",
        "difficulty": "medium",
        "text": "I need to redirect my shipment to an international address. I originally selected domestic delivery.",
        "source": "synthetic",
        "notes": "TEST — international address change — medium shipping"
    },
    {
        "id": "UC3_068", "label": "SHIPPING",
        "category": "SHIPPING", "subcategory": "Missing_Package",
        "difficulty": "hard",
        "text": "The package arrived badly damaged and the product inside is broken. I need a replacement sent urgently.",
        "source": "synthetic",
        "notes": "TEST — damaged delivery — hard, shipping vs returns ambiguity"
    },

    # ══════════════════════════════════════════════════════════
    # RETURNS — 16 items (UC3_069 – UC3_084)
    # Test items: UC3_080 – UC3_084
    # ══════════════════════════════════════════════════════════

    {
        "id": "UC3_069", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Return_Request",
        "difficulty": "easy",
        "text": "I would like to return a product I purchased last week. It is not what I expected.",
        "source": "synthetic",
        "notes": "Basic return request — clear returns"
    },
    {
        "id": "UC3_070", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Return_Request",
        "difficulty": "easy",
        "text": "How do I start a return? The product does not meet my needs and I have not opened it.",
        "source": "synthetic",
        "notes": "Return process inquiry — clear returns"
    },
    {
        "id": "UC3_071", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Exchange",
        "difficulty": "easy",
        "text": "I received the wrong item in my order and would like to exchange it for the correct one.",
        "source": "synthetic",
        "notes": "Wrong item exchange — clear returns"
    },
    {
        "id": "UC3_072", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Defective_Item",
        "difficulty": "easy",
        "text": "The product I received stopped working after two days. I would like a replacement.",
        "source": "synthetic",
        "notes": "Defective product — returns"
    },
    {
        "id": "UC3_073", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Return_Request",
        "difficulty": "easy",
        "text": "Can you send me a prepaid return shipping label for my return?",
        "source": "synthetic",
        "notes": "Return label request — clear returns"
    },
    {
        "id": "UC3_074", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Return_Request",
        "difficulty": "medium",
        "text": "I opened the product before realizing it was the wrong model. Can I still return it?",
        "source": "synthetic",
        "notes": "Opened item return — medium returns"
    },
    {
        "id": "UC3_075", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Refund_Status",
        "difficulty": "medium",
        "text": "I returned the item but was given store credit instead of a refund to my original payment method.",
        "source": "synthetic",
        "notes": "Refund method dispute — returns"
    },
    {
        "id": "UC3_076", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Refund_Status",
        "difficulty": "medium",
        "text": "I returned my full order but the refund I received does not match the original amount paid.",
        "source": "synthetic",
        "notes": "Partial refund dispute — medium returns"
    },
    {
        "id": "UC3_077", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Refund_Status",
        "difficulty": "medium",
        "text": "The warehouse confirmed receiving my return three weeks ago but my refund has not been issued.",
        "source": "synthetic",
        "notes": "Delayed refund — clear returns"
    },
    {
        "id": "UC3_078", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Exchange",
        "difficulty": "easy",
        "text": "I would like to exchange the item I ordered for the same product in a different size.",
        "source": "synthetic",
        "notes": "Size exchange — clear returns"
    },
    {
        "id": "UC3_079", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Refund_Status",
        "difficulty": "medium",
        "text": "My replacement item has not been shipped yet, even though the original was returned two weeks ago.",
        "source": "synthetic",
        "notes": "Replacement not sent — returns follow-up"
    },
    # ── RETURNS TEST ITEMS (080–084) ───────────────────────────
    {
        "id": "UC3_080", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Refund_Status",
        "difficulty": "easy",
        "text": "My refund has not appeared after two weeks. The return was marked as received.",
        "source": "synthetic",
        "notes": "TEST — missing refund — easy returns"
    },
    {
        "id": "UC3_081", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Return_Request",
        "difficulty": "easy",
        "text": "I accidentally sent back the wrong item in my return package. Can you send it back to me?",
        "source": "synthetic",
        "notes": "TEST — wrong item returned — easy returns"
    },
    {
        "id": "UC3_082", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Return_Request",
        "difficulty": "medium",
        "text": "I am outside the standard 30-day return window. Is there any exception I can request?",
        "source": "synthetic",
        "notes": "TEST — late return request — medium returns"
    },
    {
        "id": "UC3_083", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Return_Request",
        "difficulty": "medium",
        "text": "I need to return several items from the same order but I would like to send them separately.",
        "source": "synthetic",
        "notes": "TEST — multi-item separate return — medium returns"
    },
    {
        "id": "UC3_084", "label": "RETURNS",
        "category": "RETURNS", "subcategory": "Return_Request",
        "difficulty": "hard",
        "text": "I purchased a digital download and the content was not as described. Can I get a refund?",
        "source": "synthetic",
        "notes": "TEST — digital product return — hard, policy-dependent edge case"
    },

    # ══════════════════════════════════════════════════════════
    # GENERAL — 16 items (UC3_085 – UC3_100)
    # Test items: UC3_096 – UC3_100
    # ══════════════════════════════════════════════════════════

    {
        "id": "UC3_085", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Pricing_Inquiry",
        "difficulty": "easy",
        "text": "Do you offer special pricing or discounts for registered nonprofits?",
        "source": "synthetic",
        "notes": "Nonprofit discount — general product/pricing question"
    },
    {
        "id": "UC3_086", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Product_Question",
        "difficulty": "easy",
        "text": "What are your customer support hours? I want to know when I can reach someone by phone.",
        "source": "synthetic",
        "notes": "Support hours — general info"
    },
    {
        "id": "UC3_087", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Product_Question",
        "difficulty": "easy",
        "text": "Do you have a mobile app available for Android? I could not find it in the Play Store.",
        "source": "synthetic",
        "notes": "Product availability — general"
    },
    {
        "id": "UC3_088", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Feedback",
        "difficulty": "medium",
        "text": "I have some feedback about the recent changes to your dashboard layout. Who should I send it to?",
        "source": "synthetic",
        "notes": "Feedback routing — general"
    },
    {
        "id": "UC3_089", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Pricing_Inquiry",
        "difficulty": "medium",
        "text": "Can you recommend the best plan for a team of around 10 people with mixed usage needs?",
        "source": "synthetic",
        "notes": "Plan recommendation — medium, could seem BILLING but is pre-purchase"
    },
    {
        "id": "UC3_090", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Pricing_Inquiry",
        "difficulty": "easy",
        "text": "Is there a free trial available before committing to a paid subscription?",
        "source": "synthetic",
        "notes": "Free trial inquiry — general"
    },
    {
        "id": "UC3_091", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Product_Question",
        "difficulty": "easy",
        "text": "What languages does your platform currently support for the user interface?",
        "source": "synthetic",
        "notes": "Language support — general product"
    },
    {
        "id": "UC3_092", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Product_Question",
        "difficulty": "medium",
        "text": "I read about your product in an article. Where can I learn more about what it does?",
        "source": "synthetic",
        "notes": "Prospect inquiry — general"
    },
    {
        "id": "UC3_093", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Product_Question",
        "difficulty": "medium",
        "text": "Do you offer any official training courses or certifications for using your platform?",
        "source": "synthetic",
        "notes": "Training inquiry — general"
    },
    {
        "id": "UC3_094", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Policy",
        "difficulty": "medium",
        "text": "What is your company's data retention policy? How long do you keep customer data?",
        "source": "synthetic",
        "notes": "Data policy question — general, not technical"
    },
    {
        "id": "UC3_095", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Pricing_Inquiry",
        "difficulty": "hard",
        "text": "I would like to speak with your enterprise sales team about a custom contract for our organization.",
        "source": "synthetic",
        "notes": "Enterprise sales — hard, general routing to sales"
    },
    # ── GENERAL TEST ITEMS (096–100) ───────────────────────────
    {
        "id": "UC3_096", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Pricing_Inquiry",
        "difficulty": "easy",
        "text": "Do you offer discounts for students or academic institutions?",
        "source": "synthetic",
        "notes": "TEST — student discount — easy general"
    },
    {
        "id": "UC3_097", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Pricing_Inquiry",
        "difficulty": "easy",
        "text": "I am thinking about upgrading. What additional features do I get on the premium tier?",
        "source": "synthetic",
        "notes": "TEST — feature comparison — easy general, pre-purchase inquiry not billing"
    },
    {
        "id": "UC3_098", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Integration_Inquiry",
        "difficulty": "medium",
        "text": "Does your platform integrate natively with Salesforce CRM?",
        "source": "synthetic",
        "notes": "TEST — integration inquiry — medium general, could seem TECHNICAL"
    },
    {
        "id": "UC3_099", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Integration_Inquiry",
        "difficulty": "hard",
        "text": "I am a developer and want to build on top of your platform. Where can I find the API documentation?",
        "source": "synthetic",
        "notes": "TEST — API docs request — hard, developer inquiry could route to TECHNICAL"
    },
    {
        "id": "UC3_100", "label": "GENERAL",
        "category": "GENERAL", "subcategory": "Feedback",
        "difficulty": "medium",
        "text": "I would like to submit a positive review of your service. Is there a specific place to do that?",
        "source": "synthetic",
        "notes": "TEST — review submission inquiry — medium general"
    },
]


def assign_splits():
    """Assign train/test split: last 5 items in each category = test."""
    # Group by category maintaining insertion order
    from collections import defaultdict
    cat_items = defaultdict(list)
    for item in GOLD_SET:
        cat_items[item["category"]].append(item)

    for category, items in cat_items.items():
        test_start = len(items) - 5
        for i, item in enumerate(items):
            item["split"] = "test" if i >= test_start else "train"


def build_csv():
    assign_splits()
    filepath = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    fieldnames = [
        "id", "text", "label", "category", "subcategory",
        "difficulty", "source", "notes", "split"
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(GOLD_SET)
    return filepath


def build_metadata():
    assign_splits()
    categories  = ["BILLING", "TECHNICAL", "ACCOUNT", "SHIPPING", "RETURNS", "GENERAL"]
    label_dist  = {c: sum(1 for x in GOLD_SET if x["label"] == c) for c in categories}
    diff_dist   = {d: sum(1 for x in GOLD_SET if x["difficulty"] == d)
                   for d in ["easy", "medium", "hard"]}
    test_items  = [x for x in GOLD_SET if x.get("split") == "test"]
    train_items = [x for x in GOLD_SET if x.get("split") == "train"]

    # S³ calculation
    scores  = {"TC": 2, "OS": 3, "SK": 2, "DS": 2, "LT": 3, "VL": 5}
    weights = {"TC": 1.0, "OS": 0.8, "SK": 1.2, "DS": 0.8, "LT": 1.0, "VL": 0.6}
    weighted_sum = sum(scores[d] * weights[d] for d in scores)
    s3_score = round(weighted_sum / 27.0 * 5, 2)

    meta = {
        "use_case": "UC3",
        "name": "Support Ticket Routing",
        "pre_registration_date": "2026-03-02",
        "version": "1.0",
        "s3_score": s3_score,
        "s3_prediction": "Pure SLM",
        "s3_dimensions": {
            "Task_Complexity":     {"score": scores["TC"], "weight": weights["TC"],
                                    "rationale": "Simple intent classification, well-defined categories"},
            "Output_Structure":    {"score": scores["OS"], "weight": weights["OS"],
                                    "rationale": "Single label from 6 fixed routing categories"},
            "Stakes":              {"score": scores["SK"], "weight": weights["SK"],
                                    "rationale": "Misrouting causes delay, easily correctable, no irreversible harm"},
            "Data_Sensitivity":    {"score": scores["DS"], "weight": weights["DS"],
                                    "rationale": "Standard customer data, no financial/health records"},
            "Latency_Requirement": {"score": scores["LT"], "weight": weights["LT"],
                                    "rationale": "Near-real-time preferred, not millisecond-critical"},
            "Volume":              {"score": scores["VL"], "weight": weights["VL"],
                                    "rationale": "Enterprise: thousands of support tickets daily"}
        },
        "s3_formula": {
            "weighted_sum": round(weighted_sum, 1),
            "denominator": 27.0,
            "formula": "S3 = weighted_sum / 27.0 * 5",
            "result": s3_score
        },
        "total_items": len(GOLD_SET),
        "label_distribution": label_dist,
        "routing_categories": categories,
        "difficulty_distribution": diff_dist,
        "split": {
            "train": len(train_items),
            "test": len(test_items)
        },
        "split_method": "last_5_per_category_as_test",
        "evaluation_metrics": [
            "Accuracy",
            "Macro F1",
            "Per-class F1 (all 6 categories)",
            "6x6 Confusion Matrix",
            "Hallucination Rate",
            "Latency P50/P95"
        ],
        "pre_registered_hypotheses": [
            "H3.1: Best SLM achieves >= 90% of LLM accuracy on UC3",
            "H3.2: Best SLM P95 latency < 2000ms",
            "H3.3: UC3 graduates to Pure SLM (S3=2.67, Stakes=2)",
            "H3.4: GENERAL category will have lowest per-class F1 (most semantically ambiguous)"
        ]
    }

    meta_path = os.path.join(OUTPUT_DIR, META_FILE)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return meta_path


def print_summary():
    assign_splits()
    categories  = ["BILLING", "TECHNICAL", "ACCOUNT", "SHIPPING", "RETURNS", "GENERAL"]
    test_items  = [x for x in GOLD_SET if x.get("split") == "test"]
    train_items = [x for x in GOLD_SET if x.get("split") == "train"]

    print()
    print("=" * 64)
    print("  UC3 GOLD SET — Build Complete")
    print("  Support Ticket Routing — Pre-Registration v1.0")
    print("=" * 64)
    print()
    print(f"  Total items  : {len(GOLD_SET)}")
    print(f"  Train / Test : {len(train_items)} / {len(test_items)}")
    print()
    print("  Category distribution:")
    for cat in categories:
        n        = sum(1 for x in GOLD_SET if x["label"] == cat)
        n_train  = sum(1 for x in GOLD_SET if x["label"] == cat and x.get("split") == "train")
        n_test   = sum(1 for x in GOLD_SET if x["label"] == cat and x.get("split") == "test")
        bar      = "█" * n
        print(f"    {cat:<12} {bar:<20} {n:>3} items  ({n_train} train / {n_test} test)")

    print()
    print("  Difficulty distribution:")
    for diff in ["easy", "medium", "hard"]:
        n   = sum(1 for x in GOLD_SET if x["difficulty"] == diff)
        bar = "█" * n
        print(f"    {diff:<8} {bar:<55} {n}")

    scores  = {"TC": 2, "OS": 3, "SK": 2, "DS": 2, "LT": 3, "VL": 5}
    weights = {"TC": 1.0, "OS": 0.8, "SK": 1.2, "DS": 0.8, "LT": 1.0, "VL": 0.6}
    weighted_sum = sum(scores[d] * weights[d] for d in scores)
    s3_score = round(weighted_sum / 27.0 * 5, 2)

    print()
    print(f"  S³ Score     : {s3_score}  (weighted sum = {weighted_sum} / 27.0 × 5)")
    print(f"  Prediction   : Pure SLM (≤ 3.2)")
    print()
    print("  Files saved:")
    print(f"    data/gold_sets/{OUTPUT_FILE}")
    print(f"    data/gold_sets/{META_FILE}")
    print()
    print("  ✅  Gold set locked — DO NOT MODIFY after this point")
    print()
    print("  NEXT STEP:")
    print("  → python3 scripts/run_benchmark_uc3.py")
    print("=" * 64)
    print()


if __name__ == "__main__":
    print()
    print("Building UC3 Gold Set — Support Ticket Routing...")
    build_csv()
    build_metadata()
    print_summary()