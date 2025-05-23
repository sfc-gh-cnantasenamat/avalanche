# -- Create AVALANCHE_DB.AVALANCHE_SCHEMA.CUSTOMER_REVIEWS table
# CREATE TABLE AVALANCHE_DB.AVALANCHE_SCHEMA.CUSTOMER_REVIEWS AS
# SELECT * FROM AVALANCHE_DB.PUBLIC.CUSTOMER_REVIEWS;

# M2 Lab2
import streamlit as st
import altair as alt
import pandas as pd
from snowflake.snowpark.context import get_active_session
from snowflake.core import Root # requires snowflake>=0.8.0
# Install snowflake.core

# Get the current credentials
# session = get_active_session()
session = st.connection("snowflake").session()

st.set_page_config(page_title="Avalanche Data Set",
                    page_icon="🏔️",
                    layout="wide")

st.title("🏔️ Avalanche Data Set")

df = session.sql("SELECT * FROM AVALANCHE_DB.AVALANCHE_SCHEMA.CUSTOMER_REVIEWS").to_pandas()
# # # df = pd.read_csv("data/customer_reviews.csv")
# df

# Ensure SENTIMENT_SCORE is numeric
df['SENTIMENT_SCORE'] = pd.to_numeric(df['SENTIMENT_SCORE'])

# Convert DATE to datetime explicitly
df['DATE'] = pd.to_datetime(df['DATE'])

# Add date components
df['DAY'] = df['DATE'].dt.day
df['WEEK'] = df['DATE'].dt.isocalendar().week
df['MONTH'] = df['DATE'].dt.month
df['YEAR'] = df['DATE'].dt.year

# Product sentiment score
product_bar_chart = alt.Chart(df).mark_bar(size=15).encode(
    y=alt.Y('PRODUCT:N',
            axis=alt.Axis(
                labelAngle=0,  # Horizontal labels
                labelOverlap=False,  # Prevent label overlap
                labelPadding=10  # Add some padding
            )
    ),
    x=alt.X('mean(SENTIMENT_SCORE):Q',  # Aggregate mean sentiment score
            title='MEAN SENTIMENT_SCORE'),
    color=alt.condition(
        alt.datum.mean_SENTIMENT_SCORE >= 0,
        alt.value('#2ecc71'),  # green for positive
        alt.value('#e74c3c')   # red for negative
    ),
    tooltip=['PRODUCT:N', 'mean(SENTIMENT_SCORE):Q']
).properties(
    height=400
)

# Create tabs
tab = st.tabs(['Daily / Weekly / Monthly', 'Product', 'Data', 'Chat'])
# tab = st.tabs(['Daily / Weekly / Monthly', 'Product', 'Data'])

