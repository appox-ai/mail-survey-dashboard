import json
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
from datetime import datetime

# ---------------------------
# 1. Read JSON from file
# ---------------------------

with open("data.json") as f:
    data = json.load(f)

# ---------------------------
# 2. Process the data
# ---------------------------

df = pd.DataFrame(data)

# Convert the 'date' column to datetime
df['date'] = pd.to_datetime(df['date'])

# get time dimensions
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day'] = df['date'].dt.day

# Convert the 'rate' column to numeric
df['rate'] = pd.to_numeric(df['rate'])

# Calculate the rate percentage: 1 = 25% , 2 = 50% , 3 = 75% , 4 = 100%
df['rate_percent'] = df['rate'] * 100/4

# Sort by date
df = df.sort_values('date')

# ---------------------------
# 3. Create the Dash app
# ---------------------------

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Customer satisfaction"),
    
    dcc.Dropdown(
        id='year-dropdown',
        options=[{"label": col, "value": col} for col in df['year'].unique()],
        value=df['year'].unique(),
        style={'width': '48%'}
    ),
    dcc.Dropdown(
        id='month-dropdown',
        options=[{"label": col, "value": col} for col in df['month'].unique()],
        value=df['month'].unique(),
        style={'width': '48%'}
    ),

    dcc.Graph(id="grafico"),

    html.Button("Exportar a HTML", id="btn-export", n_clicks=0),
    html.Div(id="mensaje-export"),
    
    html.Div([
        html.H3("Datos brutos"),
        html.Pre(df.to_string())
    ], style={'marginTop': 20})
])

# ---------------------------
# 4. Callback to update the graph
# ---------------------------

@app.callback(
    Output("grafico", "figure"),
    Input("year-dropdown", "value"),
    Input("month-dropdown", "value")
)
def actualizar_grafico(selected_years, selected_months):
    # Ensure that selected_years and selected_months are lists
    if not isinstance(selected_years, list):
        selected_years = [selected_years]
    if not isinstance(selected_months, list):
        selected_months = [selected_months]
    
    # Filter the dataframe by the selected years and months
    filtered_df = df[
        (df['year'].isin(selected_years)) & 
        (df['month'].isin(selected_months))
    ]
    
    if filtered_df.empty:
        filtered_df = df

    # Create the graph with the filtered data
    fig = px.line(
        filtered_df, 
        x='date', 
        y='rate_percent', 
        markers=True,
        title="Customer Satisfaction Over Time",
        labels={'date': 'Date', 'rate_percent': 'Satisfaction (%)'}
    )
    
    # Improve the graph layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Satisfaction (%)',
        yaxis=dict(
            tickmode='array',
            tickvals=[25, 50, 75, 100],
            ticktext=['25% (1)', '50% (2)', '75% (3)', '100% (4)']
        ),
        hovermode='x unified'
    )
    
    return fig

# ---------------------------
# 5. Run the app
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)