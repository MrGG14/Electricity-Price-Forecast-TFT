import os
import sys
from datetime import datetime, date
import numpy as np

basepath = os.path.dirname(__file__)  # script directory
from config.config_file import DATE_INFO, YEAR, FASE1_SETTINGS


# sys.path.insert(1, os.path.join(basepath, "../"))  # add root directory

try:
    username = basepath.split("\\")[2]
except:
    username = ""
##################### CONNECTION CONFIGURATION #########################
DIR = "LOCAL"

PATHS = {
    "LOCAL": {
        # automate prefix by user
        "root": os.path.join(
            "C:/Users/",
            username,
            "C:/Users/nicov/Desktop/TFG_code_local/src",
        ),
        # Carpeta de descargas local
        "local_download": os.path.join("C:/Users/", username, "Downloads"),
        # Carpeta de descargas
        "download": "01 Ficheros/1_Ficheros_descargas/",
        # input (Fase 1 y Fase2)
        "input": "01 Ficheros/2_Datasets_input/",
        # output (Fase 1 y Fase 2)
        "output": "01 Ficheros/3_Datasets_output/",
        # input Fase1
        "src_fase1": "datasets/",
        # input Fase2
        "zip_data_omie": "01 Ficheros/1_Ficheros_descargas/Fase2/raw_data_omie",
        "raw_data_omie": "01 Ficheros/2_Datasets_input/Fase2/raw_data_omie",
        "src_data_omie": "01 Ficheros/2_Datasets_input/Fase2/src_data_omie",
        "temp_data_omie": "01 Ficheros/2_Datasets_input/Fase2/temp_data_omie",
        "mod_data_omie": "01 Ficheros/2_Datasets_input/Fase2/mod_data_omie",
        # output fase1
        "output_fase1": "01 Ficheros/3_Datasets_output/Fase1",
        "trained_models_fase1": "01 Ficheros/3_Datasets_output/Fase1/trained_models",
        "plots_output": "01 Ficheros/3_Datasets_output/Fase1/plots_output",
        # output fase2
        "output_fase2": "01 Ficheros/3_Datasets_output/Fase2",
        "vun_fase2": "01 Ficheros/3_Datasets_output/Fase2/vun_data_omie",
        # exploratorio
        "exploration": "02 Ejecución/2_Comprension_datos/",
        "dataset_input_name": "dataset_input_v0.xlsx",  # TODO incluir en setting fase 1?
        # paths web scraping
        "download_path": os.path.join("C:/Users/", username, "Downloads"),
        # "chrome_driver_path": os.path.join(
        #     "C:/Users/",
        #     username,
        #     "OneDrive - Universidad Politécnica de Madrid\TFG\chromedriver.exe",
        # ),
        "chrome_driver_path": r"c:\Users\nvegamun\OneDrive - NTT DATA EMEAL\Escritorio\tfg_code\chromedriver.exe",
        "firefox_driver_path": os.path.join(
            "C:/Users/",
            username,
            "NTT DATA EMEAL/businessanalytics - Bidding de Mercado/geckodriver.exe",
        ),
        "firefox_binary_path": os.path.join(
            "C:/Users/",
            username,
            "AppData/Local/Mozilla Firefox/firefox.exe",
        ),
    },
    "AZURE": {
        # root de la nfs
        "root": "/home/nfsadmin/",
        # Carpeta de descargas
        "local_download": "/home/nfsadmin/Downloads/",
        # Informacion Fase2
        "data": "/home/nfsadmin/data/",
        # Input Fase1
        "src_fase1": "/home/nfsadmin/data/Fase2/src_fase1",
        # Directorio de datos fase2
        "fase2": "/home/nfsadmin/data/Fase2",
        "raw_data_omie": "/home/nfsadmin/data/Fase2/raw_data_omie",
        "src_data_omie": "data/Fase2/src_data_omie",
        "temp_data_omie": "data/Fase2/tmp_data_omie",
        "val_data_omie": "data/Fase2/val_data_omie",
        "mod_data_omie": "data/Fase2/mod_data_omie",
        "vun_fase2": "data/Fase2/vun_data_omie",
        # Output fase2
        "output_fase2": "data/Fase2/model_outputs",
        # Directorio carpeta public SAS
        "sas_public": "/export/pvs/sasviya-cas-default-data-pvc-9cbfad16-5233-4d8f-8ab6-0fa4179c8fbe/caslibs/public/",
        "dataset_input_name": "dataset_input_v0.xlsx",
    },
}


