username <- str_split(getwd(), "/")[[1]][[3]]
PATHS <- list(
    root = file.path("C:", "Users", username, "NTT DATA EMEAL/businessanalytics - Bidding de Mercado"),
    mod_data_omie = "01 Ficheros/2_Datasets_input/Fase2/mod_data_omie",
    model_outputs = "01 Ficheros/3_Datasets_output/Fase2/model_outputs/hts_R",
    validation_outputs = "01 Ficheros/3_Datasets_output/Fase2/validacion_outputs/Predictions",
    src_data_omie = "01 Ficheros/2_Datasets_input/Fase2/src_data_omie",
    input_fase1 = "01 Ficheros/2_Datasets_input/Fase1"
)
