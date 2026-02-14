import pandas as pd
import altair as alt

# 1. โหลดข้อมูล
df = pd.read_csv('C:/Users/User/OneDrive/เดสก์ท็อป/Info visual/combined_transcript_final_complete.csv')

# ---------------------------------------------------------
# Step 1: คำนวณ Time Leader
# ---------------------------------------------------------
time_leader_map = {}

for conv_id, group in df.groupby('conversation_id'):
    if len(group) == 2:
        group = group.sort_values('age')
        younger = group.iloc[0]
        older = group.iloc[1]

        winner = 'Tie'

        if older['age'] > younger['age']:
            if older['total_speaking_time'] > younger['total_speaking_time']:
                winner = 'Elder'
            elif younger['total_speaking_time'] > older['total_speaking_time']:
                winner = 'Younger'
        else:
            winner = 'Same Age'

        time_leader_map[conv_id] = winner

df['time_leader'] = df['conversation_id'].map(time_leader_map)

# ---------------------------------------------------------
# Step 2: เตรียมข้อมูลให้ 1 คู่ = 1 observation และตัด same age, tie
# ---------------------------------------------------------
df_convo = df.drop_duplicates(subset=['conversation_id'])
df_filtered = df_convo[df_convo['time_leader'].isin(['Elder', 'Younger'])]

counts = (
    df_filtered
    .groupby(['age_diff', 'time_leader'])
    .size()
    .reset_index(name='count')
)

total_per_diff = counts.groupby('age_diff')['count'].transform('sum')
counts['percentage'] = (counts['count'] / total_per_diff) * 100
counts = counts.sort_values('age_diff')

# ---------------------------------------------------------
# Step 3: Altair Visualization 
# ---------------------------------------------------------
bar = alt.Chart(counts).mark_bar().encode(
    x=alt.X('age_diff:O',
            title='Age Difference (Years)',
            sort='ascending'),
    xOffset='time_leader:N',  
    y=alt.Y('percentage:Q',
            title='Percentage of Wins (%)'),
    color=alt.Color(
        'time_leader:N',
        scale=alt.Scale(
            domain=['Elder', 'Younger'],
            range=["#A50A7C", "#61F74E"]
        ),
        title='Who spoke more?'
    )
).properties(
    width=700,
    height=400,
    title='Percentage of Speaking Time Wins by Age Gap'
)


final_chart = bar 

# save เป็น png
final_chart.save('chart2.png')