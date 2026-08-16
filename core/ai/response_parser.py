"""Response Parser and Deterministic Offline Fallback Engine for PMLA-SCWE AI Copilot.

When OpenAI and Gemini are unreachable or unconfigured, this engine generates high-quality,
transparent, rule-based responses using core.explainability and core.risk_engine.
"""

from __future__ import annotations
from typing import Any
from datetime import date, timedelta


def parse_and_validate_copilot_response(
    raw_response: str,
    action_type: str,
    metadata: dict[str, Any]
) -> dict[str, Any]:
    """Cleans, formats, and attaches standard disclaimer banners to AI responses."""
    cleaned = raw_response.strip()

    # Prepend advisory banner if not already present
    advisory_header = (
        "> ⚠️ **AI TEACHER COPILOT ADVISORY DRAFT**\n"
        "> *This AI-generated analysis is for decision support only. All recommendations require teacher review and confirmation before applying.*\n\n"
    )

    if "AI TEACHER COPILOT" not in cleaned and "ADVISORY" not in cleaned:
        final_text = advisory_header + cleaned
    else:
        final_text = cleaned

    return {
        "success": True,
        "action": action_type,
        "response": final_text,
        "provider": metadata.get("provider", "AI Provider"),
        "model": metadata.get("model", "Default"),
        "fallback_used": metadata.get("fallback_used", False),
        "is_offline_fallback": metadata.get("is_offline_fallback", False),
        "error": metadata.get("error")
    }


