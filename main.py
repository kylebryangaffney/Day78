import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import seaborn as sns
from sklearn.linear_model import LinearRegression

## setup pandas
pd.options.display.float_format = '{:,.2f}'.format
register_matplotlib_converters()

## read the movie cost vs revenue 
data = pd.read_csv('cost_revenue_dirty.csv')
data.head()
data.shape

## identify the NAN data points
nan_data = data.isna().values.any()
print(nan_data)

## identify the duplicate data points
duplicate_data = data.duplicated().values.any()
print(duplicate_data)

## identify the datatype of each column
data.info()

## remove the ',' and '$' from all of the money columns and convert the str -> float
bad_chars = [',', '$']
money_columns = ["USD_Production_Budget", "USD_Worldwide_Gross", "USD_Domestic_Gross"]

## iterate through the columns in the df
for col in money_columns:
    ## iterate through the two chars in the array
    for char in bad_chars:
        ## remove the chars from the str
        data[col] = data[col].astype(str).str.replace(char, '')
    ## convert the strs to numbers 
    data[col] = pd.to_numeric(data[col])

## updatae the release data column to pandas date time objects
data["Release_Date"] = pd.to_datetime(data["Release_Date"])
data.info()

## find all of the basic statistics of the data in the csv
data.describe()

## identify how many grossed 0 dometic
no_dom_movies = data[data["USD_Domestic_Gross"] == 0]
print(no_dom_movies)
print(len(no_dom_movies))
## sort the movies with 0 domenstic by the most expensive budget
print(no_dom_movies.sort_values("USD_Production_Budget", ascending=False))


## identify how many grossed 0 worldwide
no_world_movies = data[data["USD_Worldwide_Gross"] == 0]
print(no_world_movies)
print(len(no_world_movies))
## sort the movies with 0 domenstic by the most expensive budget
print(no_world_movies.sort_values("USD_Production_Budget", ascending=False))

## identify movies that were only released outside of the US
non_us_movies = data.loc[(data["USD_Domestic_Gross"] == 0) & data["USD_Worldwide_Gross"] != 0]
print(len(non_us_movies))
print(non_us_movies)

## using query() method to do the same
international_releases = data.query("USD_Domestic_Gross == 0 and USD_Worldwide_Gross != 0")
print(len(international_releases))
print(international_releases.tail())

# Date of Data Collection
scrape_date = pd.Timestamp('2018-5-1')
to_be_released = data[data["Release_Date"] >= scrape_date]
print(len(to_be_released))
print(to_be_released)

## identify the released movies
released_movies = data[data["Release_Date"] < scrape_date]
print(released_movies)

## use the drop method to do the same
clean_data = data.drop(to_be_released.index)
print(clean_data)

clean_data.describe()

## identify which movies lost money
failed_movies = clean_data.query("USD_Production_Budget > USD_Worldwide_Gross")
print(len(failed_movies))
## transform that number into a percentage of the movies that have been releaseed
print(len(failed_movies)/len(clean_data))

## create a seaborn scatterplot of the clean data
sns.scatterplot(data=clean_data, x="USD_Production_Budget", y="USD_Worldwide_Gross")
## reconfigure the scatter plot using matlab attributes
plt.figure(figsize=(8,4), dpi=200)
ax = sns.scatterplot(data=clean_data, x="USD_Production_Budget", y="USD_Worldwide_Gross")
ax.set(ylim=(0, 3000000000), xlim=(0, 450000000), ylabel="Revenue in USD Billions" ,xlabel="Budget in USD 100 Millions")
plt.show()


## update to bubble chart showing size and color intensity for movies
plt.figure(figsize=(8,4), dpi=200)
ax = sns.scatterplot(data=clean_data, x="USD_Production_Budget", y="USD_Worldwide_Gross", hue="USD_Worldwide_Gross", size="USD_Worldwide_Gross")
ax.set(ylim=(0, 3000000000), xlim=(0, 450000000), ylabel="Revenue in USD Billions" ,xlabel="Budget in USD 100 Millions")
plt.show()

