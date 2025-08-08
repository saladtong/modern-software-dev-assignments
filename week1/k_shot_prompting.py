import os
from dotenv import load_dotenv
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

STARTER_SYSTEM_PROMPT = """
You are a helpful assistant that converts words from reverses the order of letters in a word.
"""

USER_PROMPT = """
Convert the following word:

httpstatuscode
"""

COMPLETED_SYSTEM_PROMPT = """
You are a helpful assistant that converts words from reverses the order of letters in a word.

<examples>
Input: HTTP
Output: PTTH

Input: orderme
Output: emredro

Input: httpstatus
Output: sutatsptth

Input: makeathing
Output: gnihtaekam

Input: finallyifoundyou
Output: uoydnuofiyllanif

Input: elephant 
Output: tnahpele

Input: computer 
Output: retupmoc

Input: chocolate 
Output: etalocohc
<examples>
"""

EXPECTED_OUTPUT = """
edocsutatsptth
"""

if __name__ == "__main__":
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "developer", "content": STARTER_SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT}
        ]
    )
    print(completion.choices[0].message.content)