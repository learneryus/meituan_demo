# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 13:36:07 2026

@author: jiayou
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --------------------------
# 1. 页面基础配置（美观设置）
# --------------------------
st.set_page_config(
    page_title="美团跨业务导流分析",
    layout="wide",
    page_icon="📊"
)

st.markdown("""<style>
    .stDeployButton {visibility:hidden;}
    footer {visibility:hidden;}
    .main {background-color: #f8f9fa;}
</style>""", unsafe_allow_html=True)

st.title("📈 美团跨业务导流效果可视化分析")
st.markdown("---")

# --------------------------
# 2. 读取数据
# --------------------------
# 请确保路径正确
df = pd.read_excel(r"result_2_1.xlsx")
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

bu_map = {0: "跨BU", 1: "同BU"}
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

# 🔴 核心修复点：强制重置索引，确保连续的 0,1,2,3... 
# 这样 Plotly 在依据 color 拆分图层时，内部数组绝对不会错位！
filtered_df = filtered_df.reset_index(drop=True)

# --------------------------
# 5. 按钮：显示路径
# --------------------------
st.subheader("🫧 导流效果气泡图")
show_label = st.button("显示路径")  # 按钮状态会触发图表重绘

# --------------------------
# 6. 绘制气泡图（彻底告别错位版）
# --------------------------
if len(filtered_df) > 0:
    
    # 1. 提前在 DataFrame 中构造好需要显示的文本路径
    filtered_df['path_name'] = filtered_df['first_cate_name_A'] + " → " + filtered_df['first_cate_name_B']

    # 2. 将 custom_data 直接交给 px.scatter
    custom_cols = ['path_name', 'Flow_Rate1', 'Flow_Rate2', 'Flow_Diff', 'CVR_1', 'CVR_2', 'CVR_Diff']
    
    fig = px.scatter(
        filtered_df,
        x="Flow_Diff",
        y="CVR_Diff",
        size="n_A_to_B",
        color="category_A",   
        size_max=60,
        opacity=0.85,
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        text="path_name" if show_label else None,  
        custom_data=custom_cols                    
    )

    # 3. 散点旁的固定文本样式
    if show_label:
        fig.update_traces(
            textposition="top center", 
            textfont=dict(size=11, color="#333333"), 
            texttemplate="%{text}"
        )

    # 4. 彻底重写悬浮框模板
    # 注意最后的 <extra></extra>，只要索引不错乱，这个魔法标签能100%干掉旁边那个带颜色的提示尾巴
    hover_template = (
        "<b>%{customdata[0]}</b><br>"
        "---------------------<br>"
        "Flow_Rate1: %{customdata[1]:.4f}<br>"
        "Flow_Rate2: %{customdata[2]:.4f}<br>"
        "Flow_Diff:  %{customdata[3]:.4f}<br>"
        "---------------------<br>"
        "CVR_1:    %{customdata[4]:.4f}<br>"
        "CVR_2:    %{customdata[5]:.4f}<br>"
        "CVR_Diff: %{customdata[6]:.4f}<extra></extra>"
    )

    fig.update_traces(hovertemplate=hover_template)

    # 5. 添加基准线
    fig.add_vline(x=0, line_width=2, line_color="#999999", line_dash="dash")
    fig.add_hline(y=0, line_width=2, line_color="#999999", line_dash="dash")

    # 6. 图表全局美化
    fig.update_layout(
        xaxis_title="导流率差值 (Flow_Diff)",
        yaxis_title="转化率差值 (CVR_Diff)",
        font=dict(family="Microsoft YaHei", size=13),
        legend_title="来源业务分类 (大类)",
        height=650,
        plot_bgcolor="white",
        paper_bgcolor="white",
        hoverlabel=dict(
            bgcolor="white", 
            font_size=12, 
            font_family="Microsoft YaHei",
            bordercolor="#ccc"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ 当前筛选条件下无数据，请调整筛选条件")

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
    # 这里的 show_df 因为是从 filtered_df copy 的，索引已经干净了
    show_df = filtered_df[table_cols].copy()
    show_df["Flow_Rate1"] = show_df["Flow_Rate1"].round(4)
    show_df["CVR_1"] = show_df["CVR_1"].round(4)
    st.dataframe(show_df, use_container_width=True, height=400)