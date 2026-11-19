from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="My First Streamlit App", page_icon="👋")
st.title("Hi, Hello! 👋")
st.write("Welcome to my first Streamlit app.")

with st.form("details_form"):
    name = st.text_input("Enter your name")
    email = st.text_input("Enter your email")
    age = st.number_input("Age", min_value=1, max_value=100, value=20)
    bio = st.text_area("Introduce yourself")
    language = st.selectbox("Languages", ["Python", "Java", "React", "CSS & HTML", "Streamlit"])
    skills = st.multiselect("Skills", ["Machine Learning", "Deep Learning", "Artificial Intelligence", "Database"])
    level = st.slider("Skill level", 0, 10, 5)
    gender = st.radio("Choose one", ["Male", "Female", "Other"])
    dob = st.date_input("Date of birth", value=date(2003, 1, 1),
                        min_value=date(1980, 1, 1), max_value=date.today())
    file = st.file_uploader("Upload a file", type=["csv", "pdf", "png"])
    photo = st.camera_input("Take a photo")
    color = st.color_picker("Pick a color", "#4B8BBE")

    submitted = st.form_submit_button("Submit")

if submitted:
    if not name.strip():
        st.warning("Please enter your name first.")
    else:
        st.success(f"Hello, {name}! Your details were submitted.")
        st.subheader("Your Details")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {name}")
            st.write(f"**Email:** {email}")
            st.write(f"**Age:** {age}")
            st.write(f"**Gender:** {gender}")
            st.write(f"**Date of birth:** {dob}")
        with col2:
            st.write(f"**Language:** {language}")
            st.write(f"**Skills:** {', '.join(skills) if skills else 'None selected'}")
            st.write(f"**Skill level:** {level}/10")
            st.write(f"**Favourite color:** {color}")
            st.color_picker("Color preview", color, disabled=True)

        st.write("**About you:**")
        st.info(bio if bio.strip() else "No introduction provided.")

        if photo:
            st.image(photo, caption="Your photo", width=250)

        if file:
            st.write(f"**Uploaded file:** {file.name}")
            if file.type == "text/csv":
                st.dataframe(pd.read_csv(file))
            elif file.type.startswith("image"):
                st.image(file, width=250)
    