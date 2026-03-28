import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import base64

st.set_page_config(page_title="OTERKPOLU RC JHS Report Card", layout="wide")

# ====================== PASSWORD PROTECTION ======================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

PASSWORD = "oterkpolu2026"   # ← Change this to your preferred password

if not st.session_state.logged_in:
    st.title("OTERKPOLU RC JHS Report Card System")
    st.subheader("🔐 Login Required")
    password_input = st.text_input("Enter Password", type="password")
    
    if st.button("Login", type="primary"):
        if password_input == PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Incorrect password")
    st.stop()

# ====================== LOGOUT BUTTON ======================
st.sidebar.header("🔐 Account")
if st.sidebar.button("🚪 Logout", type="secondary"):
    st.session_state.logged_in = False
    st.rerun()

# ====================== MAIN APP ======================
st.title("OTERKPOLU RC JHS Report Card Management System")
st.caption(f"✅ Logged in • {st.session_state.get('current_grade', 'JHS 1')} {st.session_state.get('current_term', 'Term 2')}")

# === Your full app code (session state, students, tabs, scores, preview, PDF) ===
if 'current_grade' not in st.session_state:
    st.session_state.current_grade = "JHS 1"
if 'current_term' not in st.session_state:
    st.session_state.current_term = "Term 2"

if 'school_data' not in st.session_state:
    st.session_state.school_data = {}

current_key = (st.session_state.current_grade, st.session_state.current_term)
if current_key not in st.session_state.school_data:
    st.session_state.school_data[current_key] = pd.DataFrame({
        "NO.": [1, 2, 3],
        "STUDENT NAME": ["ADAMNOR CARING", "AMETRI AMOS", "ANYA BLESS"],
        "GENDER": ["M", "M", "F"],
        "DAYS PRESENT": [56, 56, 56],
        "OUT OF": [56, 56, 56],
        "CONDUCT": ["Excellent behaviour", "Respectful", "Good behaviour"],
        "TALENTS & INTERESTS": ["Sports & games", "Creative arts & drawing", "Mathematics & puzzles"],
        "CLASS TEACHER REMARK": ["A pleasure to teach – very attentive.", "Excellent progress this term.", "Improving steadily."],
        "HEAD TEACHER REMARK": ["Keep up the good work!", "Well done!", "Continue to work hard."]
    })

if 'score_data' not in st.session_state:
    st.session_state.score_data = {}

students = st.session_state.school_data[current_key]

# Sidebar (School Settings)
st.sidebar.markdown("---")
st.sidebar.header("School Settings")
grades = ["JHS 1", "JHS 2", "JHS 3"]
terms = ["Term 1", "Term 2", "Term 3"]

new_grade = st.sidebar.selectbox("Grade / Class", grades, index=grades.index(st.session_state.current_grade))
new_term = st.sidebar.selectbox("Term", terms, index=terms.index(st.session_state.current_term))

if new_grade != st.session_state.current_grade or new_term != st.session_state.current_term:
    st.session_state.current_grade = new_grade
    st.session_state.current_term = new_term
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header(f"Students - {st.session_state.current_grade} {st.session_state.current_term}")

search = st.sidebar.text_input("Search student", "")
filtered = students[students["STUDENT NAME"].str.contains(search, case=False, na=False)] if search else students

selected_name = st.sidebar.selectbox(
    "Select Student", 
    options=filtered["STUDENT NAME"].tolist() if not filtered.empty else ["No students"]
)

# Add New Student & Delete Student (same as before)
st.sidebar.subheader("Add New Student")
new_name = st.sidebar.text_input("Student Name", key="add_name")

if st.sidebar.button("➕ Save New Student", type="primary"):
    if new_name and new_name.strip():
        new_row = pd.DataFrame([{
            "NO.": len(students) + 1,
            "STUDENT NAME": new_name.strip(),
            "GENDER": "M",
            "DAYS PRESENT": 56,
            "OUT OF": 56,
            "CONDUCT": "Good behaviour",
            "TALENTS & INTERESTS": "Sports & games",
            "CLASS TEACHER REMARK": "Improving steadily in all subjects.",
            "HEAD TEACHER REMARK": "Keep up the good work!"
        }])
        st.session_state.school_data[current_key] = pd.concat([students, new_row], ignore_index=True)
        st.success(f"✅ **{new_name.strip()}** added successfully!")
        st.rerun()
    else:
        st.sidebar.error("Student Name is required!")