# Display the chart
with tab[0]:
    st.subheader('Sentiment score analysis')

    # Add time period selection
    time_period = st.selectbox(
        "Select time period",
        options=["Daily", "Weekly", "Monthly"]
    )

    # Process data based on selected time period
    if time_period == "Daily":
        period_label = "Daily"
        chart_data = df.copy()
        x_encoding = alt.X('DATE:T', axis=alt.Axis(format='%Y-%m-%d', labelAngle=90))
        tooltip_encoding = ['DATE:T', 'SENTIMENT_SCORE:Q', 'PRODUCT:N']
        avg_sentiment = chart_data['SENTIMENT_SCORE'].mean()
        highest_sentiment = chart_data['SENTIMENT_SCORE'].max()
        lowest_sentiment = chart_data['SENTIMENT_SCORE'].min()

    elif time_period == "Weekly":
        period_label = "Weekly"
        chart_data = df.groupby(['YEAR', 'WEEK', 'PRODUCT']).agg(
            SENTIMENT_SCORE=('SENTIMENT_SCORE', 'mean'),
            DATE=('DATE', 'first')
        ).reset_index()
        chart_data['WEEK_LABEL'] = chart_data.apply(lambda row: f"{row['YEAR']}-W{int(row['WEEK']):02d}", axis=1)
        x_encoding = alt.X('WEEK_LABEL:N', sort=None, title='Week') # Use nominal type for explicit labels
        tooltip_encoding = ['WEEK_LABEL:N', 'SENTIMENT_SCORE:Q', 'PRODUCT:N']
        avg_sentiment = chart_data['SENTIMENT_SCORE'].mean()
        highest_sentiment = chart_data['SENTIMENT_SCORE'].max()
        lowest_sentiment = chart_data['SENTIMENT_SCORE'].min()

    else:  # Monthly
        period_label = "Monthly"
        chart_data = df.groupby(['YEAR', 'MONTH', 'PRODUCT']).agg(
            SENTIMENT_SCORE=('SENTIMENT_SCORE', 'mean'),
            DATE=('DATE', 'first')
        ).reset_index()
        chart_data['MONTH_LABEL'] = chart_data.apply(lambda row: f"{row['YEAR']}-{row['MONTH']:02d}", axis=1)
        x_encoding = alt.X('MONTH_LABEL:N', sort=None, title='Month') # Use nominal type for explicit labels
        tooltip_encoding = ['MONTH_LABEL:N', 'SENTIMENT_SCORE:Q', 'PRODUCT:N']
        avg_sentiment = chart_data['SENTIMENT_SCORE'].mean()
        highest_sentiment = chart_data['SENTIMENT_SCORE'].max()
        lowest_sentiment = chart_data['SENTIMENT_SCORE'].min()

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label=f"{period_label} Average Sentiment",
            value=f"{avg_sentiment:.2f}" if 'avg_sentiment' in locals() else "N/A",
        )

    with col2:
        st.metric(
            label=f"{period_label} Highest Sentiment",
            value=f"{highest_sentiment:.2f}" if 'highest_sentiment' in locals() else "N/A",
        )

    with col3:
        st.metric(
            label=f"{period_label} Lowest Sentiment",
            value=f"{lowest_sentiment:.2f}" if 'lowest_sentiment' in locals() else "N/A",
        )

    # Update chart based on selected period
    sentiment_chart = alt.Chart(chart_data).mark_bar(size=15).encode(
        x=x_encoding,
        y=alt.Y('SENTIMENT_SCORE:Q'),
        color=alt.condition(
            alt.datum.SENTIMENT_SCORE >= 0,
            alt.value('#2ecc71'),  # green for positive
            alt.value('#e74c3c')   # red for negative
        ),
        tooltip=tooltip_encoding
    ).properties(
        height=400
    )

    st.altair_chart(sentiment_chart, use_container_width=True)

with tab[1]:
    st.subheader('Product sentiment score')
    st.altair_chart(product_bar_chart, use_container_width=True)

with tab[2]:
    st.subheader('Prepared Data set')
    st.dataframe(df)

##################################################################

# M3 Lab3
MODELS = ["mistral-large", "claude-3-5-sonnet", "llama3-8b"]

def init_chatbot():
    if "service_metadata" not in st.session_state:
        services = session.sql("SHOW CORTEX SEARCH SERVICES;").collect()
        service_metadata = []
        if services:
            for s in services:
                svc_name = s["name"]
                svc_search_col = session.sql(
                    f"DESC CORTEX SEARCH SERVICE {svc_name};"
                ).collect()[0]["search_column"]
                service_metadata.append(
                    {"name": svc_name, "search_column": svc_search_col}
                )

        st.session_state.service_metadata = service_metadata
    
    # Sidebar
    st.sidebar.title("⚙️ Chat settings")
    
    st.sidebar.selectbox(
        "Select cortex search service:",
        [s["name"] for s in st.session_state.service_metadata],
        key="selected_cortex_search_service",
    )

    st.sidebar.button("Clear conversation", key="clear_conversation")
    st.sidebar.toggle("Debug", key="debug", value=False)
    st.sidebar.toggle("Use chat history", key="use_chat_history", value=True)

    with st.sidebar.expander("Advanced options"):
        st.selectbox("Select model:", MODELS, key="model_name")
        st.number_input(
            "Select number of context chunks",
            value=20,
            key="num_retrieved_chunks",
            min_value=1,
            max_value=20,
        )
        st.number_input(
            "Select number of messages to use in chat history",
            value=3,
            key="num_chat_messages",
            min_value=1,
            max_value=20,
        )

    st.sidebar.expander("Session State").write(st.session_state)
    if st.session_state.clear_conversation or "messages" not in st.session_state:
        st.session_state.messages = []

