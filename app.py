import re
import streamlit as st
from collections import Counter

st.set_page_config(page_title="Smart Resume ATS Matcher", page_icon="ðŸ“„", layout="wide")

st.title("ðŸ“„ Smart Resume ATS Matcher")
st.caption("A simple keyword-based ATS score and skill-gap analyzer for academic demonstration.")

DEFAULT_SKILLS = "python, sql, excel, machine learning, data analysis, pandas, numpy, communication, teamwork, power bi, statistics, html, css, javascript"

def clean(text):
    return re.sub(r"[^a-z0-9+#. ]", " ", text.lower())

def extract_skills(text, skill_list):
    t = clean(text)
    found = []
    for skill in skill_list:
        s = clean(skill.strip())
        if s and s in t:
            found.append(skill.strip())
    return sorted(set(found), key=str.lower)

def keyword_score(resume, job, skills):
    resume_words = set(re.findall(r"[a-z0-9+#.]+", clean(resume)))
    job_words = set(re.findall(r"[a-z0-9+#.]+", clean(job)))
    stop = {"and","the","with","for","from","that","this","are","you","your","our","will","have","has","using","into","about","work","role","job"}
    important = {w for w in job_words if len(w) > 2 and w not in stop}
    matched = resume_words & important
    return round((len(matched) / len(important) * 100) if important else 0, 1), sorted(matched), sorted(important - resume_words)

with st.sidebar:
    st.header("Settings")
    skills_text = st.text_area("Skills database (comma-separated)", DEFAULT_SKILLS, height=150)
    skill_list = [x.strip() for x in skills_text.split(",") if x.strip()]
    st.info("This prototype uses transparent keyword matching. It is not a hiring decision system.")

col1, col2 = st.columns(2)
with col1:
    resume = st.text_area("Paste candidate resume", height=360, placeholder="Paste resume text here...")
with col2:
    job = st.text_area("Paste job description", height=360, placeholder="Paste job description here...")

if st.button("Analyze Resume", type="primary", use_container_width=True):
    if not resume.strip() or not job.strip():
        st.warning("Please enter both the resume and job description.")
    else:
        score, matched_words, missing_words = keyword_score(resume, job, skill_list)
        resume_skills = extract_skills(resume, skill_list)
        required_skills = extract_skills(job, skill_list)
        missing_skills = [s for s in required_skills if s.lower() not in {x.lower() for x in resume_skills}]
        skill_score = round(len(resume_skills) / len(required_skills) * 100, 1) if required_skills else 0
        final_score = round((score * 0.6) + (skill_score * 0.4), 1)

        st.subheader("Results")
        a,b,c = st.columns(3)
        a.metric("Overall ATS Score", f"{final_score}%")
        b.metric("Keyword Match", f"{score}%")
        c.metric("Skill Coverage", f"{skill_score}%")
        st.progress(min(final_score/100, 1.0))

        left, right = st.columns(2)
        with left:
            st.markdown("### Skills found")
            st.write(", ".join(resume_skills) if resume_skills else "No configured skills found.")
            st.markdown("### Matched job keywords")
            st.write(", ".join(matched_words[:40]) if matched_words else "No strong keyword matches.")
        with right:
            st.markdown("### Skill gaps")
            if missing_skills:
                for s in missing_skills:
                    st.error(f"Develop or mention: {s}")
            else:
                st.success("No configured skill gaps detected.")
            st.markdown("### Other missing keywords")
            st.write(", ".join(missing_words[:40]) if missing_words else "None detected.")

        st.download_button("Download analysis", f"Overall ATS Score: {final_score}%\nKeyword Match: {score}%\nSkill Coverage: {skill_score}%\nSkills Found: {', '.join(resume_skills)}\nSkill Gaps: {', '.join(missing_skills)}", "ats_analysis.txt")

st.divider()
st.caption("Educational prototype â€¢ Improve results by adding synonyms, section weighting, and PDF/DOCX text extraction.")