#####################  DATA DOWNLOAD  #########################

# TOKEN = "77950bffd128cd8d944e2c91166db4b2d16e523c8b023bb5fbd3917e755b7c70" # opc1
TOKEN = (
    "c42a362132c3b39ff321cfdd13011b721b337865247ffd8f147e447d23451a3e"  # opc2
)
HEADERS = {
    "Accept": "application/json; application/vnd.esios-api-v1+json",
    "Content-Type": "application/json",
    # "Host": "api.esios.ree.es",
    # "Authorization": 'Token token="' + TOKEN + '"',
    # "Authorization": 'Token token="' + TOKEN + '"',
    "x-api-key": TOKEN,
    # "Cookie": "",
}

dict_months = {
    "01": f"JAN{str(date.today().year)[2:]}",
    "03": f"MAR{str(date.today().year)[2:]}",
    "04": f"APR{str(date.today().year)[2:]}",
    "06": f"JUN{str(date.today().year)[2:]}",
    "12": f"DEC{str(date.today().year)[2:]}",
    "12_24": "MAR24",
}

FASE1_DATA_SCRAPING = {
    # ESIOS: demand, price, generation
    "url_esios": "https://api.esios.ree.es/indicators/",
    # "url_esios": "https://apip.esios.ree.es/indicators/", # SOLO PARA PRUEBAS
    "indicator_dict_esios": {
        "col_target": "600",  # precio_spot
        "col_demand": "1293",  # demanda real
        "col_demand_prev12": "1775",  # demanda prevista d+1 -
        "col_demand_prev36": "460",  # demanda prevista d - permite hace
        "col_eolic": "551",  # generacion T.Real eólica
        "col_eolic_prev12": "541",  # prevision produccion eolica peninsular
        "col_eolic_prev36": "541",  # prevision produccion eolica peninsular
        "col_solar": "10206",  # generacion T.Real Solar
        "col_solar_prev12": "10034",  # generacion prevista solar
        "col_solar_prev36": "10034",  # generacion prevista solar
        "col_nuclear": "549",  # nuclear T.Real
        "col_combined_cycle": "550",  # ciclo combinado T.Real
        "col_cogeneration": "1297",  # cogeneracion T.Real
        "col_hydraulic": "546",  # hidraulica T.Real
        "col_renewable": "10351",  # renovable T.Real
        "col_not_renewable": "10352",  # no renovable T.Real
        "col_co2_free": "10006",  # libre CO2 T.Real
        "col_interchanges": "553",  # intercambios T.Real
        "col_interconexion_francia": "10275",  # Saldo interconexion Francia PHFC
        "col_interconexion_global": "10284",  # Saldo interconexiones global PHFC
        "col_interconexion_marruecos": "10277",  # Saldo interconexion Marruecos PHFC
        "col_demanda_residual": "10249",  # Demanda Residual -
        "col_telemedida_francia": "10207",  # Saldo Telemedida Francia
        "col_telemedida_portugal": "10208",  # Saldo Telemedida Portugal
        "col_telemedida_marruecos": "10209",  # Saldo Telemedida Marruecos
        "col_saldo_neto_p48": "10026",  # Saldo total interconexiones programa 99-p48
        "col_eolic_prevision": "541",  # prevision produccion eolica peninsular
        "col_solar_prevision": "10034",  # generacion prevista solar
        "col_demand_prevision": "460",  # demanda prevista d
    },
    "token_esios": "77950bffd128cd8d944e2c91166db4b2d16e523c8b023bb5fbd3917e755b7c70",
    "headers_esios": {
        "Accept": "application/json; application/vnd.esios-api-v1+json",
        "Content-Type": "application/json",
        "Host": "api.esios.ree.es",
        # "Authorization": 'Token token="' + TOKEN + '"',
        "x-api-key": TOKEN,
        # "Cookie": "",
    },
    # GAS
    "url_gas": "https://www.mibgas.es",
    "url_gas_2": "https://www.mibgas.es/es/file-access?path=AGNO_"
    + YEAR
    + "/XLS",
    "gas_file_name": "MIBGAS_Data_" + YEAR + ".xlsx",
    # CO2
    "url_co2_1": "https://www.sendeco2.com/es/precios-co2",
    "url_co2_2": "https://www.theice.com/products/197/EUA-Futures/data",
    # "co2_file_name": "historico-precios-CO2-_" + YEAR + "_.csv",
    "co2_file_name": "historico-precios-CO2-_2024_.csv",
    "eua_index_name": dict_months["12"],
}

