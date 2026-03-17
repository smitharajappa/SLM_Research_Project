"""
build_gold_set_uc6.py — UC6 Healthcare Clinical Triage
S³ Research Project | UT Dallas | March 2026

Pre-registered S³ Score: 4.4  →  LLM Only predicted

S³ Dimensions:
  Task Complexity (×1.0): 5  → Expert clinical reasoning: integrate vitals, symptoms, history
  Output Structure (×0.8): 4  → One of 4 defined triage labels, strict
  Stakes         (×1.2): 5  → Wrong triage = patient harm or death (irreversible)
  Data Sensitivity (×0.8): 5  → PHI — maximum regulation (HIPAA)
  Latency        (×1.0): 4  → Clinical decision support, minutes acceptable
  Volume         (×0.6): 3  → Tens of thousands/month at hospital level

Weighted sum = (5×1.0) + (4×0.8) + (5×1.2) + (5×0.8) + (4×1.0) + (3×0.6)
             = 5.0 + 3.2 + 6.0 + 4.0 + 4.0 + 1.8 = 24.0
S³ = 24.0 / 27.0 × 5 = 4.44  →  LLM Only predicted

Task: Given a triage note (chief complaint + vitals + brief history), assign one of:
  CRITICAL     — Immediate life threat, intervention in < 10 minutes
  URGENT       — Potentially life-threatening, care within 30 minutes
  SEMIURGENT   — Significant but stable, care within 2 hours
  NONURGENT    — Minor, can wait, routine care

Gold set: 100 items, stratified by triage level + clinical category, 70/30 train/test split.

LLM Only Confirmation Criteria:
  Confirmed if: no SLM achieves ≥90% overall accuracy parity with LLM
             OR no SLM achieves ≥80% CRITICAL recall (safety failure threshold)
"""

import csv
import json
import os
import random
from datetime import datetime

random.seed(42)

PREREGISTRATION = {
    "use_case": "UC6 — Healthcare Clinical Triage",
    "locked_date": "2026-03-10",
    "s3_score": 4.44,
    "s3_prediction": "LLM Only",
    "s3_threshold_llm_only": 4.0,
    "dimensions": {
        "TC_task_complexity":  {"score": 5, "weight": 1.0, "note": "Expert clinical reasoning: integrate vitals, symptoms, history simultaneously"},
        "OS_output_structure": {"score": 4, "weight": 0.8, "note": "One of 4 defined triage labels — structured but requires expert judgment to reach"},
        "SK_stakes":           {"score": 5, "weight": 1.2, "note": "Under-triage of CRITICAL = patient death; irreversible harm — maximum stakes"},
        "DS_data_sensitivity": {"score": 5, "weight": 0.8, "note": "PHI — protected health information, maximum regulatory exposure (HIPAA)"},
        "LT_latency":          {"score": 4, "weight": 1.0, "note": "Clinical decision support tool; minutes acceptable (not real-time interactive)"},
        "VL_volume":           {"score": 3, "weight": 0.6, "note": "Tens of thousands/month at hospital ED level"},
    },
    "hypotheses": {
        "H6.1": "Best SLM overall accuracy < 90% of LLM accuracy (parity not achieved)",
        "H6.2": "SLM CRITICAL recall < 80% (systematic under-triage of life-threatening cases)",
        "H6.3": "UC6 classified as LLM Only — SLMs fail minimum safety threshold",
        "H6.4": "SLMs under-triage CRITICAL as URGENT (not as lower categories) — partial knowledge",
    },
    "llm_only_confirmation_criteria": {
        "primary":   "No SLM achieves ≥90% overall accuracy parity with LLM",
        "secondary": "No SLM achieves ≥80% CRITICAL recall",
        "note":      "Either criterion alone is sufficient to confirm LLM Only. Both expected.",
    },
    "comparison_baseline": "Manchester Triage System and Emergency Severity Index (ESI) standards.",
}

# ── Gold set ──────────────────────────────────────────────────────────────────
# Categories: cardiac, respiratory, neurological, trauma, sepsis_infection
# Difficulty: easy (clear cut), medium (borderline / atypical), hard (requires expert synthesis)
# Labels: CRITICAL, URGENT, SEMIURGENT, NONURGENT

