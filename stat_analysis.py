import sqlite3
import pandas as pd
from scipy import stats
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def resp_queries(population):
    neg_query = f"""
        SELECT ps.percentage
        FROM populations_samplewise ps
        JOIN samples samp ON samp.sample = ps.sample
        JOIN subjects sub ON sub.subject = samp.subject
        WHERE samp.response = 'no'
        AND sub.treatment = 'miraclib'
        AND sub.sample_type = 'PBMC'
        AND sub.condition = 'melanoma'
        AND ps.population = '{population}'
        """
    
    pos_query = f"""
        SELECT ps.percentage
        FROM populations_samplewise ps
        JOIN samples samp ON samp.sample = ps.sample
        JOIN subjects sub ON sub.subject = samp.subject
        WHERE samp.response = 'yes'
        AND sub.treatment = 'miraclib'
        AND sub.sample_type = 'PBMC'
        AND sub.condition = 'melanoma'
        AND ps.population = '{population}'
        """
    
    return (pos_query, neg_query)


def boxplots_histograms_confidences(population):
    bins = 20
    conn = sqlite3.connect('data.db')

    pos_query, neg_query = resp_queries(population)
    neg = pd.read_sql_query(neg_query, conn)["percentage"]
    pos = pd.read_sql_query(pos_query, conn)["percentage"]

    xmin, xmax = min(neg.min(), pos.min()), max(neg.max(), pos.max())

    fig = make_subplots(rows=1, cols=2, column_widths=[0.3, 0.7],
                        subplot_titles=(f"{population} Boxplot", f"{population} Histogram"))

    for trace, col in [
        (go.Box(x=neg, name="Non-resp", marker_color="royalblue", orientation="h"), 1),
        (go.Box(x=pos, name="Resp", marker_color="firebrick", orientation="h"), 1),
        (go.Histogram(x=neg, name="Non-resp", marker_color="royalblue", opacity=.6, nbinsx=bins, showlegend=False), 2),
        (go.Histogram(x=pos, name="Resp", marker_color="firebrick", opacity=.6, nbinsx=bins, showlegend=False), 2)
    ]:
        fig.add_trace(trace, row=1, col=col)

    fig.update_xaxes(range=[xmin, xmax], row=1, col=1, title_text=f"Percentage of Sample Cells of Type {population}")
    fig.update_xaxes(range=[xmin, xmax], row=1, col=2, title_text=f"Percentage of Sample Cells of Type {population}")
    fig.update_yaxes(title_text="Frequency", row=1, col=2)

    fig.update_layout(title=f"{population} Percentage of Sample Cells Boxplot and Histogram for Responding vs Non-responding Samples", barmode="overlay", template="plotly_white", height=500)

    t_stat, p_value = stats.ttest_ind(neg, pos, equal_var=False)
    confidence = [population, t_stat, p_value]

    conn.close()

    return fig, confidence

def report_statistical_significance(population, t_stat, p_value):
    yes_sig = "a statistically significant difference between the responding and nonresponding samples since the p-value is < 0.05."
    not_sig = "not a statistically significant difference between the responding and nonresponding samples since the p-value is >= 0.05."

    sig = yes_sig
    if p_value >= 0.05:
        sig = not_sig
    return f"For population '{population.replace('_', ' ').title()}' proportions, with a t-stat and p-value of {t_stat:.4f} and {p_value:.4f}, respectively, there is {sig}"



if __name__ == "__main__":
    populations = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
    print('Part 3: The following are comments on the statistical significance of each cell type in PBMC cells from melanoma patients receiving miraclib between responders and non-responders. Boxplots and histograms are made in the background.')
    for population in populations:
        fig, confidence = boxplots_histograms_confidences(population)
        fig.show()
        print(report_statistical_significance(*confidence))
    print('\n\n')
