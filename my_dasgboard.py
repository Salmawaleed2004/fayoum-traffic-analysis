import streamlit as st
import pandas as pd
import plotly.express as px

# 1. إعدادات الصفحة - تغيير العنوان ليكون خاص بالفيوم
st.set_page_config(page_title="تحليل مرور الفيوم", layout="wide")

# تصميم العناوين بالاسم الجديد
st.title("📊 لوحة تحليل حركة المرور - محافظة الفيوم")
st.markdown("مشروع التخرج: تحليل مسارات المركبات وتصنيفها بناءً على إحداثيات الحركة")
st.markdown("---")

# 2. تحميل البيانات (تأكدي أن اسم الملف data.csv موجود في نفس المجلد)
@st.cache_data
def load_data():
    file_path = 'data.csv'
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is not None:
    # 3. الفلاتر الجانبية
    st.sidebar.header("فلاتر البيانات")
    
    # فلتر أنواع المركبات
    if 'class_name' in df.columns:
        classes = df['class_name'].unique().tolist()
        selected_classes = st.sidebar.multiselect("اختر فئة المركبة:", classes, default=classes)
    else:
        selected_classes = []

    # فلتر مستوى الثقة
    if 'confidence' in df.columns:
        conf_level = st.sidebar.slider("مستوى الثقة (Confidence):", 0.0, 1.0, 0.4)
    else:
        conf_level = 0

    # تطبيق الفلاتر
    mask = pd.Series([True] * len(df))
    if 'class_name' in df.columns:
        mask &= (df['class_name'].isin(selected_classes))
    if 'confidence' in df.columns:
        mask &= (df['confidence'] >= conf_level)
    
    filtered_df = df[mask]

    # 4. عرض الإحصائيات (Metrics)
    c1, c2, c3 = st.columns(3)
    c1.metric("عدد المركبات المكتشفة", len(filtered_df))
    
    if 'track_id' in df.columns:
        c2.metric("عدد المسارات (Tracks)", filtered_df['track_id'].nunique())
    
    if 'confidence' in df.columns:
        c3.metric("متوسط الدقة", f"{filtered_df['confidence'].mean():.2f}")

    st.markdown("---")

    # 5. عرض الخريطة الإحداثية
    st.subheader("📍 خريطة مسارات حركة المرور في الفيوم")
    
    # نستخدم x1 و y1 للرسم
    if 'x1' in df.columns and 'y1' in df.columns:
        fig = px.scatter(filtered_df, 
                         x="x1", y="y1", 
                         color="class_name" if 'class_name' in df.columns else None,
                         hover_data=['track_id'] if 'track_id' in df.columns else [],
                         title="توزيع حركة المركبات في شوارع الفيوم",
                         labels={"x1": "الإحداثي الأفقي", "y1": "الإحداثي الرأسي"},
                         template="plotly_dark")

        fig.update_traces(marker=dict(size=6))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("أعمدة الإحداثيات (x1, y1) غير موجودة في ملف data.csv")

    # 6. تحليل أنواع المركبات (Chart)
    if 'class_name' in df.columns:
        st.subheader("📈 توزيع أنواع المركبات")
        class_counts = filtered_df['class_name'].value_counts().reset_index()
        class_counts.columns = ['النوع', 'العدد']
        fig_bar = px.bar(class_counts, x='النوع', y='العدد', 
                         color='النوع', title="إحصائيات أنواع المركبات")
        st.plotly_chart(fig_bar, use_container_width=True)

    # 7. عرض البيانات
    if st.checkbox("عرض جدول البيانات"):
        st.dataframe(filtered_df.head(100))

else:
    st.error("❌ لم يتم العثور على ملف data.csv")
    st.info("تأكدي من وضع ملف البيانات في نفس المجلد الذي يحتوي على ملف البرمجة وتسميته data.csv")