GOLD_SET = [

    # ══════════════════════════════════════════════════════════════════════════
    #  CRITICAL — 15 items (life-threatening, needs immediate intervention)
    # ══════════════════════════════════════════════════════════════════════════

    # ── Cardiac CRITICAL ──────────────────────────────────────────────────────
    {
        "category": "cardiac", "difficulty": "easy", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Crushing chest pain radiating to left arm, sweating profusely\n"
            "Vitals: HR 58 | BP 88/52 | RR 22 | SpO2 94% | Temp 36.8°C | GCS 15/15\n"
            "History: 62-year-old male, sudden onset 20 minutes ago. Diaphoretic on arrival. "
            "12-lead ECG shows ST elevation in leads II, III, aVF. Known hypertensive."
        ),
    },
    {
        "category": "cardiac", "difficulty": "hard", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sudden tearing pain between shoulder blades, now extending to abdomen\n"
            "Vitals: HR 102 | BP Right arm 148/90 Left arm 96/60 | RR 20 | SpO2 97% | Temp 37.1°C | GCS 15/15\n"
            "History: 58-year-old male, hypertensive, pain onset 30 minutes ago while at rest. "
            "Describes pain as 'ripping'. BP differential between arms of 52mmHg. No chest wall tenderness."
        ),
    },
    {
        "category": "cardiac", "difficulty": "medium", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sudden onset severe breathlessness, unable to speak in full sentences\n"
            "Vitals: HR 124 | BP 96/60 | RR 34 | SpO2 82% | Temp 37.2°C | GCS 14/15\n"
            "History: 74-year-old female, known ischaemic heart disease. Pink frothy sputum. "
            "Diffuse bilateral crackles on auscultation. Marked peripheral oedema. Cold extremities."
        ),
    },

    # ── Respiratory CRITICAL ─────────────────────────────────────────────────
    {
        "category": "respiratory", "difficulty": "easy", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Cannot breathe, turning blue\n"
            "Vitals: HR 138 | BP 104/68 | RR 36 | SpO2 72% | Temp 37.0°C | GCS 13/15\n"
            "History: 29-year-old male, known severe asthma, last used blue inhaler 10 min ago with no effect. "
            "Using all accessory muscles, tripod position, cyanosis visible centrally."
        ),
    },
    {
        "category": "respiratory", "difficulty": "medium", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Throat tightening and difficulty swallowing after wasp sting\n"
            "Vitals: HR 132 | BP 78/46 | RR 28 | SpO2 91% | Temp 36.9°C | GCS 15/15\n"
            "History: 35-year-old female, stung 15 minutes ago in the garden. "
            "Audible stridor, urticaria covering trunk. No prior allergy history. Tongue visibly swollen."
        ),
    },
    {
        "category": "respiratory", "difficulty": "hard", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Chest pain and worsening shortness of breath after road traffic accident\n"
            "Vitals: HR 118 | BP 92/58 | RR 32 | SpO2 88% | Temp 36.8°C | GCS 14/15\n"
            "History: 44-year-old male, driver in MVA 1 hour ago. Appears to be deteriorating. "
            "Absent breath sounds on left, trachea deviated to right, distended neck veins. "
            "Chest X-ray not yet obtained."
        ),
    },

    # ── Neurological CRITICAL ─────────────────────────────────────────────────
    {
        "category": "neurological", "difficulty": "easy", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sudden right-sided weakness and can't speak properly\n"
            "Vitals: HR 84 | BP 192/106 | RR 18 | SpO2 96% | Temp 36.7°C | GCS 13/15\n"
            "History: 68-year-old female, onset 40 minutes ago during breakfast. "
            "Right face droop, right arm drift, expressive aphasia. FAST positive. "
            "Last seen well 45 minutes ago. No anticoagulants."
        ),
    },
    {
        "category": "neurological", "difficulty": "medium", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Prolonged seizure, not stopping\n"
            "Vitals: HR 148 | BP 164/94 | RR 24 | SpO2 89% | Temp 37.6°C | GCS 6/15\n"
            "History: 31-year-old male, witnessed tonic-clonic seizure for 22 minutes, still ongoing. "
            "No prior epilepsy history. Oxygen administered. Jaw clenched, incontinent of urine."
        ),
    },
    {
        "category": "neurological", "difficulty": "hard", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Worst headache of my life, came on suddenly while lifting\n"
            "Vitals: HR 58 | BP 178/98 | RR 16 | SpO2 98% | Temp 37.8°C | GCS 14/15\n"
            "History: 47-year-old male, sudden onset 'thunderclap' headache rated 10/10, "
            "onset during weight training 1 hour ago. Neck stiffness on passive flexion. "
            "Vomiting twice. No prior headache history. No focal neurology."
        ),
    },

    # ── Trauma CRITICAL ───────────────────────────────────────────────────────
    {
        "category": "trauma", "difficulty": "easy", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Unresponsive following head-on vehicle collision\n"
            "Vitals: HR 56 | BP 168/92 | RR 8 | SpO2 88% | Temp 36.6°C | GCS 5/15\n"
            "History: 22-year-old male, driver in 80km/h head-on collision 20 minutes ago. "
            "Unequal pupils (R 6mm fixed, L 3mm reactive). Significant scalp laceration. "
            "Cervical collar in place."
        ),
    },
    {
        "category": "trauma", "difficulty": "medium", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Stab wound to left chest\n"
            "Vitals: HR 126 | BP 88/56 | RR 30 | SpO2 87% | Temp 36.7°C | GCS 14/15\n"
            "History: 26-year-old male, single stab wound left anterior chest, 5th intercostal space. "
            "Decreased air entry left side, haemoptysis, patient deteriorating. "
            "2 large-bore IV cannulas inserted en route."
        ),
    },
    {
        "category": "trauma", "difficulty": "hard", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Abdominal pain after being struck by forklift at work\n"
            "Vitals: HR 108 | BP 102/68 | RR 22 | SpO2 97% | Temp 36.8°C | GCS 15/15\n"
            "History: 39-year-old male, struck by slow-moving forklift 30 minutes ago, initially walked around. "
            "Now has worsening periumbilical pain. Abdomen rigid on palpation, guarding present. "
            "Repeat BP 88/52 ten minutes after arrival."
        ),
    },

    # ── Sepsis / Infection CRITICAL ───────────────────────────────────────────
    {
        "category": "sepsis_infection", "difficulty": "easy", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Confusion and feeling very unwell, brought by ambulance\n"
            "Vitals: HR 138 | BP 70/40 | RR 28 | SpO2 94% | Temp 39.8°C | GCS 12/15\n"
            "History: 71-year-old female, nursing home resident. 24 hours of progressive confusion. "
            "Mottled skin, cold extremities, not passing urine. Suspected urinary source. "
            "No antibiotics administered yet."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "medium", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Severe headache, neck stiffness, rash spreading quickly\n"
            "Vitals: HR 128 | BP 96/58 | RR 26 | SpO2 95% | Temp 40.2°C | GCS 13/15\n"
            "History: 19-year-old male, university student. 6-hour history of worsening headache and fever. "
            "Non-blanching petechial rash spreading to trunk. Photophobia, neck stiffness. "
            "Roommate recently had similar illness."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "hard", "triage_label": "CRITICAL",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Mild fever and generally unwell in patient receiving chemotherapy\n"
            "Vitals: HR 112 | BP 106/68 | RR 20 | SpO2 96% | Temp 38.3°C | GCS 15/15\n"
            "History: 54-year-old female, day 10 of cycle 3 chemotherapy for diffuse large B-cell lymphoma. "
            "Feels 'off' since yesterday. No obvious source of infection. "
            "Last CBC showed neutrophils 0.3 × 10⁹/L. On granulocyte colony-stimulating factor."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    #  URGENT — 35 items (potentially life-threatening, care within 30 min)
    # ══════════════════════════════════════════════════════════════════════════

    # ── Cardiac URGENT (7) ───────────────────────────────────────────────────
    {
        "category": "cardiac", "difficulty": "easy", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Chest pain at rest for 2 hours, came in by taxi\n"
            "Vitals: HR 88 | BP 148/92 | RR 18 | SpO2 97% | Temp 36.8°C | GCS 15/15\n"
            "History: 58-year-old male, central chest tightness radiating to jaw, came on at rest. "
            "Known type 2 diabetic, smoker, previous angioplasty 3 years ago. "
            "ECG shows ST depression leads V4-V6. Troponin pending."
        ),
    },
    {
        "category": "cardiac", "difficulty": "easy", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Heart racing and feels faint for the past 3 hours\n"
            "Vitals: HR 148 (irregular) | BP 118/74 | RR 18 | SpO2 98% | Temp 36.9°C | GCS 15/15\n"
            "History: 66-year-old female, known hypertensive. Palpitations onset 3 hours ago at home. "
            "No chest pain. Mildly lightheaded but not syncopal. "
            "ECG shows atrial fibrillation with rapid ventricular response."
        ),
    },
    {
        "category": "cardiac", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Severe headache and blurred vision\n"
            "Vitals: HR 76 | BP 218/124 | RR 16 | SpO2 98% | Temp 36.7°C | GCS 15/15\n"
            "History: 52-year-old male, non-adherent hypertensive. Frontal headache and bilateral blurred vision "
            "for 4 hours. No neurological deficit. ECG normal. Fundoscopy shows papilloedema bilaterally."
        ),
    },
    {
        "category": "cardiac", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sharp chest pain worse on breathing, mild fever\n"
            "Vitals: HR 96 | BP 128/78 | RR 20 | SpO2 97% | Temp 38.2°C | GCS 15/15\n"
            "History: 28-year-old male, sharp pleuritic chest pain for 2 days, worse lying flat, "
            "relieved by leaning forward. Recent viral illness. ECG shows saddle-shaped ST elevation throughout."
        ),
    },
    {
        "category": "cardiac", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Increasing breathlessness and leg swelling over 5 days\n"
            "Vitals: HR 102 | BP 138/88 | RR 24 | SpO2 93% | Temp 36.9°C | GCS 15/15\n"
            "History: 78-year-old male, known heart failure. Worsening orthopnoea, bilateral ankle oedema. "
            "SpO2 drops to 88% on exertion. Bibasal crackles, JVP elevated. Missed diuretics for 2 weeks."
        ),
    },
    {
        "category": "cardiac", "difficulty": "hard", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sudden severe pain in the right calf and foot, foot gone cold\n"
            "Vitals: HR 82 | BP 136/84 | RR 16 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 61-year-old male, smoker with peripheral vascular disease. "
            "Right foot cold, pale, and pulseless below the knee, onset 3 hours ago. "
            "Pain on passive dorsiflexion. Femoral pulse present. Dorsalis pedis and posterior tibial absent."
        ),
    },
    {
        "category": "cardiac", "difficulty": "hard", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sudden onset rapid palpitations, near-blackout episode\n"
            "Vitals: HR 226 | BP 102/68 | RR 18 | SpO2 97% | Temp 36.8°C | GCS 15/15\n"
            "History: 24-year-old male, first episode, no cardiac history. "
            "ECG shows wide-complex tachycardia with short PR interval and delta waves. "
            "Near-syncope resolved spontaneously after 5 minutes but still tachycardic."
        ),
    },

    # ── Respiratory URGENT (7) ───────────────────────────────────────────────
    {
        "category": "respiratory", "difficulty": "easy", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Severe wheeze and shortness of breath\n"
            "Vitals: HR 118 | BP 126/78 | RR 26 | SpO2 91% | Temp 37.0°C | GCS 15/15\n"
            "History: 22-year-old female, known asthma. Peak flow 38% predicted. "
            "Audible wheeze, speaking in short phrases. 4 puffs of salbutamol in last 2 hours with partial effect."
        ),
    },
    {
        "category": "respiratory", "difficulty": "easy", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Productive cough, fever and difficulty breathing for 3 days\n"
            "Vitals: HR 112 | BP 108/68 | RR 26 | SpO2 92% | Temp 39.4°C | GCS 15/15\n"
            "History: 70-year-old male with COPD. Right lower lobe consolidation on CXR. "
            "Meeting 2 of 3 CURB-65 criteria (urea 9.2, RR 26). Was managing at home but deteriorating."
        ),
    },
    {
        "category": "respiratory", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sudden onset breathlessness and pleuritic chest pain\n"
            "Vitals: HR 114 | BP 128/82 | RR 24 | SpO2 93% | Temp 37.1°C | GCS 15/15\n"
            "History: 34-year-old female, 6 weeks post-partum. Right-sided pleuritic pain, "
            "haemodynamically stable. D-dimer elevated. Wells score 5. CT-PA ordered."
        ),
    },
    {
        "category": "respiratory", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sudden left-sided chest pain and breathlessness in tall thin man\n"
            "Vitals: HR 104 | BP 122/74 | RR 22 | SpO2 94% | Temp 36.7°C | GCS 15/15\n"
            "History: 23-year-old male, 6'4\", spontaneous onset 1 hour ago at rest. "
            "Decreased left-sided breath sounds. No trauma. CXR shows left pneumothorax ~25%."
        ),
    },
    {
        "category": "respiratory", "difficulty": "easy", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Worsening breathlessness and increased sputum in COPD patient\n"
            "Vitals: HR 106 | BP 136/84 | RR 24 | SpO2 88% | Temp 38.1°C | GCS 15/15\n"
            "History: 72-year-old male, COPD Gold stage III. Increased dyspnoea over 48 hours, "
            "purulent sputum. Bilaterally reduced air entry, prolonged expiration. "
            "Baseline SpO2 at home is 90-92%."
        ),
    },
    {
        "category": "respiratory", "difficulty": "hard", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Choking episode, now settled but intermittent cough and wheeze\n"
            "Vitals: HR 96 | BP 122/78 | RR 20 | SpO2 96% | Temp 36.9°C | GCS 15/15\n"
            "History: 3-year-old male, sudden onset choking while eating peanuts. "
            "Episode seemed to resolve but now has persistent unilateral wheeze and hypoxia dips. "
            "CXR shows air trapping right lower lobe. Parent very anxious."
        ),
    },
    {
        "category": "respiratory", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Increasing breathlessness and right-sided dullness\n"
            "Vitals: HR 102 | BP 116/74 | RR 22 | SpO2 93% | Temp 37.2°C | GCS 15/15\n"
            "History: 67-year-old male, known mesothelioma. Worsening dyspnoea over 1 week. "
            "Stony dullness right base, absent breath sounds. Estimated 1.5L effusion on CXR. "
            "Requires urgent drainage."
        ),
    },

    # ── Neurological URGENT (7) ──────────────────────────────────────────────
    {
        "category": "neurological", "difficulty": "easy", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sudden onset of slurred speech and right hand weakness, resolved\n"
            "Vitals: HR 78 | BP 172/98 | RR 16 | SpO2 98% | Temp 36.8°C | GCS 15/15\n"
            "History: 65-year-old male, symptoms lasted 20 minutes then fully resolved. "
            "ABCD2 score 5 (high risk). Known AF not on anticoagulation. "
            "Still has full resolution of deficit but urgent imaging required."
        ),
    },
    {
        "category": "neurological", "difficulty": "easy", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: First ever seizure in a 42-year-old\n"
            "Vitals: HR 112 | BP 148/88 | RR 18 | SpO2 97% | Temp 37.0°C | GCS 14/15\n"
            "History: 42-year-old female, witnessed tonic-clonic seizure lasting 3 minutes, "
            "now post-ictal and confused. No prior epilepsy. "
            "Headaches for 2 months preceding this episode. Urgent CT head required."
        ),
    },
    {
        "category": "neurological", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sudden onset severe headache 6 hours ago, now almost resolved\n"
            "Vitals: HR 72 | BP 158/90 | RR 16 | SpO2 99% | Temp 37.0°C | GCS 15/15\n"
            "History: 38-year-old female, sudden maximal onset headache while at computer, "
            "rated 10/10, now 4/10 and improving. CT head done in ED is normal. "
            "Needs LP to exclude xanthochromia given thunderclap onset."
        ),
    },
    {
        "category": "neurological", "difficulty": "hard", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sudden onset vertigo, vomiting, can't walk straight\n"
            "Vitals: HR 88 | BP 162/92 | RR 16 | SpO2 97% | Temp 37.0°C | GCS 15/15\n"
            "History: 62-year-old male, hypertensive, sudden onset severe vertigo with vomiting. "
            "Unable to walk. Horizontal nystagmus. HINTS exam shows abnormal head impulse test. "
            "Finger-nose dysmetria. Cannot exclude posterior circulation stroke."
        ),
    },
    {
        "category": "neurological", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Suddenly became confused, not recognising family\n"
            "Vitals: HR 94 | BP 142/86 | RR 18 | SpO2 96% | Temp 38.4°C | GCS 13/15\n"
            "History: 78-year-old male, sudden onset confusion, agitated, pulling at clothes. "
            "CAM positive. No known dementia. Possible urinary source. "
            "Requires urgent work-up to exclude CNS cause and organ failure."
        ),
    },
    {
        "category": "neurological", "difficulty": "hard", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Left facial drooping and eye won't close properly, ear pain\n"
            "Vitals: HR 74 | BP 128/80 | RR 16 | SpO2 99% | Temp 37.6°C | GCS 15/15\n"
            "History: 52-year-old male, rapid onset left-sided facial palsy 6 hours ago. "
            "Vesicles visible in external auditory canal. Hyperacusis, taste disturbance. "
            "Ramsay Hunt syndrome suspected — time-critical for antiviral treatment."
        ),
    },
    {
        "category": "neurological", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Headache, fever, and confusion over 48 hours\n"
            "Vitals: HR 118 | BP 106/68 | RR 20 | SpO2 96% | Temp 39.6°C | GCS 13/15\n"
            "History: 24-year-old female, gradually worsening headache, fever, and unusual behaviour. "
            "No rash, no neck stiffness. HSV encephalitis cannot be excluded. "
            "MRI head and LP arranged. Time-critical for aciclovir."
        ),
    },

    # ── Trauma URGENT (7) ────────────────────────────────────────────────────
    {
        "category": "trauma", "difficulty": "easy", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Hip pain, unable to weight-bear after a fall\n"
            "Vitals: HR 98 | BP 142/86 | RR 18 | SpO2 97% | Temp 36.9°C | GCS 15/15\n"
            "History: 82-year-old female, fell from standing height at home. "
            "Right leg shortened and externally rotated. Significant pain. "
            "Cognitively intact. X-ray shows displaced intracapsular neck of femur fracture."
        ),
    },
    {
        "category": "trauma", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Badly broken forearm, sensation changed below injury\n"
            "Vitals: HR 106 | BP 124/78 | RR 18 | SpO2 98% | Temp 36.8°C | GCS 15/15\n"
            "History: 31-year-old male, fell from bike at speed. Compound midshaft radius-ulna fracture "
            "with bone protruding. Reduced sensation in ring and little finger. Weak grip."
        ),
    },
    {
        "category": "trauma", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Neck pain after head-on collision, tingling in both arms\n"
            "Vitals: HR 82 | BP 118/72 | RR 16 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 28-year-old male, moderate-speed MVA. Cervical spine immobilised. "
            "Bilateral arm tingling and mild weakness. Cervical spine CT ordered — possible C5/6 injury."
        ),
    },
    {
        "category": "trauma", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Chemical splash in both eyes 15 minutes ago\n"
            "Vitals: HR 88 | BP 122/76 | RR 16 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 34-year-old male, industrial alkali splash to both eyes. "
            "Copious irrigation started by paramedics. Corneal whitening visible, "
            "severe pain. Time-critical irrigation to limit corneal damage."
        ),
    },
    {
        "category": "trauma", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Right-sided chest pain after striking steering wheel\n"
            "Vitals: HR 112 | BP 118/74 | RR 26 | SpO2 94% | Temp 36.9°C | GCS 15/15\n"
            "History: 45-year-old female, low-speed MVA, struck steering wheel. "
            "Right-sided chest tenderness, splinted breathing, no pneumothorax on CXR. "
            "Multiple rib fractures. Monitoring required for development of haemothorax."
        ),
    },
    {
        "category": "trauma", "difficulty": "easy", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Deep laceration to palm with ongoing bleeding\n"
            "Vitals: HR 102 | BP 108/68 | RR 18 | SpO2 98% | Temp 36.8°C | GCS 15/15\n"
            "History: 38-year-old male, cut hand on broken glass 30 minutes ago. "
            "Deep laceration across palm with significant ongoing blood loss. "
            "Reduced index finger flexion. Possible flexor tendon involvement."
        ),
    },
    {
        "category": "trauma", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Hit in the head by cricket ball, briefly lost consciousness\n"
            "Vitals: HR 88 | BP 128/76 | RR 16 | SpO2 99% | Temp 36.7°C | GCS 14/15\n"
            "History: 17-year-old male, direct blow to temporal region with cricket ball. "
            "Brief LOC 1-2 minutes, now GCS 14 with persistent headache and vomiting. "
            "CT head indicated per NICE criteria."
        ),
    },

    # ── Sepsis/Infection URGENT (7) ──────────────────────────────────────────
    {
        "category": "sepsis_infection", "difficulty": "easy", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: High fever, rigors and generally very unwell\n"
            "Vitals: HR 118 | BP 102/66 | RR 22 | SpO2 96% | Temp 39.8°C | GCS 15/15\n"
            "History: 48-year-old male, 2 days of fever, rigors, right-sided loin pain. "
            "SIRS criteria met (HR >90, RR >20, Temp >38). No organ dysfunction yet. "
            "Haemodynamically marginal — requires urgent IV access and cultures."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Vomiting, abdominal pain, and fruity breath in known diabetic\n"
            "Vitals: HR 114 | BP 108/68 | RR 28 | SpO2 97% | Temp 37.6°C | GCS 15/15\n"
            "History: 18-year-old male, type 1 diabetes. Nausea and vomiting for 24 hours. "
            "Kussmaul breathing, glucose 32.4 mmol/L, large ketones. "
            "Haemodynamically marginal — moderate DKA."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "easy", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Severe central abdominal pain moving to right side\n"
            "Vitals: HR 108 | BP 118/74 | RR 18 | SpO2 98% | Temp 38.2°C | GCS 15/15\n"
            "History: 24-year-old female, 12-hour history of periumbilical pain now localising to RIF. "
            "Rovsing's sign positive, rebound tenderness at McBurney's point. Elevated WBC. "
            "Clinical diagnosis of acute appendicitis. Surgical review requested."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sudden onset severe left-sided scrotal pain in teenager\n"
            "Vitals: HR 104 | BP 124/76 | RR 16 | SpO2 99% | Temp 37.2°C | GCS 15/15\n"
            "History: 15-year-old male, acute onset testicular pain 3 hours ago, woke from sleep. "
            "Left testis high-riding and horizontal lie, extremely tender to palpation. "
            "Time-critical: testicular torsion cannot be excluded without surgical exploration."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "hard", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Sore throat with difficulty swallowing for 3 days, worsening\n"
            "Vitals: HR 102 | BP 118/76 | RR 20 | SpO2 97% | Temp 38.8°C | GCS 15/15\n"
            "History: 35-year-old female, odynophagia for 3 days, drooling, muffled 'hot potato' voice. "
            "No stridor at rest but progressive difficulty swallowing secretions. "
            "Peritonsillar swelling visible. Epiglottitis and deep space neck infection must be excluded."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "hard", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Right-sided abdominal pain, nausea, and positive pregnancy test\n"
            "Vitals: HR 116 | BP 108/64 | RR 18 | SpO2 98% | Temp 37.1°C | GCS 15/15\n"
            "History: 29-year-old female, 6 weeks amenorrhoea. Right iliac fossa pain, shoulder tip pain "
            "on lying flat. Beta-hCG positive. No products on TVUS. Peritoneal signs. "
            "Ectopic pregnancy until excluded."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "medium", "triage_label": "URGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: High fever, back pain and rigors in patient with recent cystitis\n"
            "Vitals: HR 116 | BP 106/68 | RR 22 | SpO2 97% | Temp 39.6°C | GCS 15/15\n"
            "History: 33-year-old female, treated for UTI 1 week ago with trimethoprim. "
            "Now worsening, right loin pain, rigors. Urine dipstick strongly positive. "
            "SIRS criteria met — ascending pyelonephritis with possible bacteraemia."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    #  SEMIURGENT — 35 items (significant but stable, care within 2 hours)
    # ══════════════════════════════════════════════════════════════════════════

    # ── Cardiac SEMIURGENT (7) ───────────────────────────────────────────────
    {
        "category": "cardiac", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Chest pain for 2 days, worse on pressing\n"
            "Vitals: HR 72 | BP 128/80 | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 45-year-old female, costochondritis-pattern chest pain. Reproducible on palpation "
            "of costochondral junctions. No radiation. No diaphoresis. ECG normal. Low-risk features."
        ),
    },
    {
        "category": "cardiac", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Intermittent palpitations for the last week\n"
            "Vitals: HR 82 | BP 124/78 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 38-year-old male, palpitations lasting seconds, resolving spontaneously. "
            "No syncope. ECG in sinus rhythm with frequent ectopic beats. Caffeine excess. "
            "No structural heart disease. Ambulatory monitoring arranged."
        ),
    },
    {
        "category": "cardiac", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Stood up and nearly fainted in young female\n"
            "Vitals: HR 88 | BP 102/68 (lying) / 80/52 (standing) | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 22-year-old female, pre-syncopal episode on standing from lying. "
            "Orthostatic drop confirmed. No cardiac history. Likely vasovagal or dehydration. "
            "Needs ECG and electrolytes to exclude secondary cause."
        ),
    },
    {
        "category": "cardiac", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Routine visit for monitoring after recent medication change\n"
            "Vitals: HR 68 | BP 148/88 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 64-year-old male, hypertensive, started new beta-blocker last week. "
            "Mild dizziness when standing. No other symptoms. Requires ECG and review "
            "of antihypertensive regimen."
        ),
    },
    {
        "category": "cardiac", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Mild breathlessness and ankle swelling, on treatment\n"
            "Vitals: HR 76 | BP 132/84 | RR 18 | SpO2 95% | Temp 36.8°C | GCS 15/15\n"
            "History: 71-year-old female, known stable heart failure on optimal medical therapy. "
            "Mild increase in ankle oedema and exertional dyspnoea over 1 week. "
            "Haemodynamically stable. Medication review and diuretic adjustment needed."
        ),
    },
    {
        "category": "cardiac", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Feeling of missed heartbeats, no other symptoms\n"
            "Vitals: HR 74 (regular) | BP 118/74 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 55-year-old male, isolated ectopic beats, aware of them for months. "
            "ECG shows frequent isolated PVCs, no sustained arrhythmia. "
            "Thyroid function normal. Reassurance and Holter monitor indicated."
        ),
    },
    {
        "category": "cardiac", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Leg pain on walking, relieved by rest\n"
            "Vitals: HR 78 | BP 138/88 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 64-year-old male smoker, intermittent claudication bilateral calves for 6 months. "
            "ABPI 0.72. Pulses present but reduced. No rest pain. Vascular clinic referral needed."
        ),
    },

    # ── Respiratory SEMIURGENT (7) ───────────────────────────────────────────
    {
        "category": "respiratory", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Mild wheeze, responding well to inhaler\n"
            "Vitals: HR 86 | BP 118/76 | RR 18 | SpO2 96% | Temp 37.0°C | GCS 15/15\n"
            "History: 19-year-old female, mild asthma exacerbation. Peak flow 68% predicted. "
            "Speaking in full sentences. Improved with 4 puffs salbutamol. "
            "Requires further observation and optimisation of inhaler technique."
        ),
    },
    {
        "category": "respiratory", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Productive cough and fever for 4 days\n"
            "Vitals: HR 94 | BP 122/76 | RR 18 | SpO2 96% | Temp 38.4°C | GCS 15/15\n"
            "History: 42-year-old female, productive cough with yellow sputum. "
            "Right lower lobe consolidation on CXR. CURB-65 score 1 — suitable for oral antibiotics. "
            "Haemodynamically stable. Sent home on amoxicillin."
        ),
    },
    {
        "category": "respiratory", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Dry cough and occasional breathlessness for 3 weeks\n"
            "Vitals: HR 82 | BP 124/80 | RR 16 | SpO2 97% | Temp 36.8°C | GCS 15/15\n"
            "History: 58-year-old male, non-smoker, on ACE-inhibitor. Dry cough persisting. "
            "Spirometry pending. CXR clear. Likely ACE inhibitor-induced cough."
        ),
    },
    {
        "category": "respiratory", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Pleuritic left-sided chest pain, no breathlessness\n"
            "Vitals: HR 78 | BP 118/74 | RR 16 | SpO2 98% | Temp 36.9°C | GCS 15/15\n"
            "History: 30-year-old male, sharp left-sided pain on inspiration for 2 days. "
            "CXR normal, D-dimer 0.3 (low). Wells score 1. No clinical PE features. "
            "Pleurisy, likely viral aetiology."
        ),
    },
    {
        "category": "respiratory", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Seasonal wheeze and runny nose, known hay fever\n"
            "Vitals: HR 76 | BP 112/72 | RR 14 | SpO2 98% | Temp 36.8°C | GCS 15/15\n"
            "History: 26-year-old female, known seasonal allergic rhinitis and mild asthma. "
            "Seasonal exacerbation. Peak flow 75%. Asks for antihistamine and steroid inhaler review. "
            "No acute distress."
        ),
    },
    {
        "category": "respiratory", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Worsening breathlessness, known interstitial lung disease\n"
            "Vitals: HR 88 | BP 118/76 | RR 20 | SpO2 93% | Temp 36.8°C | GCS 15/15\n"
            "History: 68-year-old female, known IPF. Gradual worsening over 2 weeks. "
            "Stable on supplemental oxygen at home (2L). No fever, no new consolidation on CXR. "
            "Requires review of oxygen titration and respiratory clinic follow-up."
        ),
    },
    {
        "category": "respiratory", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Coughing up small amounts of blood twice, smoker\n"
            "Vitals: HR 82 | BP 128/80 | RR 16 | SpO2 97% | Temp 36.8°C | GCS 15/15\n"
            "History: 56-year-old male, 35 pack-year smoker. Two episodes of haemoptysis yesterday, "
            "< 10 mL each. CXR shows right upper lobe mass. Haemodynamically stable. "
            "Urgent CT chest and respiratory referral required."
        ),
    },

    # ── Neurological SEMIURGENT (7) ──────────────────────────────────────────
    {
        "category": "neurological", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Severe headache, usual migraine pattern\n"
            "Vitals: HR 82 | BP 128/78 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 34-year-old female, known migraineur with typical visual aura preceding headache. "
            "Gradual onset, no fever, no meningism. Same as previous episodes. "
            "Requires antiemetic and analgesia. Photophobia but neurology normal."
        ),
    },
    {
        "category": "neurological", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Tension-type headache with nausea for 2 days\n"
            "Vitals: HR 76 | BP 122/78 | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 28-year-old male, bilateral pressing headache, worse with stress. "
            "No neurological symptoms, no meningism. Usual tension pattern. "
            "Analgesia and hydration advised."
        ),
    },
    {
        "category": "neurological", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Ongoing dizziness, unsteady gait, known inner ear problem\n"
            "Vitals: HR 80 | BP 124/78 | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 48-year-old female, known benign paroxysmal positional vertigo. "
            "Episodic triggered positional vertigo since this morning. Normal neurological exam. "
            "Responds to Epley manoeuvre. No new onset focal symptoms."
        ),
    },
    {
        "category": "neurological", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Tingling and numbness in both hands, worse at night\n"
            "Vitals: HR 74 | BP 118/76 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 42-year-old female, 3-month history of bilateral hand paraesthesia, "
            "worse at night and with prolonged keyboard use. Positive Phalen's test. "
            "No acute neurology. Likely bilateral carpal tunnel syndrome."
        ),
    },
    {
        "category": "neurological", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Memory problems and personality change over 4 weeks\n"
            "Vitals: HR 76 | BP 128/80 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 14/15\n"
            "History: 67-year-old male, family reports progressive confusion and personality change. "
            "MMSE 22/30. No fever. No focal deficit. CT head pending. "
            "Subacute presentation — could be reversible cause or early dementia."
        ),
    },
    {
        "category": "neurological", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Headaches and visual blurring since stopping steroids 1 week ago\n"
            "Vitals: HR 78 | BP 118/74 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 32-year-old female, known IIH (idiopathic intracranial hypertension), "
            "stopped acetazolamide 1 week ago. Pulsatile tinnitus returned. "
            "Needs urgent ophthalmology for visual fields and papilloedema assessment."
        ),
    },
    {
        "category": "neurological", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Neck pain and stiffness after long car journey\n"
            "Vitals: HR 72 | BP 122/76 | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 36-year-old female, mechanical neck pain for 3 days after long drive. "
            "No radiculopathy, no weakness, no red flags. Full range of movement on examination. "
            "Simple analgesia and physio referral appropriate."
        ),
    },

    # ── Trauma SEMIURGENT (7) ────────────────────────────────────────────────
    {
        "category": "trauma", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Wrist pain and swelling after falling onto outstretched hand\n"
            "Vitals: HR 78 | BP 118/74 | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 55-year-old female, fell on outstretched right hand. X-ray shows "
            "minimally displaced Colles-type distal radius fracture. "
            "Neurovascular intact distal. Requires manipulation and plaster cast."
        ),
    },
    {
        "category": "trauma", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Twisted ankle during sport, mild swelling\n"
            "Vitals: HR 76 | BP 118/72 | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 22-year-old male, rolled ankle during football. Ottawa ankle rules negative. "
            "Weight-bearing with pain. Mild swelling over lateral ligament complex. "
            "No fracture. RICE advice and referral to physiotherapy."
        ),
    },
    {
        "category": "trauma", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Head laceration, not actively bleeding now\n"
            "Vitals: HR 82 | BP 122/78 | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 48-year-old male, 5cm scalp laceration from falling against door frame. "
            "Pressure applied, now oozing. GCS 15. No LOC. No nausea. "
            "No CT indications. Wound closure required."
        ),
    },
    {
        "category": "trauma", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Dog bite to forearm\n"
            "Vitals: HR 80 | BP 118/74 | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 31-year-old female, bitten by neighbour's dog 2 hours ago. "
            "3 puncture wounds to right forearm, cleaned at scene. "
            "Tetanus status unknown. Requires wound assessment, irrigation, antibiotics."
        ),
    },
    {
        "category": "trauma", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Burn to right forearm after touching oven rack\n"
            "Vitals: HR 86 | BP 122/78 | RR 14 | SpO2 99% | Temp 36.9°C | GCS 15/15\n"
            "History: 29-year-old female, contact burn from hot oven rack. "
            "Superficial-partial thickness burn approximately 3% BSA right forearm. "
            "Blistering present. Significant pain. Requires dressings and analgesia."
        ),
    },
    {
        "category": "trauma", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Eye is sore, feels like something is in it\n"
            "Vitals: HR 74 | BP 116/72 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 35-year-old male, metalwork without eye protection. "
            "Right eye pain, photophobia, profuse watering. Slit lamp shows small corneal foreign body. "
            "Requires removal under local anaesthetic."
        ),
    },
    {
        "category": "trauma", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Soft tissue injury to knee, limping in\n"
            "Vitals: HR 78 | BP 118/74 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 40-year-old female, twisting injury during running. Knee swollen, "
            "limited range of movement. Lachman test equivocal. Ottawa knee rules negative. "
            "Weight-bearing with difficulty. MRI ligament injury arranged."
        ),
    },

    # ── Sepsis/Infection SEMIURGENT (7) ─────────────────────────────────────
    {
        "category": "sepsis_infection", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Burning urination and lower abdominal discomfort\n"
            "Vitals: HR 82 | BP 118/74 | RR 14 | SpO2 99% | Temp 37.6°C | GCS 15/15\n"
            "History: 28-year-old female, dysuria, frequency, suprapubic pain for 2 days. "
            "Urine dipstick: nitrites and leucocytes positive. No systemic features. "
            "Simple UTI — oral trimethoprim prescribed."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Red spreading rash on lower leg, mild fever\n"
            "Vitals: HR 90 | BP 124/78 | RR 16 | SpO2 98% | Temp 37.9°C | GCS 15/15\n"
            "History: 55-year-old male, cellulitis right lower leg extending to knee. "
            "Ascending margin marked with pen for monitoring. Systemically well. "
            "No abscess. IV antibiotics if no oral response, currently starting oral flucloxacillin."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Painful lump in armpit, increasingly tender\n"
            "Vitals: HR 80 | BP 118/74 | RR 14 | SpO2 99% | Temp 37.8°C | GCS 15/15\n"
            "History: 23-year-old male, tender fluctuant abscess right axilla for 5 days. "
            "Increased in size yesterday. Systemically well. Surrounding cellulitis. "
            "Requires incision and drainage under local anaesthetic."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Fever and generalised body aches for 4 days\n"
            "Vitals: HR 96 | BP 118/74 | RR 16 | SpO2 97% | Temp 38.8°C | GCS 15/15\n"
            "History: 32-year-old male, viral illness with myalgia, headache, fatigue. "
            "No localising symptoms. WBC normal. Influenza rapid test positive. "
            "Haemodynamically stable. Symptomatic management."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Colicky right-sided flank pain and blood in urine\n"
            "Vitals: HR 96 | BP 124/78 | RR 16 | SpO2 99% | Temp 37.0°C | GCS 15/15\n"
            "History: 38-year-old male, first episode of severe right loin-to-groin colicky pain. "
            "Haematuria on dipstick. USKG shows 4mm right ureteric calculus. No fever. "
            "Requires analgesia and urology follow-up. Not obstructed."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "medium", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Severe toothache and swelling of the jaw for 2 days\n"
            "Vitals: HR 88 | BP 122/76 | RR 14 | SpO2 99% | Temp 37.8°C | GCS 15/15\n"
            "History: 40-year-old male, dental abscess with submandibular swelling. "
            "Trismus present. No dysphagia, no stridor. Airway not at risk currently. "
            "Requires IV antibiotics and urgent dental or maxillofacial review."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "easy", "triage_label": "SEMIURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Skin rash and itching all over\n"
            "Vitals: HR 78 | BP 116/72 | RR 14 | SpO2 99% | Temp 37.0°C | GCS 15/15\n"
            "History: 26-year-old female, widespread maculopapular urticarial rash after starting "
            "new antibiotic. No airway involvement, no angioedema. Haemodynamically stable. "
            "Drug reaction. Cetirizine prescribed, medication stopped."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    #  NONURGENT — 15 items (minor, can wait, routine)
    # ══════════════════════════════════════════════════════════════════════════

    # ── Cardiac NONURGENT (3) ────────────────────────────────────────────────
    {
        "category": "cardiac", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Routine review of blood pressure readings at home\n"
            "Vitals: HR 70 | BP 142/88 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 58-year-old male, known mild hypertension on one agent. Home readings "
            "slightly elevated. No symptoms. No end organ damage signs. "
            "Medication review and lifestyle advice needed."
        ),
    },
    {
        "category": "cardiac", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Occasional awareness of heartbeat, especially lying in bed\n"
            "Vitals: HR 72 | BP 118/74 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 29-year-old female, anxious, notices heartbeat at night. "
            "No arrhythmia on ECG, no structural disease. Caffeine and anxiety likely factors. "
            "Reassurance and lifestyle modification."
        ),
    },
    {
        "category": "cardiac", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Wants prescription renewed for regular blood pressure medication\n"
            "Vitals: HR 68 | BP 132/82 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 67-year-old male, well-controlled hypertension. Stable on ramipril. "
            "Ran out of medication. No symptoms. GP letter provided. "
            "Requires prescription renewal."
        ),
    },

    # ── Respiratory NONURGENT (3) ────────────────────────────────────────────
    {
        "category": "respiratory", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Runny nose, sore throat, mild cough for 3 days\n"
            "Vitals: HR 76 | BP 116/72 | RR 14 | SpO2 99% | Temp 37.3°C | GCS 15/15\n"
            "History: 24-year-old male, typical viral upper respiratory tract infection. "
            "No difficulty breathing. Throat mildly red but no exudate. No cervical lymphadenopathy. "
            "Symptomatic advice only — rest, fluids, paracetamol."
        ),
    },
    {
        "category": "respiratory", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Mild cough for 1 week, no fever\n"
            "Vitals: HR 72 | BP 114/72 | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 36-year-old female, dry cough for 1 week after recent cold. "
            "Improving. No dyspnoea, no wheeze. Lungs clear. "
            "Post-viral cough — no treatment required, reassurance given."
        ),
    },
    {
        "category": "respiratory", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Seasonal hay fever, wants prescription for antihistamine\n"
            "Vitals: HR 74 | BP 112/70 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 21-year-old female, known seasonal allergic rhinitis. "
            "Runny nose and itchy eyes annually in spring. Requests cetirizine prescription. "
            "No wheeze, no breathing difficulty."
        ),
    },

    # ── Neurological NONURGENT (3) ───────────────────────────────────────────
    {
        "category": "neurological", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Chronic tension headache, seeking advice on long-term management\n"
            "Vitals: HR 70 | BP 116/72 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 30-year-old female, bilateral pressing headache for years, no red flags. "
            "Pattern unchanged. Normal neurological exam. Analgesic overuse excluded. "
            "Preventive treatment discussion needed."
        ),
    },
    {
        "category": "neurological", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Lower back pain, standing job, no red flags\n"
            "Vitals: HR 74 | BP 118/74 | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 44-year-old male, chronic low back pain related to work standing on concrete. "
            "No radiculopathy, no cauda equina symptoms, no night pain. "
            "Physiotherapy and ergonomic advice appropriate."
        ),
    },
    {
        "category": "neurological", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Difficulty sleeping and mild anxiety\n"
            "Vitals: HR 76 | BP 118/74 | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 35-year-old male, stress at work, sleep onset insomnia for 3 months. "
            "No suicidal ideation, no depression. CBT-I and sleep hygiene advice. "
            "GP follow-up arranged."
        ),
    },

    # ── Trauma NONURGENT (3) ─────────────────────────────────────────────────
    {
        "category": "trauma", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Small cut on finger from kitchen knife\n"
            "Vitals: HR 72 | BP 116/72 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 25-year-old female, 1cm superficial laceration right index fingertip. "
            "Bleeding stopped with pressure. Neurovascular intact. "
            "Wound cleaned and steristripped. Tetanus up to date."
        ),
    },
    {
        "category": "trauma", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Mild ankle soreness after walking on uneven ground\n"
            "Vitals: HR 70 | BP 114/70 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 19-year-old female, minimal swelling left lateral ankle. "
            "Full weight-bearing, Ottawa ankle rules negative. "
            "RICE advice provided. No imaging required."
        ),
    },
    {
        "category": "trauma", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Bee sting on arm, no systemic reaction\n"
            "Vitals: HR 72 | BP 118/72 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 44-year-old male, single bee sting right forearm 1 hour ago. "
            "Local erythema and mild swelling at sting site only. No urticaria, no dyspnoea. "
            "Stinger removed. Antihistamine tablet recommended."
        ),
    },

    # ── Sepsis/Infection NONURGENT (3) ───────────────────────────────────────
    {
        "category": "sepsis_infection", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Mild sore throat for 2 days, no fever\n"
            "Vitals: HR 74 | BP 114/72 | RR 14 | SpO2 99% | Temp 36.9°C | GCS 15/15\n"
            "History: 20-year-old male, mild pharyngitis. FeverPAIN score 1 (low). "
            "No exudate, no cervical lymphadenopathy, no trismus. Viral aetiology. "
            "Symptomatic advice only — not indicated for antibiotics."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Slightly sore and itchy ear for a few days\n"
            "Vitals: HR 72 | BP 116/72 | RR 14 | SpO2 99% | Temp 36.8°C | GCS 15/15\n"
            "History: 32-year-old female, mild external otitis after swimming. "
            "External ear canal erythematous and moist. Tympanic membrane intact. "
            "Topical acetic acid drops prescribed. No fever."
        ),
    },
    {
        "category": "sepsis_infection", "difficulty": "easy", "triage_label": "NONURGENT",
        "presentation": (
            "Triage Note:\n"
            "Chief Complaint: Requesting repeat prescription for antifungal cream\n"
            "Vitals: HR 70 | BP 118/74 | RR 14 | SpO2 99% | Temp 36.7°C | GCS 15/15\n"
            "History: 48-year-old male, recurrent tinea pedis (athlete's foot). "
            "Chronic, well-managed with clotrimazole. No systemic signs. "
            "Prescription renewed and hygiene advice reinforced."
        ),
    },
]


