"""Prompt Templates and Safety Directives for PMLA-SCWE AI Teacher Copilot.

Enforces:
1. Strict grounding in verified data.
2. Explicit statement of uncertainty / missing observations.
3. Distinction between observed facts and statistical projections.
4. Non-autonomous human-in-the-loop teacher review.
5. No medical or psychological diagnoses.
"""

from __future__ import annotations

SYSTEM_COPILOT_PROMPT = """You are the PMLA-SCWE AI Teacher Copilot — an intelligent, explainable decision-support assistant for educators.

Your primary mission is to assist teachers in interpreting student learning analytics, predicting risks, planning personalized remedial actions, and drafting constructive communications.

CRITICAL OPERATIONAL RULES:
1. STRICT GROUNDING: Use only the verified student and classroom metrics provided in the context. Never invent or hallucinate student names, test scores, attendance records, or dates.
2. UNCERTAINTY & CONFIDENCE: When data completeness is low or observations are missing (e.g. fewer than 2 weekly milestones for linear regression), explicitly state this limitation.
3. ADVISORY HUMAN-IN-THE-LOOP: All outputs are advisory recommendations and drafts. Clearly remind the educator that teacher review, discretion, and confirmation are required before implementing any plan.
4. NO MEDICAL/PSYCHOLOGICAL DIAGNOSES: Discuss digital wellness, sleep, and screen exposure strictly from an educational habits and classroom engagement perspective. Avoid clinical or psychological assertions.
5. RESPECTFUL & CONSTRUCTIVE TONE: Provide encouraging, actionable pedagogical guidance. When comparing students, highlight differentiated learning trajectories rather than competitive ranking.
6. STRUCTURED OUTPUT: Format responses with clear markdown headers, bold keywords, and organized bullet points for rapid classroom scanning.
"""


def build_explain_risk_prompt(context_text: str) -> str:
    """Builds prompt for Explain Student Risk action."""
    return f"""Context:
{context_text}

Task: Explain the student's current learning risk profile to the teacher.

Please structure your response into the following exact sections:

### 1. EXECUTIVE SUMMARY
Provide a 2-3 sentence overview of the student's current standing, composite risk score, and risk tier.

### 2. MAIN CONTRIBUTING FACTORS
List each specific factor contributing points to the risk score with its point contribution and impact level.

### 3. WHAT THE DATA SHOWS (EVIDENCE)
Provide concrete, data-grounded evidence from recent academic scores, attendance records, trajectory slope, and wellness metrics.

### 4. RECOMMENDED NEXT STEPS (TEACHER ACTION)
Provide 3-4 concrete, prioritized steps the teacher should consider taking this week.

IMPORTANT: This analysis is advisory decision-support. Teacher confirmation is required before initiating formal interventions.
"""


def build_study_plan_prompt(context_text: str, duration_days: int = 7) -> str:
    """Builds prompt for Create Personalized Study Plan action."""
    timeframe_label = f"{duration_days}-Day" if duration_days <= 14 else "30-Day (4-Week)"
    
    return f"""Context:
{context_text}

Task: Create a structured, personalized {timeframe_label} Remedial Study Plan tailored specifically to this student's weakest learning areas and current performance trajectory.

Please structure your response as follows:

### 🎯 STUDY PLAN OBJECTIVE
Briefly state the target improvement goal and key topics targeted.

### 📅 {timeframe_label.upper()} SCHEDULE & MILESTONES
Organize into a structured table or day-by-day/week-by-week format with the following columns:
• **Timeframe** (e.g., Day 1-2 or Week 1)
• **Focus Area / Topic** (Specifically targeting weak areas)
• **Suggested Micro-Learning Activity** (e.g., 20-min practice problem set, concept flashcards, revision quiz)
• **Measurable Checkpoint Goal** (e.g., Achieve >= 75% on practice set)

### 💡 TEACHER & PARENT SUPPORT TIPS
Provide 2 practical tips on study habits and screen time pacing during this period.

*Note: This study schedule is an editable advisory draft. The teacher may adjust milestones based on classroom syllabus pacing.*
"""


def build_weak_topics_prompt(context_text: str) -> str:
    """Builds prompt for Identify Weak Topics action."""
    return f"""Context:
{context_text}

Task: Analyze the student's assessment history to identify weak learning objectives and provide targeted remedial strategies.

Please structure your response as follows:

### 🔍 CRITICAL LEARNING GAPS
Identify topics or subject areas where the student's mastery is below 60% or showing negative trajectory.

### 📊 EVIDENCE FROM ASSESSMENTS
Cite specific quiz scores, assessment dates, and performance deficits.

### 🛠️ TARGETED REMEDIAL STRATEGIES
For each identified weak area, recommend:
1. Core concept to re-explain.
2. Recommended practice exercise type.
3. Quick formative assessment checkpoint.

### ⏱️ ESTIMATED MASTERY RECOVERY TIME
Provide realistic timeframe estimate for the student to achieve passing mastery.
"""


