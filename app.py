
import io
import os
import uuid
from datetime import date

import streamlit as st
import pymupdf as fitz
import pytesseract
from PIL import Image

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

st.set_page_config(
    page_title="MediKiosk",
    page_icon="🏥",
    layout="wide"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "patients" not in st.session_state:
    st.session_state.patients = []

if "current_case_id" not in st.session_state:
    st.session_state.current_case_id = None


def get_current_case():
    case_id = st.session_state.current_case_id

    for case in st.session_state.patients:
        if case["case_id"] == case_id:
            return case

    return None


def make_clinical_summary(case):
    patient = case["patient"]
    history = case.get("history", {})
    report_text = case.get("report_text", "")

    sections = [
        "MEDIKIOSK - CLINICAL SUMMARY",
        "=" * 35,
        "",
        "PATIENT DETAILS",
        f"Patient Name: {patient['name']}",
        f"Age: {patient['age']}",
        f"Language: {patient['language']}",
        f"Department: {patient['department']}",
        f"Visit Date: {patient['visit_date']}",
        "",
        "MEDICAL HISTORY",
    ]

    fields = [
        ("Chief Complaint", "Chief complaint"),
        ("Duration", "Duration of symptoms"),
        ("Other Symptoms", "Other symptoms"),
        ("Past History", "Past illnesses or surgeries"),
        ("Medicines", "Current medicines"),
        ("Allergies", "Allergies"),
        ("Family History", "Family medical history"),
        ("Personal History", "Diet, sleep and lifestyle"),
    ]

    for key, label in fields:
        sections.append(
            f"{label}: {history.get(key, '') or 'Not provided'}"
        )

    sections.extend([
        "",
        "MEDICAL REPORT FINDINGS",
        report_text or "No medical report text uploaded.",
        "",
        "DOCTOR'S NOTES",
        case.get("doctor_notes", "") or "Not provided",
        "",
        "IMPORTANT DISCLAIMER",
        "This is an automatically organized summary, not a diagnosis.",
        "Verify all extracted information against the original documents.",
        "A qualified doctor must review the case.",
    ])

    return "\n".join(sections)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🏥 MediKiosk")
st.subheader("Patient Case-Taking Software")

st.write(
    "A digital system for patient registration, medical history, "
    "medical report scanning and doctor review."
)

st.info(
    "Demonstration application. Use fictional patient information. "
    "This application does not provide a medical diagnosis."
)

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Registration",
    "2. Medical History",
    "3. Report Scanning",
    "4. Clinical Summary",
    "5. Doctor Dashboard",
])

# ==================================================
# STEP 1: PATIENT REGISTRATION
# ==================================================

with tab1:
    st.header("1. Patient Registration")

    with st.form("registration_form"):
        name = st.text_input("Patient Name")

        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=25
        )

        language = st.selectbox(
            "Preferred Language",
            ["English", "Kannada", "Hindi", "Tamil", "Telugu", "Other"]
        )

        department = st.selectbox(
            "Department",
            [
                "General Medicine",
                "Ayurveda",
                "Cardiology",
                "Other"
            ]
        )

        visit_date = st.date_input("Visit Date", value=date.today())

        consent = st.checkbox(
            "I consent to this demonstration"
        )

        register_button = st.form_submit_button(
            "Register Patient"
        )

    if register_button:
        if not name.strip():
            st.error("Please enter the patient name.")
        elif not consent:
            st.warning("Please confirm consent.")
        else:
            patient = {
                "name": name.strip(),
                "age": age,
                "language": language,
                "department": department,
                "visit_date": str(visit_date),
            }

            case = {
                "case_id": str(uuid.uuid4())[:8],
                "patient": patient,
                "history": {},
                "report_text": "",
                "uploaded_report_names": [],
                "summary": "",
                "doctor_notes": "",
                "review_status": "Pending",
            }

            st.session_state.patients.append(case)
            st.session_state.current_case_id = case["case_id"]

            st.success(
                f"Patient registered! Case ID: {case['case_id']}"
            )
            st.info(
                "Continue to Step 2: Medical History."
            )

    current_case = get_current_case()

    if current_case:
        st.caption(
            f"Current patient: {current_case['patient']['name']} "
            f"| Case ID: {current_case['case_id']}"
        )

# ==================================================
# STEP 2: MEDICAL HISTORY
# ==================================================

