import pandas as pd
import matplotlib.pyplot as plt

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import plotly.graph_objects as go
import seaborn as sns


def section_TS(data, var_exo, windows={'por dia': 24, 'por semana': 168, 'por mes': 720}):
    data.set_index('fechaHora')

  # Crear figura
    fig = go.Figure()

    # Agregar serie temporal original
    fig.add_trace(go.Scatter(x=data['fechaHora'], y=data[var_exo], mode='lines', name='Original'))

    # Agregar medias móviles
    for key, value in windows.items():
        smoothed_data = data[var_exo].rolling(window=value).mean()
        fig.add_trace(go.Scatter(x=data['fechaHora'], y=smoothed_data, mode='lines', name=f'Suavizado {key}'))

    # Configurar diseño
    fig.update_layout(
        title=f"{var_exo}: {str(data['fechaHora'].iloc[0])[:10]} a {str(data['fechaHora'].iloc[-1])[:10]} con medias móviles",
        xaxis_title='Fecha',
        yaxis_title=var_exo,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    fig.show()


# Gráfico boxplot para estacionalidad anual
# ==============================================================================
def seasonality_annual (data, var_exo):    
    fig, ax = plt.subplots(figsize=(7, 3.5))
    data['mes'] = data['fechaHora'].dt.month
    data.boxplot(column=var_exo, by='mes', ax=ax,)
    data.groupby('mes')[var_exo].median().plot(style='o-', linewidth=0.3, ax=ax)
    data.drop(columns=['mes'], inplace=True)
    ax.set_ylabel(var_exo)
    ax.set_title('Distribución '+var_exo+' por mes')
    fig.suptitle('')
# Gráfico boxplot para estacionalidad semanal
# ==============================================================================
def seasonality_weekly(data, var_exo):
    fig, ax = plt.subplots(figsize=(7, 3.5))
    data['dia_semana'] = data['fechaHora'].dt.day_name()
    data.boxplot(column=var_exo, by='dia_semana', ax=ax)
    data.groupby('dia_semana')[var_exo].median().plot(style='o-', linewidth=0.8, ax=ax)
    data.drop(columns=['dia_semana'], inplace=True)

    ax.set_ylabel(var_exo)
    ax.set_title('Distribución '+var_exo+' por día de la semana')
    fig.suptitle('')
# Gráfico boxplot para estacionalidad diaria
# ==============================================================================
def seasonality_daily(data, var_exo):    
    fig, ax = plt.subplots(figsize=(9, 3.5))
    data['hora_dia'] = data['fechaHora'].dt.hour
    data.boxplot(column=var_exo, by='hora_dia', ax=ax)
    data.groupby('hora_dia')[var_exo].median().plot(style='o-', linewidth=0.8, ax=ax)
    data.drop(columns=['hora_dia'], inplace=True)
    ax.set_ylabel(var_exo)
    ax.set_title('Distribución '+var_exo+' por hora del día')
    fig.suptitle('')
# Gráfico autocorrelación
# ==============================================================================
def autocorrelation_graph(data, var_exo):
    fig, ax = plt.subplots(figsize=(7, 3))
    plot_acf(data[var_exo], ax=ax, lags=72)
    plt.show()
# Gráfico autocorrelación parcial
# ==============================================================================
def partial_autocorr_graph(data, var_exo):
    fig, ax = plt.subplots(figsize=(7, 3))
    plot_pacf(data[var_exo], ax=ax, lags=72)
    plt.show()

def plot_distr_funcs(df):
    sns.set(style="ticks")
    sns.pairplot(df.iloc[:, 1:], diag_kind="kde", kind="scatter")
    plt.show()

