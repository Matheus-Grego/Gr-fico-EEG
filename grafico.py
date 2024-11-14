import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html, Dash, Input, Output
from scipy.signal import butter, filtfilt, iirnotch

try:
    df = pd.read_csv('dados-eeg-white-1.csv', on_bad_lines="skip")
except Exception as e:
    print(f'Ocorreu um erro ao ler o arquivo CSV: {e}')
    exit()

# Função para aplicar filtro notch
def apply_notch_filter(data, fs, notch_freq, quality_factor=30):
    b, a = iirnotch(notch_freq, quality_factor, fs)
    return filtfilt(b, a, data)

# Função para aplicar filtro Bandpass
def apply_bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

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
    html.Label('Frequência do Notch (Hz):'),
    dcc.Slider(
        id='notch-freq-slider',
        min=1,
        max=100,
        step=1,
        value=60,
        marks={i: str(i) for i in range(1, 101, 10)}
    ),
    dcc.Graph(id='eeg-graph')
])

@app.callback(
    Output('eeg-graph', 'figure'),
    Input('num-amostras-slider', 'value'),
    Input('notch-freq-slider', 'value')
)

def update_graph(num_amostras, notch_freq):
    eeg_data = df[['Timestamp', 'EEG Channel 1', 'EEG Channel 2', 
                   'EEG Channel 3', 'EEG Channel 4', 'EEG Channel 5', 
                   'EEG Channel 6', 'EEG Channel 7', 'EEG Channel 8']]

    eeg_data = eeg_data.iloc[300:]

    # Amostrar uniformemente os dados
    indices = np.linspace(0, len(eeg_data)-1, num_amostras, dtype=int)
    eeg_data_sampled = eeg_data.iloc[indices]

    # Definindo a frequência de amostragem
    fs = 256  # Exemplo de frequência de amostragem em Hz

    # Aplicar filtro Bandpass a cada canal
    for i in range(1, 9):
        eeg_data_sampled[f'EEG Channel {i}'] = apply_bandpass_filter(eeg_data_sampled[f'EEG Channel {i}'], 2, 38, fs)
        eeg_data_sampled[f'EEG Channel {i}'] = apply_notch_filter(eeg_data_sampled[f'EEG Channel {i}'], fs, notch_freq)

    fig = go.Figure()

    # Calcular as diferenças entre os canais especificados e escalar
    diffs = {
        'Diferença Canal 1 - Canal 3': (eeg_data_sampled['EEG Channel 1'] - eeg_data_sampled['EEG Channel 3']) * 0.1,
        'Diferença Canal 3 - Canal 7': (eeg_data_sampled['EEG Channel 3'] - eeg_data_sampled['EEG Channel 7']) * 0.1,
        'Diferença Canal 7 - Canal 8': (eeg_data_sampled['EEG Channel 7'] - eeg_data_sampled['EEG Channel 8']) * 0.1,
        'Diferença Canal 5 - Canal 2': (eeg_data_sampled['EEG Channel 5'] - eeg_data_sampled['EEG Channel 2']) * 0.1,
        'Diferença Canal 2 - Canal 4': (eeg_data_sampled['EEG Channel 2'] - eeg_data_sampled['EEG Channel 4']) * 0.1,
        'Diferença Canal 4 - Canal 6': (eeg_data_sampled['EEG Channel 4'] - eeg_data_sampled['EEG Channel 6']) * 0.1
    }

    # Adicionar as diferenças ao gráfico
    for name, diff in diffs.items():
        fig.add_trace(go.Scatter(x= eeg_data_sampled['Timestamp'], y=diff,
                                 mode='lines', name=name))

    fig.update_layout(title='Diferenças entre Canais de EEG Amostrados e Filtrados',
                      xaxis_title='Timestamp',
                      yaxis_title='Diferença (Ajustada)',
                      legend_title='Diferenças',
                      template='plotly_white')

    fig.update_xaxes(rangeslider_visible=True)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
