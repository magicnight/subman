"""
数据导入模块 - 支持从文件导入订阅数据（备份恢复）
"""
import io
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any

from ..config import (
    SUBSCRIPTIONS_FILE,
    CSV_ENCODING,
    REQUIRED_COLUMNS,
    DEFAULT_CURRENCY
)
from .validator import validate_dataframe, ValidationError
from .data_loader import save_subscriptions, load_subscriptions


def parse_csv_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    解析上传的 CSV 文件
    
    Args:
        uploaded_file: Streamlit 上传的文件对象
        
    Returns:
        pd.DataFrame: 解析后的数据框，失败返回 None
    """
    try:
        # 读取 CSV 文件
        df = pd.read_csv(
            uploaded_file,
            encoding=CSV_ENCODING,
            dtype=str  # 先全部读取为字符串，后续转换
        )
        
        # 检查必需的列
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            st.error(f"❌ 缺少必需的列: {', '.join(missing_cols)}")
            return None
        
        # 数据清洗和转换
        df = clean_imported_data(df)
        
        return df
    except Exception as e:
        st.error(f"❌ 解析 CSV 文件失败: {str(e)}")
        return None


def parse_excel_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    解析上传的 Excel 文件
    
    Args:
        uploaded_file: Streamlit 上传的文件对象
        
    Returns:
        pd.DataFrame: 解析后的数据框，失败返回 None
    """
    try:
        # 读取 Excel 文件（第一个工作表）
        df = pd.read_excel(uploaded_file, sheet_name=0, dtype=str)
        
        # 检查必需的列
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            st.error(f"❌ 缺少必需的列: {', '.join(missing_cols)}")
            return None
        
        # 数据清洗和转换
        df = clean_imported_data(df)
        
        return df
    except Exception as e:
        st.error(f"❌ 解析 Excel 文件失败: {str(e)}")
        return None


def parse_json_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    解析上传的 JSON 文件
    
    Args:
        uploaded_file: Streamlit 上传的文件对象
        
    Returns:
        pd.DataFrame: 解析后的数据框，失败返回 None
    """
    try:
        # 读取 JSON 文件
        content = uploaded_file.read()
        data = pd.read_json(io.BytesIO(content), orient='records')
        
        # 检查必需的列
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in data.columns]
        if missing_cols:
            st.error(f"❌ 缺少必需的列: {', '.join(missing_cols)}")
            return None
        
        # 数据清洗和转换
        df = clean_imported_data(data)
        
        return df
    except Exception as e:
        st.error(f"❌ 解析 JSON 文件失败: {str(e)}")
        return None


def clean_imported_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    清洗导入的数据
    
    Args:
        df: 原始数据框
        
    Returns:
        pd.DataFrame: 清洗后的数据框
    """
    # 去除前后空格
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
    
    # 处理空值
    df = df.replace(['', 'nan', 'None', 'null'], pd.NA)
    
    # 转换数据类型
    if '金额' in df.columns:
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce')
    
    if '月均成本' in df.columns:
        df['月均成本'] = pd.to_numeric(df['月均成本'], errors='coerce')
    
    if '剩余天数' in df.columns:
        df['剩余天数'] = pd.to_numeric(df['剩余天数'], errors='coerce')
    
    # 处理日期
    if '下次付费时间' in df.columns:
        df['下次付费时间'] = pd.to_datetime(df['下次付费时间'], errors='coerce')
    
    # 处理布尔值
    if '自动续费' in df.columns:
        df['自动续费'] = df['自动续费'].apply(parse_boolean)
    
    # 处理货币字段（如果缺失，使用默认值）
    if '货币' not in df.columns or df['货币'].isna().all():
        df['货币'] = DEFAULT_CURRENCY
    
    # 填充空值
    if '供应商' in df.columns:
        df['供应商'] = df['供应商'].fillna('')
    
    return df


def parse_boolean(value: Any) -> bool:
    """
    解析布尔值（支持多种格式）
    
    Args:
        value: 输入值
        
    Returns:
        bool: 解析后的布尔值
    """
    if pd.isna(value):
        return False
    
    value_str = str(value).strip().upper()
    
    # 支持多种格式
    true_values = ['TRUE', 'T', 'YES', 'Y', '1', '是', '真', 'TRUE']
    false_values = ['FALSE', 'F', 'NO', 'N', '0', '否', '假', 'FALSE']
    
    if value_str in true_values:
        return True
    elif value_str in false_values:
        return False
    else:
        return False  # 默认值