FASE2_DATA_SCRAPING = {
    # AEMET
    "aemet_path": "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/",
    "token_aemet": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJiY2hpdmFwb0BldmVyaXMuY29tIiwianRpIjoiYjVlZmE3MmItNTE4Yy00M2FlLTgwNTYtNTczZTA0OTFiMWI3IiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE2MjI3MDQxOTAsInVzZXJJZCI6ImI1ZWZhNzJiLTUxOGMtNDNhZS04MDU2LTU3M2UwNDkxYjFiNyIsInJvbGUiOiIifQ.akov64QOLc77sFvUvBKC0mSxq62VB08wMmGBt5jDraI",
    "fecha_ini_aemet": "2021-12-26T00:00:00UTC",
    "fecha_fin_aemet": "2021-12-26T23:59:59UTC",
    "url_omie_unidades": "https://www.omie.es/es/listado-de-agentes",
    "unidades_file_name": "LISTA_UNIDADES",
}

##################### FASE 1 #########################
FASE1_DATASET = {
    "columns_input_v0": {
        "col_date": "fechaHora",
        "col_target": "precio_spot",
        "col_demand": "demanda",
        "col_demand_prev12": "demanda_prev12",
        "col_demand_prev36": "demanda_prev36",
        "col_co2": "EUA",
        "col_co2_prev24": "EUA_prev24",
        "col_co2_prev48": "EUA_prev48",
        "col_gas": "precio_gas",
        "col_gas_prev24": "gas_prev24",
        "col_gas_prev48": "gas_prev48",
        "col_eolic": "prod_eolica",
        "col_eolic_prev12": "eolica_prev12",
        "col_eolic_prev36": "eolica_prev36",
        "col_solar": "prod_solar",
        "col_solar_prev12": "solar_prev12",
        "col_solar_prev36": "solar_prev36",
        "col_nuclear": "nuclear",
        "col_combined_cycle": "c_combinado",
        "col_cogeneration": "cogeneracion",
        "col_hydraulic": "hidraulica",
        "col_renewable": "renovables",
        "col_not_renewable": "no_renovables",
        "col_co2_free": "libre_co2",
        "col_demanda_residual": "demanda_residual",
        "col_eolic_prevision": "eolica_prevision",
        "col_solar_prevision": "solar_prevision",
        "col_demand_prevision": "demanda_prevision",
    },
    "col_day_of_weekend": "bool_we",  # NOTE: No se utilizan en el web scraping
    "col_ajuste_gas": "ajuste_gas",  # NOTE: No se utilizan en el web scraping
    "features": [
        "demanda",
        "EUA",
        "precio_gas",
        "prod_eolica",
        "prod_solar",
        "dow",
    ],
}

# target_day = '2021-11-20' # day to predict price (start date when leading!=0) -> usually d+1
# target_lead = 0 # extra hours to predict, 24*number of extra days (24 for 1 extra day, 144 for 6)

