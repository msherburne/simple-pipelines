from simple_pipelines.logging import Logger, LogLevel

### Test 1: Logging Levels ###
def test_logger_levels():
    logs = []
    
    def test_logger(message):
        logs.append(message)

    logger = Logger(publish_function=test_logger, levels=[LogLevel.INFO, LogLevel.ERROR])

    logger.info("This is an info log")
    logger.success("This should not be logged")
    logger.error("This is an error log")

    

    assert len(logs) == 2, "Logger should only log INFO and ERROR messages"
    assert "[INFO] This is an info log" in logs, logs # "Missing INFO log"
    assert "[ERROR] This is an error log" in logs, "Missing ERROR log"
