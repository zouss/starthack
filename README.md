# Getting Started with Start Hack Project -> Market at Glance

[Demo]() is also available

# Project Description

On the coding side, we build a dashboard called “The Market at a Glance” (Based on Plotly Dash)
For now, this dashboard has 3 mains tabs/functionalities:

- Live Balance: In this tab, the trader can see the live balance per country. It shows the live consumption (actuals and forecast in dashed line) versus the production (We show also the actuals and the forecast per energy source). We have coded the script that fetches the physical flows from, but we hadn’t the time to add it to the balance. This helps the trader assess the imbalance in the market and put a price number on it.

  `NB: we also tried working on price forecasting based on NN using the all the data that we were able to connect to. (The code can be found in a stand-alone folder in the git repository).`

- Deep dive: In this tab, the traders can select the energy source (The upper left button) and the dashboard will update dynamically. Forecast Vs Actuals: this shows the traders the actuals compared to the 3 latest forecast points for 3 forecast sources (EC, GFS and ICON). NB: For each forecast source, the colors go from the lightest (the oldest forecast) to the darkest (the latest forecast). Then we have a box plot to assess the Mean /Std/Outliers for each forecast source. Forecast Vs Normal: this shows the divergence of the forecast (The EC in this case) from the normal. This divergence is compared to a normal distribution of 10 years divergences history (right side chart shows the histogram). This enables us to assess how different and rare each divergence is. Then the important ones are highlighted in the main chart.

- Flows: This tab shows the “in” and “out” flows to the German grid from the neighboring countries (France, Denmark, Netherlands, …)

We also wanted to fetch the outages data from the EEX Transparency webpage using Selenium for dynamic JS scrapping. This is an interesting data source as the unplanned outages can have a huge impact on the market conditions. And hence, this can have an important impact on the intraday prices. But, for time optimization, we decided to focus on the other parts of the dashboard.

## Project Build Instructions

Make sure you've `git`, `python` installed in your system.

Open terminal and follow these steps;

- Step 1: Clone the repo.

```bash
git clone https://github.com/zouss/starthack.git
```

You should now see a `starthack` folder in your present working directory. Let's change directory to it.

```bash
cd starthack
```

- Step 2: Install dependencies.

```bash
pip install -r requirements.txt
```

- Step 3: Start the project.

```bash
python index.py
```

This will run a local instance of the application `http://127.0.0.1:8050/live_balance`

## Project Screenshots

![Img 1](https://github.com/zouss/starthack/blob/main/screenshots/Screenshot_1.png)

![Img 2](https://github.com/zouss/starthack/blob/main/screenshots/Screenshot_2.png)

![Img 3](https://github.com/zouss/starthack/blob/main/screenshots/Screenshot_3.png)

![Img 4](https://github.com/zouss/starthack/blob/main/screenshots/Screenshot_4.png)

![Img 5](https://github.com/zouss/starthack/blob/main/screenshots/Screenshot_5.png)

## Thank You
