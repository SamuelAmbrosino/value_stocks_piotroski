#!/bin/bash

# Crear carpetas principales
mkdir -p data/raw data/processed data/external
mkdir -p notebooks
mkdir -p src/data src/features src/models src/visualization src/utils
mkdir -p reports/figures
mkdir -p docs

# Crear archivos base vacíos
touch README.md LICENSE requirements.txt setup.py
touch notebooks/01_data_exploration.ipynb notebooks/02_feature_engineering.ipynb notebooks/03_modeling.ipynb notebooks/04_visualization.ipynb
touch src/data/data_loader.py src/features/fscore.py src/models/predictive_model.py src/visualization/dashboard.py src/utils/helpers.py
# El archivo final_report.pdf se crea normalmente generándolo, aquí solo se deja el directorio de destino.

echo "Estructura del proyecto creada exitosamente."
