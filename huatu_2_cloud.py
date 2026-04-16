# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 13:36:07 2026

@author: jiayou
"""

# 导入核心库
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --------------------------
# 1. 页面基础配置
# --------------------------
st.set_page_config(
    page_title="美团跨业务导流分析",
    layout="wide",
    page_icon="📊"
)

st.markdown("""<style>
    .stDeployButton {visibility:hidden;}
    footer {visibility:hidden;}
    .main {background-color:#f8f9fa;}
</style>""", unsafe_allow_html=True)

st.title("📈 美团跨业务导流效果可视化分析")
st.markdown("---")

# --------------------------
# 2. 云端专用：相对路径读取数据（✅ 已改好）
# --------------------------
df = pd.read_excel("result_2.xlsx")
df = df.dropna()
df['revenue'] = df['n_A_to_B_order'].astype(int).astype(str) + "p"

# --------------------------
# 3. 侧边栏筛选器
# --------------------------
st.sidebar.header("🔍 筛选条件")

min_flow = st.sidebar.slider("最小流转会话数(n_A_to_B)", 
                             min_value=int(df["n_A_to_B"].min()), 
                             max_value=int(df["n_A_to_B"].max()), 
                             value=100)

b_list = ["全部"] + sorted(df["first_cate_name_B"].unique().tolist())
target_b = st.sidebar.selectbox("目标业务(first_cate_name_B)", b_list)

a_list = ["全部"] + sorted(df["first_cate_name_A"].unique().tolist())
source_a = st.sidebar.selectbox("流量来源(first_cate_name_A)", a_list)

bu_choice = st.sidebar.selectbox("业务类型", ["全部", "跨BU", "同BU"])

# --------------------------
# 4. 执行筛选
# --------------------------
filtered_df = df[df["n_A_to_B"] >= min_flow].copy()

if target_b != "全部":
    filtered_df = filtered_df[filtered_df["first_cate_name_B"] == target_b]
if source_a != "全部":
    filtered_df = filtered_df[filtered_df["first_cate_name_A"] == source_a]
if bu_choice != "全部":
    bu_val = 0 if bu_choice == "跨BU" else 1
    filtered_df = filtered_df[filtered_df["is_same_category"] == bu_val]

# --------------------------
# 5. 按钮：显示路径
# --------------------------
st.subheader("🫧 导流效果气泡图")
show_label = st.button("显示路径")

# --------------------------
# 6. 绘制气泡图（✅ 已修复：十字线 + 标签 + 悬浮提示）
# --------------------------
if len(filtered_df) > 0:
    hover_template = """
    <b>%{text}</b><br>
    Flow_Rate1: %{customdata[0]:.4f}<br>
    Flow_Rate2: %{customdata[1]:.4f}<br>
    Flow_Diff: %{customdata[2]:.4f}<br>
    CVR_1: %{customdata[3]:.4f}<br>
    CVR_2: %{customdata[4]:.4f}<br>
    CVR_Diff: %{customdata[5]:.4f}<br>
    """
    text_data = filtered_df['first_cate_name_A'] + " → " + filtered_df['first_cate_name_B']
    custom_data = filtered_df[['Flow_Rate1','Flow_Rate2','Flow_Diff','CVR_1','CVR_2','CVR_Diff']].values

    if show_label:
        fig = px.scatter(
            filtered_df, x="Flow_Diff", y="CVR_Diff",
            size="n_A_to_B", color="category_A",
            size_max=60, opacity=0.85,
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            text=text_data
        )
        fig.update_traces(textposition="top center", textfont=dict(size=11))
    else:
        fig = px.scatter(
            filtered_df, x="Flow_Diff", y="CVR_Diff",
            size="n_A_to_B", color="category_A",
            size_max=60, opacity=0.85,
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

    # ✅ 十字线
    fig.add_vline(x=0, line_width=2, line_color="#999", line_dash="dash")
    fig.add_hline(y=0, line_width=2, line_color="#999", line_dash="dash")

    fig.update_layout(
        xaxis_title="导流率差值 (Flow_Diff)",
        yaxis_title="转化率差值 (CVR_Diff)",
        font=dict(family="Microsoft YaHei", size=13),
        height=650, plot_bgcolor="white", paper_bgcolor="white"
    )

    fig.update_traces(hovertemplate=hover_template, text=text_data, customdata=custom_data)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ 当前筛选条件下无数据")

# --------------------------
# 7. 数据表格
# --------------------------
st.markdown("---")
st.subheader("📋 筛选结果详情表")
table_cols = [
    "first_cate_name_A", "first_cate_name_B",
    "category_A", "category_B",
    "n_A_to_B", "n_A_to_B_order",
    "n_A", "Flow_Rate1", "CVR_1", "revenue"
]

if len(filtered_df) > 0:
    show_df = filtered_df[table_cols].reset_index(drop=True)
    show_df["Flow_Rate1"] = show_df["Flow_Rate1"].round(4)
    show_df["CVR_1"] = show_df["CVR_1"].round(4)
    st.dataframe(show_df, use_container_width=True, height=400)