FASE1_DATASET["exogenous_vars"] = [
    FASE1_DATASET["columns_input_v0"]["col_demand"],
    FASE1_DATASET["columns_input_v0"]["col_eolic"],
    FASE1_DATASET["columns_input_v0"]["col_solar"],
    FASE1_DATASET["columns_input_v0"]["col_co2"],
    "demanda_residual",
    "rampa",
    "eolica_solar",
    "escalon_renovable",
    # FASE1_DATASET["col_day_of_weekend"],
] + (
    [FASE1_DATASET["col_ajuste_gas"]]
    if (FASE1_SETTINGS["ajuste"] == 2)
    else [FASE1_DATASET["columns_input_v0"]["col_gas"]]
)

##################### FASE 2 #########################

FASE2_SETTINGS = {
    # "aemet": "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/",
    "datosomie_flow": "DATOSOMIE.csv",
    "totalcorr": "dataset_input_v0.xlsx",
    "lista_tecnologia": "/home/nfsadmin/data/Fase2/Lista_Unidades_Oferta_Tecnologias.XLS",
    "lista_unidades": "/home/nfsadmin/data/Fase2/LISTA_UNIDADES.XLS",
    "checkpoint_empresas": "/home/nfsadmin/data/Fase2/checkpoint_df_empresas.xlsx",
    "dataset_modelar_fase2": "MOD_FASE2_INPUT.csv",
    "dataset_global_modelar_fase2": "MOD_GLOBAL_DATASET_FASE2.csv",
    # "dataset_fase2": os.path.join('C:/Users/',username,'OneDrive - NTT DATA EMEAL/Bidding de Mercado/01 Ficheros/2_Datasets_input/Fase2/datosomie_13042022.csv'),
    "dataset_para_dia": os.path.join(
        "C:/Users/",
        username,
        "NTT DATA EMEAL/businessanalytics - Bidding de Mercado/01 Ficheros/3_Datasets_output/Fase2/dataset_fase_2_2022-06-28.csv",
    ),
    "finalmerge_datosomie": "/home/nfsadmin/data/Fase2/FINALMERGE_DATOSOMIE.csv",
}

