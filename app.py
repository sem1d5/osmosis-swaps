import pandas as pd 
import plotly.express as px
import streamlit as st
import json
import datetime
from dateutil.relativedelta import relativedelta


st.set_page_config(page_title = "Osmosis Swaps",
					page_icon = ":atom_symbol:",
					layout =  "wide"
					)



# load claims into df
df = pd.read_json(
    f"https://node-api.flipsidecrypto.com/api/v2/queries/d671aca6-e624-453f-910f-68d7cc5b42df/data/latest",
    convert_dates=["DAY"])
    

df_top_bought = pd.read_json(
    f"https://node-api.flipsidecrypto.com/api/v2/queries/97335537-13b6-4f03-a194-398f4bb4328f/data/latest")

df_top_sold = pd.read_json(
    f"https://node-api.flipsidecrypto.com/api/v2/queries/aa21ab49-0e8b-42b0-8995-5afb57424cae/data/latest")
    
df_swapped_to = pd.read_json(
    f"https://node-api.flipsidecrypto.com/api/v2/queries/b6713cda-56a0-413e-8df3-26c6339cca13/data/latest")
     


st.title("Osmosis Swaps ⚛️")
"Hi friends, before we begin, TOP RIGHT SETTINGS --> THEME --> LIGHT MODE."
"There ya go, much better. This dashboard has 2 parts:"
"First, an overview swap stats on Osmosis in the past 7 days." 
"Then, a token deep dive that lets you select a token and monitors its swap transactions in the past 30 days."

st.markdown("---")
st.write("")
st.header("Overview Swaps in the past 7 days")

overviewtext1, overviewtext2 = st.columns((3,1))
with overviewtext1:
	"The overview stats below only includes swap transactions where the respective token prices are available on Coinmarketcap. This excludes arbitrage swaps - i.e. OSMO --> ATOM --> OSMO in one transaction are not counted.",
	"Also, 🟣 and 🌉 are just excuses to use emojis hehe. If you zoomed in close enough, you can see that 🌉 is a bridge."

st.write("")
#big overview stats 

today = pd.datetime.today().date()
selected_date = pd.date_range(today - pd.to_timedelta(6, unit='d'), today, freq='D')
df_datesselected = df[df["DAY"].isin(selected_date)]

weekly_volume = int(df_datesselected["DAILY_VOLUME_SUM"].sum())
weekly_volume_median = int(df_datesselected["DAILY_VOLUME_MEDIAN"].mean())
weekly_transactions = int(df_datesselected["DAILY_SWAP_TRANSACTIONS"].sum())
weekly_traders = int(df_datesselected["DAILY_UNIQUE_TRADERS"].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Weekly Volumes (USD)", f"${weekly_volume:,}", )
col2.metric("Average Weekly Median Volumes (USD)", f"${weekly_volume_median:,}", )
col3.metric("Total Weekly Transactions", f"{weekly_transactions:,}", )
col4.metric("Weekly Traders", f"{weekly_traders:,}", )

st.write("")
overviewcol1, overviewcol2, overviewcol3 = st.columns((3, 1, 3))

with overviewcol1: 
	st.write("Top 10 tokens bought by volume (USD)")
	#st.markdown(top_bought.tolist()) - alternative to list them 
	st.dataframe(df_top_bought, width = 1000, height = 800)

with overviewcol3:
	st.write("Top 10 tokens sold by volume (USD)")
	#st.markdown(top_bought.tolist()) - alternative to list them 
	st.dataframe(df_top_sold, width = 1000, height = 800)




st.markdown("---")
st.write("")
st.header("Token Overview in the past 30 days")

bottom_col1, bottom_col2 = st.columns((1,2)) # this makes the ratio of the columns, col2 is 2 times bigger than col1

with bottom_col1:
    select_token = st.selectbox(
    "Search or select a token: ",
    options=df["CURRENCY"].unique(),
    index=0)

df_selection = df.query(
	"CURRENCY == @select_token")

df_pie_selection = df_swapped_to.query(
	"FROM_TOKEN_DENOM_NAME == @select_token")
	

if "CURRENCY" in df_selection:
	st.subheader(f"30-Day daily stats for the {df_selection['CURRENCY'].unique()} token:")
st.write("Direction 'Buy' here means transactions that are swapping for ATOM while 'Sell' means swapping ATOM for another token")



fig_daily_swap_volume = px.line(
	df_selection,
	x = 'DAY',
	y = 'DAILY_VOLUME_SUM',
	color = 'DIRECTION',
	#markers=True, this gives each point a dot in the graph
	title="<b>Daily Swap Volume (USD)</b>",
	hover_data=['DAY', 'DAILY_VOLUME_SUM'],
	width = 1000,
	height = 500,
	)

fig_daily_swap_volume.update_layout(
    plot_bgcolor="ghostwhite")
#	plot_bgcolor = 'ivory'


fig_daily_median_swap_volume = px.line(
	df_selection,
	x = 'DAY',
	y = 'DAILY_VOLUME_MEDIAN',
	color = 'DIRECTION',
	title="<b>Daily Median Swap Volume (USD) </b>",
	hover_data=['DAY', 'DAILY_VOLUME_MEDIAN'],
	width = 1000,
	height = 500,
	)
fig_daily_median_swap_volume.update_layout(
    plot_bgcolor="ghostwhite")


fig_swap_count = px.line(
	df_selection,
	x = 'DAY',
	y = 'DAILY_SWAP_TRANSACTIONS',
	color = 'DIRECTION',
	title="<b>Daily Number of Transactions</b>",
	hover_data=['DAY', 'DAILY_SWAP_TRANSACTIONS'],
	width = 1000,
	height = 500,
	)
fig_swap_count.update_layout(
    plot_bgcolor="ghostwhite")


fig_daily_traders = px.line(
	df_selection,
	x = 'DAY',
	y = 'DAILY_UNIQUE_TRADERS',
	color = 'DIRECTION',
	title="<b>Daily Trader Count</b>",
	hover_data=['DAY', 'DAILY_UNIQUE_TRADERS'],
	width = 1000,
	height = 500,
	)
fig_daily_traders.update_layout(
    plot_bgcolor="ghostwhite")




pie_fig = px.pie(df_pie_selection, values='TRANSACTION_COUNT', names='CURRENCY',
             title='Most swapped to assets by num. of transactions',
             #hover_data=['lifeExp'], labels={'lifeExp':'life expectancy'}
             )
pie_fig.update_traces(textposition='inside', textinfo='percent+label')


graphcol1, graphcol2 = st.columns(2)

with graphcol1:
	st.plotly_chart(fig_daily_swap_volume, use_container_width=True)

with graphcol2:
	st.plotly_chart(fig_daily_median_swap_volume, use_container_width=True)


graphcol3, graphcol4 = st.columns(2)

with graphcol3:
	st.plotly_chart(fig_swap_count, use_container_width=True)

with graphcol4:
	st.plotly_chart(fig_daily_traders, use_container_width=True)


st.plotly_chart(pie_fig)

st.markdown("---")

"Made by [Sam](https://twitter.com/sem1d5) with data from [Flipsidecrypto](https://flipsidecrypto.xyz/)"
"Fork the sql or download the CSV file [here:](https://app.flipsidecrypto.com/dashboard/osmosis-streamlit-swap-dashboard-B0P6Nd)" 














