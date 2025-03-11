import pytest
import pandas as pd
from simple_pipelines import SimplePipeline

### Test 1: Basic Pipeline Execution ###
def test_pipeline_execution():
    pipeline = SimplePipeline("Test Pipeline")

    # Define an ingest function
    pipeline.create_ingest(lambda: pd.DataFrame({"A": [1, 2, 3]}), "ingest1")

    # Define a processing function
    def add_column(input, ingests):
        input["B"] = input["A"] + 1
        return input

    pipeline.pipe(add_column, "Add Column B")

    # Define an output function
    def store_output(input):
        assert isinstance(input, pd.DataFrame), "Output must be a DataFrame"
        assert "B" in input.columns, "Column 'B' should be added"
    
    pipeline.output(store_output, "Final Output")

    pipeline.execute()

### Test 2: Condition Branching ###
def test_condition_branching():
    pipeline = SimplePipeline("Test Condition Pipeline")

    pipeline.create_ingest(lambda: pd.DataFrame({"A": [10, 20, 30]}), "ingest1")

    def condition_fn(input, ingests):
        return input["A"].sum() > 50

    def branch_high(input, ingests):
        input["Category"] = "High"
        return input

    def branch_low(input, ingests):
        input["Category"] = "Low"
        return input

    pipeline.condition({condition_fn: branch_high}, default_branch=branch_low, name="Check A Sum")

    result = pipeline.execute()

    assert "Category" in result.columns, "Condition function did not add a category column"
    assert result["Category"].iloc[0] == "High", "Incorrect condition execution"

### Test 3: Handling Failing Steps ###
def test_failing_step():
    pipeline = SimplePipeline("Test Failure Handling")

    pipeline.create_ingest(lambda: pd.DataFrame({"A": [1, 2, 3]}), "ingest1")

    def faulty_step(input, ingests):
        raise ValueError("This step is broken!")

    pipeline.pipe(faulty_step, "Failing Step")

    result = pipeline.execute()

    assert result is None, "Pipeline should stop execution on failure"