with tab2:
    st.header("2. Medical History Questionnaire")

    case = get_current_case()

    if not case:
        st.warning("Please register a patient in Step 1 first.")
    else:
        st.write(
            f"Patient: **{case['patient']['name']}**"
        )

        old_history = case.get("history", {})

        with st.form("history_form"):
            complaint = st.text_area(
                "Chief Complaint",
                value=old_history.get("Chief complaint", ""),
                placeholder="Example: Fever and headache"
            )

            duration = st.text_input(
                "Duration of Symptoms",
                value=old_history.get("Duration", ""),
                placeholder="Example: 2 days"
            )

            symptoms = st.text_area(
                "Other Symptoms",
                value=old_history.get("Other symptoms", "")
            )

            past = st.text_area(
                "Past Illnesses or Surgeries",
                value=old_history.get("Past history", "")
            )

            medicines = st.text_area(
                "Current Medicines",
                value=old_history.get("Medicines", "")
            )

            allergies = st.text_area(
                "Drug or Other Allergies",
                value=old_history.get("Allergies", "")
            )

            family = st.text_area(
                "Family Medical History",
                value=old_history.get("Family history", "")
            )

            personal = st.text_area(
                "Diet, Sleep and Lifestyle",
                value=old_history.get("Personal history", "")
            )

            history_button = st.form_submit_button(
                "Save Medical History"
            )

        if history_button:
            if not complaint.strip():
                st.error("Please enter the chief complaint.")
            else:
                case["history"] = {
                    "Chief complaint": complaint.strip(),
                    "Duration": duration.strip(),
                    "Other symptoms": symptoms.strip(),
                    "Past history": past.strip(),
                    "Medicines": medicines.strip(),
                    "Allergies": allergies.strip(),
                    "Family history": family.strip(),
                    "Personal history": personal.strip(),
                }

                # Refresh the summary when history changes.
                case["summary"] = ""

                st.success("Medical history saved successfully!")

# ==================================================
# STEP 3: MEDICAL REPORT SCANNING
# ==================================================

with tab3:
    st.header("3. Medical Report Scanning")

    case = get_current_case()

    if not case:
        st.warning("Please register a patient in Step 1 first.")
    else:
        st.write(
            f"Patient: **{case['patient']['name']}**"
        )

        st.write(
            "Upload a PDF, prescription image or laboratory report. "
            "Scanned PDFs and images are processed using OCR."
        )

        uploaded_files = st.file_uploader(
            "Choose medical reports",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key=f"reports_{case['case_id']}"
        )

        if st.button(
            "Extract and Save Report Text",
            key=f"extract_{case['case_id']}"
        ):
            if not uploaded_files:
                st.warning("Please upload at least one report.")
            else:
                all_text = []
                file_names = []
                extraction_errors = []

                with st.spinner("Reading uploaded reports..."):
                    for uploaded_file in uploaded_files:
                        file_names.append(uploaded_file.name)
                        file_bytes = uploaded_file.getvalue()

                        try:
                            if uploaded_file.name.lower().endswith(".pdf"):
                                pdf = fitz.open(
                                    stream=file_bytes,
                                    filetype="pdf"
                                )

                                try:
                                    for page_number, page in enumerate(pdf):
                                        page_text = page.get_text().strip()

                                        # Use OCR for scanned PDF pages.
                                        if not page_text:
                                            pix = page.get_pixmap(
                                                matrix=fitz.Matrix(2, 2),
                                                alpha=False
                                            )

                                            page_image = Image.open(
                                                io.BytesIO(
                                                    pix.tobytes("png")
                                                )
                                            )

                                            page_text = (
                                                pytesseract.image_to_string(
                                                    page_image,
                                                    lang="eng"
                                                ).strip()
                                            )

                                        all_text.append(
                                            f"\nFILE: {uploaded_file.name}"
                                            f"\nPAGE: {page_number + 1}\n"
                                            f"{page_text}"
                                        )
                                finally:
                                    pdf.close()

                            else:
                                image_file = Image.open(
                                    io.BytesIO(file_bytes)
                                ).convert("RGB")

                                image_text = (
                                    pytesseract.image_to_string(
                                        image_file,
                                        lang="eng"
                                    ).strip()
                                )

                                all_text.append(
                                    f"\nFILE: {uploaded_file.name}\n"
                                    f"{image_text}"
                                )

                        except Exception as error:
                            extraction_errors.append(
                                f"{uploaded_file.name}: {error}"
                            )

                extracted_text = "\n\n".join(all_text).strip()

                case["report_text"] = extracted_text
                case["uploaded_report_names"] = file_names
                case["summary"] = ""

                if extracted_text:
                    st.success("Report text extracted and saved!")
                    st.text_area(
                        "Extracted Text — Verify Against Original",
                        value=extracted_text,
                        height=250,
                        key=f"extracted_preview_{case['case_id']}"
                    )
                else:
                    st.warning(
                        "No readable text was extracted. "
                        "Try a clearer report."
                    )

                for error_message in extraction_errors:
                    st.error(error_message)

        if case.get("uploaded_report_names"):
            st.write("**Saved reports:**")
            for report_name in case["uploaded_report_names"]:
                st.write(f"- {report_name}")

