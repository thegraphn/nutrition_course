import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.title("🏃‍♂️ Sugar Consumption During Running")

# Initialize predefined items library (now with optional default comments)
if 'items_library' not in st.session_state:
    st.session_state.items_library = {
        'Food': {
            'Powerbar Fuel Gel 30 ': {'sugar': 30, 'default_comment': 'Liquide, pas très bon'},
            'LIQUID GEL APPLE': {'sugar': 28.0, 'default_comment': 'Reaction hypo'},
            'RAW BITE LIME': {'sugar': 44,'protein':10, 'default_comment': 'Assez bon'},
            'ENERGY GUMS* COLA + CAFFEINE': {'sugar': 32, 'default_comment': 'Assez bon'},
            'MAURTEN Gel 100 CAF 100': {'sugar': 25, 'default_comment': 'Fiable'},
            'ENERGY GUMS* ORANGE + MAGNESIUM': {'sugar': 32, 'default_comment': 'Assez bon'},
        },
        'Drink': {
            'ISO DRINK LEMON': {'sugar': 35.0, 'default_comment': 'Gout ok'},
        }
    }

# Initialize empty DataFrame (now with comments)
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        'Start Time (min)': [0],
        'End Time (min)': [0],
        'Item': [''],
        'Type': ['Food'],
        'Sugar (g)': [0.0],
        'Comment': ['']
    })

# Sidebar for managing items library
st.sidebar.header("📚 Items Library")

# View current library
with st.sidebar.expander("View All Items", expanded=False):
    for item_type in ['Food', 'Drink']:
        st.write(f"**{item_type}:**")
        for item_name, item_data in st.session_state.items_library[item_type].items():
            sugar = item_data['sugar']
            default_comment = item_data.get('default_comment', '')
            st.write(f"- {item_name}: {sugar}g")
            if default_comment:
                st.write(f"  💬 _{default_comment}_")

# Add new item to library
with st.sidebar.expander("Add New Item to Library"):
    new_item_type = st.selectbox("Type", ["Food", "Drink"], key="new_item_type")
    new_item_name = st.text_input("Item Name", key="new_item_name")
    new_item_sugar = st.number_input("Sugar Content (g)", min_value=0.0, value=0.0, step=0.1, key="new_item_sugar")
    new_item_comment = st.text_input("Default Comment (optional)", key="new_item_comment",
                                     placeholder="e.g., Great taste, quick energy")

    if st.button("Save to Library"):
        if new_item_name and new_item_sugar > 0:
            st.session_state.items_library[new_item_type][new_item_name] = {
                'sugar': new_item_sugar,
                'default_comment': new_item_comment
            }
            st.success(f"Added {new_item_name} to {new_item_type} library!")

# Data input section
st.subheader("📝 Add Data")

