import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import streamlit as st

class Data:
    def __init__(self, filename):
        path = os.path.dirname(__file__)
        self.df = pd.read_excel(path+'/data/'+filename+'.xlsx')

    def get_data(self):
        return self.df
    
    def get_data_by_name(self, name):
        return self.df[self.df['Name of the Instrument'] == name]
    
    def get_data_by_ID(self, ID):
        return self.df[self.df['Instrument ID*/ ID thiết bị'] == ID]
    
def data_filter(df, type):
    try:
        if type=="Maintenance":
            columns = ['Name of the Instrument', 'Instrument ID*/ ID thiết bị','Department/Section\nBộ phận','Major/ Minor\nThiết bị chính/ Thiết bị phụ',
                    'Preventive maintence Date/ Ngày bảo trì bảo dưỡng cuối','PM Frequency/ lịch bảo trì bảo dưỡng định kỳ\n(month)',
                    'Preventive Maintence Due Date/ Hạn bảo trì bảo dưỡng','Expected date of maintenance / Ngày dự kiến bảo trì','Status of Maintenance'
                    ]
        elif type=="Calibration":
            columns = ['Name of the Instrument', 'Instrument ID*/ ID thiết bị','Department/Section\nBộ phận','Major/ Minor\nThiết bị chính/ Thiết bị phụ',
                    'Calibration Date/ Ngày hiệu chuẩn cuối','Calibration frequency/ Lịch hiệu chuẩn\n(year)',
                    'Calibration Due date/ Ngày hết hạn hiệu chuẩn','Expected date of calibration / Ngày dự kiến hiệu chuẩn','Status of Calibration'
                    ]
        return df[columns].dropna().reset_index(drop=True)
    except:
        return df

def create_schedule(raw_df, report_df, type):
    # Prepare raw data
    columns = ['Name of the Instrument', 'Instrument ID*/ ID thiết bị','Department/Section\nBộ phận','Major/ Minor\nThiết bị chính/ Thiết bị phụ']
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
    raw_df.rename(columns={'Name of the Instrument':'Name'}, inplace=True)
    raw_df.rename(columns={'Instrument ID*/ ID thiết bị':'ID'}, inplace=True)
    raw_df.rename(columns={'Department/Section\nBộ phận':'Department'}, inplace=True)
    raw_df.rename(columns={'Major/ Minor\nThiết bị chính/ Thiết bị phụ':'Major/Minor'}, inplace=True)

    # Prepare report data
    report_df = report_df[report_df['Type'] == type]
    report_df.rename(columns={'ID':'PID'}, inplace=True)
    report_df.rename(columns={'Instrument ID':'ID'}, inplace=True)
    report_df.rename(columns={'Complete Time':'Date'}, inplace=True)
    report_df['Date'] = report_df['Date'].dt.strftime('%Y/%m')
    report_df.drop_duplicates(subset=['ID','Date'], inplace=True)
    report_df = report_df[['ID','Date']]
    report_df['Date'] = report_df['Date'].str.replace('/0','/')
    report_df.sort_values(by=['ID','Date'], inplace=True, ascending=True)
    report_df.reset_index(drop=True, inplace=True)
    report_df

    # Create schedule
    calendar = pd.DataFrame()
    calendar['ID'] = raw_df['ID']
    calendar['Name'] = raw_df['Name']
    calendar['Department'] = raw_df['Department']
    calendar['Major/Minor'] = raw_df['Major/Minor']
    calendar['Date'] = raw_df['Date']
    calendar['Frequency'] = raw_df['Frequency']
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
st.write('This is a report for instrument data')
# Raw data
raw = Data('Instrument_Data')
raw_df = raw.get_data()
report = Data('report_data')
report_df = report.get_data()
# Form
form = st.form("Choice data")
instrument_list = np.insert(raw_df['Name of the Instrument'].unique(),0,'All')
name = form.selectbox("Name of instrument: ", instrument_list)
instrument_list_ID = np.insert(raw_df[raw_df['Name of the Instrument']==name]['Instrument ID*/ ID thiết bị'].unique(),0,'All')
ID = form.selectbox("Instrument ID: ", instrument_list_ID)
handle_type = form.selectbox("Type of table: ",['All','Breakdown','Maintenance','Calibration'])
form.form_submit_button("Get data")

# Showing data tables
menu = st.container()
col1, col2, col3 = menu.columns(3)
raw_btn = col1.button("Raw data")
report_btn = col2.button("Report data")
handle_btn = col3.button("Handle data")
# ''''''

if __name__=="__main__":
    # Raw data
    if raw_btn:
        raw_container = st.container()
        raw_container.header('Raw Data')
        raw_container.write(raw_df)
    # Data by report
    if report_btn:
        if name != 'All':
            report_df = report_df[report_df['Name']==name]
        if ID != 'All':
            report_df = report_df[report_df['Instrument ID']==ID]
        if handle_type != 'All':
            report_df = report_df[report_df['Type']==handle_type]

        instrument_container = st.container()
        instrument_container.header('Data by Instrument')
        instrument_container.write(report_df)
    # Handle data
    if handle_btn:
        if handle_type in ['Maintenance', 'Calibration']:
            data_filtered = data_filter(raw_df, handle_type)
            report_dt = report_df[report_df['Type']==handle_type]
            schedule = create_schedule(data_filtered,report_dt, handle_type)

            handle_container = st.container()
            handle_container.header(f'Table for {handle_type}')
            handle_container.write(data_filtered)
            handle_container.header(f'Schedule for {handle_type}')
            handle_container.write(schedule)
            schedule.to_csv(f'output/{handle_type}_schedule.csv')
        else:
            st.text("Wrong type of table")