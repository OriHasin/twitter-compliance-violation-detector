from openai import AsyncOpenAI
import json
from config import OPENAI_API_KEY




# Initialize client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def check_tweet_compliance(tweet: str, policy_rules: list):
    try:
        rules_text = "\n".join(policy_rules)
        

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
            "posted_at": "Timestamp of the tweet"
            }
            """
        }

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_message, user_message, assistant_message]
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"error": "Invalid response format"}
        
    except Exception as e:
            return {"error": f"OPENAI API error: {str(e)}"}
