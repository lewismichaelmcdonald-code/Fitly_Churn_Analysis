# 1 - Import libraries 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#2 - Loading data
print('='*30)
print('Loading Datasets')
print('='*30)

account_info = pd.read_csv('C:/Users/lewis/Desktop/Projects/Datacamp Practical Project/da_fitly_account_info.csv')
customer_support = pd.read_csv('C:/Users/lewis/Desktop/Projects/Datacamp Practical Project/da_fitly_customer_support.csv')
user_activity = pd.read_csv('C:/Users/lewis/Desktop/Projects/Datacamp Practical Project/da_fitly_user_activity.csv')

# Check data imported properly
print(account_info.head(5))
print(customer_support.head(5))
print(user_activity.head(5))

#3 - Data Validation
#3.1 - GDPR boolean mask
users_to_remove = customer_support[customer_support['comments'].notna()]['user_id'].unique()

#3.2 - Account info cleaning and validation
print('='*30)
print('Account Info - Cleaning and Validation')
print('='*30)

# Ensuring there are no negative prices
account_info = account_info[account_info['plan_list_price'] >= 0]

# Changing churn_status to from Y/NaN to bool
account_info['churn_status'] = account_info['churn_status'].notna()

# Get user id's from email adresses in account info and use users_to_remove boolean mask for GDPR
account_info['user_id'] = account_info['email'].str.partition('@')[0]
account_info['user_id'] = account_info['user_id'].str.replace('user','')
account_info['user_id'] = account_info['user_id'].astype(int)
account_info = account_info[~account_info['user_id'].isin(users_to_remove)]

print('\nShape:',account_info.shape)
print('\nMissing values per column:')
print(account_info.isna().sum())
print(account_info['plan'].value_counts())
churn_rate = round((account_info['churn_status'].sum() / account_info['churn_status'].count())*100,1)
print('\nChurn rate is',churn_rate,'%')

#3.3 - Customer support cleaning and validation
print('='*30)
print('Customer Support - Cleaning and Validation')
print('='*30)

# Ensuring there are no resoluion times
customer_support = customer_support[customer_support['resolution_time_hours'] >= 0]

# Changing date columns data type from str to datetime
customer_support['ticket_time'] = pd.to_datetime(customer_support['ticket_time'])
#user_activity['event_time'] = pd.to_datetime(user_activity['event_time'])

# GDPR requests and drop 'comments' column as it will be empty after GDPR requests are removed
customer_support = customer_support[~customer_support['user_id'].isin(users_to_remove)]
customer_support = customer_support.drop(columns=('comments'))

# Replace '-' values in channel column with 'unknown' for clarity
customer_support['channel'] = customer_support['channel'].str.replace('-','unknown')

# Checking for duplicate tickets
if customer_support.duplicated().sum() == 0:
    pass
else:
    customer_support.drop_duplicates(inplace=True)

print('\nShape:',customer_support.shape)
print('\nMissing values per column:')
print(customer_support.isna().sum())
print(customer_support['channel'].value_counts())
print(customer_support['topic'].value_counts())

#3.4 - User activity cleaning and validation
print('='*30)
print('User activity - Cleaning and Validation')
print('='*30)

# GDPR requests
user_activity = user_activity[~user_activity['user_id'].isin(users_to_remove)]

# Changing date columns data type from str to datetime
user_activity['event_time'] = pd.to_datetime(user_activity['event_time'])

print('\nShape:',user_activity.shape)
print('\nMissing values per column:')
print(user_activity.isna().sum())
print(user_activity['event_type'].value_counts())

# Creating analysis dataframe
print('='*30)
print('Analysis Dataframe')
print('='*30)

# Aggregate before merging two or more 'many' tables
support_agg = (customer_support
    .groupby('user_id')
    .agg(
        ticket_count=('ticket_time', 'count'),
        avg_resolution=('resolution_time_hours', 'mean')
    ).reset_index()
)

activity_agg = (user_activity
    .groupby('user_id')
    .agg(
        event_count=('user_id', 'count')
    ).reset_index()
)

analysis_df = account_info.merge(activity_agg, on='user_id', how='left')
analysis_df = analysis_df.merge(support_agg, on='user_id', how='left')

#Replace NaN values with 0 to reflect users who didnt contact support or did no activities
analysis_df['event_count'] = analysis_df['event_count'].fillna(0).astype(int)
analysis_df['ticket_count'] = analysis_df['ticket_count'].fillna(0).astype(int)
analysis_df['avg_resolution'] = analysis_df['avg_resolution'].fillna(0)

print('\nAnalysis dataframe shape:',analysis_df.shape)
print('\nAnalysis dataframe columns:',analysis_df.columns.to_list())

#4 - Figures

# Setting style of figures
sns.set_style('whitegrid')

