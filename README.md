# SimplePipeline

*A lightweight Python library for building and executing data pipelines with logging and error handling.*

![Python](https://img.shields.io/badge/python-3.7+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 📖 Features

✅ Define **data pipelines** with processing steps, conditions, and outputs  
✅ Support **multiple ingests** (data sources)  
✅ **Graceful failure handling** with logging  
✅ Customizable logging with **plug-and-play loggers** (`FileLogger`)  
✅ Filter logs by level (`INFO`, `SUCCESS`, `ERROR`)  
✅ **Visualize** the pipeline with an interactive graph  

## 📥 Installation

### **Prerequisites**

Ensure you have Python **3.9+** installed. You can check your Python version with:

```sh
python --version
```

### **Installing SimplePipeline**

To install SimplePipeline, run the following command:

```sh
pip install simple-pipelines
```

## 📝 Usage

### **Creating a Pipeline**

To create a pipeline, import the `SimplePipeline` class from the `simple_pipelines` module:

```python
from simple_pipelines import SimplePipeline
```

Create a new pipeline instance:

```python
pipeline = SimplePipeline("My Pipeline")
```

### **Adding Ingests**

Ingests are functions that return data. You can add ingests to your pipeline using the `create_ingest` method:

```python
def ingest_users():
    return pd.DataFrame({
        "ID": [1, 2, 3, 4, 5],
        "Age": [25, 32, 40, 23, 36],
        "Score": [80, 90, 85, 78, 88]
    })

pipeline.create_ingest(ingest_users, "Users")
```

The `create_ingest` method takes two arguments: the ingest function and a name for the ingest. The ingest function should return a `pandas.DataFrame` or a dictionary.

### **Adding Steps**

Steps are functions that process data. You can add steps to your pipeline using the `pipe` method:

```python
def process_users(input, ingests):
    df = ingests["Users"].copy()
    df["B"] = df["Age"] * 2
    return df

pipeline.pipe(process_users, "Process Users")
```

The `pipe` method takes two arguments: the step function and a name for the step. The step function should take two arguments: `input`, which is the output of the previous step, and `ingests`, which is a dictionary containing all ingests. The step function should return the processed data.

### **Adding Conditions**

Conditions are functions that evaluate whether a step should be executed. You can add conditions to your pipeline using the `condition` method:

```python
def is_vip(input, ingests):
    return input["Purchase_Amount"].sum() > 150

def branch_vip(input, ingests):
    input["Classification"] = "VIP"
    return input

def branch_regular(input, ingests):
    input["Classification"] = "Regular"
    return input

pipeline.condition(
    conditions={is_vip: branch_vip},
    default_branch=branch_regular,
    name="Check VIP Status"
)
```

The `condition` method takes three arguments: a dictionary of conditions and their corresponding branches, a default branch, and a name for the condition. The conditions should be functions that take two arguments: `input`, which is the output of the previous step, and `ingests`, which is a dictionary containing all ingests. The branches should be functions that take two arguments: `input`, which is the output of the previous step, and `ingests`, which is a dictionary containing all ingests. The default branch should be a function that takes two arguments: `input`, which is the output of the previous step, and `ingests`, which is a dictionary containing all ingests.

### **Adding Outputs**

Outputs are functions that do not return data. You can add outputs to your pipeline using the `output` method:

```python
def final_output(input):
    print("Final Processed Data:")
    print(input)

pipeline.output(final_output, "Final Output")
```

The `output` method takes two arguments: the output function and a name for the output. The output function should take one argument: `input`, which is the output of the previous step.

### **Executing the Pipeline**

To execute the pipeline, call the `execute` method:

```python
pipeline.execute()
```

The `execute` method returns the output of the last step, or `None` if the pipeline fails.

### **Visualizing the Pipeline**

To visualize the pipeline, call the `visualize` method:

```python
pipeline.visualize()
```

This will generate an interactive left-to-right visualization of the pipeline using Plotly without Graphviz.

## 📝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes and commit them.
4. Push your changes to your forked repository.
5. Create a pull request to the main repository.

## 📝 License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