def build_intervention_plan_prompt(context_text: str) -> str:
    """Builds prompt for Generate Intervention Plan action."""
    return f"""Context:
{context_text}

Task: Draft an official Teacher Intervention Plan draft for this student.

Please structure your response into the following exact sections:

### 📋 INTERVENTION PLAN DRAFT
• **Student Name**: [Extract from context]
• **Class & Section**: [Extract from context]
• **Priority Tier**: [HIGH / MEDIUM / LOW based on risk score]
• **Primary Observed Issue**: [Concise summary of core deficit]

### 🔍 EVIDENCE BASE
Summarize the quantitative metrics justifying this intervention (attendance rate, quiz average, trajectory slope).

### 🛠️ PROPOSED TEACHER ACTIONS
Detail 3 specific pedagogical interventions (e.g., 1-on-1 counseling, remedial worksheet assignment, peer-assisted study).

### 📅 REVIEW SCHEDULE & SUCCESS INDICATOR
• **Target Review Date**: (Suggested date 2-3 weeks out)
• **Measurable Success Criterion**: (e.g., Raise attendance above 75% CBSE threshold, improve next milestone quiz by >= 10 points)

⚠️ **TEACHER REVIEW REQUIRED**: This intervention plan draft is generated by the AI Copilot for educator review. It is NOT automatically registered until reviewed and confirmed by the teacher.
"""


def build_class_summary_prompt(class_context_text: str) -> str:
    """Builds prompt for Summarize Class Performance action."""
    return f"""Context:
{class_context_text}

Task: Provide a high-level executive briefing for the classroom teacher on cohort performance, risk distribution, and collective vulnerabilities.

Please structure your response as follows:

### 📊 COHORT PERFORMANCE OVERVIEW
Executive summary of class averages, participation, and general health score.

### ⚠️ RISK & VULNERABILITY BREAKDOWN
Summary of students in High Risk, Medium Risk, and Low Risk categories, highlighting the primary cohort challenge.

### 🎯 CLASS-WIDE PEDAGOGICAL RECOMMENDATIONS
Provide 3 strategic teaching adjustments (e.g., whole-class review of common weak topic, attendance reminders, screen wellness guidance).

### 📋 IMMEDIATE TEACHER ACTION CHECKLIST
Top 3 priority tasks for the educator this week.
"""


def build_compare_students_prompt(comparison_context_text: str) -> str:
    """Builds prompt for Compare Two Students action."""
    return f"""Context:
{comparison_context_text}

Task: Provide a balanced, constructive pedagogical comparison between the two students to help the teacher design differentiated learning strategies.

Please structure your response as follows:

### ⚖️ COMPARATIVE PROFILE OVERVIEW
Side-by-side balanced comparison table across:
• Academic Performance & Trajectory
• Attendance & Regularity
• Learning Health & Digital Routine
• Primary Strengths

### 🌟 INDIVIDUAL STRENGTHS & OPPORTUNITIES
• **Student A**: Distinct strengths and specific growth areas.
• **Student B**: Distinct strengths and specific growth areas.

### 🤝 PEER LEARNING & DIFFERENTIATED TEACHING OPPORTUNITIES
Suggest how these students might benefit from paired study or how the educator can differentiate instruction between them.

*Directives: Maintain a constructive, respectful educational tone without ranking or demoralizing language.*
"""


def build_parent_summary_prompt(context_text: str) -> str:
    """Builds prompt for Draft Parent-Friendly Summary action."""
    return f"""Context:
{context_text}

Task: Draft a respectful, supportive, and clear parent communication letter regarding the student's progress and support plan.

Please structure your response as a formal email / letter draft:

**Subject**: Academic Progress & Learning Support Update for [Student Name] — Class [Class Section]

**Dear [Parent / Guardian Name],**

[Opening paragraph: Warm greeting and appreciation of partnership.]

[Second paragraph: Balanced overview of student's progress, highlighting their strongest topic and current engagement.]

[Third paragraph: Gentle, constructive explanation of areas where support is needed (e.g., regular attendance, topic revision, healthy sleep/study routine).]

[Fourth paragraph: Support steps being taken at school (remedial sessions, check-ins) and how the home environment can encourage regular study.]

**Warm regards,**
[Teacher Name / Academic Support Team]
PMLA-SCWE Decision Support System

*Note for Teacher: This draft is provided for your review. Please adjust names, dates, or details as needed before sending.*
"""


def build_suggest_actions_prompt(context_text: str) -> str:
    """Builds prompt for Suggest Teacher Follow-Up Actions action."""
    return f"""Context:
{context_text}

Task: Suggest prioritized, actionable next steps for the educator based on this student's 360 profile and risk breakdown.

Please structure your response as follows:

### ⚡ IMMEDIATE ACTIONS (THIS WEEK)
Top 2 urgent actions (e.g., Attendance check, 1-on-1 concept review).

### 📅 MEDIUM-TERM FOLLOW-UP (NEXT 2-3 WEEKS)
2 follow-up checkpoints (e.g., Progress milestone quiz, parent check-in).

### 📈 METRICS TO MONITOR
Key indicators the teacher should watch over the next 14 days.
"""


def build_general_copilot_prompt(context_text: str | None, query: str) -> str:
    """Builds prompt for free-form teacher inquiries."""
    if context_text:
        return f"""Verified Context Data:
{context_text}

Teacher Inquiry: {query}

Please provide an evidence-grounded, structured response addressing the teacher's inquiry using the verified data provided."""
    else:
        return f"""Teacher Inquiry: {query}

Please provide an educational analytics advisory response assisting the educator."""
