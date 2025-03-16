from openai import AsyncOpenAI
import json
from app.core.config import OPENAI_API_KEY
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type



# Initialize client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

@retry(
      stop=stop_after_attempt(3),                                       # Stop after 3 failed attempts
      wait=wait_exponential(multiplier=1, min=2, max=60),               # Wait 2s, then 4s, then 8s...
      retry=retry_if_exception_type((ConnectionError, TimeoutError))    # Only retry these errors
)
async def check_tweet_compliance(tweet: str, policy_rules: list):
    # Format each rule dictionary into a string
    rule_strings = []
    for rule in policy_rules:
        if isinstance(rule, dict):
            # Format: [RULE-ID] CATEGORY: Description
            rule_str = f"[{rule.get('rule_id', 'N/A')}] {rule.get('category', 'N/A')}: {rule.get('description', 'N/A')}"
            rule_strings.append(rule_str)
        else:
            # If it's already a string, use it as is
            rule_strings.append(str(rule))

    # Join the formatted rules with newlines
    rules_text = "\n".join(rule_strings)
    

    system_message = {
        "role": "system",
        "content": "You are an AI compliance officer. Analyze tweets based on compliance policies."
    }
    

    user_message = {
        "role": "user",
        "content": f"""
        Analyze the following tweet based on these compliance policies:
        {rules_text}

        Tweet: "{tweet}"
        """
    }
    

    assistant_message = {
        "role": "assistant",
        "content": """
        Respond in JSON format:
        {
        "violation": "YES" or "NO",
        "tweet": "Tweet text",
        "policy": "Policy name just if violation is YES",
        "rule_id": "Rule ID just if violation is YES",
        "rule_violated": "Rule description just if violation is YES",
        "reason": "Explain why just if violation is YES",
        }
        """
    }

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[system_message, user_message, assistant_message]
    )

    try:    
        return json.loads(response.choices[0].message.content.replace("```json", "").replace("```", ""))
    except json.JSONDecodeError as json_err:
        print(f"❌ JSON parsing error: {json_err}")
        return {"error": "Invalid response format"}