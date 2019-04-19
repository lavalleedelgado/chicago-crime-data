'''
Machine Learning Pipeline
Patrick Lavallee Delgado
University of Chicago, CS & Harris MSCAPP '20
April 2019

'''

from datetime import datetime
from bokeh.io import export_png
from bokeh.layouts import gridplot
from bokeh.plotting import figure, output_file, save
import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn import tree
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

class Plumbum:

    def __init__(self, dataset_path, definitions_path=None, seed=0):

        self._dataset = self._clean(pd.read_csv(dataset_path, index_col=False))
        self._definitions = self._read_definitions(definitions_path)
        self._metadata = {
            variable_name: self._summarize_feature(variable_name)
            for variable_name in self._dataset.columns
        }
        self._seed = seed
    

    def _clean(self, dataset):

        return self._clean_string_whitespace(
            self._clean_numeric_nas(
                dataset
            )
        )
    

    def _clean_numeric_nas(self, dataset):

        num_variable_medians = {
            variable_name: dataset[variable_name].median()
            for variable_name in dataset.columns
            if pd.api.types.is_numeric_dtype(dataset[variable_name])
        }
        return dataset.fillna(value=num_variable_medians)

    
    def _clean_string_whitespace(self, dataset):

        dataset.columns = [
            variable_name.strip()
            for variable_name in dataset.columns
        ]
        str_variables = [
            variable_name
            for variable_name in dataset.columns
            if pd.api.types.is_string_dtype(dataset[variable_name])
        ]
        for variable_name in str_variables:
            dataset[variable_name] = dataset[variable_name].str.strip()
        return dataset


    def _read_definitions(self, definitions_path):

        definitions = {
            variable_name: None
            for variable_name in self._dataset.columns
        }
        if definitions_path is not None:
            definitions_file = pd.read_csv(definitions_path, index_col=False)
            definitions_file = pd.Series(
                definitions_file["definition"].values,
                index=definitions_file["variable_name"]
            )
            definitions_file = definitions_file.to_dict()
            for variable_name in definitions_file:
                definitions[variable_name] = definitions_file[variable_name]
        return definitions


    def _summarize_feature(self, variable_name, definition=False):

        assert self._validate_variable(variable_name)
        return {
            "summary": self._dataset[variable_name].describe(),
            "definition": self._definitions[variable_name]
        }
    
    
    def _plot_distribution(self, variable_name):

        assert self._validate_variable(variable_name)
        variable = self._dataset[variable_name]
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
        export_png(
            obj=plot,
            filename=variable_name.lower() + ".png"
        )


    def _validate_variable(self, variable_name):

        assert variable_name in self._dataset.columns, \
            variable_name + "does not exist."
        return True
    

    def _update_metadata(self, parameter, value):

        assert isinstance(value, dict)
        if parameter in self._metadata:
            self._metadata[parameter].update(value)
        else:
            self._metadata[parameter] = value
        self._metadata["correlations"] = self._dataset.corr()

    
    def request(self, variable_names=None):

        if not variable_names:
            return self._metadata
        return_metadata = {}
        if not isinstance(variable_names, list):
            variable_names = [variable_names]
        for variable_name in variable_names:
            assert self._validate_variable(variable_name)
            if variable_name in self._dataset.columns:
                self._update_metadata(
                    parameter=variable_name,
                    value=self._summarize_feature(variable_name)
                )
                self._plot_distribution(variable_name)
            if variable_name in self._metadata:
                return_metadata[variable_name] = self._metadata[variable_name]
        if len(return_metadata) == 1:
            return return_metadata[variable_names[0]]
        return return_metadata


    def as_discrete(self, variable_name, bins):

        assert self._validate_variable(variable_name)
        variable = self._dataset[variable_name]
        assert pd.api.types.is_numeric_dtype(variable)
        discrete_label = variable.name + "_as_discrete"
        self._dataset[discrete_label], bounds= pd.qcut(
            x=variable,
            q=bins,
            labels=False,
            retbins=True
        )
        bin_labels = {
            b: "".join(["(", str(bounds[b]), ", ", str(bounds[b + 1]), "]"])
            for b in range(bins)
        }
        new_metadata = self._summarize_feature(discrete_label)
        new_metadata.update({"quantiles": bin_labels})
        self._update_metadata(
            parameter=discrete_label,
            value=new_metadata
        )


    def as_dummy(self, variable_name):

        assert self._validate_variable(variable_name)
        variable = self._dataset[variable_name]
        dummies = list(variable.unique())
        dummy_labels = []
        for dummy in dummies:
            dummy_label = variable.name + "_is_" + "_".join([str(dummy)])
            dummy_labels.append(dummy_label)
            self._dataset[dummy_label] = (variable == dummy).astype(int)
            self._update_metadata(
                parameter=dummy_label,
                value=self._summarize_feature(dummy_label)
            )
        self._update_metadata(
            parameter=variable_name,
            value={"dummies": dummy_labels}
        )

    
    def as_classifier(self, variable_name, test_size=0.3):

        assert self._validate_variable(variable_name)
        train_X, test_X, train_y, test_y = train_test_split(
            self._dataset.drop(columns=variable_name),
            self._dataset[variable_name],
            test_size=test_size,
            random_state=self._seed
        )
        classifier = tree.DecisionTreeClassifier()
        classifier = classifier.fit(
            X=train_X,
            y=train_y
        )
        predictions = pd.Series(classifier.predict_proba(test_X)[:,1])
        predictions.name = "Classifier Predictions for " + variable_name
        self._update_metadata(
            parameter=variable_name,
            value={
                "classifier_object": classifier,
                "classifier_predictions": predictions,
                "classifier_accuracy": accuracy_score(predictions, test_y)
            }
        )


    def __repr__(self):

        return "\n".join(
            ["Available metadata:"] +
            ["    " + key for key in self._metadata.keys()]
            )

