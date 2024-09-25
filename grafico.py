import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html, Dash, Input, Output

try:
    df = pd.read_csv('dados-eeg-white-1.csv', on_bad_lines="skip")
except Exception as e:
    print(f'Ocorreu um erro ao ler o arquivo CSV: {e}')
    exit()

# Função para aplicar filtro de média móvel
def apply_moving_average(data, window_size):
    return data.rolling(window=window_size, min_periods=1).mean()

# aplicação web
app = Dash(__name__)
app.layout = html.Div([
    html.H1('Visualização Interativa dos Dados EEG'),

    html.Label('Número de Amostras:'),
    dcc.Slider(
        id='num-amostras-slider',
        min=1000,
        max=40000,
        step=1000,
        value=10000,
        marks={i: str(i) for i in range(1000, 50001, 5000)}
    ),
    html.Label('Tamanho da Janela de Média Móvel:'),
    dcc.Slider(
        id='window-size-slider',
        min=1,
        max=50,
        step=1,
        value=5,
        marks={i: str(i) for i in range(1, 51, 5)}
    ),
    dcc.Graph(id='eeg-graph')
])

@app.callback(
    Output('eeg-graph', 'figure'),
    Input('num-amostras-slider', 'value'),
    Input('window-size-slider', 'value')
)
def update_graph(num_amostras, window_size):
    eeg_data = df[['Timestamp', 'EEG Channel 1', 'EEG Channel 2', 'EEG Channel 3', 'EEG Channel 4', 
                   'EEG Channel 5', 'EEG Channel 6', 'EEG Channel 7', 'EEG Channel 8']]

    # Amostrar uniformemente os dados
    eeg_data_sampled = eeg_data.iloc[::len(eeg_data)//num_amostras]

    for i in range(1, 9):
        eeg_data_sampled[f'EEG Channel {i}'] = apply_moving_average(eeg_data_sampled[f'EEG Channel {i}'], window_size)

    fig = go.Figure()

    # Calcular as diferenças entre os canais especificados
    diffs = {
        'Diferença Canal 1 - Canal 3': eeg_data_sampled['EEG Channel 1'] - eeg_data_sampled['EEG Channel 3'],
        'Diferença Canal 3 - Canal 7': eeg_data_sampled['EEG Channel 3'] - eeg_data_sampled['EEG Channel 7'],
        'Diferença Canal 7 - Canal 8': eeg_data_sampled['EEG Channel 7'] - eeg_data_sampled['EEG Channel 8'],
 'Diferença Canal 5 - Canal 2': eeg_data_sampled['EEG Channel 5'] - eeg_data_sampled['EEG Channel 2'],
        'Diferença Canal 2 - Canal 4': eeg_data_sampled['EEG Channel 2'] - eeg_data_sampled['EEG Channel 4'],
        'Diferença Canal 4 - Canal 6': eeg_data_sampled['EEG Channel 4'] - eeg_data_sampled['EEG Channel 6']
    }

    # Adicionar as diferenças ao gráfico
    for name, diff in diffs.items():
        fig.add_trace(go.Scatter(x=eeg_data_sampled['Timestamp'], y=diff,
                                 mode='lines', name=name))

    fig.update_layout(title='Diferenças entre Canais de EEG Amostrados e Suavizados',
                      xaxis_title='Timestamp',
                      yaxis_title='Diferença',
                      legend_title='Diferenças',
                      template='plotly_white')

    fig.update_xaxes(rangeslider_visible=True)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

