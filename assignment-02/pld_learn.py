'''
Machine Learning Pipeline
Patrick Lavallee Delgado
University of Chicago, CS & Harris MSCAPP '20
April 2019

'''

from datetime import datetime
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn import tree
from sklearn.model_selection import train_test_split
from tabulate import tabulate

class Plumbum:

    def __init__(self, dataset, name=None, seed=0):

        self._dataset = pd.read_csv(dataset, index_col=False)
        self._update_metadata(metadata=("name", name), new=True)
        self._update_summary()
        self._seed = seed
    

    def _update_metadata(self, metadata=None, new=False):

        if new:
            self._metadata = {
                "create_date": datetime.now()
            }
        if metadata:
            parameter, value = metadata
            self._metadata[parameter] = value
        else:
            self._metadata["modify_date"] = datetime.now()
            self._metadata["n_cols"] = self._dataset.shape[0]
            self._metadata["n_rows"] = self._dataset.shape[1]

    
    def _update_summary(self):

        self._summary = {
            "aggregations": self._dataset.describe(),
            "correlations": self._dataset.corr(),
            "distributions": [
                self._plot_distribution(self._dataset[variable])
                for variable in self._dataset.columns()
            ]
        }
 

    def _plot_distribution(self, variable):

        histogram, edges = np.histogram(variable, density=True, bins=50)
        pdf_x = np.linspace(variable.min(), variable.max(), variable.count())
        pdf_y = stats.skewnorm.pdf(pdf_x, *stats.skewnorm.fit(variable))
        plot = figure(
            title="Distribution of " + variable.name,
            tools="",
            background_fill_color="#FAFAFA"
        )
        plot.quad(
            top=histogram,
            bottom=0,
            left=edges[:-1],
            right=edges[1:],
            fill_color="navy",
            line_color="#FFFFFF",
            alpha=0.5
        )
        plot.line(
            x = pdf_x,
            y = pdf_y,
            color = "navy"
        )
        plot.xaxis.axis_label = variable.name
        plot.yaxis.axis_label = "frequency"
        plot.grid.grid_line_color="#FFFFFF"
        return plot


    def clean(self):

        # Fill numeric variable NAs with variable median.
        num_variable_medians = {
            variable: self._dataset[variable].median()
            for variable in self._dataset.columns
            if pd.api.types.is_numeric_dtype(variable)
        }
        self._dataset = self._dataset.fillna(value=num_variable_medians)

        # Strip string variable whitespace.
        str_variables = [
            variable
            for variable in self._dataset.columns
            if pd.api.types.is_string_dtype(variable)
        ]
        for variable in str_variables:
            self._dataset[variable] = self._dataset[variable].str.strip()
    

    def as_discrete(self, variable_name, bins):

        variable = self._dataset[variable_name]
        assert pd.api.types.is_numeric_dtype(variable)
        discrete_label = variable.name + "_as_discrete"
        self._dataset[discrete_label] = pd.qcut(
            x=variable,
            q=bins,
            labels=False
        )


    def as_dummy(self, variable_name):

        variable = self._dataset[variable_name]
        assert pd.api.types.is_string_dtype(variable)
        dummies = variable.unique()
        for dummy in dummies:
            dummy_label = variable.name + "_is_" + "_".join([dummy])
            self._dataset[dummy_label] = (variable == dummy).astype(int)

    
    def to_classifier(self, variable_name, test_size=0.3):

        train_X, test_X, train_y, test_y = train_test_split(
            self._dataset.drop(columns=variable_name),
            self._dataset[variable_name],
            test_size=test_size,
            random_state=self._seed
        )
        self._classifier = tree.DecisionTreeClassifier()
        self._classifier = self._classifier.fit(
            X=train_X,
            y=train_y
        )
        predictions = self._classifier.predict_proba(test_X)[:,1]
        predictions.name = "Predictions for " + variable_name
        return self._plot_distribution(predictions)


    def __repr__(self):

        return self._dataset


    def __str__(self):

        return tabulate(
            self._dataset,
            headers="keys",
            tablefmt="simple",
            showindex="never"
            )


    
    



