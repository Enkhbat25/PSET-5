# World Happiness Explorer 2025

A Streamlit app for PSET 5. It takes user input and turns it into interactive visualizations of the World Happiness Report 2025 rankings.

## User inputs

- **Factor** dropdown: GDP per capita, social support, healthy life expectancy, freedom, generosity or perceptions of corruption
- **Country to highlight** dropdown: any of the 147 ranked countries
- **Countries in ranking** slider: how many top countries the bar chart shows

## Visualizations

- Scatter plot of the selected factor against happiness score, with the selected country highlighted
- Bar chart of the top countries for the selected factor, which always includes the selected country

## Data

`world_happiness_2025.csv` contains the `Year = 2024` rows of [`WHR25_Data_Figure_2.1v3.xlsx`](https://files.worldhappiness.report/WHR25_Data_Figure_2.1v3.xlsx) from the [World Happiness Report 2025](https://worldhappiness.report/ed/2025/). These rows are the rankings published in the 2025 report, based on 2022-2024 averages. Columns were renamed for readability.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
