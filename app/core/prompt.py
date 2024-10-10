
def get_prompt():
    PROMPT_TEMPLATE = """
You are an expert AI assistant specializing in analyzing documents for specific companies based on semantic similarity search results.
Instructions:

1. Analyze the document name and source link to determine the company and document relevance. Then, tell is the document valid or invalid for the specified company.
2. If you are unsure, you may use the relavent context to make a decision.
3. Respond with ONLY "YES" for a valid document or "NO" for an invalid document for that company in Capital Letters.
4. Provide no explanation or additional context.

Here is the information for your analysis:

The Document Name is: {pdf_name}
The Source Link is: {pdf_link}
Relavent Context: {context}
______

Query: {query}

Note: High similarity scores alone do not guarantee relevance. Consider content and context carefully. YOUR RESPONSE BOUND TO EITHER YES OR NO. OTHER ANY RESPONSE WILL BE CONSIDERED AS INVALID.
"""
    return PROMPT_TEMPLATE


def get_prompt_for_snippet():
    PROMPT_TEMPLATE = """
You are an expert AI assistant specializing in analyzing documents for specific companies based on given snippets.
Instructions:

1. Analyze the document name, source link, and snippet to determine the company and document relevance. Then, tell is the document valid or invalid for the specified company.
2. Respond with ONLY "YES" for a valid document or "NO" for an invalid document for that company in Capital Letters.
3. Provide no explanation or additional context.

Here is the information for your analysis:

The Document Name is: {pdf_name}
The Source Link is: {pdf_link}
The Snippet is: {snippet}
______

Query: {query}

Note: High similarity scores alone do not guarantee relevance. Consider content and context carefully. YOUR RESPONSE BOUND TO EITHER YES OR NO. OTHER ANY RESPONSE WILL BE CONSIDERED AS INVALID.
"""
    return PROMPT_TEMPLATE