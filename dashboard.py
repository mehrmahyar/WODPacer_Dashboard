import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import altair as alt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.cm as cm
import datetime
from st_aggrid import AgGrid



table_style = """
<style>
    table {
        border-spacing: 1px;
        border-collapse: collapse;
        background: white;
        border-radius: 6px;
        overflow: hidden;
        max-width: 800px;
        width: 100%;
        margin: 0 auto;
        position: relative;
    }

    table td,
    table th {
        padding-left: 8px;
        text-align: left;
    }

    table thead tr {
        height: 60px;
        background: #FFED86;
        font-size: 16px;
    }

    table tbody tr {
        height: 48px;
        border-bottom: 1px solid #E3F1D5;
    }

    table tbody tr:last-child {
        border: 0;
    }

    table td.l {
        text-align: right;
    }

    table td.c,
    table th.c {
        text-align: center;
    }

    table td.r {
        text-align: center;
    }

    @media (max-width: 35.5em) {
        table {
            display: block;
            max-width: none;
        }

        table thead {
            display: none;
        }

        table tbody tr {
            height: auto;
            padding: 8px 0;
        }

        table tbody tr td {
            padding-left: 45%;
            margin-bottom: 12px;
        }

        table tbody tr td:last-child {
            margin-bottom: 0;
        }

        table tbody tr td:before {
            position: absolute;
            font-weight: 700;
            width: 40%;
            left: 10px;
            top: 0;
        }

        table tbody tr td:nth-child(1):before {
            content: "Code";
        }

        table tbody tr td:nth-child(2):before {
            content: "Stock";
        }

        table tbody tr td:nth-child(3):before {
            content: "Cap";
        }

        table tbody tr td:nth-child(4):before {
            content: "Inch";
        }

        table tbody tr td:nth-child(5):before {
            content: "Box Type";
        }
    }
</style>
"""

# Define the HTML content with the CSS component
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Percentage Scale Component</title>
<style>
/* CSS for the percentage scale component */
.percentage-scale {
  position: relative;
  width: 300px; /* Adjust width as needed */
}

.percentage-scale-header {
  margin-bottom: 10px;
}

.scale-line {
  height: 4px;
  background-color: #ccc;
  position: relative;
}

.circle-bullet {
  width: 10px;
  height: 10px;
  background-color: #007bff; /* Change color as needed */
  border-radius: 50%;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
}

.percentage-label {
  position: absolute;
  top: -30px; /* Adjust vertical position of percentage label */
  left: 0;
}
</style>
</head>
<body>

<div class="percentage-scale">
  <div class="percentage-scale-header">Percentage: 75%</div>
  <div class="scale-line">
    <div class="circle-bullet" style="left: 75%;"></div>
  </div>
  <div class="percentage-label">0%</div>
  <div class="percentage-label" style="left: 50%;">50%</div>
  <div class="percentage-label" style="left: 100%;">100%</div>
</div>

