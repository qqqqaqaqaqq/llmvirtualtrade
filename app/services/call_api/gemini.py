from google import genai   # ✅ 수정

def gemini_2_5_pro(api_key:str, prompt_text:str, userid:str, user_logger=None):
    msg = None
    try:
        client = genai.Client(api_key=api_key)

        config = {
            "max_output_tokens": 20000,
            "temperature": 0.7,
        }

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                {
                    "role": "user",
                    "parts": [{
                        "text": (
                            "You are a rational and intelligent stock trading trainer."
                            f"{prompt_text}"
                        )
                    }]
                }
            ],
            config=config
        )


        msg = response.text

        total_tokens = response.usage_metadata.total_token_count
        prompt_tokens = response.usage_metadata.prompt_token_count       
        output_tokens = response.usage_metadata.thoughts_token_count 
        prompt_cost = prompt_tokens / 1_000_000 * 1.25
        output_cost = output_tokens / 1_000_000 * 10.0
        total_cost = prompt_cost + output_cost

        if user_logger:
            user_logger.log(f"{userid} API 호출 비용 영수증")
            user_logger.log(f"{userid} 총 처리 토큰 수: {total_tokens}")
            user_logger.log(f"{userid} 입력 토큰: {prompt_tokens}, 비용: ${prompt_cost:.4f}")
            user_logger.log(f"{userid} 출력 토큰: {output_tokens}, 비용: ${output_cost:.4f}")
            user_logger.log(f"{userid} 총 비용: ${total_cost:.4f}")
        else:
            print("user_logger : None")

    except Exception as e:
        user_logger.log(f"gemini_2_5_pro 생성실패 {e}")

        return None
        
    return msg


def gemini_3_flash_preview(api_key:str, prompt_text:str, userid=str, user_logger=None):
    msg = None
    try:
        client = genai.Client(api_key=api_key)

        config = {
            "max_output_tokens": 20000,
            "temperature": 0.7,
        }

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                {
                    "role": "user",
                    "parts": [{
                        "text": (
                            "You are a rational and intelligent stock trading trainer."
                            f"{prompt_text}"
                        )
                    }]
                }
            ],
            config=config
        )

        msg = response.text

        total_tokens = response.usage_metadata.total_token_count
        prompt_tokens = response.usage_metadata.prompt_token_count       
        output_tokens = response.usage_metadata.thoughts_token_count 
        prompt_cost = prompt_tokens / 1_000_000 * 0.50
        output_cost = output_tokens / 1_000_000 * 3.00
        total_cost = prompt_cost + output_cost

        if user_logger:
            user_logger.log(f"{userid} API 호출 비용 영수증")
            user_logger.log(f"{userid} 총 처리 토큰 수: {total_tokens}")
            user_logger.log(f"{userid} 입력 토큰: {prompt_tokens}, 비용: ${prompt_cost:.4f}")
            user_logger.log(f"{userid} 출력 토큰: {output_tokens}, 비용: ${output_cost:.4f}")
            user_logger.log(f"{userid} 총 비용: ${total_cost:.4f}")
        else:
            print("user_logger : None")

    except Exception as e:
        print(f"Critical! call api error {e}!")
            
        if user_logger:
            user_logger.log(f"gemini_3_flash_preview 생성실패 {e}")

        return None
    
    return msg