def import_subscriptions(df: pd.DataFrame, merge_mode: str = 'replace') -> bool:
    """
    导入订阅数据
    
    Args:
        df: 要导入的数据框
        merge_mode: 合并模式 ('replace' 替换, 'append' 追加, 'merge' 合并)
        
    Returns:
        bool: 是否成功
    """
    try:
        # 确保数据框包含必需的列
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            st.error(f"❌ 缺少必需的列: {', '.join(missing_cols)}")
            return False
        
        # 验证数据（如果验证器可用）
        try:
            validate_dataframe(df)
        except Exception as e:
            # 验证失败时给出警告，但不阻止导入
            st.warning(f"⚠️ 数据验证警告: {str(e)}，将继续导入")
        
        # 移除计算字段（这些字段会在加载时重新计算）
        df_clean = df.drop(columns=['剩余天数', '月均成本'], errors='ignore')
        
        # 根据合并模式处理数据
        if merge_mode == 'replace':
            # 直接替换
            result_df = df_clean.copy()
        elif merge_mode == 'append':
            # 追加到现有数据
            existing_df = load_subscriptions()
            if existing_df.empty:
                result_df = df_clean.copy()
            else:
                # 移除计算字段以便合并
                existing_df_clean = existing_df.drop(columns=['剩余天数', '月均成本'], errors='ignore')
                result_df = pd.concat([existing_df_clean, df_clean], ignore_index=True)
                # 去除重复（基于名称）
                result_df = result_df.drop_duplicates(subset=['名称'], keep='last')
        elif merge_mode == 'merge':
            # 合并（更新现有，添加新的）
            existing_df = load_subscriptions()
            if existing_df.empty:
                result_df = df_clean.copy()
            else:
                # 移除计算字段以便合并
                existing_df_clean = existing_df.drop(columns=['剩余天数', '月均成本'], errors='ignore')
                
                # 合并数据框
                result_df = existing_df_clean.copy()
                for _, row in df_clean.iterrows():
                    name = row['名称']
                    # 如果存在则更新，否则追加
                    if name in result_df['名称'].values:
                        idx = result_df[result_df['名称'] == name].index[0]
                        result_df.loc[idx] = row
                    else:
                        result_df = pd.concat([result_df, pd.DataFrame([row])], ignore_index=True)
        else:
            st.error(f"❌ 未知的合并模式: {merge_mode}")
            return False
        
        # 保存数据
        if save_subscriptions(result_df):
            return True
        else:
            st.error("❌ 保存数据失败")
            return False
            
    except ValidationError as e:
        st.error(f"❌ 数据验证失败: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ 导入失败: {str(e)}")
        import traceback
        st.error(f"详细错误: {traceback.format_exc()}")
        return False


def render_import_section():
    """渲染导入数据界面"""
    st.markdown("#### 📥 从文件导入数据")
    st.caption("支持 CSV、Excel、JSON 格式。可用于备份恢复或批量导入。")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "选择文件",
        type=['csv', 'xlsx', 'xls', 'json'],
        help="支持格式: CSV (.csv), Excel (.xlsx, .xls), JSON (.json)"
    )
    
    if uploaded_file is not None:
        # 显示文件信息
        file_type = uploaded_file.name.split('.')[-1].lower()
        st.info(f"📄 已选择文件: {uploaded_file.name} ({file_type.upper()})")
        
        # 解析文件
        df = None
        if file_type == 'csv':
            df = parse_csv_file(uploaded_file)
        elif file_type in ['xlsx', 'xls']:
            df = parse_excel_file(uploaded_file)
        elif file_type == 'json':
            df = parse_json_file(uploaded_file)
        else:
            st.error(f"❌ 不支持的文件格式: {file_type}")
            return
        
        if df is not None and not df.empty:
            # 显示预览
            st.markdown("**📋 数据预览** (前5行):")
            st.dataframe(df.head(), width='stretch')
            
            st.markdown(f"**📊 统计**: 共 {len(df)} 条记录")
            
            # 合并模式选择
            st.markdown("**⚙️ 导入模式**:")
            merge_mode = st.radio(
                "选择导入方式",
                ['replace', 'append', 'merge'],
                format_func=lambda x: {
                    'replace': '🔄 替换全部数据（清空现有数据）',
                    'append': '➕ 追加数据（添加到现有数据）',
                    'merge': '🔀 合并数据（更新现有，添加新的）'
                }[x],
                horizontal=False
            )
            
            # 确认导入
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("✅ 确认导入", type="primary", width='stretch'):
                    if import_subscriptions(df, merge_mode):
                        st.success(f"✅ 成功导入 {len(df)} 条订阅数据！")
                        st.rerun()
                    else:
                        st.error("❌ 导入失败，请检查数据格式")
            
            with col2:
                if st.button("❌ 取消", width='stretch'):
                    st.rerun()
        else:
            st.warning("⚠️ 无法解析文件或文件为空")
