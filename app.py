# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Sugar Consumption Rate", layout="wide")
st.title("🏃‍♂️ Sugar Consumption Rate During Running")

# ---------------------
# Constants & columns
# ---------------------
COLUMNS = ['Start Time (min)', 'End Time (min)', 'Item', 'Type', 'Sugar (g)', 'Comment']

# ---------------------
# Initialize library & df
# ---------------------
if 'items_library' not in st.session_state:
    st.session_state.items_library = {
        'Food': {
            'Powerbar Fuel Gel 30': {'sugar': 30.0, 'default_comment': 'Liquide, pas très bon'},
            'LIQUID GEL APPLE': {'sugar': 28.0, 'default_comment': 'Reaction hypo'},
            'RAW BITE LIME': {'sugar': 44.0, 'default_comment': 'Assez bon'},
            'ENERGY BAR': {'sugar': 18.0, 'default_comment': 'Bonne mastication'},
        },
        'Drink': {
            'ISO DRINK LEMON': {'sugar': 35.0, 'default_comment': 'Goût ok'},
        }
    }

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=COLUMNS)

# session comment helper
if 'comment_text' not in st.session_state:
    st.session_state.comment_text = ""

# ---------------------
# Helper functions
# ---------------------
def safe_add_to_library(item_type: str, name: str, sugar: float, comment: str):
    lib = st.session_state.items_library.setdefault(item_type, {})
    base = name.strip()
    candidate = base
    i = 1
    while candidate in lib:
        candidate = f"{base} ({i})"
        i += 1
    lib[candidate] = {'sugar': float(sugar), 'default_comment': comment or ''}
    return candidate

def sanitize_df(df_in: pd.DataFrame):
    df = df_in.copy()
    for col in ['Item', 'Comment', 'Type']:
        if col in df.columns:
            df[col] = df[col].fillna('').astype(str)
    for col in ['Start Time (min)', 'End Time (min)', 'Sugar (g)']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    # Ensure End >= Start for drinks by defaulting end to start if missing
    df['End Time (min)'] = df['End Time (min)'].where(df['End Time (min)'] >= df['Start Time (min)'], df['Start Time (min)'])
    return df[COLUMNS]

# ---------------------
# Sidebar: library
# ---------------------
st.sidebar.header("📚 Items Library")

with st.sidebar.expander("View All Items", expanded=False):
    for t in ['Food', 'Drink']:
        st.markdown(f"**{t}**")
        items = st.session_state.items_library.get(t, {})
        if not items:
            st.write("_No items_")
        for name, data in items.items():
            sugar = data.get('sugar', 0.0)
            comment = data.get('default_comment', '')
            st.write(f"- {name}: {sugar} g")
            if comment:
                st.write(f"  💬 _{comment}_")

with st.sidebar.expander("Add New Item to Library"):
    new_type = st.selectbox("Type", ["Food", "Drink"], key="new_item_type")
    new_name = st.text_input("Item Name", key="new_item_name")
    new_sugar = st.number_input("Sugar Content (g)", min_value=0.0, value=0.0, step=0.1, key="new_item_sugar")
    new_comment = st.text_input("Default Comment (optional)", key="new_item_comment")
    if st.button("Save to Library"):
        if not new_name.strip():
            st.error("Please provide an item name.")
        elif new_sugar <= 0:
            st.error("Sugar must be > 0 g.")
        else:
            saved = safe_add_to_library(new_type, new_name.strip(), new_sugar, new_comment)
            st.success(f"Saved '{saved}' to {new_type} library")

# ---------------------
# Import / Export CSV
# ---------------------
st.subheader("📁 Data Import / Export")
col1, col2 = st.columns(2)

with col1:
    uploaded = st.file_uploader("Upload your consumption data (CSV)", type=['csv'])
    if uploaded is not None:
        try:
            imported = pd.read_csv(uploaded)
            if all(col in imported.columns for col in COLUMNS):
                st.session_state.df = sanitize_df(imported)
                st.success(f"Imported {len(st.session_state.df)} rows")
            else:
                st.error(f"CSV must contain columns: {COLUMNS}")
                st.write("Your CSV columns:", list(imported.columns))
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

with col2:
    if not st.session_state.df.empty:
        buf = io.StringIO()
        st.session_state.df.to_csv(buf, index=False)
        st.download_button("Download CSV", buf.getvalue(), "sugar_consumption.csv", "text/csv")
    else:
        st.write("No data to export")

