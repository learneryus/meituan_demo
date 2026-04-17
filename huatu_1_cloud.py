# -*- coding: utf-8 -*-
"""
cd D:\美团商赛\美团业务选题\our_work\demo

streamlit run huatu_1.py

"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --------------------------
# 1. 页面基础配置
# --------------------------
st.set_page_config(
    page_title="美团跨业务导流分析(本地版-修复版)",
    layout="wide",
    page_icon="📊"
)

st.markdown("""<style>
    .stDeployButton {visibility:hidden;}
    footer {visibility:hidden;}
    .main {background-color:#f8f9fa;}
</style>""", unsafe_allow_html=True)

st.title("📈 美团跨业务导流效果可视化分析 (完美修复版)")
st.markdown("---")

# --------------------------
# 2. 本地读取数据
# --------------------------
# 🌟 请确保该路径与你本地实际路径一致 🌟
file_path = r"result_1_1.xlsx" 

df = pd.read_excel(file_path)
df = df.dropna()

# 生成 revenue 列
df['revenue'] = df['n_A_to_B_order'].astype(int).astype(str) + "p"

# --------------------------
# 3. 侧边栏筛选器
# --------------------------
st.sidebar.header("🔍 筛选条件")

min_flow = st.sidebar.slider("最小流转会话数(n_A_to_B)", 
                             min_value=int(df["n_A_to_B"].min()), 
                             max_value=int(df["n_A_to_B"].max()), 
                             value=100)

b_list = ["全部"] + sorted(df["category_B"].unique().tolist())
target_b = st.sidebar.selectbox("目标业务(category_B)", b_list)

a_list = ["全部"] + sorted(df["category_A"].unique().tolist())
source_a = st.sidebar.selectbox("流量来源(category_A)", a_list)

bu_choice = st.sidebar.selectbox("业务类型", ["全部", "跨BU", "同BU"])

# --------------------------
# 4. 执行筛选
# --------------------------
filtered_df = df[df["n_A_to_B"] >= min_flow].copy()

if target_b != "全部":
    filtered_df = filtered_df[filtered_df["category_B"] == target_b]
if source_a != "全部":
    filtered_df = filtered_df[filtered_df["category_A"] == source_a]
if bu_choice != "全部":
    bu_val = 0 if bu_choice == "跨BU" else 1
    filtered_df = filtered_df[filtered_df["is_same_category"] == bu_val]

# --------------------------
# 5. 按钮：显示路径
# --------------------------
st.subheader("🫧 导流效果气泡图")
show_label = st.button("显示路径")

# --------------------------
# 6. 绘制气泡图（彻底修复悬浮框错位 Bug 版）
# --------------------------
if len(filtered_df) > 0:
    # 1. 将生成的文本列直接加到 dataframe 中，避免索引错乱
    filtered_df['path_name'] = filtered_df['category_A'] + " → " + filtered_df['category_B']
    
    # 2. 创建图表：将 custom_data 直接写进 px.scatter 里
    # 这样 Plotly 在按 color 拆分图层时，会自动帮你把 custom_data 也拆分对齐！
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
        text="path_name" if show_label else None,  # 直接指定列名
        # ⚠️ 关键修复：把需要悬浮显示的列名，按顺序放在这里
        custom_data=['path_name', 'Flow_Rate1', 'Flow_Rate2', 'Flow_Diff', 'CVR_1', 'CVR_2', 'CVR_Diff']
    )

    # 3. 调整散点旁边的固定标签样式
    if show_label:
        fig.update_traces(
            textposition="top center", 
            textfont=dict(size=11, color='#333333'),  # 深灰色
            texttemplate="%{text}" # 强制只显示文本
        )

    # 4. 设置悬浮框模板
    # 这里的 customdata 索引严格对应上面 px.scatter 里的 custom_data 列表顺序
    hover_template = (
        "<b>路径：%{customdata[0]}</b><br>"
        "---------------------<br>"
        "Flow_Rate1: %{customdata[1]:.4f}<br>"
        "Flow_Rate2: %{customdata[2]:.4f}<br>"
        "Flow_Diff:  %{customdata[3]:.4f}<br>"
        "---------------------<br>"
        "CVR_1:    %{customdata[4]:.4f}<br>"
        "CVR_2:    %{customdata[5]:.4f}<br>"
        "CVR_Diff: %{customdata[6]:.4f}<extra></extra>" 
    )

    # 5. 仅更新模板，不再传入 values
    fig.update_traces(hovertemplate=hover_template)

    # 6. 添加十字基准线
    fig.add_vline(x=0, line_width=2, line_color="#999", line_dash="dash")
    fig.add_hline(y=0, line_width=2, line_color="#999", line_dash="dash")

    # 7. 整体布局与UI优化
    fig.update_layout(
        xaxis_title="导流率差值 (Flow_Diff)",
        yaxis_title="转化率差值 (CVR_Diff)",
        font=dict(family="Microsoft YaHei", size=13),
        height=650, 
        plot_bgcolor="white", 
        paper_bgcolor="white",
        hoverlabel=dict(
            bgcolor="white", 
            font_size=12, 
            font_family="Microsoft YaHei",
            bordercolor="#ccc"
        ),
        legend=dict(
            title="流量来源 (A)", 
            orientation="v"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ 当前筛选条件下无数据")

# --------------------------
# 7. 数据表格
# --------------------------
st.markdown("---")
st.subheader("📋 筛选结果详情表")
table_cols = [
    "category_A", "category_B",
    "n_A_to_B", "n_A_to_B_order",
    "n_A", "Flow_Rate1", "CVR_1", "CVR_Diff", "revenue"
]

if len(filtered_df) > 0:
    show_df = filtered_df[table_cols].reset_index(drop=True)
    # 保留6位小数，方便核对数据
    show_df["Flow_Rate1"] = show_df["Flow_Rate1"].round(6)
    show_df["CVR_1"] = show_df["CVR_1"].round(6)
    show_df["CVR_Diff"] = show_df["CVR_Diff"].round(6)
    st.dataframe(show_df, use_container_width=True, height=400)