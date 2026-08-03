import streamlit as st

from app.services.chat_service import ChatService


def render_chat_section(report, df):

    if not st.session_state.analysis:
        return

    st.subheader("💬 Chat with your Dataset")

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Ask anything about your dataset..."
    )

    if prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        chat = ChatService()

        with st.spinner("Thinking..."):

            answer = chat.ask(
                report,
                df,
                prompt
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        with st.chat_message("assistant"):
            st.markdown(answer)

    st.divider()