if selected_name and selected_name != "No students":
    st.sidebar.subheader("Delete Student")
    if st.sidebar.button("🗑️ Delete Selected Student", type="secondary"):
        if st.sidebar.checkbox("Confirm deletion (cannot be undone)"):
            idx = students[students["STUDENT NAME"] == selected_name].index[0]
            for key in list(st.session_state.score_data.keys()):
                if key[0] == st.session_state.current_grade and key[1] == st.session_state.current_term:
                    if selected_name in st.session_state.score_data[key]:
                        del st.session_state.score_data[key][selected_name]
            st.session_state.school_data[current_key] = students.drop(idx).reset_index(drop=True)
            st.success(f"🗑️ **{selected_name}** deleted!")
            st.rerun()

# Main Tabs (Student Information, Enter Scores, Report Preview)
tab1, tab2, tab3 = st.tabs(["Student Information", "Enter Scores", "Report Preview"])

with tab1:
    st.header(f"Student Information - {st.session_state.current_grade} {st.session_state.current_term}")
    if selected_name and selected_name != "No students":
        idx = students[students["STUDENT NAME"] == selected_name].index[0]
        student = students.loc[idx]

        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Student Name", value=student.get("STUDENT NAME", ""))
            new_gender = st.selectbox("Gender", ["M", "F"], index=0 if student.get("GENDER") == "M" else 1)
            new_days = st.number_input("Days Present", value=int(student.get("DAYS PRESENT", 0)), min_value=0)
            new_out_of = st.number_input("Out of", value=int(student.get("OUT OF", 0)), min_value=0)

        with col2:
            new_conduct = st.selectbox("Conduct", options=["Excellent behaviour", "Very good behaviour", "Good behaviour", "Respectful", "Very respectful", "Regular & punctual", "Cooperative & helpful", "Playful but controlled", "Active & energetic", "Courteous & polite", "Friendly with peers", "Quiet & focused", "Easily distracted", "Needs reminders to stay on task", "Needs more self-control", "Needs improvement in behaviour"], index=0)
            new_interests = st.selectbox("Talents & Interests", options=["Reading & writing", "Mathematics & puzzles", "Science experiments", "Creative arts & drawing", "Music & singing", "Sports & games", "Leadership & group work", "Ghanaian culture & language", "ICT & technology", "Gardening & nature", "Dancing & drama"], index=0)

        new_class_remark = st.selectbox("Class Teacher's Remark", options=["A pleasure to teach – very attentive and hardworking.", "Excellent progress this term. Keep it up!", "Shows strong creativity in projects.", "Consistent and punctual. Well done!", "Needs more practice with homework.", "Active participant with positive attitude.", "Improving steadily in all subjects.", "Great leadership qualities in class.", "Polite and respectful to everyone.", "Enthusiastic learner – a joy to have!"], index=0)
        new_head_remark = st.selectbox("Head Teacher's Remark", options=["Keep up the good work!", "Well done! Continue to aim higher.", "Satisfactory performance.", "You have shown great improvement.", "Work harder next term.", "Excellent overall performance."], index=0)

        if st.button("💾 Save Student Details", type="primary"):
            students.loc[idx, "STUDENT NAME"] = new_name
            students.loc[idx, "GENDER"] = new_gender
            students.loc[idx, "DAYS PRESENT"] = new_days
            students.loc[idx, "OUT OF"] = new_out_of
            students.loc[idx, "CONDUCT"] = new_conduct
            students.loc[idx, "TALENTS & INTERESTS"] = new_interests
            students.loc[idx, "CLASS TEACHER REMARK"] = new_class_remark
            students.loc[idx, "HEAD TEACHER REMARK"] = new_head_remark
            st.success(f"✅ Details for **{new_name}** saved!")
            st.rerun()
    else:
        st.info("Select a student from the sidebar.")

