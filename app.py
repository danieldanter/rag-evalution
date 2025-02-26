import streamlit as st
import pandas as pd
import io

# Load the Excel file
excel_file = "combined_rag_answers.xlsx"
df = pd.read_excel(excel_file)


# Add an evaluation column if it doesn't exist
if "evaluation" not in df.columns:
    df["evaluation"] = ""

# Streamlit app title
st.title("Answer Evaluation App")

# Initialize session state for question navigation and evaluation status
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "evaluated" not in st.session_state:
    st.session_state.evaluated = [False] * len(df)  # Track if each question is evaluated

# Sidebar for navigation (disabled until evaluation is submitted)
st.sidebar.header("Navigation")
question_index = st.session_state.question_index
st.sidebar.slider("Select Question", 0, len(df) - 1, question_index, disabled=True)

# Display the selected question and ground truth
question = df.loc[question_index, "question"]
ground_truth = df.loc[question_index, "ground_truth"]
st.write(f"**Question {question_index + 1}:** {question}")
st.write(f"**Ground Truth:** {ground_truth}")

# Display the two answers
answer_rag1 = df.loc[question_index, "answer_rag1"]
answer_rag2 = df.loc[question_index, "answer_rag2"]
st.markdown("---")  # Horizontal line after Answer RAG1
st.write("**Answer RAG1:**")
st.write(answer_rag1)
st.markdown("---")  # Horizontal line after Answer RAG1

st.write("**Answer RAG2:**")
st.write(answer_rag2)
st.markdown("---")  # Horizontal line after Answer RAG1

# Checkboxes for user evaluation
st.subheader("Which answer is better?")
col1, col2 = st.columns(2)
with col1:
    rag1_selected = st.checkbox("Answer RAG1 is better", key=f"rag1_{question_index}")
with col2:
    rag2_selected = st.checkbox("Answer RAG2 is better", key=f"rag2_{question_index}")

# Buttons for submitting evaluation and moving to the next question
col3, col4 = st.columns(2)
with col3:
    if st.button("Submit Evaluation", key=f"submit_{question_index}"):
        if rag1_selected and rag2_selected:
            evaluation = "Both"
        elif rag1_selected:
            evaluation = "Answer RAG1"
        elif rag2_selected:
            evaluation = "Answer RAG2"
        else:
            evaluation = "None"
        
        # Update the DataFrame with the evaluation
        df.loc[question_index, "evaluation"] = evaluation
        st.success(f"Evaluation saved: {evaluation}")

        # Save the updated DataFrame back to the Excel file
        df.to_excel(excel_file, index=False)

        # Mark this question as evaluated
        st.session_state.evaluated[question_index] = True

        # Move to the next unevaluated question
        next_index = question_index + 1
        while next_index < len(df) and st.session_state.evaluated[next_index]:
            next_index += 1
        if next_index < len(df):
            st.session_state.question_index = next_index
        else:
            st.warning("All questions have been evaluated!")

with col4:
    # Show "Next" button only if the current question is evaluated
    if st.session_state.evaluated[question_index]:
        if st.button("Next", key=f"next_{question_index}"):
            next_index = question_index + 1
            while next_index < len(df) and st.session_state.evaluated[next_index]:
                next_index += 1
            if next_index < len(df):
                st.session_state.question_index = next_index
            else:
                st.warning("This is the last unevaluated question!")
    else:
        st.write("Please submit an evaluation before proceeding to the next question.")

# Display current evaluation (if any)
current_eval = df.loc[question_index, "evaluation"]
if current_eval:
    st.write(f"**Current Evaluation:** {current_eval}")
else:
    st.write("**Current Evaluation:** Not evaluated yet")

# Check if all questions are evaluated
all_evaluated = all(st.session_state.evaluated)

# Add a download button if all questions are evaluated or always show it
st.subheader("Download Results")
if all_evaluated:
    st.write("All questions have been evaluated. You can now download the results.")
buffer = io.BytesIO()
df.to_excel(buffer, index=False)
buffer.seek(0)
st.download_button(
    label="Download Excel File",
    data=buffer,
    file_name="evaluated_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Optional: Show the full DataFrame for debugging
if st.checkbox("Show full table"):
    st.write(df)