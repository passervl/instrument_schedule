import pandas as pd
import numpy as np
import os

class Data:
    def __init__(self, filename):
        path = os.path.dirname(__file__).replace('src','')
        self.df = pd.read_excel(path+'/data/'+filename+'.xlsx')
        self.df.rename(columns={'Name of the Instrument':'Name'}, inplace=True)
        self.df.rename(columns={'Department/Section\nBộ phận':'Department'}, inplace=True)
        self.df.rename(columns={'Major/ Minor\nThiết bị chính/ Thiết bị phụ':'Major/Minor'}, inplace=True)
        self.df.rename(columns={'Manufacturer/ Model\nHãng sản xuất/ Model':'Manufacturer/Model'}, inplace=True)
        self.df.rename(columns={'Serial Number/ Số máy':'Serial Number'}, inplace=True)
        self.df.rename(columns={'ID':'PID'}, inplace=True)
        self.df.rename(columns={'Instrument ID*/ ID thiết bị':'ID'}, inplace=True)
        self.df.rename(columns={'Instrument ID':"ID"}, inplace=True)

        self.names = self.df['Name'].unique()
        self.IDs = self.df['ID'].unique()

    def get_data(self):
        return self.df
    
    def get_data_by_name(self, name):
        return self.df[self.df['Name of the Instrument'] == name]
    
    def get_data_by_ID(self, ID):
        return self.df[self.df['Instrument ID*/ ID thiết bị'] == ID]
    

def data_filter(df, type):
    try:
        if type=="Maintenance":
            columns = ['Name', 'ID','Department','Major/Minor',
                    'Preventive maintence Date/ Ngày bảo trì bảo dưỡng cuối','PM Frequency/ lịch bảo trì bảo dưỡng định kỳ\n(month)',
                    'Preventive Maintence Due Date/ Hạn bảo trì bảo dưỡng','Expected date of maintenance / Ngày dự kiến bảo trì','Status of Maintenance'
                    ]
        elif type=="Calibration":
            columns = ['Name', 'ID','Department','Major/Minor',
                    'Calibration Date/ Ngày hiệu chuẩn cuối','Calibration frequency/ Lịch hiệu chuẩn\n(year)',
                    'Calibration Due date/ Ngày hết hạn hiệu chuẩn','Expected date of calibration / Ngày dự kiến hiệu chuẩn','Status of Calibration'
                    ]
        return df[columns].dropna().reset_index(drop=True)
    except:
        return df