with tab2:
    st.header(f"Enter Scores - {st.session_state.current_grade} {st.session_state.current_term}")
    selected_subject = st.selectbox("Select Subject", options=["ENGLISH LANGUAGE", "SOCIAL STUDIES", "CAREER TECHNOLOGY", "GHANAIAN LANGUAGE", "MATHEMATICS", "INTEGRATED SCIENCE", "COMPUTING", "CREATIVE ARTS", "R.M.E"])
    st.subheader(f"Score Entry for: {selected_subject}")

    score_key = (current_key, selected_subject)
    if score_key not in st.session_state.score_data:
        st.session_state.score_data[score_key] = {}

    for i, row in students.iterrows():
        name = row["STUDENT NAME"]
        st.markdown(f"<h4 style='color: #ffd700; margin-bottom: 10px;'>{name}</h4>", unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: t1 = st.number_input("Class Test 1 (15)", min_value=0.0, max_value=15.0, value=0.0, key=f"t1_{i}_{selected_subject}")
        with col2: t2 = st.number_input("Class Test 2 (15)", min_value=0.0, max_value=15.0, value=0.0, key=f"t2_{i}_{selected_subject}")
        with col3: gw = st.number_input("Group Work (10)", min_value=0.0, max_value=10.0, value=0.0, key=f"gw_{i}_{selected_subject}")
        with col4: proj = st.number_input("Project Work (20)", min_value=0.0, max_value=20.0, value=0.0, key=f"proj_{i}_{selected_subject}")
        with col5: exam = st.number_input("Exam (100)", min_value=0.0, max_value=100.0, value=0.0, key=f"exam_{i}_{selected_subject}")

        st.session_state.score_data[score_key][name] = {"t1": t1, "t2": t2, "gw": gw, "proj": proj, "exam": exam}
        st.markdown("---")

    st.success("✅ Scores auto-save as you type!")

with tab3:
    st.header(f"Report Preview - {st.session_state.current_grade} {st.session_state.current_term}")
    if selected_name and selected_name != "No students":
        student = students[students["STUDENT NAME"] == selected_name].iloc[0]
        
        st.markdown(f"<h2 style='text-align: center;'>OTERKOPOLU RC JHS - {st.session_state.current_grade}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>{st.session_state.current_term} 2025/2026</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center;'>{student.get('STUDENT NAME', '')}</h4>", unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("**SUBJECT RESULTS**")
        data = []
        total_sum = 0
        count = 0
        grades_dict = {}

        for sub in ["ENGLISH LANGUAGE", "SOCIAL STUDIES", "CAREER TECHNOLOGY", "GHANAIAN LANGUAGE", "MATHEMATICS", "INTEGRATED SCIENCE", "COMPUTING", "CREATIVE ARTS", "R.M.E"]:
            class_a = exam_b = total = 0.0
            grade = 9
            remark = "Lowest"

            score_key = (current_key, sub)
            if score_key in st.session_state.score_data and selected_name in st.session_state.score_data[score_key]:
                s = st.session_state.score_data[score_key][selected_name]
                t1 = s.get("t1", 0)
                t2 = s.get("t2", 0)
                gw = s.get("gw", 0)
                proj = s.get("proj", 0)
                exam = s.get("exam", 0)

                sba_raw = t1 + t2 + gw + proj
                class_a = round((sba_raw / 60) * 50, 1)
                exam_b = round(exam / 2, 1)
                total = round(class_a + exam_b, 1)

                if total >= 90: grade, remark = 1, "Highest"
                elif total >= 80: grade, remark = 2, "Higher"
                elif total >= 70: grade, remark = 3, "High"
                elif total >= 60: grade, remark = 4, "High Average"
                elif total >= 55: grade, remark = 5, "Average"
                elif total >= 50: grade, remark = 6, "Low Average"
                elif total >= 40: grade, remark = 7, "Low"
                elif total >= 35: grade, remark = 8, "Lower"
                else: grade, remark = 9, "Lowest"

            data.append([sub, f"{class_a:.1f}", f"{exam_b:.1f}", f"{total:.1f}", grade, remark])
            grades_dict[sub] = grade
            total_sum += total
            count += 1

        st.dataframe(pd.DataFrame(data, columns=["Subject", "Class Score (A)", "Exam Score (B)", "Total", "Grade", "Remarks"]), use_container_width=True, hide_index=True)

        if count > 0:
            core = [grades_dict.get(s, 9) for s in ["MATHEMATICS", "ENGLISH LANGUAGE", "INTEGRATED SCIENCE", "SOCIAL STUDIES"]]
            remaining = [g for sub, g in grades_dict.items() if sub not in ["MATHEMATICS", "ENGLISH LANGUAGE", "INTEGRATED SCIENCE", "SOCIAL STUDIES"]]
            remaining.sort()
            best_two = remaining[:2]
            aggregate = sum(core) + sum(best_two)

            st.markdown("---")
            st.markdown("**OVERALL PERFORMANCE**")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Raw Score (Total for all Subjects)", f"{total_sum:.1f}")
            with col2:
                st.metric("Aggregate", aggregate)

        st.markdown("---")
        st.write(f"**Attendance:** {student.get('DAYS PRESENT', 0)} / {student.get('OUT OF', 0)}")
        st.write(f"**Conduct:** {student.get('CONDUCT', '')}")
        st.write(f"**Talents & Interests:** {student.get('TALENTS & INTERESTS', '')}")
        st.write(f"**Class Teacher Remark:** {student.get('CLASS TEACHER REMARK', '')}")
        st.write(f"**Head Teacher Remark:** {student.get('HEAD TEACHER REMARK', '')}")

        if st.button("📄 Download PDF Report Card", type="primary"):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width/2, height - 50, "OTERKOPOLU RC JHS")
            c.setFont("Helvetica", 14)
            c.drawCentredString(width/2, height - 80, f"{st.session_state.current_grade} - {st.session_state.current_term} 2025/2026")
            c.drawCentredString(width/2, height - 110, f"{student.get('STUDENT NAME', '')}")

            y = height - 160
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "SUBJECT")
            c.drawString(220, y, "Class Score (A)")
            c.drawString(320, y, "Exam Score (B)")
            c.drawString(420, y, "Total")
            c.drawString(480, y, "Grade")
            c.drawString(540, y, "Remarks")
            y -= 20
            c.line(50, y + 15, 570, y + 15)

            c.setFont("Helvetica", 10)
            for row in data:
                c.drawString(50, y, str(row[0])[:35])
                c.drawString(230, y, str(row[1]))
                c.drawString(330, y, str(row[2]))
                c.drawString(430, y, str(row[3]))
                c.drawString(490, y, str(row[4]))
                c.drawString(540, y, str(row[5]))
                y -= 18

            y -= 30
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"Raw Score (Total): {total_sum:.1f}   |   Aggregate: {aggregate}")

            y -= 40
            c.setFont("Helvetica", 10)
            c.drawString(50, y, f"Attendance: {student.get('DAYS PRESENT', 0)} / {student.get('OUT OF', 0)}")
            y -= 18
            c.drawString(50, y, f"Conduct: {student.get('CONDUCT', '')}")
            y -= 18
            c.drawString(50, y, f"Talents & Interests: {student.get('TALENTS & INTERESTS', '')}")
            y -= 18
            c.drawString(50, y, f"Class Teacher Remark: {student.get('CLASS TEACHER REMARK', '')}")
            y -= 18
            c.drawString(50, y, f"Head Teacher Remark: {student.get('HEAD TEACHER REMARK', '')}")

            c.save()
            buffer.seek(0)
            b64 = base64.b64encode(buffer.read()).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="{student.get("STUDENT NAME", "Student")}_Report.pdf">📥 Click here to Download PDF Report Card</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("PDF generated successfully!")

    else:
        st.info("Select a student from the sidebar.")

st.sidebar.info(f"Current: {st.session_state.current_grade} - {st.session_state.current_term}")