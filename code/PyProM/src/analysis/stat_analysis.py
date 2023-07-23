import numpy as np
from scipy import stats
import math

class StatAnalyzer(object):

	def __init__(self, eventlog):
		super(StatAnalyzer, self).__init__()
		self.eventlog = eventlog
		self.data = self.produce_basic_stat(eventlog)

	def produce_basic_stat(self, eventlog):
		grouped = eventlog.groupby('RESOURCE')

		def count(x):
			return x.count()

		data = grouped.VALUE.agg([count, np.mean, np.std])

		return data


	def produce_KS_test(self, alpha_normality=0.05):
		print("KS_test begins, alpha = {}".format(alpha_normality))

		def eval_normality(unique_resource):
		    resource = self.eventlog[self.eventlog['RESOURCE'] == unique_resource]
		    d, p_value = stats.kstest(resource['VALUE'], 'norm')
		    """
		    if len(resource['VALUE']) > 3:
		        d, p_value = stats.shapiro(resource['VALUE'])
		    else:
		        p_value = 0.0
		    """
		    return p_value

		self.data.loc[:,'normality_p_value'] = self.data.index.to_series().apply(eval_normality)
		self.data.loc[:,'Normality'] = self.data['normality_p_value'] > alpha_normality
		print("KS_test completed: {}".format(len(self.data)))
		#print(self.data)
		return self.data

	def produce_ANOVA_test(self, alpha_ANOVA = 0.05, alpha_KRUSKAL=0.05):
		print("STEP_TEST begins, alpha = {}".format(alpha_ANOVA))
		#step별 정리
		unique_activities = self.eventlog.get_activities()

		normal_resources = self.data[self.data.loc[:,'Normality'] == True].index.unique()

		for unique_activity in unique_activities:
			#self.eventlog를 특정 STEP으로 filtering
			cnt_resource = len(set(self.eventlog.loc[self.eventlog['ACTIVITY'] == unique_activity, 'RESOURCE']))
			#print("STEP {} has resource: {}".format(unique_activity, cnt_resource))
			if cnt_resource < 2:
				print("Doesn't require ANOVA test")
				continue
			filtered = self.eventlog.loc[self.eventlog['ACTIVITY'] == unique_activity, :]

			unique_resources = self.eventlog.loc[self.eventlog['ACTIVITY'] == unique_activity, 'RESOURCE'].unique()

			if all(x in normal_resources for x in unique_resources):
				ANOVA = True
			else:
				ANOVA = False

			#step 내 설비들의 VALUE를 저장
			step_resource_values = {}
			for unique_resource in unique_resources:
				#filtered['RESOURCE']가 필요, 모든 observation이 필요하므로
				step_resource_values[unique_resource]=(filtered.loc[filtered['RESOURCE']==unique_resource, 'VALUE'])

			if ANOVA == False:
				statistic, p_value = stats.kruskal(*step_resource_values.values())
				self.data.loc[unique_resources, 'kruskal_p_value'] = p_value
				self.data.loc[:,'KRUSKAL'] = self.data['kruskal_p_value'] > alpha_KRUSKAL
			else:
				statistic, p_value = stats.f_oneway(*step_resource_values.values())
				self.data.loc[unique_resources, 'anova_p_value'] = p_value
				self.data.loc[:,'ACTIVITY_TEST'] = self.data['anova_p_value'] > alpha_ANOVA
		print("ACTIVITY_TEST completed: {}".format(len(self.data)))
		#print(self.data)
		return self.data

	def Linear_Contrast(self, row, other_rows, activity):
	    #N is total observations
	    N = other_rows.count_event()

	    filtered = self.eventlog.loc[self.eventlog['ACTIVITY'] == activity, :]
	    filtered_VALUE = filtered.loc[filtered['RESOURCE'].isin(other_rows.index), 'VALUE']

	    #calculate SS_error
	    sum_y_squared = sum([value**2 for value in filtered_VALUE])
	    SS_error = sum_y_squared - sum(filtered.groupby('RESOURCE').sum()['VALUE']**2/filtered.groupby('RESOURCE').size())

	    #exclude 비교대상
	    other_rows = other_rows.drop(row.name)

	    #k is # groups
	    k = len(other_rows.index)

	    #calcualte SS contrast
	    L = k*row['mean']
	    for mean in other_rows['mean']:
	        L -= mean

	    denominator = k*k/row['count']
	    for no_obs in other_rows['count']:
	        denominator += 1/no_obs
	        N +=no_obs

	    #degrees of freedom
	    DFbetween = 1
	    DFwithin = N - k

	    MS_error = SS_error / DFwithin

	    std = math.sqrt(MS_error*denominator)

	    t_contrast = L/std

	    p_value = stats.t.sf(t_contrast, DFwithin)
	    return p_value

	def Nonparametric_Linear_Contrast(self, row, other_rows, activity):
	    #N is total observations
	    other_rows = other_rows.drop(row.name)


	    filtered = self.eventlog[self.eventlog['ACTIVITY'] == activity]
	    other_rows_filtered_VALUE = filtered.loc[filtered['RESOURCE'].isin(other_rows.index), 'VALUE']
	    row_filtered_VALUE = filtered.loc[filtered['RESOURCE'] == row.name, 'VALUE']
	    statistic, p_value = stats.mannwhitneyu(other_rows_filtered_VALUE, row_filtered_VALUE)
	    return p_value