# Distribution of customer plans
plan_dist = sns.countplot(data = analysis_df, x = 'plan', order = ['Free','Basic','Enterprise','Pro'], hue = 'plan', hue_order = ['Free','Basic','Enterprise','Pro'])
plan_dist.set(xlabel='Plan Type', ylabel='Count of Users')
plt.suptitle('Distribution of Customer Plans', fontweight = 'bold')
# Data labels
for container in plan_dist.containers:
    plan_dist.bar_label(container, fontweight = 'bold')
plt.show()

# Distibution of support tickets
ticket_dist = sns.histplot(data = analysis_df, x = 'ticket_count', binwidth = 1)
ticket_dist.set(xlabel = 'Tickets Raised', ylabel = 'Count of Tickets')
plt.suptitle('Distribution of Support Tickets Raised', fontweight = 'bold')
# Data labels
for container in ticket_dist.containers:
    ticket_dist.bar_label(container, fontweight = 'bold')
plt.show()

# Churn rate by plan type
churn_by_plan = (
    analysis_df
    .groupby('plan')
    .agg(
        user_churn_per_plan = ('churn_status','sum'),
        users_per_plan = ('churn_status','count')
    ).reset_index()
)

churn_by_plan['churn_rate'] = round(churn_by_plan['user_churn_per_plan'] / churn_by_plan['users_per_plan'] * 100, 1)

churn_rate_by_plan_fig = sns.barplot(data = churn_by_plan, x = 'plan', y = 'churn_rate', order = ['Free','Basic','Enterprise','Pro'], hue = 'plan', hue_order = ['Free','Basic','Enterprise','Pro'])
churn_rate_by_plan_fig.set(xlabel = 'User Plan Type', ylabel= 'Churn Rate (%)')
# Data labels
for container in churn_rate_by_plan_fig.containers:
    churn_rate_by_plan_fig.bar_label(container, fontweight = 'bold', fmt = '%.1f%%')
plt.suptitle('Churn Rate by Plan Type', fontweight = 'bold')
plt.show()

#Churn rate by no. support tickets
churn_by_tickets = (
    analysis_df
    .groupby('ticket_count')
    .agg(
        user_churn_per_amount = ('churn_status','sum'),
        users_contacting_support_per_amount = ('churn_status','count')
    ).reset_index()
)

churn_by_tickets['churn_rate'] = round(churn_by_tickets['user_churn_per_amount'] / churn_by_tickets['users_contacting_support_per_amount'] * 100, 1)

churn_by_tickets_fig = sns.barplot(data = churn_by_tickets, x = 'ticket_count', y = 'churn_rate')
churn_by_tickets_fig.set(xlabel = 'Amount of Support Tickets', ylabel = 'Churn Rate (%)')
#Data labels
for container in churn_by_tickets_fig.containers:
    churn_by_tickets_fig.bar_label(container, fontweight = 'bold', fmt = '%.1f%%')
plt.suptitle('Churn Rate by Amount of Support Tickets', fontweight = 'bold')
plt.show()

# Support ticket resolution time by churn status (only customers who raised a ticket)

resolution_by_churn = analysis_df[analysis_df['ticket_count'] > 0]
resolution_by_churn['churn_label'] = resolution_by_churn['churn_status'].map({True: 'Churned', False: 'Retained'})
custom_palette = {'Red','Green'}

resolution_by_churn_fig = sns.boxplot(data=resolution_by_churn, x='churn_label', y='avg_resolution',order=['Retained', 'Churned'], hue = 'churn_label', palette = custom_palette, legend=False)
resolution_by_churn_fig.set(xlabel='Churn Status', ylabel='Average Ticket Resolution Time (hours)')
plt.suptitle('Support Ticket Resolution Time by Churn Status', fontweight='bold')
plt.show()

# Distribution of users by engagement level
events_dist = sns.histplot(data = analysis_df, x = 'event_count', binwidth = 1)
events_dist.set(xlabel='Event Count', ylabel='Count of Users')
plt.suptitle('Distribution of Users by Engagement Level', fontweight = 'bold')
# Data labels
for container in events_dist.containers:
    events_dist.bar_label(container, fontweight = 'bold')
plt.show()

#Churn rate by engagement level (no. events)
churn_by_engagement_level = (
    analysis_df
    .groupby('event_count')
    .agg(
        user_churn_per_engagement_level = ('churn_status', 'sum'),
        users_per_engagement_level = ('churn_status', 'count')
    ).reset_index()
)

churn_by_engagement_level['churn_rate'] = churn_by_engagement_level['user_churn_per_engagement_level'] / churn_by_engagement_level['users_per_engagement_level'] * 100

churn_by_engagement_level_fig = sns.barplot(data = churn_by_engagement_level, x = 'event_count', y = 'churn_rate')
churn_by_engagement_level_fig.set(xlabel = 'Number of Events', ylabel = 'Churn Rate (%)')
for container in churn_by_engagement_level_fig.containers:
    churn_by_engagement_level_fig.bar_label(container, fontweight = 'bold', fmt = '%.1f%%')
plt.suptitle('Churn Rate by Engagement Level', fontweight = 'bold')
plt.show()