def stratified_split(items, n_test_total=30):
    """Split items into train/test preserving triage label proportions.
    Guarantees EXACTLY n_test_total test items using floor-then-remainder allocation.
    Remainder items go to the largest groups first (most headroom).
    """
    import math
    from collections import defaultdict

    groups = defaultdict(list)
    for item in items:
        groups[item["triage_label"]].append(item)
    for group in groups.values():
        random.shuffle(group)

    # Floor allocation per label
    n_floor = {label: math.floor(len(g) / len(items) * n_test_total)
               for label, g in groups.items()}
    remainder = n_test_total - sum(n_floor.values())

    # Distribute remainder 1-by-1 to largest groups first
    for label in sorted(groups, key=lambda l: len(groups[l]), reverse=True)[:remainder]:
        n_floor[label] += 1

    assert sum(n_floor.values()) == n_test_total, \
        f"Split produced {sum(n_floor.values())} test items, expected {n_test_total}"

    train, test = [], []
    for label, group in groups.items():
        n = n_floor[label]
        test.extend(group[:n])
        train.extend(group[n:])
    return train, test


def main():
    os.makedirs("data/gold_sets", exist_ok=True)
    os.makedirs("data/metadata",  exist_ok=True)

    train_items, test_items = stratified_split(GOLD_SET, n_test_total=30)

    gold_path = "data/gold_sets/uc6_clinical_triage.csv"
    with open(gold_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "item_id", "split", "category", "difficulty", "triage_label", "presentation"
        ])
        writer.writeheader()
        for idx, (split, items) in enumerate([("train", train_items), ("test", test_items)]):
            for i, item in enumerate(items):
                writer.writerow({
                    "item_id":     f"uc6_{split}_{i+1:03d}",
                    "split":       split,
                    "category":    item["category"],
                    "difficulty":  item["difficulty"],
                    "triage_label": item["triage_label"],
                    "presentation": item["presentation"],
                })

    # Metadata
    from collections import Counter
    all_labels = [i["triage_label"] for i in GOLD_SET]
    test_labels = [i["triage_label"] for i in test_items]
    meta = {**PREREGISTRATION,
            "build_date": datetime.now().isoformat(),
            "total_items": len(GOLD_SET),
            "train_items": len(train_items),
            "test_items":  len(test_items),
            "triage_distribution": dict(Counter(all_labels)),
            "test_triage_distribution": dict(Counter(test_labels)),
            "category_distribution": dict(Counter(i["category"] for i in GOLD_SET)),
            "difficulty_distribution": dict(Counter(i["difficulty"] for i in GOLD_SET)),
            }
    with open("data/metadata/uc6_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print("=" * 72)
    print("  UC6 Gold Set — Healthcare Clinical Triage")
    print("  S³ Research Project | UT Dallas | March 2026")
    print("=" * 72)
    print(f"  Total items  : {len(GOLD_SET)}")
    print(f"  Train        : {len(train_items)}")
    print(f"  Test         : {len(test_items)}")
    print(f"\n  Triage distribution (all):")
    for label, count in sorted(Counter(all_labels).items()):
        print(f"    {label:<14} {count:3d} total | {Counter(test_labels).get(label,0):2d} test")
    print(f"\n  Pre-registered S³ = 4.44  →  LLM Only predicted")
    print(f"  Gold set saved to : {gold_path}")
    print()


if __name__ == "__main__":
    main()