from openai import OpenAI

def grok_3_mini(api_key:str, prompt_text:str, userid:str, user_logger=None):
    msg = None
    try:
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="grok-3-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a rational and intelligent stock trading trainer."
                },
                {
                    "role": "user",
                    "content": prompt_text
                }
            ],
            max_completion_tokens=20000
        )
        
        msg = response.choices[0].message.content

        total_tokens = response.usage.total_tokens
        prompt_tokens = response.usage.prompt_tokens    
        output_tokens = response.usage.completion_tokens  

        prompt_cost_per_1k = 0.001
        output_cost_per_1k = 0.01

        prompt_cost = prompt_tokens / 1000 * prompt_cost_per_1k
        output_cost = output_tokens / 1000 * output_cost_per_1k
        total_cost = prompt_cost + output_cost

        # 안전하게 f-string 하나로 합쳐서 로그
        if user_logger:
            user_logger.log(f"{userid} API 호출 비용 영수증")
            user_logger.log(f"{userid} 총 처리 토큰 수: {total_tokens}")
            user_logger.log(f"{userid} 입력 토큰: {prompt_tokens}")
            user_logger.log(f"{userid} 출력 토큰: {output_tokens}")  
            user_logger.log(f"{userid} 비용 → 입력: ${prompt_cost:.4f}, 출력: ${output_cost:.4f}, 총: ${total_cost:.4f}")
        else:
            print("user_logger : None")

    except Exception as e:
        print(f"Critical! call api error {e}!")        
        user_logger.log(f"grok_3_mini 생성 실패 : {e}")

    return msg