</body>
</html>
"""





st.set_page_config(
    page_title="WODPacer Dashboard",
    page_icon="/Users/mahyarmehr/Desktop/Streamlit/resources/logo_clean.jpg",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

def send_data_to_server(athlete_name, athlete_age, athlete_gender, json_data):
    # API endpoint
    url = "your_fastapi_endpoint_here"
    
    # Prepare data
    data = {
        "athlete_name": athlete_name,
        "athlete_age": athlete_age,
        "athlete_gender": athlete_gender,
        "json_data": json_data
    }
    
    # Send POST request
    response = requests.post(url, json=data)
    
    # Return response
    return response.json()

def display_feedback(feedback):
    # Display feedback using charts and tables
    # You can use Plotly, Matplotlib, or any other library for visualization here
    pass

def download_feedback(feedback):
    # Code to download feedback as a printable and downloadable version
    pass

def ms_to_mm_ss(ms):
    delta = datetime.timedelta(milliseconds=ms, microseconds=1)
    if delta.total_seconds() < 3600:  # If duration is less than an hour
        return str(delta)[2:-7]  # Exclude hours and milliseconds
    else:
        return str(delta)[:-7]  # Include hours but exclude milliseconds
    
def create_dfs(json_data):

    
    wodSummary = pd.json_normalize(json_data['wod_summary'])

    wodBreakdown = json_data['wod_breakdown']
    wb = pd.DataFrame()

    for r in range(len(wodBreakdown)):
        temp = pd.json_normalize(wodBreakdown[r])

        wb = pd.concat([wb,temp])
    wb_seq = pd.json_normalize(json_data['wod_breakdown'], 'sequences', ['round_num'])
    wb.drop(columns=['sequences','movements'], inplace = True)
    move_bd = pd.json_normalize(json_data['movement_breakdown'])
    #Zone breaksown Data
    hr_zone_bd = pd.json_normalize(json_data['hr_zone_breakdown'])
    sum_time = np.sum(hr_zone_bd['duration_ms'])
    hr_zone_bd['%'] = (hr_zone_bd['duration_ms'] / sum_time) * 100
    hr_zone_bd.rename(columns={'duration_ms':'Duration'}, inplace=True)
    hr_zone_bd['Duration'] = hr_zone_bd['Duration'].apply(lambda x: ms_to_mm_ss(x))
    hr_zone_bd['hr_zone'] = hr_zone_bd['hr_zone'].apply(lambda x: x.replace('z','Zone '))
    hr_zone_bd.rename(columns={'hr_zone':'HR Zone'}, inplace=True)
    


    return wodSummary, wb, move_bd, hr_zone_bd, wb_seq

def plot_round_analysis(json_data):

    # Convert JSON data to DataFrame
    df = pd.json_normalize(json_data, 'sequences', ['round_num'])
# Get the number of unique movement types
    num_unique_movements = len(df['movement'].unique())

    # Generate a color palette with the desired number of colors using a colormap
    color_map = cm.get_cmap('tab10', num_unique_movements)
    mov_color_palette = [f'rgb{tuple(int(val * 255) for val in color_map(i)[:3])}' for i in range(num_unique_movements)]

    # Create a dictionary mapping each movement type to a color
    mov_color = {mov: mov_color_palette[i] for i, mov in enumerate(df['movement'].unique())}

    # Add a color for the 'break' movement type
    mov_color['break'] = 'rgb(211, 211, 211)'


    # Create subplot grid
    fig = make_subplots(
        rows=1, cols=1,
        vertical_spacing=0.05
    )

    # Plot bars for movement durations
    for index, row in df.iterrows():
        fig.add_trace(
            go.Bar(
                y=[row["round_num"]],
                x=[row["duration_ms"]],
                hoverinfo="skip",
                marker=dict(color=mov_color[row["movement"]]),
                showlegend=False,
                orientation="h",
                text=[row["movement"]+"<br>" + \
                      str(ms_to_mm_ss(row["duration_ms"]))]
            ),
            row=1, col=1
        )

    # Add layout
    fig.update_layout(
        barmode="stack",
        yaxis=dict(
            tickmode='array',
            tickvals=df['round_num'].unique(),
            ticktext=['Round ' + str(round_num) for round_num in df['round_num'].unique()]
        ),
        xaxis=dict(
            visible=False,
            showticklabels=False
        ),
        yaxis2=dict(
            title='Heart Rate (bpm)',
            overlaying='y',
            side='right'
        )
    )

    # Show plot
    st.plotly_chart(fig)


def show_dashboard():
    # Title
    left_co, cent_co,last_co = st.columns(3)
    with cent_co:
        st.image("/Users/mahyarmehr/Desktop/Streamlit/resources/logo_clean.jpg",use_column_width="always")
    st.title("Wodpacer")
    st.subheader("AI-Enhanced Performance Feedback for Functional Fitness", divider='red')

    # # Athlete Details
    # athlete_name = st.text_input("Enter Athlete's Name:")
    # athlete_age = st.number_input("Enter Athlete's Age:")
    # athlete_gender = st.selectbox("Select Athlete's Gender:", ["Male", "Female"])

    # JSON File Upload
    json_file = st.file_uploader("Upload JSON File:", type=['json'])
    if st.button("Submit"):
        if json_file is not None:
            json_data = json.load(json_file)

            wodSummary, wb, move_bd, hr_zone_bd, wb_seq = create_dfs(json_data)
            wodSummary.drop(columns=['start_ms','finish_ms'], inplace=True)
            wodSummary['percentage_moving'] = round(((wodSummary['duration_ms_moving'] / wodSummary['duration_ms']) * 100),1)
            wodSummary['percentage_break'] = round(((wodSummary['duration_ms_break'] / wodSummary['duration_ms']) * 100),1)
            # Render the HTML content within the Streamlit app
            
            st.header("Wod Summary")
            # st.markdown(table_style, unsafe_allow_html=True)
            # Define the number of columns for each row
            columns_per_row = 3
            num_metrics = len(wodSummary.columns)
            num_rows = -(-num_metrics // columns_per_row)

            for i in range(num_rows):
                row = st.columns(columns_per_row)
                for j in range(columns_per_row):
                    metric_index = i * columns_per_row + j
                    if metric_index < num_metrics:
                        metric_name = wodSummary.columns[metric_index]
                        if "ms" in metric_name.split("_"):
                            value = round(wodSummary[metric_name].iloc[0],1)
                            value = ms_to_mm_ss(value)
                            metric_name = metric_name.replace("ms","").replace("_"," ")
                            row[j].metric(label=metric_name.title(), value=value)
                        elif "percentage" in metric_name.split("_"):
                            value = "%" + str(round(wodSummary[metric_name].iloc[0],1))
                            row[j].metric(label=metric_name.replace("_"," ").title(), value=value)
                        else:
                            value = round(wodSummary[metric_name].iloc[0],1)
                            row[j].metric(label=metric_name.replace("_"," ").title(), value=value)

            col1, col2 = st.columns(2)
            with col1:
                with st.container(height=100):
                    st.header("Round Analysis")
                    plot_round_analysis(json_data['wod_breakdown'])
            with col2:
                with st.container(height=100):
                    st.header("Heart Rate Zone Breakdown")
                    st.data_editor(
                        hr_zone_bd,
                        column_config= {
                            "%": st.column_config.ProgressColumn(
                                "Percentage of time spent in the zone",
                                
                                format="%.1f%%",
                                min_value=0,
                                max_value=100
                            )

                        },
                        hide_index=True
                    )


   
        else:
            st.warning("Please upload a JSON file.")

if __name__ == "__main__":
    show_dashboard()
# streamlit run show_dashboard.py