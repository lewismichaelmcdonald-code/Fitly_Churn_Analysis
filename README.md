# Fitly Churn Analysis

A Python churn analysis for a fitness subscription app. Uses pandas and Seaborn to clean real world data, uncover what's actually driving customers to leave, and turn that into a KPI the business can track. Includes GDPR compliant data handling and a written report with recommendations.

## Overview

Fitly, a fitness subscription app, was losing over a quarter of its customers and had no clear picture of why. This project combines three raw data sources into a single customer level dataset, validates and cleans every field, and explores which factors are most strongly associated with churn. The strongest finding, support ticket resolution time, is turned into a recommended KPI with an initial baseline the business can start monitoring immediately.

## Tools Used

Python, pandas, Matplotlib, Seaborn

## Data

Three raw datasets, found in `Raw_Data/`:

* `da_fitly_account_info.csv`, plan type, price, and churn status per customer
* `da_fitly_customer_support.csv`, every support ticket raised, its channel, topic, and resolution time
* `da_fitly_user_activity.csv`, in app activity events (workouts, videos, articles)

Every column across all three tables was validated (negative values, duplicates, referential integrity between tables, and category values were all checked). 43 customers who had submitted a GDPR right to erasure request were identified and fully removed from all three datasets before any analysis took place. The final analysis dataset covers 357 customers.

## Key Findings

**Our customer base is spread fairly evenly across four plans**

![Distribution of Customer Plans](Figures/Distribution%20of%20Customer%20Plans.png)

Basic (103, 28.9%), Free (94, 26.3%), Enterprise (86, 24.1%) and Pro (74, 20.7%). No single tier dominates, which means the churn differences below are a real pattern, not a side effect of one plan being far larger than the others.

**Free plan customers churn twice as often as Pro customers**

![Churn Rate by Plan Type](Figures/Churn%20Rate%20by%20Plan%20Type.png)

Free tier churn sits at 38.3%, compared with 18.9% on Pro. Basic (24.3%) and Enterprise (25.6%) sit close to the overall average of 27.2%.

**Most customers contact support at least once**

![Distribution of Support Tickets](Figures/Distribution%20of%20Support%20Tickets.png)

90.8% of customers have raised at least one ticket, averaging 2.2 tickets per customer.

**Resolution time is the strongest predictor of churn in the dataset**

![Ticket Resolution Time by Churn Status](Figures/Ticket%20Resolution%20Time%20by%20Chrun%20Status.png)

Retained customers wait 6.6 hours on average for a ticket to be resolved, while churned customers wait 18.6 hours, close to three times as long. The correlation between resolution time and churn among customers who have raised a ticket is **0.85**, the strongest relationship found anywhere in this project. Splitting at a 12 hour threshold makes the effect clearer still: customers averaging over 12 hours to resolution churn at 91.3%, compared with just 3.4% for those resolved within 12 hours.

**Ticket volume on its own does not predict churn**

![Churn Rate by Amount of Tickets](Figures/Churn%20Rate%20by%20Amount%20Tickets.png)

Churn rate stays in a flat 22% to 31% band from 1 through 6 tickets, and the correlation between ticket count and churn among customers who have contacted support is close to zero (-0.02). Combined with the previous finding, this shows it is not how often a customer contacts support that predicts churn, it is how quickly that contact is resolved.

**Engaged customers are far less likely to churn**

![Distribution of Users by Engagement Level](Figures/Distribution%20of%20Users%20by%20Engagement%20Level.png)
![Churn Rate by Engagement Level](Figures/Churn%20Rate%20by%20Engagement%20Level.png)

135 customers (37.8%) have zero recorded engagement events and churn at 51.9%, dropping sharply to 20.6% at one event and under 10% from two events onward. The correlation between engagement level and churn is -0.41.

## Recommended KPI

**Average Support Ticket Resolution Time**, tracked against a proposed 12 hour SLA.

Current baseline: 10.0 hours average resolution time across ticket raising customers, with 28.4% of them currently above the 12 hour threshold. That group alone accounts for a churn rate of 91.3%, against 3.4% for customers resolved within 12 hours. This metric can be tracked weekly by the support team and monthly by leadership, segmented by plan and channel, and monitored alongside actual churn rate to confirm that improving resolution speed reduces churn over time.

## Recommendations

* Set and resource a 12 hour support ticket resolution target
* Follow up immediately with customers currently above that threshold
* Track resolution time weekly as a core KPI, alongside churn rate
* Re-engage customers showing zero app activity, especially on the Free plan
* Review the Free plan's value proposition given its high churn rate

## Repository Structure

```
Fitly_Churn_Analysis/
├── Churn_Analysis.py     # Full data cleaning, validation, and analysis script
├── Raw_Data/             # Original CSV datasets
├── Figures/              # All charts generated by the analysis
└── README.md
```
