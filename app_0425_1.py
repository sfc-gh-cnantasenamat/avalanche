import streamlit as st
import altair as alt
import pandas as pd

st.set_page_config(page_title="Avalanche Data Set",
                    page_icon="🏔️",
                    layout="wide")

st.title("🏔️ Avalanche Data Set")

df = pd.read_csv("data/customer_reviews.csv")

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
tab = st.tabs(['Daily / Weekly / Monthly', 'Product', 'Data'])

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
