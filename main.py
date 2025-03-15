
import streamlit as st
from few_shot import FewShot
from post_generator import generate_post
def main():
    st.title("PostPilot")
    st.subheader("An automated post generator ai")
    col1,col2,col3=st.columns(3)
    fs=FewShot()
    with col1:
        selected_tags=st.selectbox("Title",options=fs.get_tags())
    with col2:
        selected_length=st.selectbox("Length",options=["Short","Medium","Long"])
    with col3:
        selected_language=st.selectbox("Language",options=["English","Hinglish"])
    if st.button("Generate"):
        post=generate_post(selected_tags,selected_length,selected_language)
        st.write(post)


if __name__=="__main__":
    main()