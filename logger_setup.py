import logging

# =============================================================================
# LLM USAGE LOGGER SETUP
# =============================================================================
llm_logger = logging.getLogger('LLMUsage')
llm_logger.setLevel(logging.INFO)
llm_handler = logging.FileHandler('llm_usage.log', encoding='utf-8')
llm_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
if not llm_logger.hasHandlers():
    llm_logger.addHandler(llm_handler)
