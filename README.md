# Forecasting SPOT Price in the Spanish Electricity Market using Neural Networks

## Overview

This repository contains the code used for the Bachelor's Thesis titled "Forecasting SPOT Price in the Spanish Electricity Market using Neural Networks" by Nicolás Vega Muñoz. The thesis was submitted to the Escuela Técnica Superior de Ingenieros Informáticos at the Universidad Politécnica de Madrid in June 2024.

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

## Results

The study found that state-of-the-art models, particularly the Temporal Fusion Transformers (TFT), provided the most accurate predictions with a Mean Absolute Error (MAE) of 1.26. The implementation of this model is intended to improve prediction accuracy and optimize energy offer management, helping companies to bid more competitively and efficiently.

### TFT Model Results

![TFT Model Results](https://github.com/MrGG14/Electricity-Price-Forecast-NN/blob/main/predictions/test_tft.png)

### Model Comparison

The following table summarizes the performance of the four models evaluated:

| Model                       | MAE  |
|-----------------------------|------|
| Temporal Fusion Transformer | 1.26 |
| LSTM                        | 4.63 |
| CNN + LSTM                  | 4.98 |
| ARIMA                       | 10.8 |

The study found that the Temporal Fusion Transformer (TFT) provided the most accurate predictions with a Mean Absolute Error (MAE) of 1.26. The implementation of this model is intended to improve prediction accuracy and optimize energy offer management, helping companies to bid more competitively and efficiently.

### Conclusions

1. **Temporal Fusion Transformer (TFT)**: The TFT model outperformed other models with the lowest MAE, demonstrating its effectiveness in handling time series data for SPOT price prediction.
2. **LSTM**: The LSTM model, while effective, had a higher MAE compared to TFT, indicating less accuracy in predicting SPOT prices.
3. **CNN + LSTM**: Combining CNN with LSTM did not significantly improve accuracy over standalone LSTM, showing that more complexity doesn't always lead to better performance.
4. **ARIMA**: The ARIMA model had the highest MAE, indicating that traditional statistical methods are less effective for this type of prediction task compared to modern deep learning approaches.

## Repository Structure
- `old/`: Old, unused files.
- `src`: Main folder where EDA, modelling and experiments are implemented. 
- `src/models/`: Contains the implementation of the ARIMA, LSTM and CNN models evaluated in this study.
- `predictions/`: Contains the results of the best TFT models and the test predictions.
- `README.md`: This README file.
- `tfg_etsiinf_NicolasVega`: Complete thesis.
  
## How to Use

1. **Clone the repository**:
   ```sh
   git clone https://github.com/yourusername/forecasting-spot-price.git
   ```
2. **Install requirements**
   ```
   pip install -r requirements.txt
   ```
## Acknowledgements
This work was supervised by Bojan Mihaljevic at the Department of Artificial Intelligence, Escuela Técnica Superior de Ingenieros Informáticos, Universidad Politécnica de Madrid.