def query_cortex_search_service(query):
    db, schema = session.get_current_database(), session.get_current_schema()

    cortex_search_service = (
        root.databases[db]
        .schemas[schema]
        .cortex_search_services[st.session_state.selected_cortex_search_service]
    )

    context_documents = cortex_search_service.search(
        query, columns=[], limit=st.session_state.num_retrieved_chunks
    )
    results = context_documents.results

    service_metadata = st.session_state.service_metadata
    search_col = [s["search_column"] for s in service_metadata
                    if s["name"] == st.session_state.selected_cortex_search_service][0]

    context_str = ""
    for i, r in enumerate(results):
        context_str += f"Context document {i+1}: {r[search_col]} \n" + "\n"

    if st.session_state.debug:
        st.sidebar.text_area("Context documents", context_str, height=500)

    return context_str

def get_chat_history():
    start_index = max(
        0, len(st.session_state.messages) - st.session_state.num_chat_messages
    )
    return st.session_state.messages[start_index : len(st.session_state.messages) - 1]

def complete(model, prompt):
    return session.sql("SELECT snowflake.cortex.complete(?,?)", (model, prompt)).collect()[0][0]

def make_chat_history_summary(chat_history, question):
    prompt = f"""
        [INST]
        Based on the chat history below and the question, generate a query that extend the question
        with the chat history provided. The query should be in natural language.
        Answer with only the query. Do not add any explanation.

        <chat_history>
        {chat_history}
        </chat_history>
        
        <question>
        {question}
        </question>
        [/INST]
    """

    summary = complete(st.session_state.model_name, prompt)

    if st.session_state.debug:
        st.sidebar.text_area(
            "Chat history summary", summary.replace("$", "\$"), height=150
        )

    return summary

def create_prompt(user_question):
    """
    Create a prompt for the language model by combining the user question with context retrieved
    from the cortex search service and chat history (if enabled). Format the prompt according to
    the expected input format of the model.

    Args:
        user_question (str): The user's question to generate a prompt for.

    Returns:
        str: The generated prompt for the language model.
    """
    if st.session_state.use_chat_history:
        chat_history = get_chat_history()
        if chat_history != []:
            question_summary = make_chat_history_summary(chat_history, user_question)
            prompt_context = query_cortex_search_service(question_summary)
        else:
            prompt_context = query_cortex_search_service(user_question)
    else:
        prompt_context = query_cortex_search_service(user_question)
        chat_history = ""

    prompt = f"""
            [INST]
            You are a helpful AI chat assistant with RAG capabilities. When a user asks you a question,
            you will also be given context provided between <context> and </context> tags. Use that context
            with the user's chat history provided in the between <chat_history> and </chat_history> tags
            to provide a summary that addresses the user's question. Ensure the answer is coherent, concise,
            and directly relevant to the user's question.

            If the user asks a generic question which cannot be answered with the given context or chat_history,
            just say "I don't know the answer to that question.

            Don't say things like "according to the provided context".

            <chat_history>
            {chat_history}
            </chat_history>
            
            <context>
            {prompt_context}
            </context>
            
            <question>
            {user_question}
            </question>
            [/INST]
            
            Answer:
        """
    return prompt

def main():
    # st.title(f":speech_balloon: Chatbot with Cortex Search and Unstructured Data")
    st.subheader("Chatbot with Cortex Search and Unstructured Data")
    
    init_chatbot()
    icons = {"assistant": "❄️", "user": "👤"}

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.markdown(message["content"])

    disable_chat = (
        "service_metadata" not in st.session_state
        or len(st.session_state.service_metadata) == 0
    )
    if question := st.chat_input("Are there any goggles review?", disabled=disable_chat):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        # Display user message in chat message container
        with st.chat_message("user", avatar=icons["user"]):
            st.markdown(question.replace("$", "\$"))

        # Display assistant response in chat message container
        with st.chat_message("assistant", avatar=icons["assistant"]):
            message_placeholder = st.empty()
            question = question.replace("'", "")
            with st.spinner("Thinking..."):
                generated_response = complete(
                    st.session_state.model_name, create_prompt(question)
                )
                message_placeholder.markdown(generated_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": generated_response}
        )

# if __name__ == "__main__":
#     session = get_active_session()
#     root = Root(session)
#     main()

with tab[3]:
    root = Root(session)
    main()