with st.expander("📄 CSV Template"):
    sample = pd.DataFrame({
        'Start Time (min)': [30, 60, 90],
        'End Time (min)': [30, 75, 95],
        'Item': ['Energy Gel', 'Sports Drink', 'Energy Bar'],
        'Type': ['Food', 'Drink', 'Food'],
        'Sugar (g)': [25.0, 60.0, 18.0],
        'Comment': ['Good taste', 'Too sweet', 'Perfect timing']
    })
    st.dataframe(sample)

# ---------------------
# Add Data UI
# ---------------------
st.subheader("📝 Add Data")
input_method = st.radio("Input Method", ["Select from Library", "Enter Custom Item"], horizontal=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    item_type = st.selectbox("Type", ["Food", "Drink"])

with col2:
    if input_method == "Select from Library":
        available = list(st.session_state.items_library.get(item_type, {}).keys())
        if available:
            selected = st.selectbox("Select Item", available, key=f"select_{item_type}")
            item_name = selected
            item_data = st.session_state.items_library[item_type][selected]
            sugar_amount = float(item_data.get('sugar', 0.0))
            default_comment = item_data.get('default_comment', '')
            st.info(f"Sugar: {sugar_amount} g")
            if default_comment:
                st.info(f"💬 {default_comment}")
        else:
            st.warning("No library items for this type")
            item_name = ""
            sugar_amount = 0.0
            default_comment = ""
    else:
        item_name = st.text_input("Item name", placeholder="Energy gel" if item_type == "Food" else "Sports drink")
        sugar_amount = st.number_input("Sugar (g)", min_value=0.0, value=0.0, step=0.1, key="custom_sugar")
        default_comment = ""

with col3:
    if item_type == "Food":
        time_min = st.number_input("Time (min)", min_value=0, value=0, key="food_time")
        start_time = float(time_min)
        end_time = float(time_min)
    else:
        start_time = float(st.number_input("Start Time (min)", min_value=0, value=0, key="drink_start"))

with col4:
    if item_type == "Drink":
        end_time = float(st.number_input("End Time (min)", min_value=start_time + 1, value=start_time + 5, key="drink_end"))
    else:
        end_time = start_time

# Comments & quick comments
st.subheader("💬 Add Comment")
comment_col1, comment_col2 = st.columns([3, 1])
with comment_col1:
    comment = st.text_area("Comment", value=st.session_state.comment_text or default_comment, height=60,
                           placeholder="How did you feel? Any side effects? Energy level?")
with comment_col2:
    st.write("**Quick Comments:**")
    quick_comments = [
        "Felt great! 💪",
        "Good energy boost ⚡",
        "Stomach upset 😵",
        "Perfect timing ⏰",
        "Too sweet 🍯",
        "Easy to digest 👍",
        "Needed this 🎯"
    ]
    for qc in quick_comments:
        if st.button(qc, key=f"qc_{qc}"):
            st.session_state.comment_text = qc
            st.experimental_rerun()

# Add entry buttons
col_add, col_save = st.columns([1, 1])

with col_add:
    if st.button("Add Entry"):
        if not item_name or sugar_amount <= 0:
            st.error("Provide an item name and sugar > 0g")
        else:
            new_row = pd.DataFrame([{
                'Start Time (min)': start_time,
                'End Time (min)': end_time,
                'Item': item_name,
                'Type': item_type,
                'Sugar (g)': float(sugar_amount),
                'Comment': comment or ""
            }])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.success(f"Added {item_name}")

with col_save:
    if input_method == "Enter Custom Item" and st.button("Add Entry + Save to Library"):
        if not item_name or sugar_amount <= 0:
            st.error("Provide an item name and sugar > 0g")
        else:
            new_row = pd.DataFrame([{
                'Start Time (min)': start_time,
                'End Time (min)': end_time,
                'Item': item_name,
                'Type': item_type,
                'Sugar (g)': float(sugar_amount),
                'Comment': comment or ""
            }])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            saved_name = safe_add_to_library(item_type, item_name.strip(), sugar_amount, comment or "")
            st.success(f"Added {item_name} and saved to library as '{saved_name}'")

# ---------------------
# Quick Add section
# ---------------------
st.subheader("⚡ Quick Add")
popular_items = {
    'Energy Gel': ('Food', 22.0, 0),
    'Sports Drink': ('Drink', 32.0, 10),
    'Banana': ('Food', 14.0, 0),
    'Energy Bar': ('Food', 18.0, 0)
}
quick_cols = st.columns(4)
for i, (item_label, (it_type, sugar, duration)) in enumerate(popular_items.items()):
    with quick_cols[i]:
        st.markdown(f"**{item_label}**")
        q_time = st.number_input(f"Time for {item_label} (min)", min_value=0, value=0, key=f"time_q_{i}")
        q_comment = st.text_input(f"Comment for {item_label}", key=f"comment_q_{i}", placeholder="Optional comment")
        if st.button(f"Add {item_label} ({sugar}g)", key=f"quick_add_{i}"):
            if it_type == 'Food':
                q_start = q_end = float(q_time)
            else:
                q_start = float(q_time)
                q_end = float(q_time + duration)
            new_row = pd.DataFrame([{
                'Start Time (min)': q_start,
                'End Time (min)': q_end,
                'Item': item_label,
                'Type': it_type,
                'Sugar (g)': float(sugar),
                'Comment': q_comment or ""
            }])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.success(f"Quick added {item_label}")

# ---------------------
# Editable table
# ---------------------
st.subheader("📊 Your Data")
# sanitize the stored df before editing
st.session_state.df = sanitize_df(st.session_state.df)
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic")
st.session_state.df = sanitize_df(edited_df)

# ---------------------
# Processing (continuous drink model)
# ---------------------
df = st.session_state.df.copy()
df = df[df['Item'].str.strip() != ''].reset_index(drop=True)

if not df.empty:
    food_events = []
    drink_segments = []

    for _, row in df.iterrows():
        s = float(row['Start Time (min)'])
        e = float(row['End Time (min)'])
        sugar = float(row['Sugar (g)'])
        item = row['Item']
        comment = row['Comment']
        typ = row['Type']

        if typ == 'Food' or e <= s:
            # instant food event at time 's'
            food_events.append({'time': s, 'sugar': sugar, 'item': item, 'comment': comment})
        else:
            duration = max(0.0, e - s)
            # rate is grams per hour during the drink period
            rate_g_per_h = sugar / (duration / 60.0) if duration > 0 else 0.0
            drink_segments.append({'start': s, 'end': e, 'rate': rate_g_per_h, 'item': item, 'comment': comment})

    # timeline breakpoints: consider food times and drink starts/ends
    times = set()
    for f in food_events:
        times.add(f['time'])
    for d in drink_segments:
        times.add(d['start'])
        times.add(d['end'])
    if not times:
        st.info("No timeline events found (unexpected).")
    timeline = sorted(times)

    # Build rate segments: for each interval between timeline times, sum active drink rates and food spike converted into a rate over the interval
    rate_segments = []
    for i in range(len(timeline) - 1):
        t0 = timeline[i]
        t1 = timeline[i + 1]
        dt_min = t1 - t0
        if dt_min <= 0:
            continue

        # Food sugar at t0 (instant); we distribute it over dt_min to compute an equivalent rate for plotting
        food_sugar = sum(f['sugar'] for f in food_events if f['time'] == t0)
        food_rate = (food_sugar / (dt_min / 60.0)) if food_sugar > 0 else 0.0

        # Sum rates of all drinks active at t0
        drink_rate = sum(d['rate'] for d in drink_segments if d['start'] <= t0 < d['end'])

        total_rate = food_rate + drink_rate

        rate_segments.append({
            'start_time': t0,
            'end_time': t1,
            'rate': total_rate
        })

    # ---------------------
    # Plot: rate line + drink shaded zones
    # ---------------------
    st.subheader("📈 Overall Sugar Consumption Rate")

    fig = go.Figure()
    if rate_segments:
        x_pts = []
        y_pts = []
        for seg in rate_segments:
            x_pts += [seg['start_time'], seg['end_time']]
            y_pts += [seg['rate'], seg['rate']]

        fig.add_trace(go.Scatter(
            x=x_pts,
            y=y_pts,
            mode='lines',
            name='Sugar rate (g/h)',
            line=dict(width=3),
            hovertemplate="Rate: %{y:.1f} g/h<br>Time: %{x} min<extra></extra>"
        ))

    # add markers for food events and label with sugar
    for f in food_events:
        # find rate at this time (if any)
        rate_here = 0.0
        for seg in rate_segments:
            if seg['start_time'] == f['time']:
                rate_here = seg['rate']
                break
        fig.add_trace(go.Scatter(
            x=[f['time']],
            y=[rate_here if rate_here > 0 else 0],
            mode='markers',
            marker=dict(symbol='circle', size=10, line=dict(width=1, color='white')),
            name=f['item'],
            showlegend=False,
            hovertemplate=(f"<b>{f['item']}</b><br>Sugar: {f['sugar']:.1f} g<br>Time: {f['time']} min<br>Comment: {f['comment']}<extra></extra>")
        ))

    # shade drink segments
    for d in drink_segments:
        fig.add_vrect(x0=d['start'], x1=d['end'], fillcolor='blue', opacity=0.08, layer='below', line_width=0)
        # optional label could be added as annotation if desired

    fig.update_layout(
        xaxis_title="Time (minutes)",
        yaxis_title="Sugar Consumption Rate (g/h)",
        height=600,
        hovermode='closest'
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------------------
    # Stats
    # ---------------------
    st.subheader("📊 Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Sugar", f"{df['Sugar (g)'].sum():.1f} g")
    with c2:
        # total duration = last endpoint among rate segments or last event time
        if rate_segments:
            total_time = max(seg['end_time'] for seg in rate_segments)
        else:
            total_time = max((f['time'] for f in food_events), default=0)
        st.metric("Total Duration", f"{total_time:.0f} min")
    with c3:
        food_count = len(food_events)
        st.metric("Food Items", food_count)
    with c4:
        drink_count = len(drink_segments)
        st.metric("Drink Periods", drink_count)

    # ---------------------
    # Hour-by-hour summary
    # ---------------------
    st.subheader("⏱️ Sugar Intake – Hour by Hour")

    hourly_rows = []
    for _, r in df.iterrows():
        start = float(r['Start Time (min)'])
        end = float(r['End Time (min)'])
        sugar = float(r['Sugar (g)'])
        item = r['Item']
        comment = r['Comment']
        typ = r['Type']

        if typ == 'Food' or end <= start:
            hour = int(start // 60)
            hourly_rows.append({'hour': hour, 'sugar': sugar, 'item': item, 'comment': comment})
        else:
            duration = end - start
            if duration <= 0:
                hour = int(start // 60)
                hourly_rows.append({'hour': hour, 'sugar': sugar, 'item': item, 'comment': comment})
            else:
                sugar_per_min = sugar / duration
                current = start
                while current < end:
                    hour = int(current // 60)
                    hour_end = (hour + 1) * 60.0
                    overlap_end = min(end, hour_end)
                    overlap = overlap_end - current
                    if overlap > 0:
                        hourly_rows.append({
                            'hour': hour,
                            'sugar': sugar_per_min * overlap,
                            'item': item,
                            'comment': comment
                        })
                    current = overlap_end

    hourly_df = pd.DataFrame(hourly_rows)
    if not hourly_df.empty:
        summary = (
            hourly_df
            .groupby('hour')
            .agg(
                sugar_g=('sugar', 'sum'),
                products=('item', lambda x: ", ".join(sorted(set(x)))),
                comments=('comment', lambda x: " | ".join(sorted(set(c for c in x if c))))
            )
            .reset_index()
        )
        summary['Hour'] = summary['hour'].apply(lambda h: f"{h}:00–{h+1}:00")
        summary['Sugar (g)'] = summary['sugar_g'].round(1)
        summary = summary[['Hour', 'Sugar (g)', 'products', 'comments']]
        summary.columns = ['Hour', 'Sugar (g)', 'Products', 'Comments']

        st.dataframe(summary, use_container_width=True)

        # simple target checks (example thresholds)
        target_low, target_high = 60, 90
        for _, row in summary.iterrows():
            if row['Sugar (g)'] < target_low:
                st.warning(f"{row['Hour']}: Low intake ({row['Sugar (g)']} g)")
            elif row['Sugar (g)'] > target_high:
                st.error(f"{row['Hour']}: High intake ({row['Sugar (g)']} g)")
    else:
        st.info("No hourly data to show.")

else:
    st.info("No consumption entries yet. Add items above to see charts and hourly summary.")
