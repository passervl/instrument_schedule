import streamlit as st

def side_bar():
    side = st.sidebar()
    side.title('Navigation')
    side.radio('Go to', ['Home', 'Report'])
    img = side.camera_input("Take a picture")
    if img:
        side.image(img, use_column_width=True)
    return side

def home():
    st.title('Home')
    st.write('This is a home page')
    st.write('To get data, please go to Report page')
    st.write('To get schedule, please go to Schedule page')

def report():
    st.title('Report')
    st.write('This is a report for instrument data')