# Choose between predefined or custom item
input_method = st.radio("Input Method", ["Select from Library", "Enter Custom Item"], horizontal=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    item_type = st.selectbox("Type", ["Food", "Drink"])

with col2:
    if input_method == "Select from Library":
        # Dropdown with predefined items
        available_items = list(st.session_state.items_library[item_type].keys())
        if available_items:
            selected_item = st.selectbox("Select Item", available_items)
            item_name = selected_item
            item_data = st.session_state.items_library[item_type][selected_item]
            sugar_amount = item_data['sugar']
            default_comment = item_data.get('default_comment', '')
            st.info(f"Sugar: {sugar_amount}g")
            if default_comment:
                st.info(f"💬 {default_comment}")
        else:
            st.warning("No items in library for this type")
            item_name = ""
            sugar_amount = 0.0
            default_comment = ""
    else:
        # Manual input
        item_name = st.text_input("Item name", placeholder="Energy gel" if item_type == "Food" else "Sports drink")
        default_comment = ""

# Time inputs
with col3:
    if item_type == "Food":
        time_min = st.number_input("Time (min)", min_value=0, value=0)
        start_time = time_min
        end_time = time_min
    else:  # Drink
        start_time = st.number_input("Start Time (min)", min_value=0, value=0)

with col4:
    if item_type == "Drink":
        end_time = st.number_input("End Time (min)", min_value=start_time, value=start_time + 5)
    else:
        st.write("")  # Empty space for food items

    # Sugar amount input (only for custom items)
    if input_method == "Enter Custom Item":
        sugar_amount = st.number_input("Sugar (g)", min_value=0.0, value=0.0, step=0.1)

# Comment input section
st.subheader("💬 Add Comment")
comment_col1, comment_col2 = st.columns([3, 1])

with comment_col1:
    if input_method == "Select from Library" and 'default_comment' in locals():
        comment = st.text_area("Comment", value=default_comment, height=60,
                               placeholder="How did you feel? Any side effects? Energy level?")
    else:
        comment = st.text_area("Comment", value="", height=60,
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

    for quick_comment in quick_comments:
        if st.button(quick_comment, key=f"quick_comment_{quick_comment}"):
            comment = quick_comment

# Add entry with option to save custom item to library
col_add, col_save = st.columns([1, 1])

with col_add:
    if st.button("Add Entry", type="primary"):
        if item_name and sugar_amount > 0:
            new_row = pd.DataFrame({
                'Start Time (min)': [start_time],
                'End Time (min)': [end_time],
                'Item': [item_name],
                'Type': [item_type],
                'Sugar (g)': [sugar_amount],
                'Comment': [comment]
            })
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.success(f"Added {item_name}!")

with col_save:
    if input_method == "Enter Custom Item" and st.button("Add Entry + Save to Library"):
        if item_name and sugar_amount > 0:
            # Add to current session
            new_row = pd.DataFrame({
                'Start Time (min)': [start_time],
                'End Time (min)': [end_time],
                'Item': [item_name],
                'Type': [item_type],
                'Sugar (g)': [sugar_amount],
                'Comment': [comment]
            })
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)

            # Save to library
            st.session_state.items_library[item_type][item_name] = {
                'sugar': sugar_amount,
                'default_comment': comment if comment else ""
            }
            st.success(f"Added {item_name} and saved to library!")

# Quick add section for common items
st.subheader("⚡ Quick Add")
quick_cols = st.columns(4)

# Show some popular items for quick adding
popular_items = {
    'Energy Gel': ('Food', 22.0, 0),
    'Sports Drink': ('Drink', 32.0, 5),
    'Banana': ('Food', 14.0, 0),
    'Energy Bar': ('Food', 18.0, 0)
}

for i, (item, (item_type, sugar, duration)) in enumerate(popular_items.items()):
    with quick_cols[i]:
        if st.button(f"{item}\n({sugar}g)", key=f"quick_{item}"):
            time_input = st.number_input(f"Time for {item} (min)", min_value=0, value=0, key=f"time_{item}")
            quick_comment = st.text_input(f"Comment for {item}", key=f"comment_{item}", placeholder="Optional comment")

            if item_type == 'Food':
                quick_start = quick_end = time_input
            else:
                quick_start = time_input
                quick_end = time_input + duration

            new_row = pd.DataFrame({
                'Start Time (min)': [quick_start],
                'End Time (min)': [quick_end],
                'Item': [item],
                'Type': [item_type],
                'Sugar (g)': [sugar],
                'Comment': [quick_comment]
            })
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.success(f"Quick added {item}!")

# Edit DataFrame directly
st.subheader("📊 Your Data")
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic")
st.session_state.df = edited_df

# Clean and prepare data for plotting
plot_df = st.session_state.df.copy()
plot_df = plot_df[plot_df['Item'] != '']  # Remove empty rows
plot_df = plot_df.sort_values('Start Time (min)')

if not plot_df.empty:
    # Calculate cumulative sugar (add all sugar at start time for simplicity)
    cumulative_data = []
    for _, row in plot_df.iterrows():
        cumulative_data.append({
            'Time': row['Start Time (min)'],
            'Sugar': row['Sugar (g)']
        })

    cumulative_df = pd.DataFrame(cumulative_data).sort_values('Time')
    cumulative_df['Cumulative Sugar'] = cumulative_df['Sugar'].cumsum()

    # Create plot
    st.subheader("📈 Sugar Consumption Timeline")

    fig = go.Figure()

    # Add cumulative line
    fig.add_trace(go.Scatter(
        x=cumulative_df['Time'],
        y=cumulative_df['Cumulative Sugar'],
        mode='lines+markers',
        name='Cumulative Sugar',
        line=dict(color='red', width=3),
        marker=dict(size=8)
    ))

    # Add food items (points) with comments
    food_df = plot_df[plot_df['Type'] == 'Food']
    if not food_df.empty:
        # Get cumulative values for food items
        food_cumulative = []
        for _, food_row in food_df.iterrows():
            cum_value = cumulative_df[cumulative_df['Time'] <= food_row['Start Time (min)']]['Cumulative Sugar'].iloc[
                -1] if len(cumulative_df[cumulative_df['Time'] <= food_row['Start Time (min)']]) > 0 else 0
            food_cumulative.append(cum_value)

        # Create hover text with comments
        hover_text = []
        for _, row in food_df.iterrows():
            text = f"{row['Item']}<br>{row['Sugar (g)']}g"
            if row['Comment'] and str(row['Comment']).strip():
                text += f"<br>💬 {row['Comment']}"
            hover_text.append(text)

        fig.add_trace(go.Scatter(
            x=food_df['Start Time (min)'],
            y=food_cumulative,
            mode='markers',
            name='Food',
            marker=dict(symbol='square', size=15, color='green', line=dict(width=2, color='white')),
            text=hover_text,
            hovertemplate='%{text}<br>Time: %{x} min<extra></extra>'
        ))

    # Add drink items (line segments) with comments
    drink_df = plot_df[plot_df['Type'] == 'Drink']
    if not drink_df.empty:
        for _, drink_row in drink_df.iterrows():
            # Get cumulative value at start time
            cum_value = cumulative_df[cumulative_df['Time'] <= drink_row['Start Time (min)']]['Cumulative Sugar'].iloc[
                -1] if len(cumulative_df[cumulative_df['Time'] <= drink_row['Start Time (min)']]) > 0 else 0

            # Create hover text with comments
            start_text = f"{drink_row['Item']}<br>{drink_row['Sugar (g)']}g<br>Start"
            end_text = f"{drink_row['Item']}<br>{drink_row['Sugar (g)']}g<br>End"

            if drink_row['Comment'] and str(drink_row['Comment']).strip():
                comment_text = f"<br>💬 {drink_row['Comment']}"
                start_text += comment_text
                end_text += comment_text

            # Create line segment for drinking duration
            fig.add_trace(go.Scatter(
                x=[drink_row['Start Time (min)'], drink_row['End Time (min)']],
                y=[cum_value, cum_value],
                mode='lines+markers',
                name=f"🥤 {drink_row['Item']}",
                line=dict(color='blue', width=6),
                marker=dict(size=10, color='blue'),
                text=[start_text, end_text],
                hovertemplate='%{text}<br>Time: %{x} min<extra></extra>',
                showlegend=True
            ))

            # Add markers at start and end
            fig.add_trace(go.Scatter(
                x=[drink_row['Start Time (min)'], drink_row['End Time (min)']],
                y=[cum_value, cum_value],
                mode='markers',
                marker=dict(symbol=['circle', 'circle'], size=12, color=['lightblue', 'darkblue']),
                showlegend=False,
                hovertemplate='%{text}<br>Time: %{x} min<extra></extra>',
                text=[f"Start: {drink_row['Item']}", f"End: {drink_row['Item']}"]
            ))

    # Add comment annotations for items with significant comments
    for _, row in plot_df.iterrows():
        if row['Comment'] and str(row['Comment']).strip() and len(str(row['Comment'])) > 10:
            # Get cumulative value for annotation placement
            cum_value = cumulative_df[cumulative_df['Time'] <= row['Start Time (min)']]['Cumulative Sugar'].iloc[
                -1] if len(cumulative_df[cumulative_df['Time'] <= row['Start Time (min)']]) > 0 else 0

            fig.add_annotation(
                x=row['Start Time (min)'],
                y=cum_value + 2,  # Slightly above the point
                text=f"💬 {str(row['Comment'])[:30]}{'...' if len(str(row['Comment'])) > 30 else ''}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowcolor='gray',
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='gray',
                borderwidth=1,
                font=dict(size=10)
            )

    fig.update_layout(
        xaxis_title="Time (minutes)",
        yaxis_title="Cumulative Sugar (grams)",
        height=600,
        hovermode='closest'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show comments summary
    st.subheader("💬 Comments Summary")
    comments_df = plot_df[plot_df['Comment'].str.strip() != ''][['Start Time (min)', 'Item', 'Comment']]
    if not comments_df.empty:
        for _, row in comments_df.iterrows():
            st.write(f"**{row['Start Time (min)']} min** - {row['Item']}: _{row['Comment']}_")
    else:
        st.write("No comments added yet.")

    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sugar", f"{plot_df['Sugar (g)'].sum():.1f}g")
    with col2:
        st.metric("Duration", f"{max(plot_df['End Time (min)'].max(), plot_df['Start Time (min)'].max()):.0f} min")
    with col3:
        st.metric("Food Items", len(food_df))
    with col4:
        st.metric("Drink Items", len(drink_df))