FASE2_DATASET = {
    # "file_name": "01 Ficheros/2_Datasets_input/Fase2/XXX.csv", # PRECIOVARIABLE_TOTAL
    "col_date": "fechaHora",
    "tecnologia": "TIPO",
    "descripcion": "Descripcion",
    "agente": "AGENTE",
    "codigo": "Codigo",
    "periodo": "Periodo",
    "propietario": "AGENTE PROPIETARIO",
    "cv": "CV",
    "codigo_bloque": "Codigo_bloque",
    "numbloq": "NumBloq",
    "price": "PrecEuro",
    "energia": "Energia",
    "features_units_agents": [
        "Codigo",
        "Descripcion",
        "Agente",
        "Porcentaje_Propiedad",
        "Tipo_Unidad",
        "Zona_Frontera",
        "Tecnologia",
    ],
    "features_omie": [
        "fechaHora",
        "Codigo",
        "Descripcion",
        "NumBloq",
        "CV",
        "PrecEuro",
        "Energia",
    ],
    "features_agent": ["Codigo", "Descripcion", "AGENTE PROPIETARIO", "TIPO"],
    "features_merge": [
        "Codigo",
        "fechaHora",
        "PrecEuro",
        "Energia",
        "precio_spot",
        "demanda",
        "EUA",
        "precio_gas",
        "prod_eolica",
        "prod_solar",
        "NumBloq",
        "AGENTE PROPIETARIO",
        "TIPO",
    ],
    "features_tecnology": [
        "Codigo",
        "Descripcion",
        "NumBloq",
        "fechaHora",
        "PrecEuro",
        "Energia",
        "Codigo_bloque",
        "TIPO",
        "AGENTE",
    ],
    "features": [
        "Codigo",
        "Descripcion",
        "NumBloq",
        "fechaHora",
        "PrecEuro",
        "Energia",
        "precio_spot",
        "demanda",
        "EUA",
        "precio_gas",
        "prod_eolica",
        "prod_solar",
        "Codigo_bloque",
        "TIPO",
        "AGENTE",
    ],
    "features_energy": [
        "Calculation",
        "Energia",
        "DemandaPrev",
        "GasPrice",
        "TIPO",
    ],
    "features_agentes": ["Codigo", "Descripcion", "AGENTE PROPIETARIO"],
    "features_na": [
        "fechaHora",
        "NumBloq",
        "Codigo",
        "PrecEuro",
        "Energia",
        "TIPO",
    ],
    "features_price": [
        "Calculation",
        "Energia",
        "PrecEuro",
        "GasPrice",
        "TIPO",
    ],
    "features_final": [
        "Codigo",
        "Descripcion",
        "NumBloq",
        "fechaHora",
        "PrecEuro",
        "Energia",
        "TIPO",
        "AGENTE",
        "demanda",
        "precio_spot",
    ],
    "features_complete": [
        "Codigo",
        "Descripcion",
        "NumBloq",
        "fechaHora",
        "PrecEuro",
        "Energia",
        "precio_spot",
        "demanda",
        "EUA",
        "precio_gas",
        "prod_eolica",
        "prod_solar",
        "T_BARCELONA",
        "P_BARCELONA",
        "R_BARCELONA",
        "V_BARCELONA",
        "T_MADRID",
        "P_MADRID",
        "R_MADRID",
        "V_MADRID",
        "T_A_CORUÑA",
        "P_A_CORUÑA",
        "R_A_CORUÑA",
        "V_A_CORUÑA",
        "T_VIZCAYA",
        "P_VIZCAYA",
        "R_VIZCAYA",
        "V_VIZCAYA",
        "T_VALENCIA",
        "P_VALENCIA",
        "R_VALENCIA",
        "V_VALENCIA",
        "T_MALAGA",
        "P_MALAGA",
        "R_MALAGA",
        "V_MALAGA",
        "T_CACERES",
        "P_CACERES",
        "R_CACERES",
        "V_CACERES",
    ],
    "fase2_techs": {
        "Carbón de Importación": "Carbón",
        "Ciclo Combinado": "Ciclo Combinado",
        "Hidráulica Generación": "Hidráulica",
        "Hidráulica de Bombeo Puro": "Hidráulica Bombeo",
        "Hulla Antracita": "Carbón",
        "Nuclear": "Nuclear",
        "RE Mercado Eólica": "Eólica",
        "RE Mercado Hidráulica": "Hidráulica",
        "RE Mercado Solar Fotovoltáica": "Solar",
        "RE Mercado Solar Térmica": "Térmica Renovable",
        "RE Mercado Térmica Renovable": "Térmica Renovable",
        "RE Mercado Térmica no Renovab.": "Térmica no Renovable",
        "RE Tar. CUR Eólica": "Eólica",
        "RE Tar. CUR Hidráulica": "Hidráulica",
        "RE Tar. CUR Solar Fotovoltáica": "Solar",
        "RE Tar. CUR Térmica Renovable": "Térmica Renovable",
        "RE Tar. CUR Térmica no Renov.": "Térmica no Renovable",
        "RE Tarifa CUR (uof)": "RE CUR",
        "Unidad Generica": "Unidad Genérica",
        "Almacenamiento Venta": "Almacenamiento Venta",
        "RE Mercado Geotérmica": "Geotérmica",
        "Import. de agentes externos": "Importaciones",
        "NOTECH": "NOTECH",
    },
}

