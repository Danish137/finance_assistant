from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Language Agent - Narrative Synthesis")

class EarningsSurprise(BaseModel):
    company: str
    type: str
    percentage: float

class AnalysisOutput(BaseModel):
    asia_tech_allocation: float
    allocation_change: float
    earnings_surprises: List[EarningsSurprise]
    regional_sentiment: str

@app.post("/generate_brief")
def generate_brief(analysis_output: AnalysisOutput):
    brief = f"Today, your Asia tech allocation is {analysis_output.asia_tech_allocation:.0f} % of AUM, "
    
    if analysis_output.allocation_change > 0:
        brief += f"up from {analysis_output.asia_tech_allocation - analysis_output.allocation_change:.0f} % yesterday. "
    elif analysis_output.allocation_change < 0:
        brief += f"down from {analysis_output.asia_tech_allocation - analysis_output.allocation_change:.0f} % yesterday. "
    else:
        brief += "unchanged from yesterday. "

    earnings_str = []
    for surprise in analysis_output.earnings_surprises:
        earnings_str.append(f"{surprise.company} {surprise.type} estimates by {surprise.percentage:.0f} %")
    
    if earnings_str:
        brief += f"{', '.join(earnings_str)}. "
    
    brief += f"Regional sentiment is {analysis_output.regional_sentiment}"

    # LangChain Integration (example: uncomment and configure for a real LLM)
    # To use a real LLM, ensure you have the LLM provider installed (e.g., `pip install langchain-openai` for OpenAI)
    # or a local LLM setup (e.g., Ollama, ctransformers, Llama.cpp).
    # For open-source local LLMs, you might use:
    # from langchain_community.llms import Ollama
    # llm = Ollama(model="llama2")
    # from langchain_community.llms import CTransformers
    # llm = CTransformers(model='path/to/your/model.gguf', model_type='llama')

    # from langchain_openai import ChatOpenAI # For OpenAI or compatible API
    # from langchain_core.prompts import ChatPromptTemplate
    # from langchain_core.output_parsers import StrOutputParser

    # # Initialize your LLM
    # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7) # Or your chosen local LLM

    # # Define the prompt template
    # prompt_template = ChatPromptTemplate.from_messages([
    #     ("system", "You are a concise financial assistant that creates market briefs."),
    #     ("user", "Based on the following financial analysis, generate a morning market brief:
    #     Allocation: {allocation_info}
    #     Earnings Surprises: {earnings_info}
    #     Sentiment: {sentiment_info}"
    #     )
    # ])

    # # Prepare information for the prompt
    # allocation_info = f"Asia tech allocation is {analysis_output.asia_tech_allocation:.0f}% of AUM, {'up' if analysis_output.allocation_change > 0 else 'down' if analysis_output.allocation_change < 0 else 'unchanged'} by {abs(analysis_output.allocation_change):.0f}% from yesterday."
    # earnings_info_list = [f"{s.company} {s.type} estimates by {s.percentage:.0f}%" for s in analysis_output.earnings_surprises]
    # earnings_info = ", ".join(earnings_info_list) if earnings_info_list else "No significant earnings surprises."
    # sentiment_info = analysis_output.regional_sentiment

    # # Create the LangChain processing chain
    # chain = prompt_template | llm | StrOutputParser()

    # # Invoke the chain to generate the brief
    # # generated_brief = chain.invoke({
    # #     "allocation_info": allocation_info,
    # #     "earnings_info": earnings_info,
    # #     "sentiment_info": sentiment_info
    # # })

    # # For now, return the string formatted brief. Uncomment the above and replace to use LLM.
    return {"brief": brief} 