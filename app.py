import streamlit as st
import pandas as pd
from pathlib import Path

# ------------------------------------------------------------
# Retail Markdown Decision Support | Educational Prototype
# Real historical sales/price aggregates from the prepared M5 file;
# inventory and unit cost are user-entered simulation assumptions.
# ------------------------------------------------------------

st.set_page_config(
    page_title="سامانه پشتیبان تصمیم‌گیری تخفیف خرده‌فروشی",
    page_icon="🛒",
    layout="wide"
)

DATA_PATH = Path(__file__).parent / "M5_Walmart_Weekly_Store_Category.csv"

# ---------- RTL and visual style ----------
st.markdown("""
<style>
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
    direction: rtl !important;
    text-align: right !important;
    background: #171614;
    color: #EDEBE8;
}
[data-testid="stHeader"] { background: #171614; }
section[data-testid="stSidebar"] { direction: rtl; text-align: right; }
h1, h2, h3, h4, p, label, li { direction: rtl; text-align: right; }
.stTabs [data-baseweb="tab-list"] { direction: rtl; }
.stTabs [data-baseweb="tab"] { direction: rtl; }
div[data-testid="stMetric"] { direction: rtl; text-align: right; }
[data-testid="stDataFrame"], [data-testid="stTable"] {
    direction: rtl;
}
.notice {
    direction: rtl;
    text-align: right;
    background: #302917;
    border: 1px solid #685526;
    border-radius: 10px;
    padding: 13px 17px;
    color: #FBD54F !important;
    line-height: 2;
    margin: 12px 0 22px 0;
}
.notice * { color: #FBD54F !important; }
.info-panel {
    direction: rtl;
    text-align: right;
    background: #1E2A3D;
    border: 1px solid #40536D;
    border-radius: 10px;
    padding: 14px 17px;
    color: #DCE7F5 !important;
    line-height: 2;
}
.info-panel * { color: #DCE7F5 !important; }
.metric-panel {
    direction: rtl;
    text-align: right;
    background: #302D28;
    border: 1px solid #514A40;
    border-radius: 12px;
    padding: 16px;
    min-height: 105px;
}
.metric-label { color: #C9C2B8 !important; font-size: 14px; }
.metric-value { color: #FFFFFF !important; font-size: 24px; font-weight: 700; }
.small-note { color: #BDB6AC; font-size: 13px; line-height: 1.9; }
</style>
""", unsafe_allow_html=True)

# ---------- Load data ----------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["week_start"] = pd.to_datetime(df["week_start"], errors="coerce")
    df["week_end"] = pd.to_datetime(df["week_end"], errors="coerce")
    return df

if not DATA_PATH.exists():
    st.error("فایل داده M5 کنار فایل app.py پیدا نشد. هر دو فایل باید در یک پوشه باشند.")
    st.stop()

df = load_data(DATA_PATH)

if "decision_log" not in st.session_state:
    st.session_state.decision_log = []

# ---------- Header ----------
st.title("سامانه آموزشی پشتیبان تصمیم‌گیری تخفیف در خرده‌فروشی")
st.caption("Retail Markdown Decision Support | Educational Prototype")

st.markdown("""
<div class="notice">
این برنامه یک نمونه آموزشی مستقل است و سامانه CMD شرکت Walmart نیست.
فروش و قیمت تاریخی از داده تجمیعی M5 گرفته شده‌اند؛ موجودی و بهای تمام‌شده در شبیه‌ساز، فرضی و قابل تنظیم هستند.
</div>
""", unsafe_allow_html=True)

# ---------- Filters ----------
st.subheader("انتخاب داده تاریخی")
f1, f2, f3 = st.columns(3)
with f1:
    stores = sorted(df["store"].dropna().unique().tolist())
    selected_store = st.selectbox("فروشگاه", stores, index=0)
with f2:
    categories = sorted(df["category"].dropna().unique().tolist())
    selected_category = st.selectbox("دسته‌بندی محصول", categories, index=0)
with f3:
    years = sorted(df["year"].dropna().astype(int).unique().tolist())
    selected_year = st.selectbox("سال", years, index=len(years)-1)

filtered = df[
    (df["store"] == selected_store) &
    (df["category"] == selected_category) &
    (df["year"] == selected_year)
].sort_values("week_start")