FASE2_CONFIG = {
    "estaciones_dict": {
        "BARCELONA": "0076",
        "MADRID": "3129",
        "A_CORUÑA": "1387",
        "VIZCAYA": "1082",
        "VALENCIA": "8414A",
        "MALAGA": "6155A",
        "CACERES": "3469A",
    },
    "columns_cabeceras": [
        "CodOferta",
        "Version",
        "Codigo",
        "Descripcion",
        "CV",
        "Int",
        "NoUtil1",
        "OferPlazo",
        "NoUtil2",
        "NoUtil3",
        "MaxRamSub",
        "MaxRamBaj",
        "FijoEuro",
        "NoUtil4",
        "NoUtil5",
        "NoUtil6",
        "NoUtil7",
        "VarEuro",
        "MaxPot",
        "MaxRamArr",
        "MaxRamPar",
        "CodInt",
        "Year",
        "Month",
        "Day",
        "Hora",
        "Minuto",
        "Segundo",
        "fecha",
    ],
    "length_index_cabeceras": [
        0,
        8,
        10,
        17,
        47,
        49,
        50,
        58,
        66,
        68,
        76,
        84,
        92,
        100,
        108,
        116,
        124,
        132,
        140,
        146,
        153,
        155,
        159,
        161,
        163,
        165,
        167,
    ],
    "cabecera_index": {
        "CodOferta": 0,
        "Version": 7,
        "Codigo": 10,
        "Descripcion": 17,
        "CV": 47,
        "NoUtil1": 48,
        "OferPlazo": 49,
        "NoUtil2": 50,
        "NoUtil3": 67,
        "MaxRamSub": 84,
        "MaxRamBaj": 91,
        "FijoEuro": 98,
        "VarEuro": 115,
        "MaxPot": 132,
        "MaxRamArr": 139,
        "MaxRamPar": 146,
        "CodInt": 153,
        "Year": 155,
        "Month": 159,
        "Day": 161,
        "Hora": 163,
        "Minuto": 165,
        "Segundo": 167,
    },
    "columns_detalles": [
        "CodOferta",
        "Version",
        "Periodo",
        "NumBloq",
        "NoUtil",
        "PrecEuro",
        "Energia",
        "BloqInd",
        "BloqRet",
        "fecha",
        "fechaHora",
    ],
    "length_index_detalles": [0, 7, 10, 12, 14, 31, 48, 55, 56],
    # TODO: Gestion de fechas mas eficiente p.e. Reducir cantidad de fechas, incluir input, etc
    "day_bad_1": "2021-11-12",  # Formato: "%Y-%m-%d": No sé por que pero al leer el csv alguna fechas mancan las horas
    "day_bad_2": "2021-12-13",
    "string_fecha_inicio": "2021-12-26 00:00:00",  # Formato: "%Y-%d-%m %X"
    "string_fecha_fin": "2021-12-26 23:00:00",  # Formato: "%Y-%d-%m %X"
    "fecha_ini": "2021-12-26 00:00:00",  # Formato: "%Y-%m-%d %X"
    "fecha_fin": "2021-12-26 23:00:00",  # Formato: "%Y-%m-%d %X"
    "fecha_fin_train": "2021-12-26 23:00:00",
    "url_cabeceras": "https://www.omie.es/es/file-download?parents%5B0%5D=cab&filename=cab_{year_month}.zip",
    "url_detalles": "https://www.omie.es/es/file-download?parents%5B0%5D=det&filename=det_{year_month}.zip",
    "url_curva_pbc_uof": "https://www.omie.es/es/file-download?parents%5B0%5D=curva_pbc_uof&amp&filename=curva_pbc_uof_{year_month}.zip",
    "url_curva_pbc": "https://www.omie.es/es/file-access-list?parents%5B0%5D=/&parents%5B1%5D=Mercado%20Diario&parents%5B2%5D=3.%20Curvas&dir=Curvas%20agregadas%20de%20oferta%20y%20demanda%20del%20mercado%20diario&realdir=curva_pbc",
    "omie_start_date": "2021-12-26",  # Formato: "%Y-%m-%d"
    "omie_end_date": "2021-12-26",  # Formato: "%Y-%m-%d"
}

##################### STREAMLIT DASHBOARD #########################

DEFAULT_SESSION_STATE = {
    "flag": 1,
    "agg_plot": "FechaHora",
    "exog_agg": FASE1_DATASET["columns_input_v0"]["col_demand"],
    "fase_option": "MODELO 1 - Análisis",
    "fase2_agg": "Total",
    "fase2_code": None,
    "fase2_bloq": None,
    "fase2_code_box": 0,
    "fase2_bloq_box": 0,
    "fase2_show_plots": 0,
}

# LINE_COLOR_FASE_2 = {"energia": "darkorange", "precio": "olivedrab"}
