#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import numpy as np
import os
import openpyxl

st.title("📦 Optimización de Almacén: Asignación de Referencias a zona Preferente")

# Cargar archivos de entrada
st.sidebar.header("Sube los archivos de entrada")
lineas_pedidos_file = st.sidebar.file_uploader("Subir Lineas_Pedidos.xlsx", type=["xlsx"])
item_vol_file = st.sidebar.file_uploader("Subir Item_Vol.xlsx", type=["xlsx"])

if lineas_pedidos_file and item_vol_file:
    # Cargar datos
    lineas_pedidos = pd.read_excel(lineas_pedidos_file)
    item_vol = pd.read_excel(item_vol_file)
    
    # Cálculo de volúmenes
    item_vol["Volume"] = item_vol["X"] * item_vol["Y"] * item_vol["Z"]
    
    # Contar líneas por item
    lines_count = lineas_pedidos.groupby("item").size().reset_index(name="lines")
    
    # Cantidad total por item
    total_quantity = lineas_pedidos.groupby("item")["quantity"].sum().reset_index(name="total_quantity")
    
    # Fusionar datos
    item_results = pd.merge(lines_count, total_quantity, on='item')
    item_results = pd.merge(item_results, item_vol, on="item", how="left")
    
    # Calcular volumen total y índice de prioridad
    item_results["total_volume"] = item_results["Volume"] * item_results["total_quantity"]
    item_results["SQRtotal_volume"] = np.sqrt(item_results["total_volume"])
    item_results["Priority_index"] = item_results["lines"] / item_results["SQRtotal_volume"]
    
    # Ordenar por índice de prioridad
    item_results = item_results.sort_values(by="Priority_index", ascending=False)
    
    # Ingreso de parámetros por usuario
    n = st.number_input("Número de items a incluir en ZPA", min_value=1, max_value=len(item_results), value=10)
    Shelve_volume = st.number_input("Introducir huecos totales de Zona Preferente", min_value=1.0, value=100.0)
    
    # Filtrar los primeros N items
    item_results_red = item_results.head(n)
    
    # Asignar volumen
    Sum_RF = item_results_red['SQRtotal_volume'].sum()
    item_results_red['Asig_Vol'] = round(item_results_red['SQRtotal_volume'] / Sum_RF * Shelve_volume)
    
    # Mostrar resultados
    st.subheader("📊 Lista de items seleccionados con sus huecos en Zona Preferente:")
    st.dataframe(item_results_red[['item', 'Asig_Vol']])
    
    # Permitir descargar el archivo de salida
    output_path = "Item_Results.xlsx"
    item_results.to_excel(output_path, index=False)
    with open(output_path, "rb") as file:
        st.download_button(label="📥 Descargar Resultados", data=file, file_name="Item_Results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        


# In[ ]:




