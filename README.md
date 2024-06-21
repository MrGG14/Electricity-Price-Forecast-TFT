Skip to content
Navigation Menu
MrGG14
/
Electricity-Price-Forecast-NN

Type / to search

Code
Issues
Pull requests
Actions
Projects
Wiki
Security
Insights
Settings
Editing README.md in Electricity-Price-Forecast-NN
BreadcrumbsElectricity-Price-Forecast-NN
/
README.md
in
main

Edit

Preview
Indent mode

Spaces
Indent size

2
Line wrap mode

Soft wrap
Editing README.md file contents
Selection deleted
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128

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

Use Control + Shift + m to toggle the tab key moving focus. Alternatively, use esc then tab to move to the next interactive element on the page.
Ningún archivo seleccionado
Attach files by dragging & dropping, selecting or pasting them.
Editing Electricity-Price-Forecast-NN/README.md at main · MrGG14/Electricity-Price-Forecast-NN 