def generate_deterministic_fallback(
    action_type: str,
    student_id: int | None = None,
    duration_days: int = 7,
    compare_student_id: int | None = None,
    class_name: str | None = None,
    section: str | None = None,
    query: str | None = None
) -> dict[str, Any]:
    """Generates pure-Python, deterministic rule-based educational responses when AI providers are offline."""
    from core.student_profile_service import get_student_360_profile
    from core.risk_engine import compute_student_risk_profile, get_class_risk_overview
    from core import explainability

    offline_notice = (
        "> ⚪ **DETERMINISTIC OFFLINE ENGINE ACTIVE**\n"
        "> *AI cloud services are currently unavailable. The following output was computed directly from verified PMLA-SCWE rule-based analytics.*\n\n"
    )

    # 1. EXPLAIN RISK FALLBACK
    if action_type in ("explain_risk", "risk_analysis"):
        if not student_id:
            return _format_offline_error("Please specify a valid Student ID.")

        profile = compute_student_risk_profile(student_id)
        if not profile:
            return _format_offline_error(f"Student ID #{student_id} not found in database.")

        s = profile["student"]
        r_level = profile["risk_level"]
        r_score = profile["risk_score"]
        factors = profile.get("factors", [])
        why = profile.get("why_explanation", [])
        actions = profile.get("recommended_actions", [])

        lines = [
            offline_notice,
            f"### 1. EXECUTIVE SUMMARY",
            f"Student **{s['name']}** (#{s['id']}, {s['class_section']}) is currently categorized in the **{r_level} RISK** tier with a composite risk index of **{r_score if r_score is not None else 'N/A'}/100**.",
            f"Data completeness is evaluated at **{profile['data_quality']['is_valid']}** with high statistical confidence.",
            "",
            "### 2. MAIN CONTRIBUTING FACTORS",
        ]
        if factors:
            for f in factors:
                lines.append(f"• **{f['name']}** (+{f['points_contributed']:.0f} pts, {f['impact'].upper()} impact): {f['evidence']}")
        else:
            lines.append("• No critical deficit factors detected across academic or attendance records.")

        lines.extend([
            "",
            "### 3. WHAT THE DATA SHOWS (EVIDENCE)",
            f"• Academic Average: **{profile['metrics_summary']['academic_avg']}**",
            f"• Attendance Rate: **{profile['metrics_summary']['attendance_rate']}**",
            f"• Performance Trajectory: **{profile['trend']}** (Regression slope: {profile['slope']:.3f} pts/wk)",
            f"• Learning Health Score: **{profile['metrics_summary']['lhs_score']}**",
            f"• Cyber-Wellness Score: **{profile['metrics_summary']['wellness_score']}**",
            "",
            "### 4. RECOMMENDED NEXT STEPS (TEACHER ACTION)"
        ])
        if actions:
            for act in actions:
                lines.append(f"• **[{act['priority']} Priority] {act['title']}**: {act['description']}")
        else:
            lines.append("• Continue regular curriculum monitoring and weekly progress milestones.")

        return _build_offline_payload("\n".join(lines), action_type)

    # 2. STUDY PLAN FALLBACK
    elif action_type in ("study_plan", "create_study_plan"):
        if not student_id:
            return _format_offline_error("Please specify a valid Student ID.")

        p = get_student_360_profile(student_id)
        if not p:
            return _format_offline_error(f"Student ID #{student_id} not found.")

        s = p["student"]
        weak_subj = p["academic"].get("weakest_subject", "Core Subject")
        best_subj = p["academic"].get("best_subject", "Foundational Concepts")
        num_days = duration_days if duration_days in (7, 14, 30) else 7

        lines = [
            offline_notice,
            f"### 🎯 {num_days}-DAY PERSONALIZED REMEDIAL STUDY PLAN",
            f"• **Student**: {s['name']} (#{s['id']}, {s['class_section']})",
            f"• **Target Remedial Focus**: {weak_subj} (Reinforced with strengths in {best_subj})",
            f"• **Target Mastery Goal**: Achieve >= 75% on next weekly milestone quiz.",
            "",
            f"### 📅 {num_days}-DAY SCHEDULE & MILESTONES",
            "| Timeframe | Focus Area | Suggested Micro-Learning Activity | Measurable Goal |",
            "| :--- | :--- | :--- | :--- |"
        ]

        if num_days == 7:
            lines.extend([
                f"| **Day 1–2** | Diagnostic Review | Review missed concepts in {weak_subj} with flashcards | Identify 3 core formula gaps |",
                f"| **Day 3–4** | Guided Practice | Complete 10 targeted practice problems (25 mins/day) | Achieve >= 70% accuracy |",
                f"| **Day 5–6** | Independent Problem Solving | Timed practice worksheet on core weaknesses | Solve 8/10 without hints |",
                f"| **Day 7** | Formative Milestone | 15-minute concept review quiz with teacher | Score >= 75% |"
            ])
        elif num_days == 14:
            lines.extend([
                f"| **Days 1–4** | Concept Foundation | 20 mins daily concept review on {weak_subj} fundamentals | Complete chapter notes |",
                f"| **Days 5–8** | Application & Exercises | Solve 15 step-by-step application problems | Score >= 75% on practice |",
                f"| **Days 9–12** | Speed & Accuracy | Timed problem sets and peer-assisted problem solving | Reduce solve time by 20% |",
                f"| **Days 13–14** | Comprehensive Checkpoint | Full milestone practice assessment & review | Achieve >= 80% passing score |"
            ])
        else: # 30 Days (4 Weeks)
            lines.extend([
                f"| **Week 1** | Foundation & Diagnostic | Clarify foundational misconceptions in {weak_subj} | Complete diagnostic review |",
                f"| **Week 2** | Guided Problem Sets | 3 practice sessions weekly (30 mins each) | Score >= 70% on weekly quiz |",
                f"| **Week 3** | Advanced Practice & Speed | Solve multi-step problems and review error log | Error rate under 15% |",
                f"| **Week 4** | Mastery Evaluation | Comprehensive unit test simulation & teacher debrief | Score >= 80% on unit exam |"
            ])

        lines.extend([
            "",
            "### 💡 TEACHER & PARENT SUPPORT TIPS",
            "• Encourage 25-minute focused study intervals with 5-minute screen breaks (Pomodoro technique).",
            "• Maintain a quiet evening study routine with bedtime before 10:30 PM to optimize memory retention."
        ])

        return _build_offline_payload("\n".join(lines), action_type)

    # 3. WEAK TOPICS FALLBACK
    elif action_type in ("identify_weak_topics", "weak_topics"):
        if not student_id:
            return _format_offline_error("Please specify a valid Student ID.")

        p = get_student_360_profile(student_id)
        if not p:
            return _format_offline_error(f"Student ID #{student_id} not found.")

        s = p["student"]
        acad = p["academic"]
        weak_subj = acad.get("weakest_subject", "Core Topic")
        avg = acad.get("display", "N/A")

        lines = [
            offline_notice,
            f"### 🔍 CRITICAL LEARNING GAPS & TOPIC ANALYSIS",
            f"• **Student**: {s['name']} (#{s['id']}, {s['class_section']})",
            f"• **Current Academic Average**: {avg}",
            f"• **Primary Area Requiring Practice**: **{weak_subj}**",
            "",
            "### 📊 EVIDENCE FROM ASSESSMENTS",
            f"• Assessment evaluations indicate conceptual uncertainty in **{weak_subj}** relative to cohort benchmarks.",
            f"• Strongest demonstrated competence is in **{acad.get('best_subject', 'General Syllabus')}**.",
            "",
            "### 🛠️ TARGETED REMEDIAL STRATEGIES",
            f"1. **Concept Re-explanation**: Provide a 15-minute 1-on-1 walkthrough focused on {weak_subj}.",
            f"2. **Micro-Learning Worksheets**: Assign 5 scaffolded practice problems starting from basic definitions to applied questions.",
            f"3. **Formative Milestone**: Re-assess with a 5-question checkpoint quiz prior to the next chapter exam.",
            "",
            "### ⏱️ ESTIMATED MASTERY RECOVERY TIME",
            "• **7 to 10 Days** with consistent 20-minute daily practice sessions."
        ]

        return _build_offline_payload("\n".join(lines), action_type)

    # 4. INTERVENTION PLAN FALLBACK
    elif action_type in ("generate_intervention", "intervention_plan"):
        if not student_id:
            return _format_offline_error("Please specify a valid Student ID.")

        profile = compute_student_risk_profile(student_id)
        if not profile:
            return _format_offline_error(f"Student ID #{student_id} not found.")

        s = profile["student"]
        today_str = date.today().strftime("%B %d, %Y")
        review_str = (date.today() + timedelta(days=21)).strftime("%B %d, %Y")
        r_level = profile["risk_level"]
        r_score = profile["risk_score"]
        actions = profile.get("recommended_actions", [])

        lines = [
            offline_notice,
            f"### 📋 OFFICIAL TEACHER INTERVENTION PLAN (DRAFT)",
            f"• **Student Name**: {s['name']} (#{s['id']})",
            f"• **Class & Section**: {s['class_section']}",
            f"• **Priority Tier**: **{r_level}** (Composite Risk Score: {r_score if r_score is not None else 'N/A'}/100)",
            f"• **Plan Initiated**: {today_str}",
            "",
            "### 🔍 EVIDENCE BASE",
            f"• Academic Average: {profile['metrics_summary']['academic_avg']}",
            f"• Attendance Record: {profile['metrics_summary']['attendance_rate']}",
            f"• Trajectory Indicator: {profile['trend']} ({profile['slope']:.3f} pts/week)",
            "",
            "### 🛠️ PROPOSED TEACHER ACTIONS",
        ]
        if actions:
            for idx, act in enumerate(actions, start=1):
                lines.append(f"{idx}. **[{act['priority']}] {act['title']}**: {act['description']}")
        else:
            lines.append("1. **Routine Monitoring**: Conduct weekly progress check-in.")

        lines.extend([
            "",
            "### 📅 REVIEW SCHEDULE & SUCCESS INDICATORS",
            f"• **Target Review Checkpoint**: **{review_str}**",
            f"• **Measurable Success Criterion**: Attendance maintained >= 75% CBSE threshold and next quiz score improvement >= 10 points.",
            "",
            "⚠️ **TEACHER REVIEW REQUIRED**: This intervention plan draft requires educator confirmation before initiating official parent or counseling sessions."
        ])

        return _build_offline_payload("\n".join(lines), action_type)

    # 5. CLASS PERFORMANCE SUMMARY FALLBACK
    elif action_type in ("class_summary", "summarize_class"):
        overview = get_class_risk_overview(class_name=class_name or "All", section=section or "All")
        c_label = f"Class {class_name or 'All'}-{section or 'All'}"

        lines = [
            offline_notice,
            f"### 📊 CLASSROOM COHORT PERFORMANCE SUMMARY — {c_label}",
            f"• **Total Evaluated Cohort**: {overview['total_students']} Students (Showing {overview['filtered_count']})",
            "",
            "### ⚠️ RISK & THREAT DISTRIBUTION",
            f"• 🔴 **High Risk**: {overview['total_high']} students (Require urgent remedial support)",
            f"• 🟡 **Medium Risk**: {overview['total_medium']} students (Require monitoring & practice)",
            f"• 🟢 **Low Risk**: {overview['total_low']} students (Satisfactory progress)",
            f"• ⚪ **Insufficient Data**: {overview['total_insufficient']} students (Awaiting full assessment baseline)",
            "",
            f"### 🎯 PRIMARY COHORT VULNERABILITY",
            f"• **Primary Concern**: **{overview['most_common_risk_factor']}**",
            "",
            "### 📋 RECOMMENDED WHOLE-CLASS ADJUSTMENTS",
            "1. Allocate 10 minutes at the beginning of each class for whole-group revision of core topics.",
            "2. Send proactive attendance reminders to parents of students approaching the 75% attendance threshold.",
            "3. Encourage healthy study habits and daily screen balance during morning assemblies."
        ]

        return _build_offline_payload("\n".join(lines), action_type)

    # 6. COMPARE TWO STUDENTS FALLBACK
    elif action_type in ("compare_students", "compare_two_students"):
        if not student_id or not compare_student_id:
            return _format_offline_error("Please specify two valid Student IDs to compare.")

        p1 = get_student_360_profile(student_id)
        p2 = get_student_360_profile(compare_student_id)
        if not p1 or not p2:
            return _format_offline_error("One or both Student IDs could not be found.")

        s1, s2 = p1["student"], p2["student"]

        lines = [
            offline_notice,
            f"### ⚖️ CONSTRUCTIVE COMPARATIVE METRICS MATRIX",
            f"Comparing **{s1['name']}** (#{s1['id']}) vs. **{s2['name']}** (#{s2['id']})",
            "",
            "| Metric Dimension | " + f"{s1['name']} (#{s1['id']})" + " | " + f"{s2['name']} (#{s2['id']})" + " |",
            "| :--- | :--- | :--- |",
            f"| **Class & Section** | {s1['class_section']} | {s2['class_section']} |",
            f"| **Academic Average** | {p1['academic'].get('display', 'N/A')} | {p2['academic'].get('display', 'N/A')} |",
            f"| **Attendance Rate** | {p1['attendance'].get('display', 'N/A')} | {p2['attendance'].get('display', 'N/A')} |",
            f"| **Performance Trajectory** | {p1['prediction'].get('trend_direction', 'N/A')} | {p2['prediction'].get('trend_direction', 'N/A')} |",
            f"| **Learning Health Score** | {p1['learning_health'].get('display', 'N/A')} | {p2['learning_health'].get('display', 'N/A')} |",
            f"| **Screen Time** | {p1['wellness'].get('daily_screen_time', 'N/A')}h | {p2['wellness'].get('daily_screen_time', 'N/A')}h |",
            "",
            "### 🌟 DIFFERENTIATED PEDAGOGICAL OPPORTUNITIES",
            f"• **{s1['name']}**: Focus on reinforcing {p1['academic'].get('weakest_subject', 'core concepts')} and maintaining positive trajectory.",
            f"• **{s2['name']}**: Focus on encouraging consistent attendance and structured revision practice.",
            "• **Collaborative Learning**: Consider pairing these students for reciprocal peer-assisted problem solving."
        ]

        return _build_offline_payload("\n".join(lines), action_type)

    # 7. PARENT SUMMARY FALLBACK
    elif action_type in ("parent_summary", "draft_parent_summary"):
        if not student_id:
            return _format_offline_error("Please specify a valid Student ID.")

        p = get_student_360_profile(student_id)
        if not p:
            return _format_offline_error(f"Student ID #{student_id} not found.")

        s = p["student"]
        acad_avg = p["academic"].get("display", "N/A")
        att_rate = p["attendance"].get("display", "N/A")
        weak_subj = p["academic"].get("weakest_subject", "recent syllabus topics")
        best_subj = p["academic"].get("best_subject", "class coursework")

        lines = [
            offline_notice,
            f"### ✉️ PARENT-FRIENDLY PROGRESS SUMMARY (DRAFT)",
            f"**Subject**: Academic Progress & Learning Support Update for {s['name']} — Class {s['class_section']}",
            "",
            f"**Dear Parent / Guardian of {s['name']},**",
            "",
            f"I am writing from the Academic Support Team to share a regular progress update regarding {s['name']}'s learning journey in Class {s['class_section']}.",
            "",
            f"Over our recent evaluation period, {s['name']} has demonstrated commendable engagement and strength in **{best_subj}**, maintaining an overall academic average of **{acad_avg}**.",
            "",
            f"To help {s['name']} achieve their highest potential, our instructional team is providing extra practice support in **{weak_subj}**. Current attendance is logged at **{att_rate}**.",
            "",
            "We would greatly appreciate your encouragement at home in maintaining regular daily attendance and ensuring a quiet 30-minute evening study routine.",
            "",
            "Please feel free to reach out if you would like to schedule a brief discussion regarding our support plan.",
            "",
            "**Warm regards,**  ",
            "Academic Instructional Team  ",
            "PMLA-SCWE Educational Analytics System",
            "",
            "*Note for Teacher: This draft is provided for educator review. Please adjust as desired prior to communicating with parents.*"
        ]

        return _build_offline_payload("\n".join(lines), action_type)

    # 8. TEACHER ACTIONS FALLBACK
    elif action_type in ("suggest_actions", "teacher_actions"):
        if not student_id:
            return _format_offline_error("Please specify a valid Student ID.")

        profile = compute_student_risk_profile(student_id)
        if not profile:
            return _format_offline_error(f"Student ID #{student_id} not found.")

        s = profile["student"]
        actions = profile.get("recommended_actions", [])

        lines = [
            offline_notice,
            f"### 💡 PRIORITIZED TEACHER ACTION CHECKLIST",
            f"• **Student**: {s['name']} (#{s['id']}, {s['class_section']})",
            f"• **Risk Tier**: {profile['risk_level']}",
            "",
            "### ⚡ IMMEDIATE ACTIONS (THIS WEEK)",
        ]
        if actions:
            for act in actions[:2]:
                lines.append(f"• **[{act['priority']}] {act['title']}**: {act['description']}")
        else:
            lines.append("• Review latest quiz results and acknowledge positive progress.")

        lines.extend([
            "",
            "### 📅 MEDIUM-TERM FOLLOW-UP (NEXT 2–3 WEEKS)",
            "• Monitor next weekly progress score to confirm positive regression trajectory.",
            "• Verify attendance regularity remains compliant with CBSE 75% standard.",
            "",
            "### 📈 KEY METRICS TO WATCH",
            "• Weekly progression slope ($m$).",
            "• Diagnostic quiz error reduction.",
            "• Daily screen balance and study hours."
        ])

        return _build_offline_payload("\n".join(lines), action_type)

    # DEFAULT GENERAL INQUIRY FALLBACK
    else:
        text = (
            f"{offline_notice}"
            f"### 🤖 PMLA-SCWE AI TEACHER COPILOT\n\n"
            f"AI cloud services are currently offline. You can still use the 8 dedicated Copilot actions above to generate grounded risk explanations, study plans, weak topic breakdowns, parent letters, and class summaries from deterministic analytics.\n\n"
            f"**Teacher Inquiry**: {query or 'General Inquiry'}\n\n"
            f"To enable cloud AI completions, configure `OPENAI_API_KEY` or `GEMINI_API_KEY` in your environment."
        )
        return _build_offline_payload(text, "general_inquiry")


def _build_offline_payload(text: str, action: str) -> dict[str, Any]:
    return {
        "success": True,
        "action": action,
        "response": text,
        "provider": "Deterministic PMLA-SCWE Engine",
        "model": "Rule-Based Explainability (Offline)",
        "fallback_used": True,
        "is_offline_fallback": True,
        "error": None
    }


def _format_offline_error(msg: str) -> dict[str, Any]:
    return {
        "success": False,
        "action": "error",
        "response": f"⚠️ {msg}",
        "provider": "Deterministic PMLA-SCWE Engine",
        "model": "Rule-Based Explainability (Offline)",
        "fallback_used": False,
        "is_offline_fallback": True,
        "error": msg
    }
