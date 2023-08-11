import streamlit as st
import pandas as pd
import numpy as np
from data import Data, data_filter

st.title('Report')
st.write('This is a report for instrument data')

# data form for user
form = st.form("Let's get data")
instrument_list = np.insert(raw_df['Name of the Instrument'].unique(),0,'All')