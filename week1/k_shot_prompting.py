import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = ""

USER_PROMPT = """
Convert the following word. Only output the word, no other text:

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

EXPECTED_OUTPUT = "edocsutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            temperature=0.5,
        )
        output_text = completion.choices[0].message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            # print the expected output and the actual output generated
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)