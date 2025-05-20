import logging
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities.serpapi import SerpAPIWrapper

from template_prompt import grammar

logger = logging.getLogger(__name__)

class FactChecker:
    """
    Проверяет текст в два шага:
      1) Корректировка грамматики и стиля через LLM.
      2) (Stub) Фактическая проверка через SerpAPI.
    """

    def __init__(
        self,
        openai_api_key: str,
        serpapi_api_key: str,
        model_name: str = "gpt-4o"
    ):
        """
        :param openai_api_key: API-ключ OpenAI
        :param serpapi_api_key: API-ключ SerpAPI
        :param model_name: модель для LLM (грамматика)
        """
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model_name=model_name,
            temperature=0
        )
        grammar_prompt = PromptTemplate(
            input_variables=["text"],
            template=grammar
        )
        self.grammar_chain = LLMChain(llm=self.llm, prompt=grammar_prompt)

        self.serp = SerpAPIWrapper(serpapi_api_key=serpapi_api_key)

    def run(self, text: str) -> str:
        """
        Выполняет проверку текста:
          1) Грамматика
          2) Факты (заглушка)
        :param text: исходный текст
        :return: исправленный текст
        """
        try:
            corrected = self.grammar_chain.run({"text": text})
            text = corrected.strip()
            logger.info("Grammar corrected via LLM.")
        except Exception as e:
            logger.error("Error during LLM grammar correction: %s", e)

        try:
            facts = self.serp.run(text)
            logger.debug("SerpAPI stub results: %s", facts)
        except Exception as e:
            logger.warning("Error during SerpAPI stub: %s", e)

        return text