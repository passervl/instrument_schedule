import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import streamlit as st
from src.get_data import Data, data_filter
from src.side_bar import side_bar, home, report

def create_schedule(raw_df, report_df, type):
    # Prepare raw data
    columns = ['Name', 'ID','Department','Major/Minor']
    if type=="Maintenance":
        columns += ['Preventive maintence Date/ Ngày bảo trì bảo dưỡng cuối','PM Frequency/ lịch bảo trì bảo dưỡng định kỳ\n(month)']
        raw_df = raw_df[columns].dropna()
        raw_df['Preventive maintence Date/ Ngày bảo trì bảo dưỡng cuối'] = pd.to_datetime(raw_df['Preventive maintence Date/ Ngày bảo trì bảo dưỡng cuối'], format='%d/%m/%Y')
        raw_df.rename(columns={'Preventive maintence Date/ Ngày bảo trì bảo dưỡng cuối':'Date'}, inplace=True)
        raw_df.rename(columns={'PM Frequency/ lịch bảo trì bảo dưỡng định kỳ\n(month)':'Frequency'}, inplace=True)            
    elif type=="Calibration":
        columns += ['Calibration Date/ Ngày hiệu chuẩn cuối','Calibration frequency/ Lịch hiệu chuẩn\n(year)']
        raw_df = raw_df[columns].dropna()
        raw_df['Calibration Date/ Ngày hiệu chuẩn cuối'] = pd.to_datetime(raw_df['Calibration Date/ Ngày hiệu chuẩn cuối'], format='%d/%m/%Y')
        raw_df.rename(columns={'Calibration Date/ Ngày hiệu chuẩn cuối':'Date'}, inplace=True)
        raw_df.rename(columns={'Calibration frequency/ Lịch hiệu chuẩn\n(year)':'Frequency'}, inplace=True)
    raw_df['Date'] = raw_df['Date'].dt.strftime('%Y/%m')
    raw_df['Frequency'] = raw_df['Frequency'].astype(int)

    # Prepare report data
    report_df = report_df[report_df['Type'] == type]
    report_df.rename(columns={'Complete Time':'Date'}, inplace=True)
    report_df['Date'] = report_df['Date'].dt.strftime('%Y/%m')
    report_df.drop_duplicates(subset=['ID','Date'], inplace=True)
    report_df = report_df[['ID','Date']]
    report_df['Date'] = report_df['Date'].str.replace('/0','/')
    report_df.sort_values(by=['ID','Date'], inplace=True, ascending=True)
    report_df.reset_index(drop=True, inplace=True)

    # Create schedule
    calendar = pd.DataFrame()
    calendar['ID'] = raw_df['ID']
    calendar['Name'] = raw_df['Name']
    calendar['Department'] = raw_df['Department']
    calendar['Major/Minor'] = raw_df['Major/Minor']
    calendar['Date'] = raw_df['Date']
    if type == "Maintenance": calendar['Frequency'] = raw_df['Frequency']
    else: calendar['Frequency'] = raw_df['Frequency']*12
    for i in range(len(calendar)):
        frequency = calendar.iloc[i]['Frequency']
        if frequency == 0: calendar.iloc[i]['Frequency'] = 1

        ID = calendar.iloc[i]['ID']
        if type == 'Maintenance':
            months = report_df[report_df['ID']==ID]['Date'].str.split('/').str[1].astype(int)
            month_base = months.min()
            month_last = months.max()
            for j in range(1,13):
                if j in [month_base+n*frequency for n in range(-12,12)] and j <= month_last:
                    calendar.loc[i,f'2023/{j}'] = False
        for date in report_df[report_df['ID']==ID]['Date']:
            calendar.loc[i,date] = True

    header = ['ID', 'Name', 'Department', 'Major/Minor', 'Date', 'Frequency']
    for i in range(1,13):
        header.append(f'2023/{i}')
    return calendar.reindex(columns=header)

# '''Repairing data'''
st.title('Report')
st.write('Create report and schedule for instruments data')
# Raw data
raw = Data('Instrument_Data')
raw_df = raw.get_data()
report = Data('report_data')
report_df = report.get_data()
# Form
form = st.form("Choice data")
instrument_list = np.insert(raw_df['Name'].unique(),0,'All')
name = form.selectbox("Name of instrument: ", instrument_list)
instrument_list_ID = np.insert(raw_df[raw_df['Name']==name]['ID'].unique(),0,'All')
ID = form.selectbox("Instrument ID: ", instrument_list_ID)
handle_type = form.selectbox("Type of table: ",['All','Breakdown','Maintenance','Calibration'])
form.form_submit_button("Get data")

# Showing data tables
menu = st.container()
col1, col2, col3 = menu.columns(3)
raw_btn = col1.button("Raw data")
report_btn = col2.button("Report data")
handle_btn = col3.button("Handle data")

side_bar()
# ''''''

if __name__=="__main__":
    # Raw data
    if raw_btn:
        raw_container = st.container()
        raw_container.header('Raw Data')
        raw_container.write(raw_df)
    # Data by report
    if report_btn:
        file_name = 'report'
        if name != 'All':
            report_df = report_df[report_df['Name']==name]
            file_name +=f'_{name}'
        if ID != 'All':
            report_df = report_df[report_df['ID']==ID]
            file_name +=f'_{ID}'
        if handle_type != 'All':
            report_df = report_df[report_df['Type']==handle_type]
            file_name +=f'_{handle_type}'

        instrument_container = st.container()
        instrument_container.header('Data by Instrument')
        instrument_container.write(report_df)
        report_df.to_csv(f'output/report/{file_name}.csv',encoding='utf-8-sig')
    # Handle data
    if handle_btn:
        if handle_type in ['Maintenance', 'Calibration']:
            data_filtered = data_filter(raw_df, handle_type)
            report_dt = report_df[report_df['Type']==handle_type]
            schedule = create_schedule(data_filtered,report_dt, handle_type)

            handle_container = st.container()
            handle_container.header(f'Report for {handle_type}')
            handle_container.write(data_filtered)
            data_filtered.to_csv(f'output/report/{handle_type}_report.csv', encoding='utf-8-sig')
            handle_container.header(f'Schedule for {handle_type}')
            handle_container.write(schedule)
            schedule.to_csv(f'output/schedule/{handle_type}_schedule.csv', encoding='utf-8-sig')
        else:
            st.text("Wrong type of table")