# ==================================================
# STEP 4: CLINICAL SUMMARY
# ==================================================

with tab4:
    st.header("4. Clinical Summary")

    case = get_current_case()

    if not case:
        st.warning("Please register a patient first.")
    elif not case.get("history"):
        st.warning("Please save the medical history in Step 2 first.")
    else:
        st.write(
            "Create a structured summary for the doctor to review."
        )

        if st.button(
            "Generate Clinical Summary",
            key=f"summary_{case['case_id']}"
        ):
            case["summary"] = make_clinical_summary(case)

        if case.get("summary"):
            st.success("Clinical summary is ready for review.")

            st.text_area(
                "Generated Clinical Summary",
                value=case["summary"],
                height=400,
                key=f"summary_view_{case['case_id']}"
            )

            st.download_button(
                "Download Clinical Summary",
                data=case["summary"],
                file_name=f"clinical_summary_{case['case_id']}.txt",
                mime="text/plain",
                key=f"summary_download_{case['case_id']}"
            )

            st.warning(
                "This version automatically organizes information; "
                "it does not use a real AI model or diagnose diseases. "
                "The doctor must verify the summary and original reports."
            )
        else:
            st.info(
                "Click Generate Clinical Summary after saving "
                "the medical history."
            )

# ==================================================
# STEP 5: DOCTOR DASHBOARD
# ==================================================

with tab5:
    st.header("5. Doctor Dashboard")

    patients = st.session_state.patients

    if not patients:
        st.info("No patient cases yet. Register a patient first.")
    else:
        total_patients = len(patients)
        pending_reviews = sum(
            1 for item in patients
            if item["review_status"] == "Pending"
        )
        completed_reviews = total_patients - pending_reviews

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Cases", total_patients)
        col2.metric("Pending Reviews", pending_reviews)
        col3.metric("Reviewed Cases", completed_reviews)

        st.divider()

        for item in reversed(patients):
            patient = item["patient"]

            with st.expander(
                f"{patient['name']} | Age {patient['age']} "
                f"| Case {item['case_id']}"
            ):
                st.write("**Department:**", patient["department"])
                st.write("**Language:**", patient["language"])
                st.write("**Visit Date:**", patient["visit_date"])

                st.write("**Review Status:**", item["review_status"])

                st.subheader("Medical History")

                if item["history"]:
                    for key, value in item["history"].items():
                        st.write(
                            f"**{key}:** {value or 'Not provided'}"
                        )
                else:
                    st.write("Medical history not yet saved.")

                st.subheader("Uploaded Reports")

                report_names = item.get(
                    "uploaded_report_names", []
                )

                if report_names:
                    for report_name in report_names:
                        st.write(f"- {report_name}")
                else:
                    st.write("No reports uploaded.")

                st.subheader("Clinical Summary")

                if item.get("summary"):
                    st.text_area(
                        "Summary",
                        value=item["summary"],
                        height=220,
                        key=f"dashboard_summary_{item['case_id']}"
                    )
                else:
                    st.write("Summary has not been generated.")

                st.subheader("Doctor's Review")

                notes = st.text_area(
                    "Doctor's Notes",
                    value=item.get("doctor_notes", ""),
                    placeholder="Enter verified observations...",
                    key=f"doctor_notes_{item['case_id']}"
                )

                review_status = st.selectbox(
                    "Review Status",
                    ["Pending", "Reviewed"],
                    index=(
                        1 if item["review_status"] == "Reviewed"
                        else 0
                    ),
                    key=f"review_status_{item['case_id']}"
                )

                if st.button(
                    "Save Doctor Review",
                    key=f"save_review_{item['case_id']}"
                ):
                    item["doctor_notes"] = notes
                    item["review_status"] = review_status
                    st.success("Doctor review saved for this session.")

                if item.get("summary"):
                    dashboard_download = (
                        item["summary"]
                        + "\n\nDoctor's Notes:\n"
                        + item.get("doctor_notes", "")
                    )

                    st.download_button(
                        "Download Case Summary",
                        data=dashboard_download,
                        file_name=f"case_{item['case_id']}.txt",
                        mime="text/plain",
                        key=f"dashboard_download_{item['case_id']}"
                    )

        st.caption(
            "Demo dashboard: patient records are stored in session memory. "
            "They may be lost when the session resets. "
            "A production system needs secure persistent storage and access control."
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption(
    "MediKiosk | Patient Case-Taking Demonstration | "
    "Clinical decisions must be made by qualified healthcare professionals."
)
