import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import json  # Import the json module


# Loading Data
@st.cache_data
def load_data(sheet_url):
    try:
        data = pd.read_csv(sheet_url)
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Generate Bar Chart
def generate_grouped_bar_chart(data, entity):
    filtered_df = data[data['Entity'] == entity]
    fig = px.bar(filtered_df, x='Function', y=['Applied', 'Approved', 'Unique_LCs'],
                 title=f'Grouped Bar Chart for {entity}',
                 labels={'value': 'Count', 'Function': 'Function'},
                 barmode='group')
    return fig

# Function to create a bar chart based on the specified metric
def create_bar_chart_seperate(df, entity, metric, title):
    filtered_df = df[df['Entity'] == entity]
    fig = px.bar(filtered_df, x='Function', y=metric, title=title, labels={'Function': 'Function', 'Entity': 'Entity', metric: metric}, color='Function')
    return fig

# Function to create a bar chart based on the total points of each entity
def create_bar_chart(entity_sum):
    # Convert entity sum dictionary to DataFrame
    df_entity_sum = pd.DataFrame.from_dict(entity_sum, orient='index')
    
    # Reset index to make entity a column instead of index
    df_entity_sum.reset_index(inplace=True)
    df_entity_sum.rename(columns={'index': 'Entity'}, inplace=True)
    
    # Create a bar chart using Plotly Express
    fig = px.bar(df_entity_sum, x='Entity', y='Total', title='Total Points by Entity', labels={'Entity': 'Entity', 'Total': 'Total Points'})
    return fig

# Function to calculate sum of points and unique LCs for each entity
def calculate_entity_sum(df):
    entity_sum = {}
    for index, row in df.iterrows():
        entity = row['Entity']
        app_points = row['APP_Points']
        apd_points = row['APD_Points']
        unique_lcs = row['Unique_LCs']
        
        if entity not in entity_sum:
            entity_sum[entity] = {
                'APP_Points': app_points,
                'APD_Points': apd_points,
                'Unique_LCs': unique_lcs,
                'Total': app_points + apd_points + unique_lcs
            }
        else:
            entity_sum[entity]['APP_Points'] += app_points
            entity_sum[entity]['APD_Points'] += apd_points
            entity_sum[entity]['Unique_LCs'] += unique_lcs
            entity_sum[entity]['Total'] += app_points + apd_points + unique_lcs
    
    return entity_sum


# Main Streamlit app
def main():
    st.set_page_config(layout="wide")
    st.title("Exchange Marathon Leaderboard - AIESEC In Sri Lanka")

    # URL to your Google Sheets data
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSnfmLEUELfQt94C9wgiHAsO4ydTXNK9pCJB2gyWLLkyXID4uJflVtGozLXEvTQ-lCu9ZuhJPT3KltQ/pub?gid=945643676&single=true&output=csv"

    # Load data using the cached function
    data = load_data(sheet_url)

    if data is not None:
        #st.write("Data loaded successfully:")
        #st.write(data)

        # Check if the 'Entity' column exists in the DataFrame
        if 'Entity' in data.columns:
            
            # Calculate entity sum
            entity_sum = calculate_entity_sum(data)

            # Convert entity sum to JSON object
            entity_sum_json = json.dumps(entity_sum)

            # Create the bar chart
            bar_chart = create_bar_chart(entity_sum)

            # Display the bar chart using Plotly Chart
            st.plotly_chart(bar_chart, use_container_width=True)

            # Select entity
            entities = data['Entity'].unique()
            selected_entity = st.selectbox('Select Entity', entities)

            # Generate and display grouped bar chart
            #st.plotly_chart(generate_grouped_bar_chart(data, selected_entity))


             # Create individual bar charts for each metric
            bar_chart_applied = create_bar_chart_seperate(data, selected_entity, 'Applied', f'Applied Metrics for {selected_entity}')
            bar_chart_approved = create_bar_chart_seperate(data, selected_entity, 'Approved', f'Approved Metrics for {selected_entity}')
            bar_chart_unique_lcs = create_bar_chart_seperate(data, selected_entity, 'Unique_LCs', f'Unique LCs Metrics for {selected_entity}')

            # Display the bar charts using Plotly Chart
            col1, col2, col3 = st.columns(3)

            with col1:
                st.plotly_chart(bar_chart_applied, use_container_width=True)

            with col2:
                st.plotly_chart(bar_chart_approved, use_container_width=True)

            with col3:
                st.plotly_chart(bar_chart_unique_lcs, use_container_width=True)

        else:
            st.error("The 'Entity' column does not exist in the loaded data.")
    else:
        st.error("Failed to load data.")

if __name__ == "__main__":
    main()