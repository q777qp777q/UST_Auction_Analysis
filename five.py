import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re


path = "" #  URL of csv here
df = pd.read_csv(path, low_memory=False)


#  reformat Auction Date column
df["Auction Date"] = pd.to_datetime(df["Auction Date"])

#  filter dataframe
yield_curve_data = df[["Auction Date", "Security Term", "High Yield", "High Investment Rate", "Offering Amount"]]

#  create a column combining High Yield and High Investment Rate
yield_curve_data["Yield_or_Investment_Rate"] = yield_curve_data.loc[:, "High Yield"].fillna(yield_curve_data.loc[:, "High Investment Rate"])

#  reformat Offering Amount column
offering_columns = ["Offering Amount"] #  other columns in broader dataset in this format: "Allocation Percentage", "Average / Median Yield"
for column in offering_columns:
    yield_curve_data.loc[:, column] = yield_curve_data.loc[:, column].str.replace(",", "")
    yield_curve_data.loc[:, column] = yield_curve_data.loc[:, column].str.replace("$", "")
yield_curve_data.loc[:, "Offering Amount"] = pd.to_numeric(yield_curve_data.loc[:, "Offering Amount"], errors="raise")

#  function to convert Terms from current format X-Year Y-Month etc. to decimal years
def convert_term_to_years(term):
    years = re.search(r"(\d+)-Year", term)
    months = re.search(r"(\d+)-Month", term)
    weeks = re.search(r"(\d+)-Week", term)
    days = re.search(r"(\d+)-Day", term)

    years = int(years.group(1)) if years else 0
    months = int(months.group(1)) if months else 0
    weeks = int(weeks.group(1)) if weeks else 0
    days = int(days.group(1)) if days else 0

    return years + (months/12) + (weeks/52) + (days/365)


#  convert Security Term to decimal years
yield_curve_data.loc[:, "Security Term"] = yield_curve_data.loc[:, "Security Term"].apply(convert_term_to_years)
yield_curve_data.loc[:, "Security Term"] = pd.to_numeric(yield_curve_data.loc[:, "Security Term"], errors="raise")

#  reformat Yield_or_Investment_Rate column
percentage_columns = ["Yield_or_Investment_Rate"] #  other columns in broader dataset in this format: "Allocation Percentage", "Average / Median Yield"
for column in percentage_columns:
    yield_curve_data.loc[:, column] = yield_curve_data.loc[:, column].str.replace("%", "").astype(float) / 100
yield_curve_data.loc[:, "Yield_or_Investment_Rate"] = pd.to_numeric(yield_curve_data.loc[:, "Yield_or_Investment_Rate"], errors="raise")

# normalize auction size data using max auction size, set scale for bubbles
yield_curve_data["Normalized Auction Size"] = yield_curve_data.loc[:, "Offering Amount"] / yield_curve_data.loc[:, "Offering Amount"].max() * 500  # scale factor for bubbles

#  drop rows with NaN values after combination             <-- move this section up??
yield_curve_data = yield_curve_data.loc[yield_curve_data["Yield_or_Investment_Rate"].notna()]

#  set variables for scatterplot
x = yield_curve_data["Auction Date"]
y = yield_curve_data["Security Term"].astype(float)
s = yield_curve_data["Normalized Auction Size"].astype(float) #  for size of bubble
c = yield_curve_data["Yield_or_Investment_Rate"].astype(float) #  for color of bubble

plt.figure(figsize=(90,12), dpi=200, layout="tight")

plt.scatter(
    x=x,
    y=y,
    s=s,
    c=c,
    cmap="viridis",
    alpha=0.65, #  transparency 0-1
    edgecolors="k"
)

#  format plot further
plt.xlabel("Year", fontsize=20)
plt.ylabel("Security Term (Years)", fontsize=20)
plt.title("Treasury Auction Results, 1979-11-15 to 2024-10-24", fontsize=30)
plt.colorbar(label="High Yield or Investment Rate", fraction=0.01, pad=0.008)
plt.margins(x=0.005)

#  format axes ticks and grid lines
plt.gca().xaxis.set_major_locator(mdates.YearLocator(5))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.gca().xaxis.set_minor_locator(mdates.YearLocator(1))
plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter("%Y"))
plt.grid(which="major")
plt.grid(which="minor", axis="x")
plt.gca().set_axisbelow(True) #  for grid lines behind plot (why is this not default??)

#  add citation
citation_text = f"US Treasury Marketable Securities Auction Results, retrieved from https://www.treasurydirect.gov/auctions/auction-query/\nAnalysis by Tristan Phillips"
plt.text(0, -0.1, citation_text, ha="left", va="top", fontsize=10, transform=plt.gca().transAxes)

plt.show()
#  plt.savefig("results_scatter_full_1.png", bbox_inches="tight", dpi=200)
plt.close()
