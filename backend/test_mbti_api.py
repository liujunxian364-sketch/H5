"""
测试 MBTI API 接口
运行: python -m backend.test_mbti_api
"""
import httpx
import json

MBTI_API_URL = "https://rjedu.runjian.com/rptapi/mbti/questions"
MBTI_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk1MDIyNzgsImV4cCI6MTc2OTU0NTQ3OCwidG9QbGF0Zm9ybSI6IjEiLCJ0eXBlIjoiMiIsInVzZXJJZCI6IjE5MTE3MTgyMzE2MjkzMDc5MDQyMzE3MjgifQ.S7x8El59Tq4IXnA5ZSXo"

def test_mbti_api():
    try:
        response = httpx.get(
            MBTI_API_URL,
            params={"token": MBTI_TOKEN},
            timeout=10.0,
            verify=False  # 禁用 SSL 验证
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        print("\n响应内容:")
        
        try:
            data = response.json()
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            # 分析数据结构
            print("\n\n=== 数据结构分析 ===")
            print(f"根键: {list(data.keys())}")
            
            if "result" in data:
                result = data["result"]
                if isinstance(result, list) and len(result) > 0:
                    print(f"\n题目数量: {len(result)}")
                    print(f"\n第一题示例:")
                    print(json.dumps(result[0], ensure_ascii=False, indent=2))
                    
                    if len(result) > 0:
                        first_question = result[0]
                        print(f"\n第一题的键: {list(first_question.keys())}")
        except json.JSONDecodeError:
            print("非 JSON 响应:")
            print(response.text)
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP 错误: {e.response.status_code}")
        print(f"响应内容: {e.response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_mbti_api()

