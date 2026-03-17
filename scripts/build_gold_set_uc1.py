"""
build_gold_set_uc1.py
Builds the pre-registered 100-item gold set for UC1: SMS Threat Detection
Saves to: data/gold_sets/uc1_sms_threat_detection.csv

Gold set structure:
  70 THREAT messages across 5 threat categories
  30 BENIGN messages across 3 benign categories
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
OUTPUT_FILE = "uc1_sms_threat_detection.csv"
META_FILE   = "uc1_metadata.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Gold set items ─────────────────────────────────────────────
# Columns: id, text, label, category, subcategory, difficulty, source, notes
# difficulty: easy / medium / hard
# source: synthetic / uci_augmented
# ──────────────────────────────────────────────────────────────

GOLD_SET = [

    # ══════════════════════════════════════════════════════════
    # THREAT — Category T1: Phishing / Credential Theft (20 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC1_001", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "easy",
        "text": "URGENT: Your bank account has been suspended. Verify your details immediately at secure-bank-login.com or lose access.",
        "source": "synthetic",
        "notes": "Classic phishing — urgency + fake URL"
    },
    {
        "id": "UC1_002", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "easy",
        "text": "Your Netflix account will be cancelled. Update payment at netflix-billing-update.net within 24 hours.",
        "source": "synthetic",
        "notes": "Service suspension phishing"
    },
    {
        "id": "UC1_003", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "medium",
        "text": "Apple ID: Unusual sign-in detected. Confirm your identity: apple-id-verify.support/login",
        "source": "synthetic",
        "notes": "Brand impersonation — Apple"
    },
    {
        "id": "UC1_004", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "medium",
        "text": "Your PayPal account shows suspicious activity. Click here to secure it: paypal-secure-alert.com",
        "source": "synthetic",
        "notes": "PayPal impersonation"
    },
    {
        "id": "UC1_005", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "hard",
        "text": "Hi, I noticed you applied for a loan with us. Please confirm your SSN to process your application: loans-verify.net",
        "source": "synthetic",
        "notes": "Conversational phishing — harder to detect"
    },
    {
        "id": "UC1_006", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "easy",
        "text": "CHASE BANK ALERT: Card ending 4821 blocked. Unblock now: chase-card-restore.com",
        "source": "synthetic",
        "notes": "Bank brand impersonation"
    },
    {
        "id": "UC1_007", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "medium",
        "text": "Google Account: Someone accessed your account from Russia. Secure it now at google-account-protect.net",
        "source": "synthetic",
        "notes": "Google impersonation with fear trigger"
    },
    {
        "id": "UC1_008", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "hard",
        "text": "Your recent order has a delivery issue. Confirm your address and card details to reroute: delivery-confirm.co",
        "source": "synthetic",
        "notes": "Package delivery phishing — very common pattern"
    },
    {
        "id": "UC1_009", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "medium",
        "text": "Microsoft: Your Office 365 subscription expired. Renew immediately to avoid data loss: ms365-renew.net",
        "source": "synthetic",
        "notes": "Enterprise software phishing"
    },
    {
        "id": "UC1_010", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "hard",
        "text": "Hi Sarah, this is Lisa from HR. We need to verify your direct deposit info. Please click: hr-portal-update.com",
        "source": "synthetic",
        "notes": "Spear phishing — personalised HR context"
    },
    {
        "id": "UC1_011", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "easy",
        "text": "IRS NOTICE: You owe $2,847 in unpaid taxes. Pay immediately or face arrest: irs-payment-portal.net",
        "source": "synthetic",
        "notes": "Government impersonation + arrest threat"
    },
    {
        "id": "UC1_012", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "medium",
        "text": "Amazon: We could not verify your payment for your recent order. Update now: amazon-payment-help.com",
        "source": "uci_augmented",
        "notes": "Amazon impersonation — high volume pattern"
    },
    {
        "id": "UC1_013", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "hard",
        "text": "Your Venmo payment of $250 to John failed. Verify your account to retry: venmo-verify.com",
        "source": "synthetic",
        "notes": "P2P payment phishing"
    },
    {
        "id": "UC1_014", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "medium",
        "text": "USPS: Your package 9400111899223397319671 could not be delivered. Schedule redelivery: usps-redeliver.net",
        "source": "synthetic",
        "notes": "USPS impersonation with fake tracking number"
    },
    {
        "id": "UC1_015", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "hard",
        "text": "Your health insurance claim was denied. Appeal within 48hrs by verifying at: insurance-appeal-portal.co",
        "source": "synthetic",
        "notes": "Healthcare phishing — high stakes context"
    },
    {
        "id": "UC1_016", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "easy",
        "text": "WARNING: Your email password expires today. Click to keep access: emailsecure-update.com/reset",
        "source": "synthetic",
        "notes": "Email credential phishing"
    },
    {
        "id": "UC1_017", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "medium",
        "text": "Coinbase Alert: Withdrawal of 0.5 BTC initiated. If not you, cancel at coinbase-alert.net immediately.",
        "source": "synthetic",
        "notes": "Crypto exchange phishing — financial urgency"
    },
    {
        "id": "UC1_018", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "hard",
        "text": "Your student loan forgiveness application is pending. Complete verification at studentloan-gov.net",
        "source": "synthetic",
        "notes": "Government benefit phishing — targets students"
    },
    {
        "id": "UC1_019", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "medium",
        "text": "SECURITY ALERT: New device logged into your account. Not you? Secure now: account-protect-now.com",
        "source": "synthetic",
        "notes": "Generic security alert phishing"
    },
    {
        "id": "UC1_020", "label": "THREAT",
        "category": "T1_Phishing", "subcategory": "Credential Theft",
        "difficulty": "hard",
        "text": "Congratulations! Your mortgage pre-approval is ready. Complete your application: mortgage-approve-now.net",
        "source": "synthetic",
        "notes": "Financial product phishing — positive framing"
    },

    # ══════════════════════════════════════════════════════════
    # THREAT — Category T2: Financial Fraud / Fake Prizes (15 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC1_021", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Fake Prize",
        "difficulty": "easy",
        "text": "Congratulations! You've won $5,000 in our weekly draw. Claim your prize at winner-claim.com within 24 hours!",
        "source": "uci_augmented",
        "notes": "Classic prize scam"
    },
    {
        "id": "UC1_022", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Advance Fee",
        "difficulty": "easy",
        "text": "You have a pending inheritance of $2.4M from a relative in Nigeria. Contact agent James at +1-555-0192.",
        "source": "uci_augmented",
        "notes": "Advance fee fraud — Nigerian prince variant"
    },
    {
        "id": "UC1_023", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Fake Prize",
        "difficulty": "medium",
        "text": "Your mobile number won the Walmart Customer Appreciation Award of $500. Collect: walmart-rewards.net",
        "source": "synthetic",
        "notes": "Retail brand fake prize"
    },
    {
        "id": "UC1_024", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Investment Scam",
        "difficulty": "hard",
        "text": "Bitcoin investment opportunity: guaranteed 300% returns in 7 days. Join 10,000 investors: crypto-invest-pro.com",
        "source": "synthetic",
        "notes": "Crypto investment fraud"
    },
    {
        "id": "UC1_025", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Fake Prize",
        "difficulty": "medium",
        "text": "FREE iPhone 16 Pro! You were selected as today's lucky winner. Claim before midnight: free-iphone-win.com",
        "source": "synthetic",
        "notes": "Consumer electronics prize scam"
    },
    {
        "id": "UC1_026", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Advance Fee",
        "difficulty": "medium",
        "text": "Your tax refund of $3,219 is ready. Pay a $25 processing fee to release funds: taxrefund-claim.net",
        "source": "synthetic",
        "notes": "Advance fee disguised as tax refund"
    },
    {
        "id": "UC1_027", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Investment Scam",
        "difficulty": "hard",
        "text": "Hi, my name is Jennifer. I made $47,000 last month trading forex. I can show you how: fx-trading-mentor.com",
        "source": "synthetic",
        "notes": "Pig butchering scam — conversational opener"
    },
    {
        "id": "UC1_028", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Fake Prize",
        "difficulty": "easy",
        "text": "You are the 1,000,000th visitor! Claim your $1,000 Amazon gift card now: amazongiftcard-claim.com",
        "source": "uci_augmented",
        "notes": "Milestone visitor prize scam"
    },
    {
        "id": "UC1_029", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Loan Scam",
        "difficulty": "medium",
        "text": "Bad credit? Approved! Get $5,000 cash today. No check required. Pay $75 insurance: easyloans-now.net",
        "source": "synthetic",
        "notes": "Advance fee loan scam"
    },
    {
        "id": "UC1_030", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Fake Prize",
        "difficulty": "hard",
        "text": "Your survey response qualified you for $750. To receive payment, verify your bank details: survey-payout.co",
        "source": "synthetic",
        "notes": "Survey reward scam — plausible framing"
    },
    {
        "id": "UC1_031", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Investment Scam",
        "difficulty": "hard",
        "text": "Our AI trading bot made 847% returns last quarter. Minimum investment $200. Join now: ai-trading-returns.com",
        "source": "synthetic",
        "notes": "AI trading scam — topical 2025-2026 pattern"
    },
    {
        "id": "UC1_032", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Fake Prize",
        "difficulty": "medium",
        "text": "Sprint Wireless: You have an unclaimed bill credit of $147.50. Claim at sprint-credit-claim.com",
        "source": "synthetic",
        "notes": "Telecom credit fraud"
    },
    {
        "id": "UC1_033", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Advance Fee",
        "difficulty": "medium",
        "text": "COVID-19 relief fund: You qualify for $1,400 government payment. Claim at covid-relief-fund.net",
        "source": "synthetic",
        "notes": "Government benefit fraud — COVID context"
    },
    {
        "id": "UC1_034", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Fake Prize",
        "difficulty": "easy",
        "text": "WINNER! Your number was drawn in our lottery. Prize: $10,000. Call +1-800-555-0147 to claim.",
        "source": "uci_augmented",
        "notes": "Phone lottery scam"
    },
    {
        "id": "UC1_035", "label": "THREAT",
        "category": "T2_Financial_Fraud", "subcategory": "Loan Scam",
        "difficulty": "hard",
        "text": "We reviewed your profile and pre-qualified you for a $15,000 personal loan at 2.9% APR. Apply: fastcash-loans.net",
        "source": "synthetic",
        "notes": "Fake pre-qualification — hard to distinguish from legitimate"
    },

    # ══════════════════════════════════════════════════════════
    # THREAT — Category T3: Account Takeover / OTP Abuse (15 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC1_036", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "OTP Abuse",
        "difficulty": "easy",
        "text": "Your verification code is 847291. NEVER share this code. If you did not request this, call us immediately.",
        "source": "synthetic",
        "notes": "Unsolicited OTP — attacker triggered login"
    },
    {
        "id": "UC1_037", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "OTP Request",
        "difficulty": "medium",
        "text": "Hi, I accidentally sent money to your account. Can you send it back? Also can you share the OTP you just received?",
        "source": "synthetic",
        "notes": "Social engineering OTP extraction"
    },
    {
        "id": "UC1_038", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "OTP Abuse",
        "difficulty": "hard",
        "text": "Your bank sent a one-time code to verify a $0.01 deposit. Share the code with our agent to confirm your identity.",
        "source": "synthetic",
        "notes": "Fake micro-deposit OTP extraction"
    },
    {
        "id": "UC1_039", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "Password Reset Abuse",
        "difficulty": "medium",
        "text": "We received a request to reset your password. Your reset code is 392847. Share with our support team to verify.",
        "source": "synthetic",
        "notes": "Password reset code extraction"
    },
    {
        "id": "UC1_040", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "SIM Swap",
        "difficulty": "hard",
        "text": "ACTION REQUIRED: Confirm your SIM transfer request by replying YES. Your number will move to a new device.",
        "source": "synthetic",
        "notes": "SIM swap confirmation phishing"
    },
    {
        "id": "UC1_041", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "OTP Abuse",
        "difficulty": "medium",
        "text": "Facebook security: We noticed a login attempt. Your code is 719283. Enter at facebook.com/recover",
        "source": "synthetic",
        "notes": "Social media account takeover"
    },
    {
        "id": "UC1_042", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "OTP Request",
        "difficulty": "hard",
        "text": "This is customer service. We are processing your refund but need the 6-digit code we just sent you to verify.",
        "source": "synthetic",
        "notes": "Fake customer service OTP extraction"
    },
    {
        "id": "UC1_043", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "OTP Abuse",
        "difficulty": "easy",
        "text": "Your Google verification code is 492017. Do not share it. Someone is trying to access your account.",
        "source": "synthetic",
        "notes": "Google account takeover attempt — OTP triggered"
    },
    {
        "id": "UC1_044", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "Password Reset Abuse",
        "difficulty": "medium",
        "text": "Instagram: Your password was changed. If not you, click immediately: instagram-recover.net",
        "source": "synthetic",
        "notes": "Post-takeover notification with fake recovery link"
    },
    {
        "id": "UC1_045", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "OTP Request",
        "difficulty": "hard",
        "text": "Hi, this is your bank's fraud department. We blocked a suspicious transaction. Please confirm your identity with the code you received.",
        "source": "synthetic",
        "notes": "Vishing via SMS — fake fraud department"
    },
    {
        "id": "UC1_046", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "OTP Abuse",
        "difficulty": "medium",
        "text": "WhatsApp: Your registration code is 847-291. Do not share this code with anyone. WhatsApp will never ask for it.",
        "source": "synthetic",
        "notes": "WhatsApp account takeover OTP"
    },
    {
        "id": "UC1_047", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "SIM Swap",
        "difficulty": "hard",
        "text": "Your number port request is being processed. If you did not request this, call 611 immediately. Do not ignore.",
        "source": "synthetic",
        "notes": "Carrier SIM port notification — attacker initiated"
    },
    {
        "id": "UC1_048", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "OTP Request",
        "difficulty": "hard",
        "text": "Hey, I am sending you $200 via Cash App but it requires your one-time PIN to complete. What is the code?",
        "source": "synthetic",
        "notes": "P2P payment OTP social engineering"
    },
    {
        "id": "UC1_049", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "OTP Abuse",
        "difficulty": "easy",
        "text": "Roblox: Someone is trying to log in to your account. Your verification code is 581934.",
        "source": "synthetic",
        "notes": "Gaming account takeover — targets younger users"
    },
    {
        "id": "UC1_050", "label": "THREAT",
        "category": "T3_Account_Takeover", "subcategory": "Password Reset Abuse",
        "difficulty": "medium",
        "text": "Twitter/X: We received a password reset request. Reset link: twitter-password-reset.net (expires in 10 min)",
        "source": "synthetic",
        "notes": "Fake password reset with urgency"
    },

    # ══════════════════════════════════════════════════════════
    # THREAT — Category T4: Malware / Malicious Links (10 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC1_051", "label": "THREAT",
        "category": "T4_Malware", "subcategory": "Malicious Link",
        "difficulty": "easy",
        "text": "You have 3 unread voicemails. Listen at: bit.ly/voicemail-listen-now",
        "source": "uci_augmented",
        "notes": "Fake voicemail malware delivery"
    },
    {
        "id": "UC1_052", "label": "THREAT",
        "category": "T4_Malware", "subcategory": "Fake App",
        "difficulty": "medium",
        "text": "Your phone has 4 viruses! Install our free security app to remove them now: phone-cleaner-free.apk",
        "source": "synthetic",
        "notes": "Fake antivirus — malware delivery"
    },
    {
        "id": "UC1_053", "label": "THREAT",
        "category": "T4_Malware", "subcategory": "Malicious Link",
        "difficulty": "hard",
        "text": "Your friend tagged you in a photo. View it here: photo-tag-viewer.com/id=48291",
        "source": "synthetic",
        "notes": "Social media malware — fake photo tag"
    },
    {
        "id": "UC1_054", "label": "THREAT",
        "category": "T4_Malware", "subcategory": "Malicious Link",
        "difficulty": "medium",
        "text": "BREAKING: Leaked celebrity video. Watch before it's removed: leaked-vid-2026.net/watch",
        "source": "synthetic",
        "notes": "Sensational content malware delivery"
    },
    {
        "id": "UC1_055", "label": "THREAT",
        "category": "T4_Malware", "subcategory": "Fake Update",
        "difficulty": "hard",
        "text": "WhatsApp update required to continue using the service. Download now: whatsapp-update-2026.com",
        "source": "synthetic",
        "notes": "Fake app update — malware delivery"
    },
    {
        "id": "UC1_056", "label": "THREAT",
        "category": "T4_Malware", "subcategory": "Malicious Link",
        "difficulty": "easy",
        "text": "Your device has been compromised. Emergency scan: tinyurl.com/device-scan-now",
        "source": "synthetic",
        "notes": "Fear-based malware delivery"
    },
    {
        "id": "UC1_057", "label": "THREAT",
        "category": "T4_Malware", "subcategory": "Fake App",
        "difficulty": "medium",
        "text": "New government contact tracing app required by law. Download: health-tracing-app.gov-update.com",
        "source": "synthetic",
        "notes": "Government impersonation malware"
    },
    {
        "id": "UC1_058", "label": "THREAT",
        "category": "T4_Malware", "subcategory": "Malicious Link",
        "difficulty": "hard",
        "text": "Hi! I found some old photos of us from college. You'll love these: shared-memories-2008.net",
        "source": "synthetic",
        "notes": "Personalised social engineering malware link"
    },
    {
        "id": "UC1_059", "label": "THREAT",
        "category": "T4_Malware", "subcategory": "Fake Update",
        "difficulty": "medium",
        "text": "iOS 19.2 security patch available. Critical update — install now to prevent data theft: ios-patch.apple-update.net",
        "source": "synthetic",
        "notes": "Fake iOS update — Apple impersonation"
    },
    {
        "id": "UC1_060", "label": "THREAT",
        "category": "T4_Malware", "subcategory": "Malicious Link",
        "difficulty": "hard",
        "text": "Your e-statement is ready. View your account summary: ebank-statement-viewer.com/ref=TX8291",
        "source": "synthetic",
        "notes": "Banking malware — legitimate-looking link"
    },

    # ══════════════════════════════════════════════════════════
    # THREAT — Category T5: Social Engineering (10 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC1_061", "label": "THREAT",
        "category": "T5_Social_Engineering", "subcategory": "Grandparent Scam",
        "difficulty": "hard",
        "text": "Grandma it's me! I got arrested and need bail money $2,000. Please send via Western Union. Don't tell mom.",
        "source": "synthetic",
        "notes": "Grandparent scam — emotional manipulation"
    },
    {
        "id": "UC1_062", "label": "THREAT",
        "category": "T5_Social_Engineering", "subcategory": "Romance Scam",
        "difficulty": "hard",
        "text": "Hey, I found your number online. I'm a US soldier stationed overseas. Would love to get to know you.",
        "source": "synthetic",
        "notes": "Romance scam opener"
    },
    {
        "id": "UC1_063", "label": "THREAT",
        "category": "T5_Social_Engineering", "subcategory": "Impersonation",
        "difficulty": "medium",
        "text": "This is your electric company. Your service will be disconnected in 2 hours unless you pay $187 by gift card.",
        "source": "uci_augmented",
        "notes": "Utility cutoff scam — gift card payment"
    },
    {
        "id": "UC1_064", "label": "THREAT",
        "category": "T5_Social_Engineering", "subcategory": "Impersonation",
        "difficulty": "medium",
        "text": "FBI WARNING: Your IP was linked to illegal activity. Pay $500 fine to avoid arrest: fbi-fine-portal.com",
        "source": "synthetic",
        "notes": "Law enforcement impersonation"
    },
    {
        "id": "UC1_065", "label": "THREAT",
        "category": "T5_Social_Engineering", "subcategory": "Job Scam",
        "difficulty": "hard",
        "text": "Work from home opportunity! Earn $500/day. No experience needed. Start today: remote-jobs-now.net",
        "source": "synthetic",
        "notes": "Job scam — money mule recruitment"
    },
    {
        "id": "UC1_066", "label": "THREAT",
        "category": "T5_Social_Engineering", "subcategory": "Impersonation",
        "difficulty": "hard",
        "text": "This is your boss. I'm in a meeting and need you to buy 5 Google Play gift cards $100 each urgently. I'll explain later.",
        "source": "synthetic",
        "notes": "CEO fraud via SMS — gift card request"
    },
    {
        "id": "UC1_067", "label": "THREAT",
        "category": "T5_Social_Engineering", "subcategory": "Grandparent Scam",
        "difficulty": "hard",
        "text": "Mom, I broke my phone and this is a friend's number. I need $300 for an emergency. Can you Cash App me?",
        "source": "synthetic",
        "notes": "Family impersonation emergency scam"
    },
    {
        "id": "UC1_068", "label": "THREAT",
        "category": "T5_Social_Engineering", "subcategory": "Romance Scam",
        "difficulty": "hard",
        "text": "I know this is sudden but I've developed feelings for you. I need $800 for a flight to come visit you.",
        "source": "synthetic",
        "notes": "Romance scam — money request stage"
    },
    {
        "id": "UC1_069", "label": "THREAT",
        "category": "T5_Social_Engineering", "subcategory": "Job Scam",
        "difficulty": "medium",
        "text": "Congratulations! Your resume was reviewed and you qualify for a $28/hr data entry job. Apply: jobs-remote-entry.com",
        "source": "synthetic",
        "notes": "Fake job offer — data theft or money mule"
    },
    {
        "id": "UC1_070", "label": "THREAT",
        "category": "T5_Social_Engineering", "subcategory": "Impersonation",
        "difficulty": "medium",
        "text": "Social Security Administration: Your SSN has been suspended due to suspicious activity. Call 1-800-555-0183 immediately.",
        "source": "synthetic",
        "notes": "SSA impersonation — phone-based continuation"
    },

    # ══════════════════════════════════════════════════════════
    # BENIGN — Category B1: Legitimate Bank / Financial (10 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC1_071", "label": "BENIGN",
        "category": "B1_Legitimate_Bank", "subcategory": "Transaction Alert",
        "difficulty": "medium",
        "text": "Chase: $52.34 debit at WHOLE FOODS MARKET on 03/02. Available balance: $1,847.22. Questions? chase.com",
        "source": "synthetic",
        "notes": "Legitimate bank transaction alert — real domain"
    },
    {
        "id": "UC1_072", "label": "BENIGN",
        "category": "B1_Legitimate_Bank", "subcategory": "OTP Legitimate",
        "difficulty": "hard",
        "text": "Your Bank of America sign-in code is 847291. Valid for 10 minutes. Never share this code.",
        "source": "synthetic",
        "notes": "Legitimate OTP — user initiated login"
    },
    {
        "id": "UC1_073", "label": "BENIGN",
        "category": "B1_Legitimate_Bank", "subcategory": "Service Alert",
        "difficulty": "easy",
        "text": "Wells Fargo: Your account statement is ready to view at wellsfargo.com. No action required.",
        "source": "synthetic",
        "notes": "Legitimate statement notification"
    },
    {
        "id": "UC1_074", "label": "BENIGN",
        "category": "B1_Legitimate_Bank", "subcategory": "Transaction Alert",
        "difficulty": "medium",
        "text": "AMEX: Large purchase alert. $1,200.00 at BEST BUY #0482. Not you? Call 1-800-528-4800.",
        "source": "synthetic",
        "notes": "Legitimate large purchase alert with real phone number"
    },
    {
        "id": "UC1_075", "label": "BENIGN",
        "category": "B1_Legitimate_Bank", "subcategory": "Service Alert",
        "difficulty": "easy",
        "text": "Your Citibank credit card payment of $450 is due on March 15. Pay at citi.com to avoid late fees.",
        "source": "synthetic",
        "notes": "Legitimate payment reminder"
    },
    {
        "id": "UC1_076", "label": "BENIGN",
        "category": "B1_Legitimate_Bank", "subcategory": "Low Balance",
        "difficulty": "medium",
        "text": "TD Bank: Your checking account balance is $47.18, below your $100 alert threshold. Transfer funds at tdbank.com.",
        "source": "synthetic",
        "notes": "User-configured low balance alert"
    },
    {
        "id": "UC1_077", "label": "BENIGN",
        "category": "B1_Legitimate_Bank", "subcategory": "Transaction Alert",
        "difficulty": "hard",
        "text": "Zelle payment of $150 from Mom received. Funds available in your bank account. Questions? Call your bank.",
        "source": "synthetic",
        "notes": "Legitimate P2P payment received — hard because Zelle is used in scams too"
    },
    {
        "id": "UC1_078", "label": "BENIGN",
        "category": "B1_Legitimate_Bank", "subcategory": "OTP Legitimate",
        "difficulty": "hard",
        "text": "Use code 291847 to authorize your wire transfer. Valid 5 min. Call 800-432-1000 if you did not request this.",
        "source": "synthetic",
        "notes": "Legitimate wire transfer OTP with real contact number"
    },
    {
        "id": "UC1_079", "label": "BENIGN",
        "category": "B1_Legitimate_Bank", "subcategory": "Service Alert",
        "difficulty": "easy",
        "text": "Capital One: Your new card ending in 4821 has been activated. Start using it today. capitalone.com",
        "source": "synthetic",
        "notes": "Legitimate card activation confirmation"
    },
    {
        "id": "UC1_080", "label": "BENIGN",
        "category": "B1_Legitimate_Bank", "subcategory": "Transaction Alert",
        "difficulty": "medium",
        "text": "PayPal: You sent $75.00 to john.smith@email.com. Transaction ID: 3TY82910K. View at paypal.com/activity.",
        "source": "synthetic",
        "notes": "Legitimate PayPal transaction confirmation"
    },

    # ══════════════════════════════════════════════════════════
    # BENIGN — Category B2: Normal Personal Messages (10 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC1_081", "label": "BENIGN",
        "category": "B2_Personal", "subcategory": "Casual Conversation",
        "difficulty": "easy",
        "text": "Hey! Are you coming to dinner tonight? We're meeting at 7pm at Mario's. Let me know!",
        "source": "synthetic",
        "notes": "Normal personal message"
    },
    {
        "id": "UC1_082", "label": "BENIGN",
        "category": "B2_Personal", "subcategory": "Appointment",
        "difficulty": "easy",
        "text": "Dr. Johnson's office reminder: Your appointment is tomorrow March 3 at 2:30pm. Reply CONFIRM or call 555-0147.",
        "source": "synthetic",
        "notes": "Legitimate medical appointment reminder"
    },
    {
        "id": "UC1_083", "label": "BENIGN",
        "category": "B2_Personal", "subcategory": "Casual Conversation",
        "difficulty": "easy",
        "text": "Can you pick up milk on the way home? Also we're out of coffee. Thanks!",
        "source": "synthetic",
        "notes": "Everyday personal message"
    },
    {
        "id": "UC1_084", "label": "BENIGN",
        "category": "B2_Personal", "subcategory": "Delivery",
        "difficulty": "medium",
        "text": "Your Amazon order #112-8472910-2934781 has shipped. Estimated delivery: March 4. Track at amazon.com/orders",
        "source": "synthetic",
        "notes": "Legitimate Amazon shipping notification"
    },
    {
        "id": "UC1_085", "label": "BENIGN",
        "category": "B2_Personal", "subcategory": "Casual Conversation",
        "difficulty": "easy",
        "text": "Happy birthday! Hope you have an amazing day. Let's celebrate this weekend!",
        "source": "synthetic",
        "notes": "Birthday message"
    },
    {
        "id": "UC1_086", "label": "BENIGN",
        "category": "B2_Personal", "subcategory": "Appointment",
        "difficulty": "easy",
        "text": "Haircut reminder: Your appointment with Jake is Thursday at 4pm. Reply CANCEL to reschedule.",
        "source": "synthetic",
        "notes": "Legitimate salon appointment"
    },
    {
        "id": "UC1_087", "label": "BENIGN",
        "category": "B2_Personal", "subcategory": "Delivery",
        "difficulty": "medium",
        "text": "USPS: Your package will be delivered today by 8pm. USPS Tracking: 9400111899223397319671. usps.com",
        "source": "synthetic",
        "notes": "Legitimate USPS delivery — note real domain"
    },
    {
        "id": "UC1_088", "label": "BENIGN",
        "category": "B2_Personal", "subcategory": "Casual Conversation",
        "difficulty": "easy",
        "text": "Meeting moved to 3pm tomorrow. Same room. Let everyone know. Thanks",
        "source": "synthetic",
        "notes": "Work message — schedule change"
    },
    {
        "id": "UC1_089", "label": "BENIGN",
        "category": "B2_Personal", "subcategory": "Appointment",
        "difficulty": "easy",
        "text": "Your car service is complete. Total: $287.50. You can pick up anytime during business hours. -Mike's Auto",
        "source": "synthetic",
        "notes": "Legitimate auto service completion"
    },
    {
        "id": "UC1_090", "label": "BENIGN",
        "category": "B2_Personal", "subcategory": "Delivery",
        "difficulty": "medium",
        "text": "FedEx: Delivery attempted at 2:14pm. Package held at FedEx location at 123 Main St. Redeliver: fedex.com",
        "source": "synthetic",
        "notes": "Legitimate FedEx missed delivery — note real domain"
    },

    # ══════════════════════════════════════════════════════════
    # BENIGN — Category B3: Legitimate Promotional (10 items)
    # ══════════════════════════════════════════════════════════
    {
        "id": "UC1_091", "label": "BENIGN",
        "category": "B3_Legitimate_Promo", "subcategory": "Retail Offer",
        "difficulty": "medium",
        "text": "Target: Save 20% this weekend! Use code SAVE20 at checkout. Shop at target.com. Reply STOP to opt out.",
        "source": "synthetic",
        "notes": "Legitimate retail promotion with opt-out"
    },
    {
        "id": "UC1_092", "label": "BENIGN",
        "category": "B3_Legitimate_Promo", "subcategory": "Loyalty Program",
        "difficulty": "medium",
        "text": "Starbucks Rewards: You earned 25 stars on your last visit! You now have 180 stars. starbucks.com/rewards",
        "source": "synthetic",
        "notes": "Legitimate loyalty program update"
    },
    {
        "id": "UC1_093", "label": "BENIGN",
        "category": "B3_Legitimate_Promo", "subcategory": "Retail Offer",
        "difficulty": "hard",
        "text": "Flash sale! 50% off all shoes for the next 2 hours. Shop now: nike.com/sale. Reply STOP to unsubscribe.",
        "source": "synthetic",
        "notes": "Hard: legitimate urgent promo resembles scam pattern"
    },
    {
        "id": "UC1_094", "label": "BENIGN",
        "category": "B3_Legitimate_Promo", "subcategory": "Service Update",
        "difficulty": "easy",
        "text": "Netflix: Your payment of $15.49 was processed. Thank you for being a member. netflix.com/account",
        "source": "synthetic",
        "notes": "Legitimate subscription confirmation"
    },
    {
        "id": "UC1_095", "label": "BENIGN",
        "category": "B3_Legitimate_Promo", "subcategory": "Loyalty Program",
        "difficulty": "medium",
        "text": "Delta SkyMiles: You earned 1,247 miles on your recent flight. Total balance: 23,891. delta.com/skymiles",
        "source": "synthetic",
        "notes": "Legitimate airline miles update"
    },
    {
        "id": "UC1_096", "label": "BENIGN",
        "category": "B3_Legitimate_Promo", "subcategory": "Retail Offer",
        "difficulty": "medium",
        "text": "Walmart: Your grocery pickup order is ready! Come to the pickup area. Order #WM-48291. walmart.com",
        "source": "synthetic",
        "notes": "Legitimate grocery pickup notification"
    },
    {
        "id": "UC1_097", "label": "BENIGN",
        "category": "B3_Legitimate_Promo", "subcategory": "Service Update",
        "difficulty": "easy",
        "text": "Spotify: Your Premium plan renews on March 15 for $10.99. Manage at spotify.com/account. Reply STOP to cancel.",
        "source": "synthetic",
        "notes": "Legitimate subscription renewal reminder"
    },
    {
        "id": "UC1_098", "label": "BENIGN",
        "category": "B3_Legitimate_Promo", "subcategory": "Loyalty Program",
        "difficulty": "hard",
        "text": "Congratulations! You've reached Gold status with us. Your exclusive benefits are now active. Sign in to view.",
        "source": "synthetic",
        "notes": "Hard: no URL or brand — ambiguous but no threat indicators"
    },
    {
        "id": "UC1_099", "label": "BENIGN",
        "category": "B3_Legitimate_Promo", "subcategory": "Service Update",
        "difficulty": "easy",
        "text": "T-Mobile: Your AutoPay of $85 is scheduled for March 10. View your bill at t-mobile.com/account.",
        "source": "synthetic",
        "notes": "Legitimate carrier billing reminder"
    },
    {
        "id": "UC1_100", "label": "BENIGN",
        "category": "B3_Legitimate_Promo", "subcategory": "Retail Offer",
        "difficulty": "medium",
        "text": "CVS Pharmacy: Your prescription is ready for pickup. Questions? Call 555-0182. CVS.com/pharmacy",
        "source": "synthetic",
        "notes": "Legitimate pharmacy prescription ready"
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

    # Assign 70/30 train/test split preserving category balance
    # Within each label group: first 70% train, last 30% test
    threat_items = [x for x in GOLD_SET if x["label"] == "THREAT"]
    benign_items = [x for x in GOLD_SET if x["label"] == "BENIGN"]

    # THREAT: 49 train, 21 test
    for i, item in enumerate(threat_items):
        item["split"] = "train" if i < 49 else "test"

    # BENIGN: 21 train, 9 test
    for i, item in enumerate(benign_items):
        item["split"] = "train" if i < 21 else "test"

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(GOLD_SET)

    return filepath


def build_metadata():
    """Write metadata JSON for paper appendix reference."""
    threat_items = [x for x in GOLD_SET if x["label"] == "THREAT"]
    benign_items = [x for x in GOLD_SET if x["label"] == "BENIGN"]

    meta = {
        "use_case": "UC1",
        "name": "SMS Threat Detection",
        "pre_registration_date": "2026-03-02",
        "version": "1.0",
        "total_items": len(GOLD_SET),
        "label_distribution": {
            "THREAT": len(threat_items),
            "BENIGN": len(benign_items),
        },
        "threat_categories": {
            "T1_Phishing": len([x for x in GOLD_SET if x["category"] == "T1_Phishing"]),
            "T2_Financial_Fraud": len([x for x in GOLD_SET if x["category"] == "T2_Financial_Fraud"]),
            "T3_Account_Takeover": len([x for x in GOLD_SET if x["category"] == "T3_Account_Takeover"]),
            "T4_Malware": len([x for x in GOLD_SET if x["category"] == "T4_Malware"]),
            "T5_Social_Engineering": len([x for x in GOLD_SET if x["category"] == "T5_Social_Engineering"]),
        },
        "benign_categories": {
            "B1_Legitimate_Bank": len([x for x in GOLD_SET if x["category"] == "B1_Legitimate_Bank"]),
            "B2_Personal": len([x for x in GOLD_SET if x["category"] == "B2_Personal"]),
            "B3_Legitimate_Promo": len([x for x in GOLD_SET if x["category"] == "B3_Legitimate_Promo"]),
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
        "evaluation_metrics": [
            "Exact Match Rate",
            "F1 Score",
            "Precision",
            "Recall",
            "Latency P50/P95 (ms)",
            "Cost Per Successful Task (CPS)",
            "Hallucination Rate"
        ],
        "pre_registered_hypotheses": [
            "H1.1: SLMs achieve >= 90% of LLM accuracy on binary SMS classification",
            "H1.2: SLM P95 latency < 1000ms cloud, < 15000ms local",
            "H1.3: SLM CPS <= 15% of LLM CPS at equivalent accuracy",
            "H1.4: UC1 will NOT graduate to Pure SLM (Stakes=4 requires LLM fallback)"
        ]
    }

    meta_path = os.path.join(OUTPUT_DIR, META_FILE)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return meta_path


def print_summary():
    """Print verification summary to confirm gold set is correct."""
    threat_items = [x for x in GOLD_SET if x["label"] == "THREAT"]
    benign_items = [x for x in GOLD_SET if x["label"] == "BENIGN"]

    print()
    print("=" * 62)
    print("  UC1 GOLD SET — Build Complete")
    print("  SMS Threat Detection — Pre-Registration v1.0")
    print("=" * 62)
    print()
    print(f"  Total items  : {len(GOLD_SET)}")
    print(f"  THREAT       : {len(threat_items)} items (70%)")
    print(f"  BENIGN       : {len(benign_items)} items (30%)")
    print()
    print("  THREAT breakdown:")
    for cat, label in [
        ("T1_Phishing",          "Phishing / Credential Theft"),
        ("T2_Financial_Fraud",   "Financial Fraud / Fake Prizes"),
        ("T3_Account_Takeover",  "Account Takeover / OTP Abuse"),
        ("T4_Malware",           "Malware / Malicious Links"),
        ("T5_Social_Engineering","Social Engineering"),
    ]:
        n = len([x for x in GOLD_SET if x["category"] == cat])
        print(f"    {label:<35} {n} items")

    print()
    print("  BENIGN breakdown:")
    for cat, label in [
        ("B1_Legitimate_Bank",  "Legitimate Bank / Financial"),
        ("B2_Personal",         "Normal Personal Messages"),
        ("B3_Legitimate_Promo", "Legitimate Promotional"),
    ]:
        n = len([x for x in GOLD_SET if x["category"] == cat])
        print(f"    {label:<35} {n} items")

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
    print("  Files saved:")
    print(f"    data/gold_sets/{OUTPUT_FILE}")
    print(f"    data/gold_sets/{META_FILE}")
    print()
    print("  ✅  Gold set locked — DO NOT MODIFY after this point")
    print("      This is your pre-registered ground truth.")
    print()
    print("  NEXT STEP:")
    print("  → python3 scripts/run_benchmark_uc1.py")
    print("  → Runs all 7 models against UC1 test set (30 items × 7 models × 3 runs)")
    print("=" * 62)
    print()


if __name__ == "__main__":
    print()
    print("Building UC1 Gold Set — SMS Threat Detection...")
    csv_path  = build_csv()
    meta_path = build_metadata()
    print_summary()