from typing import Callable, Dict, Any, List, Optional, Union
import pandas as pd
from .logging import Logger
import traceback


# Allowed data types for ingests and pipeline outputs
PipelineData = Union[Dict[str, Any], pd.DataFrame]
VoidFunction = Callable[[PipelineData], None]  # Output step returns None

# Pipeline function type: Takes (previous step output, all ingests) and returns PipelineData
PipelineFunction = Callable[[PipelineData, Dict[str, PipelineData]], PipelineData]

# Condition function type: Takes (input, all ingests) and returns True/False
ConditionFunction = Callable[[PipelineData, Dict[str, PipelineData]], bool]

# Ingest function type: Returns PipelineData
IngestFunction = Callable[[], PipelineData]


class SimplePipeline:
    def __init__(self, name: str, logger_enabled: bool = False, logger: Optional[Logger] = None):
        self.name: str = name
        self.steps: List[Dict[str, Any]] = []
        self.ingests: Dict[str, IngestFunction] = {}
        self.logger_enabled: bool = logger_enabled
        self.logger: Logger = logger or Logger()

    def reset(self) -> None:
        """Resets the pipeline to its initial state."""
        self.steps = []
        self.ingests = {}

    def pipe(self, function: PipelineFunction, name: str) -> None:
        """Adds a normal processing step to the pipeline."""
        if name in {step["name"] for step in self.steps}:
            raise ValueError(f"Step name '{name}' already exists.")
        self.steps.append({"name": name, "function": function, "type": "process"})

    def output(self, function: VoidFunction, name: str) -> None:
        """Adds an output step that does not return data."""
        if name in {step["name"] for step in self.steps}:
            raise ValueError(f"Step name '{name}' already exists.")
        self.steps.append({"name": name, "function": function, "type": "output"})

    def condition(self, conditions: Dict[ConditionFunction, PipelineFunction], default_branch: PipelineFunction, name: str) -> None:
        """Adds a condition step with multiple possible paths."""
        if name in {step["name"] for step in self.steps}:
            raise ValueError(f"Step name '{name}' already exists.")

        self.steps.append({
            "name": name,
            "conditions": conditions,
            "default_branch": default_branch,
            "type": "condition"
        })

    def create_ingest(self, function: IngestFunction, name: str) -> None:
        """Creates an ingest function that serves as input to the pipeline."""
        if name in self.ingests:
            raise ValueError(f"Ingest name '{name}' already exists.")
        result = function()
        if not isinstance(result, (dict, pd.DataFrame)):
            raise TypeError(f"Ingest function '{name}' must return a dict or pandas.DataFrame, but got {type(result)}")
        self.ingests[name] = function

    def execute(self) -> Optional[PipelineData]:
        """Executes the pipeline sequentially while handling conditions dynamically."""
        data: Dict[str, PipelineData] = {name: function() for name, function in self.ingests.items()}
        output: PipelineData = next(iter(data.values())) if data else {}

        for step in self.steps:
            try:
                if step["type"] == "process":
                    if self.logger_enabled:
                        self.logger.info("Executing Step", step=step["name"])
                    output = step["function"](output, data)  # ✅ Pass ingests as a dictionary
                    if not isinstance(output, (dict, pd.DataFrame)):
                        raise TypeError(f"Pipeline step '{step['name']}' must return a dict or pandas.DataFrame, but got {type(output)}")
                    if self.logger_enabled:
                        self.logger.success("Step Completed", step=step["name"], output_shape=str(output.shape if isinstance(output, pd.DataFrame) else "dict"))

                elif step["type"] == "output":
                    if self.logger_enabled:
                        self.logger.info("Executing Output", step=step["name"])
                    step["function"](output)  # Void function, returns None
                    if self.logger_enabled:
                        self.logger.success("Output Completed", step=step["name"])

                elif step["type"] == "condition":
                    if self.logger_enabled:
                        self.logger.info("Evaluating Condition", step=step["name"])
                    # Evaluate conditions in order, execute the first that matches
                    for condition, branch_fn in step["conditions"].items():
                        if condition(output, data):
                            if self.logger_enabled:
                                self.logger.success("Condition Met", condition=condition.__name__, step=step["name"])
                            output = branch_fn(output, data)
                            break
                    else:
                        if self.logger_enabled:
                            self.logger.warning("Condition Default Taken", step=step["name"])
                        # If no condition matches, execute the default branch
                        output = step["default_branch"](output, data)

                    if not isinstance(output, (dict, pd.DataFrame)):
                        raise TypeError(f"Condition step '{step['name']}' must return a dict or pandas.DataFrame, but got {type(output)}")
            except Exception as e:
                if self.logger_enabled:
                    self.logger.error("Critical Pipeline Failure", error=str(e), traceback=traceback.format_exc())
                return None  # Stops the pipeline entirely on a major failure
        if self.logger_enabled:
            self.logger.success("Pipeline Execution Finished", pipeline=self.name)
        return None if output is None else output
    
    def visualize(self) -> None:
        from .visualize import visualize_pipeline

        """Generates an interactive left-to-right visualization of the pipeline using Plotly without Graphviz."""
        visualize_pipeline(self)

