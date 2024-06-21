# Forecasting SPOT Price in the Spanish Electricity Market using Neural Networks
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12207478.svg)](https://doi.org/10.5281/zenodo.12207478)

## Overview

This repository contains the code used for the Bachelor's Thesis titled "Forecasting SPOT Price in the Spanish Electricity Market using Neural Networks" by Nicolás Vega Muñoz. The thesis was submitted to the Escuela Técnica Superior de Ingenieros Informáticos at the Universidad Politécnica de Madrid in June 2024. The full thesis is available [here](https://github.com/MrGG14/Electricity-Price-Forecast-TFT/blob/main/tfg_etsiinf_NicolasVega.pdf).

The primary objective of this work is to develop a model capable of predicting the SPOT price (price per MWh) in the Spanish electricity market for each hour of the following day. This model aims to optimize market offers by providing accurate price forecasts, which are crucial for making informed decisions in a highly volatile energy market.

## Objectives

- **Accurate Prediction**: Develop a model to predict the SPOT price with high accuracy.
- **Model Comparison**: Evaluate and compare various models, including classical methods and state-of-the-art deep learning models like Temporal Fusion Transformers (TFT).
- **Strategic Advantage**: Provide a strategic advantage for operating in the daily electricity market through improved prediction accuracy and optimized energy offer management.
- **Model Interpretability**: Highlight the importance of model interpretability for strategic decision-making.

## Methodology

The methodology applied in this work includes the following steps:

1. **Data Acquisition**: Collect and preprocess data relevant to the Spanish electricity market.
2. **Modeling**: Develop various models, including both classical and deep learning approaches.
3. **Model Comparison**: Compare the performance of different models based on metrics such as Mean Absolute Error (MAE).
4. **Results Analysis**: Analyze the results to identify the best-performing model and its potential impact on the market.

## Data Acquisition
Data was acquired from public sources by doing some Web Scrapping and using the [ESIOS API](https://www.esios.ree.es/es/pagina/api).

The variables used are:
- Gas price (€)
- European Union Allowances (EUA) price: CO2 emissions allowances. (€)
- Demand (MwH)
- Resiudal demand (MwH)
- Solar production (MwH)
- Eolic production (MwH)

  And were obtained from:
  
  # Web Scraping:
- **MIBGAS:** Gas price and forecast
- **Sendeco2:** Historical CO2 prices
- **ICE:** CO2 price and forecast

# API:
- **ESIOS:** SPOT price, production and forecast of renewables (solar and wind), demand (and forecast), and residual demand.

## Modelling

In this section, we present the various models employed to forecast electricity prices in the wholesale market. We explored both classical and deep learning approaches to identify the most accurate and robust model for our predictions.

### Classical Models

#### SARIMA and SARIMAX
Seasonal Autoregressive Integrated Moving Average (SARIMA) and its extension with exogenous variables (SARIMAX) were among the classical models we tested. These models are well-suited for capturing seasonality and trends in time series data. We trained a SARIMAX model with the configuration SARIMAX(1,1,4)(1,0,0)[24], which provided a good fit to our data with a mean absolute error (MAE) of 7.13 on the validation set. However, the model exhibited limitations in capturing complex patterns beyond repetitive seasonal components.

### Neural Network Models

#### Long Short-Term Memory (LSTM)
LSTM networks, a type of recurrent neural network (RNN), are effective for sequential data due to their ability to retain information over long periods. We implemented several LSTM architectures, starting with a basic model and progressing to more complex configurations with multiple LSTM layers and dense layers. The most effective LSTM model included dropout and regularization, achieving a promising MAE of 4.63 over a 7-day prediction horizon.

#### Convolutional Neural Networks (CNN)
We also experimented with 1D Convolutional Neural Networks (CNNs) to capture local patterns in the time series data. Starting with a simple model comprising a single convolutional layer with 16 filters followed by max pooling, we gradually increased the complexity. The best CNN model demonstrated decent performance, with a MAE of 4.98, indicating its potential for capturing significant features in the time series data.

### State of the Art model: Temporal Fusion Transformers (TFT)

To leverage the power of attention mechanisms, we employed Temporal Fusion Transformers (TFT). This state-of-the-art model excels in handling temporal dynamics and multi-horizon forecasting. Our TFT model achieved the lowest MAE of 1.1, making it the most accurate model among those evaluated. The TFT model's interpretability also provided valuable insights into the contributing factors of the forecasts, aiding strategic decision-making.


## Model Comparison

The following table summarizes the performance of the four models evaluated:

| Model                       | MAE  |
|-----------------------------|------|
| Temporal Fusion Transformer | 1.26 |
| LSTM                        | 4.63 |
| CNN + LSTM                  | 4.98 |
| ARIMA                       | 10.8 |

The study found that the Temporal Fusion Transformer (TFT) provided the most accurate predictions with a Mean Absolute Error (MAE) of 1.26. The implementation of this model is intended to improve prediction accuracy and optimize energy offer management, helping companies to bid more competitively and efficiently.

![Models Comparison](https://github.com/MrGG14/Electricity-Price-Forecast-TFT/assets/91123530/cee9a956-45e2-4ab1-99ab-30917b0846b3)


## Results

The study found that state-of-the-art models, particularly the Temporal Fusion Transformers (TFT), provided the most accurate predictions with a Mean Absolute Error (MAE) of 1.26. The implementation of this model is intended to improve prediction accuracy and optimize energy offer management, helping companies to bid more competitively and efficiently.

### TFT Model Results

![TFT Model Results](https://github.com/MrGG14/Electricity-Price-Forecast-TFT/blob/main/plots/predictions/test_tft.png))


## Interpretability of the TFT Model

The Temporal Fusion Transformer (TFT) model includes several mechanisms for enhancing interpretability, making it easier to understand the factors driving the SPOT price predictions. These mechanisms are crucial for strategic decision-making in the energy market.

### Key Mechanisms for Interpretability

1. **Variable Selection Networks**:
   - The TFT model uses variable selection networks at the instance level, selecting the most relevant variables for each prediction. This helps eliminate noisy inputs and highlights the most significant variables for making predictions.

2. **Interpretable Multi-Head Attention**:
   - The model incorporates a modified multi-head attention mechanism to learn long-term dependencies across different time points. This attention mechanism is designed to be interpretable, allowing each attention head to learn different temporal patterns while analyzing a common set of input features.

3. **Static Covariate Encoders**:
   - These encoders transform static variables into contextual representations used throughout the prediction process. Incorporating static information allows the TFT to make more accurate and contextually relevant predictions, enhancing interpretability.

4. **Temporal Fusion Decoder**:
   - The decoder includes layers that focus on learning temporal relationships within the data. For instance, the locality enhancement with a sequence-to-sequence layer helps identify significant values in relation to their neighboring values, useful for detecting anomalies, inflection points, and cyclical patterns.

### Importance of Variables

Key insights from the TFT model include the identification of the most relevant variables influencing the SPOT price predictions:

- **Demanda Residual**: The most significant feature, indicating a strong correlation between residual demand and electricity prices.
- **Precio SPOT Lagged by 72 Hours**: Highly influential, showing that past prices from three days prior are a strong predictor of future prices.
- **Relative Time Index**: Important for capturing temporal patterns and trends.
- **CO2 Levels**: Reflects the impact of carbon emissions on price fluctuations.
- **Renewable Energy Production**: Includes solar and wind energy production, highlighting their roles in influencing price predictions.

### Visual Insights

Below are visual representations of the attention mechanism and the importance of various decoder variables, which provide deeper insights into the interpretability of the TFT model:

#### Attention Mechanism
![Attention Mechanism](https://github.com/MrGG14/Electricity-Price-Forecast-TFT/blob/main/plots/tft_inerpretability/attenttion_interpr.png)

#### Encoder Variable Importance
![Encoder Variable Importance](https://github.com/MrGG14/Electricity-Price-Forecast-TFT/blob/main/plots/tft_inerpretability/decoder_intr.png)

#### Decoder Variable Importance
![Decoder Variable Importance](https://github.com/MrGG14/Electricity-Price-Forecast-TFT/blob/main/plots/tft_inerpretability/decoder_intr.png)

#### Static Variable Importance
![Static Variable Importance](https://github.com/MrGG14/Electricity-Price-Forecast-TFT/blob/main/plots/tft_inerpretability/decoder_intr.png)

### Conclusions on Interpretability

1. **Understanding Key Drivers**:
   - The TFT model's interpretability mechanisms allow for a detailed understanding of the key drivers behind SPOT price predictions. This is particularly important for stakeholders who need to make informed strategic decisions based on these predictions.

2. **Enhanced Decision-Making**:
   - By highlighting the most important features and their relationships, the model provides actionable insights that can lead to more effective and strategic energy offer management.

3. **Transparency and Trust**:
   - The transparent nature of the TFT model's predictions fosters trust among users, as they can see and understand the factors influencing the model

### Conclusions

1. **Temporal Fusion Transformer (TFT)**: The TFT model outperformed other models with the lowest MAE, demonstrating its effectiveness in handling time series data for SPOT price prediction.
2. **LSTM**: The LSTM model, while effective, had a higher MAE compared to TFT, indicating less accuracy in predicting SPOT prices.
3. **CNN + LSTM**: Combining CNN with LSTM did not significantly improve accuracy over standalone LSTM, showing that more complexity doesn't always lead to better performance.
4. **ARIMA**: The ARIMA model had the highest MAE, indicating that traditional statistical methods are less effective for this type of prediction task compared to modern deep learning approaches.

## Repository Structure
- `old/`: Old, unused files.
- `src`: Main folder where EDA, modelling and experiments are implemented. 
- `src/models/`: Contains the implementation of the ARIMA, LSTM and CNN models evaluated in this study.
- `plots/`: Contains plots generated in the project. Contains both the results of the best TFT models and its interpretability plots.
- `README.md`: This README file.
- `tfg_etsiinf_NicolasVega`: Complete thesis.
- `requirements.txt`: Necessary libraries to execute code. 
  
## How to Use

1. **Clone the repository**:
   ```sh
   git clone https://github.com/MrGG14/Electricity-Price-Forecast-TFT
   ```
2. **Install requirements**
   ```
   pip install -r requirements.txt
   ```
## Acknowledgements
This work was supervised by Bojan Mihaljevic at the Department of Artificial Intelligence, Escuela Técnica Superior de Ingenieros Informáticos, Universidad Politécnica de Madrid.


