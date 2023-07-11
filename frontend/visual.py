# importing required libraries

import numpy as np
import pandas as pd
import streamlit as st

# creating a sample data consisting different points

df = pd.DataFrame(
    np.random.randn(800, 2) / [50, 50] + [46.34, -108.7],
    columns=["latitude", "longitude"],
)


# plotting a map with the above defined points

st.map(df)