#5 - KPIs and Analysis Information
print('='*30)
print('KPIs and Analysis Information')
print('='*30)

# User counts and GDPR impact
total_users_raw = len(account_info) + len(users_to_remove)  
users_removed_gdpr = len(users_to_remove)

print('\n--- User Counts ---')
print('Total users (raw, before GDPR erasure):', total_users_raw)
print('Users removed under GDPR erasure requests:', users_removed_gdpr)
print('Total users in analysis:', len(account_info))

# Overall churn
overall_churned = analysis_df['churn_status'].sum()
overall_total = analysis_df['churn_status'].count()
overall_churn_rate = round((overall_churned / overall_total) * 100, 1)

print('\n--- Churn ---')
print('Churned users:', overall_churned)
print('Overall churn rate:', overall_churn_rate, '%')

# Support engagement
users_with_tickets = (analysis_df['ticket_count'] > 0).sum()
pct_contacted_support = round((users_with_tickets / len(analysis_df)) * 100, 1)
avg_tickets_per_user = round(analysis_df['ticket_count'].mean(), 1)
more_tickets_df = analysis_df[analysis_df['ticket_count'] >= 1]
more_tickets_corr = more_tickets_df['ticket_count'].corr(more_tickets_df['churn_status'].astype(int))

avg_resolution_time = round(analysis_df.loc[analysis_df['ticket_count'] > 0, 'avg_resolution'].mean(), 1)
contacted_support_df = analysis_df[analysis_df['ticket_count'] > 0]
avg_resolution_time_corr = contacted_support_df['avg_resolution'].corr(contacted_support_df['churn_status'].astype(int))

# Average and median resolution time, split by churn status
contacted_support_df = contacted_support_df.copy()
contacted_support_df['churn_label'] = contacted_support_df['churn_status'].map({True: 'Churned', False: 'Retained'})
resolution_stats = (
    contacted_support_df
    .groupby('churn_label')
    .agg(
        avg_resolution_time = ('avg_resolution', 'mean'),
        median_resolution_time = ('avg_resolution', 'median')
    ).reset_index()
)

# Splitting resolution time at a 12 hour threshold for more insight
below_threshold_df = analysis_df[(analysis_df['ticket_count'] > 0) & (analysis_df['avg_resolution'] < 12)]
above_threshold_df = analysis_df[(analysis_df['ticket_count'] > 0) & (analysis_df['avg_resolution'] >= 12)]

below_threshold_churn_rate = round(below_threshold_df['churn_status'].sum() / below_threshold_df['churn_status'].count() * 100, 1)
above_threshold_churn_rate = round(above_threshold_df['churn_status'].sum() / above_threshold_df['churn_status'].count() * 100, 1)

print('\n--- Support Engagement ---')
print('Users who contacted support:', users_with_tickets, '(', pct_contacted_support, '%)')
print('Average tickets per user (all users):', avg_tickets_per_user)
print('The correlation between ticket count and churn among customers who have contacted support is', more_tickets_corr)
print('Average resolution time in hours (users with tickets only):', avg_resolution_time)
print('The correlation between average ticket resolution time and churn is', avg_resolution_time_corr)

print('\n--- Resolution Time by Churn Status ---')
print(resolution_stats)

print('\n--- Support Ticket Resolution SLA (12 hours) ---')
print('Customers below 12hr SLA:', len(below_threshold_df), '(', round(len(below_threshold_df)/len(contacted_support_df)*100, 1), '% )')
print('Churn rate below SLA:', below_threshold_churn_rate, '%')
print('Customers at/above 12hr SLA:', len(above_threshold_df), '(', round(len(above_threshold_df)/len(contacted_support_df)*100, 1), '% )')
print('Churn rate at/above SLA:', above_threshold_churn_rate, '%')

# Activity
avg_events_per_user = round(analysis_df['event_count'].mean(), 1)
users_with_no_activity = (analysis_df['event_count'] == 0).sum()
activity_corr = analysis_df['event_count'].corr(analysis_df['churn_status'].astype(int))

print('\n--- Engagement ---')
print('Average events per user:', avg_events_per_user)
print('Users with zero recorded activity:', users_with_no_activity)
print('The correlation between engagement level and churn is', activity_corr)

# Plan distribution
print('\n--- Plan Distribution ---')
print(analysis_df['plan'].value_counts())
print(analysis_df['plan'].value_counts(normalize = True))

# Highest/lowest churn segments
highest_churn_plan = churn_by_plan.loc[churn_by_plan['churn_rate'].idxmax()]
lowest_churn_plan = churn_by_plan.loc[churn_by_plan['churn_rate'].idxmin()]

print('\n--- Churn by Plan Type ---')
print('Highest churn plan:', highest_churn_plan['plan'], '(', highest_churn_plan['churn_rate'], '%)')
print('Lowest churn plan:', lowest_churn_plan['plan'], '(', lowest_churn_plan['churn_rate'], '%)')
