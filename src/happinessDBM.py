import sqlite3
import streamlit as st
import pandas as pd

db_file = "happinessDB.sqlite3"
conn = sqlite3.connect(db_file)

def perform_query(year, attributes):
	"""Builds and performs a query string, returning the results"""
	q_str = "SELECT " # SELECT {att[1]}, {att[2]}, {att[3]} FROM {year};
	# Add the attributes to the q_str string
	for att in attributes:
		q_str = q_str + att
		# Add a comma if it is not the last attribute
		if att != attributes[len(attributes)-1]:
			q_str = q_str + ", "
	q_str = q_str + f" FROM year{year};"
	# st.write(f"Query: {q_str}")
	# Execute the query in the SQL database
	result = conn.execute(q_str)
	return result.fetchall()

def perform_agg_func(year, func, attribute):
	"""Builds and performs an aggregate function query, returning the result"""
	q_str = f"SELECT {func}({attribute}) FROM year{year}" # SELECT {func}({att}) FROM {year};
	# st.write(f"Query: {q_str}")
	# Execute the query in the SQL database
	result = conn.execute(q_str)
	res = result.fetchall()
	# fetchall() returns a list of tuples, so we want the 0th tuple's 0th element
	return res[0][0]

def conditional_query(year, attributes, comp_att, op, value):
	"""Builds and performs a query string using constraints, returning the results"""
	st.write("If the results are empty, it is likely that no data matches your condition.")
	# SELECT {att[1]}, {att[2]}, {att[3]} FROM {year} WHERE {comp_att} {operation} {value};
	q_str = "SELECT "
	# Add the attributes to the q_str string
	for att in attributes:
		q_str = q_str + att
		# Add a comma if it is not the last attribute
		if att != attributes[len(attributes)-1]:
			q_str = q_str + ", "
	q_str = q_str + f" FROM year{year} WHERE {comp_att} {op} {value};"
	# st.write(f"Query: {q_str}")
	# Execute the query in the SQL database
	result = conn.execute(q_str)
	return result.fetchall()

def main():
	"""Main function the Streamlit user interface."""
	st.title("Welcome to the World Happiness Database!")
	# Home is where the user can input queries
	# About will contain info about the data and the program
	menu = ["Home","About"]
	choice = st.sidebar.selectbox("Menu",menu)
	# Query form
	if choice == "Home":
		st.subheader("Querying the Database:")
		# Collect the desired year and attributes from the user
		year = st.selectbox('Please select the year:', ['2015', '2016', '2017', '2018', '2019'])
		option = st.radio('Select query type:', ['Basic Query', 'Aggregate Function Query', 'Conditional Query'])
		# Option to use aggregate functions
		if option == 'Aggregate Function Query':
			agg_func = st.selectbox('Aggregate functions:', ['AVG','MIN','MAX','SUM','COUNT'])
			# The user can only select one att and it must be a number
			attribute = st.selectbox(
				'Please select the attribute to perform the function on',
				['score','economy','family','health','freedom','generosity','trust'])
			# Use a form for submit button
			with st.form(key='query_form'):
				submit_button = st.form_submit_button("Submit Query")
			if submit_button:
				st.info("Query submitted. Your results are below.")
				result = perform_agg_func(year, agg_func, attribute)
				# Using metric for a big pretty number display
				st.metric("Result: ", result)
		elif option == 'Conditional Query':
			# if they aren't using an aggregate function, allow multiselect
			attributes = st.multiselect(
				'Please select the attribute(s) you\'re looking for',
				['country','rank','score','economy','family','health','freedom','generosity','trust'])
			comp_att = st.selectbox(
				'Attribute to compare:',
				['country','rank','score','economy','family','health','freedom','generosity','trust'])
			op = st.selectbox('Conditional operator to be used:', ['<','>','=='])
			value = st.text_input('Value to compare to:')
			# Use a form for submit button
			with st.form(key='query_form'):
				submit_button = st.form_submit_button("Submit Query")
			if submit_button:
				st.info("Query submitted. Your results are below.")
				# Perform the query
				results = conditional_query(year, attributes, comp_att, op, value)
				# Results
				# Human-readable results
				with st.expander("Result Table"):
					query_df = pd.DataFrame(results)
					st.dataframe(query_df)
				# json results
				with st.expander("Results"):
					st.write(results)
		# Basic query option
		else:
			# if they aren't using an aggregate function, allow multiselect
			attributes = st.multiselect(
				'Please select the attribute(s) you\'re looking for',
				['country','rank','score','economy','family','health','freedom','generosity','trust'])
			# Use a form for submit button
			with st.form(key='query_form'):
				submit_button = st.form_submit_button("Submit Query")
			if submit_button:
				st.info("Query submitted. Your results are below.")
				# Perform the query
				results = perform_query(year, attributes)
				# Results
				# Human-readable results
				with st.expander("Results Table"):
					query_df = pd.DataFrame(results)
					st.dataframe(query_df)
				# json results
				with st.expander("Results"):
					st.write(results)
    # About page
	else:
		st.subheader("About the Data")
		st.write(("This database contains information pertaining to the rates of "
		"happiness in countries from the year 2015 to the year 2019. The database accounts "
		"for different factors that attribute to the database including things like rate of "
		"generosity, government trust, the feeling of freedom, health and economy and a few "
		"more factors. The data measures these factors by having the public record how they feel "
		"about these factors in their country on a scale from 1 to 10 and finding the average of "
		"their responses."))
		st.subheader("The 3 Query Options")
		st.write(("For each query option, you will first be asked to select a year from the drop "
		"down menu. Once you have filled out the query of your choosing, hit the 'Submit Query' button."
		"You will see a confirmation message and two result boxes appear. Click on the 'Results "
		"Table' box to view a clean table representation of the results. Click on the 'Results' box "
		"to view the raw results of the query."))
		st.write("**Basic Query**")
		st.write(("This option is the simplest query option. With this option, you can select the "
		"year and as many attributes as you'd like."))
		st.write("**Aggregate Function Query**")
		st.write(("This option allows you to use aggregate functions in your query. Select a function "
		"and an attribute to perform the function on. Please note that only numeric data is available "
		"to choose from."))
		st.write("**Conditional Query**")
		st.write(("This option allows you to use conditional logic in your query. Similarly to the "
		"Basic Query, you can choose as many attribute as you would like to see. Next, you will be "
		"asked to select the attribute you wish to apply the conditional logic to. You will then need "
		"to select the conditional operator to use and the value to compare to. Be sure that the value "
		"you type in is exactly correct, or else your results may be empty."))

if __name__ == '__main__':
	main()