## modify the bubble chart to be in dark mode
plt.figure(figsize=(8,4), dpi=200)

with sns.axes_style("darkgrid"):
    ax = sns.scatterplot(data=clean_data, x="USD_Production_Budget", y="USD_Worldwide_Gross", hue="USD_Worldwide_Gross", size="USD_Worldwide_Gross")
    ax.set(ylim=(0, 3000000000), xlim=(0, 450000000), ylabel="Revenue in USD Billions" ,xlabel="Budget in USD 100 Millions")
    plt.show()

## build a 3d scattre plot showing the release date against the budget and world wide gross
plt.figure(figsize=(8,4), dpi=200)
with sns.axes_style("darkgrid"):
    ax = sns.scatterplot(data=clean_data, x="Release_Date", y="USD_Production_Budget", hue="USD_Worldwide_Gross", size="USD_Worldwide_Gross")
    ax.set(ylim=(0, 450000000), xlim=(clean_data["Release_Date"].min(), clean_data["Release_Date"].max()), ylabel="Budget in USD 100 Millions" ,xlabel="Year")
    plt.show()

## build a decade column
decade_index = pd.DatetimeIndex(clean_data["Release_Date"])
decades = (decade_index.year // 10) * 10
clean_data["Decade"] = decades
clean_data.sample()

## divide the data into old and new movies
old_data = clean_data.query("Decade < 1970 ")
old_data.tail()
print(len(old_data))
print(old_data.sort_values("USD_Production_Budget", ascending=False))

new_data = clean_data.query("Decade >= 1970")
new_data.head()
new_data.describe()

## build a scatter plot of the old movies showing the budget against the wolrdwide gross
plt.figure(figsize=(8,4), dpi=200)
with sns.axes_style("whitegrid"):
    sns.regplot(data=old_data, x="USD_Production_Budget", y="USD_Worldwide_Gross", scatter_kws={"alpha" : 0.4}, line_kws={"color": "black"})

## build a similar scatter plot for the new movies
plt.figure(figsize=(8,4), dpi=200)
with sns.axes_style("darkgrid"):
    sns.regplot(data=new_data, x="USD_Production_Budget", y="USD_Worldwide_Gross", color="#2f4b7c", scatter_kws={"alpha" : 0.3}, line_kws={"color": "#ff7c43"})
    ax.set(ylim=(0, 3000000000), xlim=(0, 450000000), ylabel="Revenue in Billions" ,xlabel="Budget in 100 Million")

## instanciate the linear regression object
regression = LinearRegression()
## break out the specific minimal x and y data for the linear regression model
## explanatory variable 
x = pd.DataFrame(new_data, columns=["USD_Production_Budget"])
## respone variable 
y = pd.DataFrame(new_data, columns=["USD_Worldwide_Gross"])

## find the best fit line
regression.fit(x, y)
## theta zero
regression.intercept_
## theta one 
regression.coef_
## generage the r-squared
regression.score(x, y)

## provide the same data from the old movies
old_x = pd.DataFrame(old_data, columns=["USD_Production_Budget"])
## respone variable 
old_y = pd.DataFrame(old_data, columns=["USD_Worldwide_Gross"])
## find the best fit line
regression.fit(old_x, old_y)
## theta zero
print(f"the old intercept is: {regression.intercept_[0]}")
## theta one 
print(f"the old coeficcient is: {regression.coef_[0]}")
## generage the r-squared
print(f"the old r_squared is: {regression.score(old_x, old_y)}")

budget = 350000000
rev_estimate = regression.intercept_[0] + regression.coef_[0, 0] * budget
rev_estimate = round(rev_estimate, -6)
print(f"The estimated revenue for a $350 million budget is roughly: ${rev_estimate:.10}")