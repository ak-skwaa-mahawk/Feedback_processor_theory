# create in a utils or core/helpers.py file
def root_function(fn):
    fn.is_root = True
    return fn

# use it in critical methods
class AnalysisEngine:
    @root_function
    def detect_anomaly(self, data):
        """Detects anomalies across networked feedback loops."""
        # existing code here