if filtered.empty:
    st.warning("برای این ترکیب داده‌ای وجود ندارد.")
    st.stop()

tabs = st.tabs([
    "۱. تحلیل داده‌های واقعی M5",
    "۲. شبیه‌ساز سناریوی تخفیف",
    "۳. پنل تصمیم مدیر"
])

# ---------- Tab 1: historical M5 analytics ----------
with tabs[0]:
    st.header("تحلیل فروش و قیمت تاریخی")
    st.write(
        "اطلاعات زیر از داده عمومی M5 و در سطح فروشگاه، دسته‌بندی و هفته تجمیع شده‌اند؛ "
        "این داده‌ها مربوط به یک SKU منفرد نیستند."
    )

    total_units = int(filtered["weekly_units"].sum())
    avg_price = float(filtered["avg_sell_price"].mean())
    weeks_count = int(filtered["week_start"].nunique())
    price_proxy = float(filtered["estimated_sales_value_proxy"].sum())

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("مجموع واحدهای فروش", f"{total_units:,.0f}")
    with m2:
        st.metric("میانگین قیمت تاریخی", f"${avg_price:,.2f}")
    with m3:
        st.metric("تعداد هفته‌ها", f"{weeks_count:,}")
    with m4:
        st.metric("فروش ارزشی تخمینی (Proxy)", f"${price_proxy:,.0f}")

    st.subheader("روند هفتگی فروش")
    sales_chart = filtered.set_index("week_start")[["weekly_units"]].rename(
        columns={"weekly_units": "واحد فروش"}
    )
    st.line_chart(sales_chart, width="stretch")

    st.subheader("روند میانگین قیمت تاریخی (USD)")
    price_chart = filtered.set_index("week_start")[["avg_sell_price"]].rename(
        columns={"avg_sell_price": "میانگین قیمت (USD)"}
    )
    st.line_chart(price_chart, width="stretch")

    st.subheader("داده‌های انتخاب‌شده")
    display = filtered[[
        "store", "state", "category", "week_start", "weekly_units",
        "min_sell_price", "max_sell_price", "avg_sell_price",
        "priced_item_count", "holiday_days", "event_days"
    ]].copy()
    display = display.rename(columns={
        "store": "فروشگاه",
        "state": "ایالت",
        "category": "دسته‌بندی",
        "week_start": "شروع هفته",
        "weekly_units": "واحد فروش هفتگی",
        "min_sell_price": "حداقل قیمت (USD)",
        "max_sell_price": "حداکثر قیمت (USD)",
        "avg_sell_price": "میانگین قیمت (USD)",
        "priced_item_count": "تعداد اقلام قیمت‌گذاری‌شده",
        "holiday_days": "روز تعطیل",
        "event_days": "روز رویداد"
    })
    st.dataframe(
        display,
        hide_index=True,
        width="stretch",
        column_config={
            "حداقل قیمت (USD)": st.column_config.NumberColumn(format="$%.2f"),
            "حداکثر قیمت (USD)": st.column_config.NumberColumn(format="$%.2f"),
            "میانگین قیمت (USD)": st.column_config.NumberColumn(format="$%.2f"),
        }
    )

    st.markdown("""
    <div class="info-panel">
    <b>نکته درباره کیفیت داده:</b>
    ستون «فروش ارزشی تخمینی (Proxy)» یک برآورد محاسباتی است و نباید با درآمد حسابداری یا سود واقعی Walmart یکسان تلقی شود.
    فایل آماده‌شده، داده‌ها را در سطح فروشگاه/دسته‌بندی/هفته تجمیع کرده است؛ شناسه SKU در این فایل وجود ندارد.
    </div>
    """, unsafe_allow_html=True)

