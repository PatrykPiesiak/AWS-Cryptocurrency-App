import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import boto3

# Define the S3 bucket and key for the data file
S3_BUCKET = 'cryptovisualisationapp'
S3_KEY = 'crypto_data.csv'


# Function to load data from S3 bucket
def load_data_from_s3():
    # Create an S3 client
    s3 = boto3.client('s3')

    # Get the object (data file) from the S3 bucket
    obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)

    # Read the data into a Pandas DataFrame
    df = pd.read_csv(obj['Body'])

    return df


# Create a Dash web application
app = dash.Dash(__name__)

# Load data from S3
data = load_data_from_s3()

# Melt the data for better visualization
melted_data = pd.melt(data, id_vars=['name'], value_vars=[
    'percent_change_1h', 'percent_change_24h', 'percent_change_7d', 'percent_change_30d'],
                      var_name='Time Period', value_name='Percentage Change')

# Define custom styles for the application layout
app.layout = html.Div(style={'background-color': 'white', 'color': 'black'}, children=[
    # Title at the top
    html.H1("CRYPTOCURRENCY TRACKER", style={'text-align': 'center'}),

    # Main content div
    html.Div(style={'display': 'flex'}, children=[
        # Left-side menu
        html.Div(className="four columns", style={'background-color': 'lightgray', 'padding': '20px'}, children=[
            dcc.RadioItems(
                id='data-selector',
                options=[
                    {'label': '24-Hour Trading Volume', 'value': 'volume_24h'},
                    {'label': '24-Hour Volume Change', 'value': 'volume_change_24h'},
                    {'label': 'Percentage Change', 'value': 'percentage_change'},
                    {'label': 'Prices in USD', 'value': 'price'}
                ],
                value='volume_24h',
                labelStyle={'display': 'block'},
            ),

            # Submenu for Percentage Change
            dcc.Dropdown(
                id='time-period-selector',
                options=[
                    {'label': '1 Hour', 'value': 'percent_change_1h'},
                    {'label': '24 Hours', 'value': 'percent_change_24h'},
                    {'label': '7 Days', 'value': 'percent_change_7d'},
                    {'label': '30 Days', 'value': 'percent_change_30d'}
                ],
                value='percent_change_1h',
                multi=False,
                style={'display': 'none', 'color': 'black'}
            ),
        ]),

        # Right-side content (graphs)
        html.Div(style={'width': '100%'}, children=[
            dcc.Graph(id='crypto-plot')
        ]),
    ])
])


# Define a callback to update the plot and dropdown style
@app.callback(
    Output('crypto-plot', 'figure'),
    Output('time-period-selector', 'style'),
    Input('data-selector', 'value'),
    Input('time-period-selector', 'value')
)
def update_plot(selected_data, selected_time_period):
    dropdown_style = {'display': 'none'}

    if selected_data == 'volume_24h':
        # Create a bar chart for 24-Hour Trading Volume
        fig = px.bar(data, x='name', y='volume_24h',
                     labels={'name': 'Cryptocurrency', 'volume_24h': '24h Trading Volume'},
                     title='24-Hour Trading Volume for Cryptocurrencies', color='name')
    elif selected_data == 'volume_change_24h':
        # Create a bar chart for 24-Hour Volume Change
        fig = px.bar(data, x='name', y='volume_change_24h',
                     labels={'name': 'Cryptocurrency', 'volume_change_24h': '24h Volume Change'},
                     title='24-Hour Volume Change for Cryptocurrencies', color='name')
    elif selected_data == 'price':
        # Create a bar chart for Cryptocurrency prices in USD
        fig = px.bar(data, x='name', y='price',
                     labels={'name': 'Cryptocurrency', 'price': 'Price in USD'},
                     title='Cryptocurrency prices in USD', color='name')
    else:
        # Create a bar chart for Percentage Change based on the selected time period
        filtered_data = melted_data[melted_data['Time Period'] == selected_time_period]
        fig = px.bar(filtered_data, x='name', y='Percentage Change', color='name',
                     labels={'name': 'Cryptocurrency', 'Percentage Change': 'Percentage Change'},
                     title=f'Percentage Change ({selected_time_period}) for Cryptocurrencies')
        dropdown_style = {'display': 'block'}

    # Customize the plot's appearance
    fig.update_xaxes(categoryorder='total ascending')
    fig.update_xaxes(tickangle=-45)

    return fig, dropdown_style


# Run the Dash application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