# ---------- Tab 2: markdown scenario simulator ----------
with tabs[1]:
    st.header("شبیه‌ساز سناریوهای تخفیف")
    st.write(
        "قیمت و تقاضای پایه از ردیف تاریخی انتخاب‌شده می‌آیند. "
        "موجودی و بهای تمام‌شده را به‌عنوان فرض آموزشی وارد کنید."
    )

    week_choices = filtered.sort_values("week_start")["week_start"].dropna().tolist()
    chosen_week = st.selectbox(
        "هفته مبنای شبیه‌سازی",
        week_choices,
        format_func=lambda x: x.strftime("%Y-%m-%d")
    )
    base_row = filtered[filtered["week_start"] == chosen_week].iloc[0]

    base_price = float(base_row["avg_sell_price"])
    base_demand = int(base_row["weekly_units"])

    st.markdown(
        f"**مبنای تاریخی انتخاب‌شده:** {selected_store} | {selected_category} | "
        f"{chosen_week.strftime('%Y-%m-%d')} | قیمت متوسط: **${base_price:,.2f}** | "
        f"فروش هفتگی: **{base_demand:,} واحد**"
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        assumed_stock = st.number_input(
            "موجودی فرضی (واحد)",
            min_value=1,
            max_value=10_000_000,
            value=max(1, int(base_demand * 1.15)),
            step=100
        )
    with c2:
        assumed_cost = st.number_input(
            "بهای تمام‌شده فرضی هر واحد (USD)",
            min_value=0.01,
            max_value=100_000.0,
            value=round(base_price * 0.65, 2),
            step=0.25,
            format="%.2f"
        )
    with c3:
        elasticity = st.slider(
            "ضریب واکنش فرضی تقاضا به تخفیف",
            min_value=0.0,
            max_value=3.0,
            value=1.0,
            step=0.1
        )

    objective = st.selectbox(
        "هدف تصمیم‌گیری",
        [
            "بیشینه‌سازی سود ناخالص برآوردی",
            "افزایش نرخ فروش موجودی",
            "کاهش موجودی باقی‌مانده"
        ]
    )

    scenario_rows = []
    for discount in [0, 10, 20, 30, 40]:
        price_after = base_price * (1 - discount / 100)
        estimated_demand = base_demand * (1 + elasticity * discount / 100)
        units_sold = min(int(round(estimated_demand)), int(assumed_stock))
        remaining = int(assumed_stock) - units_sold
        revenue = units_sold * price_after
        gross_profit = units_sold * (price_after - assumed_cost)
        sell_through = (units_sold / assumed_stock) * 100

        scenario_rows.append({
            "تخفیف": f"{discount}٪",
            "قیمت پس از تخفیف (USD)": round(price_after, 2),
            "تقاضای برآوردی (واحد)": round(estimated_demand),
            "فروش قابل تحقق (واحد)": units_sold,
            "موجودی باقی‌مانده": remaining,
            "ارزش فروش برآوردی (USD)": round(revenue, 2),
            "سود ناخالص برآوردی (USD)": round(gross_profit, 2),
            "نرخ فروش موجودی (%)": round(sell_through, 1)
        })

    result = pd.DataFrame(scenario_rows)

    st.subheader("مقایسه سناریوها")
    st.dataframe(
        result,
        hide_index=True,
        width="stretch",
        column_config={
            "قیمت پس از تخفیف (USD)": st.column_config.NumberColumn(format="$%.2f"),
            "ارزش فروش برآوردی (USD)": st.column_config.NumberColumn(format="$%.2f"),
            "سود ناخالص برآوردی (USD)": st.column_config.NumberColumn(format="$%.2f"),
        }
    )

    if objective == "بیشینه‌سازی سود ناخالص برآوردی":
        best_idx = result["سود ناخالص برآوردی (USD)"].idxmax()
    elif objective == "افزایش نرخ فروش موجودی":
        best_idx = result["نرخ فروش موجودی (%)"].idxmax()
    else:
        best_idx = result["موجودی باقی‌مانده"].idxmin()

    best = result.iloc[best_idx]
    st.success(
        f"سناریوی برتر بر اساس هدف انتخاب‌شده: تخفیف {best['تخفیف']}؛ "
        f"سود ناخالص برآوردی: ${best['سود ناخالص برآوردی (USD)']:,.2f}."
    )
    st.caption(
        "این محاسبه یک سناریوسازی ساده و شفاف است، نه پیش‌بینی یادگیری ماشین، "
        "نه توصیه قیمت‌گذاری واقعی و نه الگوریتم اختصاصی Walmart."
    )

# ---------- Tab 3: manager decision log ----------
with tabs[2]:
    st.header("پنل تصمیم مدیر")
    st.write("مدیر می‌تواند سناریوی موردنظر را بررسی و تصمیم خود را ثبت کند.")

    week_label = chosen_week.strftime("%Y-%m-%d")
    discount_options = ["انتخاب کنید", "۰٪", "۱۰٪", "۲۰٪", "۳۰٪", "۴۰٪"]
    selected_discount = st.selectbox(
        "سطح تخفیف مورد بررسی",
        discount_options,
        index=0
    )
    decision = st.radio(
        "تصمیم مدیر",
        ["تأیید", "رد", "انتخاب سناریوی جایگزین"],
        index=None,
        horizontal=True
    )
    manager_note = st.text_area("توضیحات مدیر (اختیاری)")
    st.caption("برای ثبت معتبر، انتخاب سطح تخفیف و نوع تصمیم مدیر هر دو الزامی هستند.")

    if st.button("ثبت تصمیم مدیر", type="primary"):
        if selected_discount == "انتخاب کنید":
            st.error("برای ثبت تصمیم، ابتدا سطح تخفیف را انتخاب کنید.")
        elif decision is None:
            st.error("لطفاً نوع تصمیم مدیر را نیز مشخص کنید.")
        else:
            discount_number = int(selected_discount.replace("٪", "").translate(
                str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
            ))
            chosen_scenario = result[result["تخفیف"] == f"{discount_number}٪"].iloc[0]
            st.session_state.decision_log.append({
                "فروشگاه": selected_store,
                "دسته‌بندی": selected_category,
                "هفته مبنا": week_label,
                "تخفیف انتخابی": selected_discount,
                "قیمت پس از تخفیف (USD)": chosen_scenario["قیمت پس از تخفیف (USD)"],
                "تقاضای برآوردی (واحد)": chosen_scenario["تقاضای برآوردی (واحد)"],
                "فروش قابل تحقق (واحد)": chosen_scenario["فروش قابل تحقق (واحد)"],
                "موجودی باقی‌مانده": chosen_scenario["موجودی باقی‌مانده"],
                "ارزش فروش برآوردی (USD)": chosen_scenario["ارزش فروش برآوردی (USD)"],
                "سود ناخالص برآوردی (USD)": chosen_scenario["سود ناخالص برآوردی (USD)"],
                "نرخ فروش موجودی (%)": chosen_scenario["نرخ فروش موجودی (%)"],
                "تصمیم مدیر": decision,
                "توضیحات": manager_note
            })
            st.success("تصمیم در سابقه همین نشست ثبت شد.")

    st.subheader("سابقه تصمیم‌های ثبت‌شده")
    if st.session_state.decision_log:
        log_df = pd.DataFrame(st.session_state.decision_log)
        st.dataframe(log_df, hide_index=True, width="stretch")
        st.download_button(
            "دریافت سابقه تصمیم‌ها | CSV",
            data=log_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="manager_decisions.csv",
            mime="text/csv"
        )
    else:
        st.info("هنوز تصمیمی ثبت نشده است.")

    st.warning(
        "این ثبت تصمیم صرفاً در نشست فعلی برنامه نگهداری می‌شود و به سامانه فروشگاهی یا POS متصل نیست."
    )

# ---------- Methodological limitations ----------
with st.expander("فرض‌ها و محدودیت‌های نمونه آموزشی"):
    st.markdown("""
    ۱. داده تاریخی فروش و قیمت از فایل تجمیعی آماده‌شده بر مبنای M5 گرفته شده است.

    ۲. داده در سطح فروشگاه، دسته‌بندی و هفته است؛ شناسه محصول منفرد در فایل حاضر وجود ندارد.

    ۳. موجودی و بهای تمام‌شده در داده عمومی حاضر موجود نیستند و در شبیه‌ساز توسط کاربر به‌صورت فرضی وارد می‌شوند.

    ۴. واکنش تقاضا به تخفیف با یک ضریب ساده و قابل تنظیم نمایش داده می‌شود؛ این ضریب از مدل آموزش‌دیده استخراج نشده است.

    ۵. هزینه‌های عملیاتی، محدودیت عمر کالا، هزینه نگهداری، اثر رقبا و محدودیت‌های زنجیره تأمین لحاظ نشده‌اند.

    ۶. این برنامه CMD واقعی Walmart نیست، به POS متصل نمی‌شود و الگوریتم محرمانه یا تولیدی Walmart را بازسازی نمی‌کند.

    ۷. هدف برنامه نمایش یک فرایند آموزشی برای تحلیل داده، مقایسه سناریوها و حفظ نقش تصمیم‌گیرنده انسانی است.
    """)
