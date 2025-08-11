import openai
import asyncio
import db
import secrets
import string

# LM Studioのエンドポイント例
LMSTUDIO_API_URL = "http://localhost:1234/v1/"  # ポートやパスは環境に合わせて変更


def create_random_string() -> str:
    """指定された長さのランダムな文字列を生成する関数"""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(8))


"""
あなたはWebサイト生成専用アシスタントです。
ユーザーから与えられる情報をもとに、適切なWebページを作成してください。

出力は **純粋なHTMLドキュメントのみ** とします。以下を厳守してください：
- 完成されたきれいなWebサイトをHTMLで作成すること。
- <!DOCTYPE html> で開始し、</html> で終了する完全なHTMLを返すこと。
- HTML文書内に <style> や <script> を含んでもよい。
- 自サイトの他ページへのリンクは /other-page のように絶対パス形式で記載すること。
- なるべく自サイトの他ページへのリンクを含めること。
"""


async def send(new_message: str, session_id: str = None):
    histories = list(db.get_history(session_id))
    if histories is None:
        histories = []
    if len(histories) == 0:
        init_message = {
            "role": "system",
            "content": """
                You are an assistant dedicated to generating websites.
                Based on the information provided by the user, create an appropriate web page.

                Your output must be **a pure HTML document only**. Follow these rules strictly:

                * Create a complete, well-designed website in HTML.
                * The HTML must start with `<!DOCTYPE html>` and end with `</html>`.
                * You may include `<style>` and `<script>` tags inside the HTML document.
                * Links to other pages within the same site should be written in absolute path format, such as `/other-page`.
                * Try to include links to other pages within the same site as much as possible.
                """,
        }
        histories.append(init_message)
        db.register_history(
            role=init_message["role"],
            content=init_message["content"],
            session_id=session_id,
        )
    histories.append({"role": "user", "content": new_message})
    db.register_history(
        role="user",
        content=new_message,
        session_id=session_id,
    )
    request = {
        "model": "google/gemma-3-4b",
        "messages": histories,
        "max_tokens": 1000,
        "temperature": 0.7,
        "top_p": 1.0,
        "n": 1,
        "stream": False,
    }
    client = openai.AsyncOpenAI(
        base_url=LMSTUDIO_API_URL,  # ← base_url → api_base
        api_key="lm-studio-api-key",  # LM StudioはAPIキー不要な場合もあり
    )
    response = await client.chat.completions.create(**request)
    res = {
        "content": response.choices[0].message.content,
        "role": response.choices[0].message.role,
    }
    db.register_history(
        role=res["role"],
        content=res["content"],
        session_id=session_id,
    )
    return res


if __name__ == "__main__":
    # テスト用のデータ
    test_data = """{
        "path": "learn/python",
        "headers": {
            "User-Agent": "test-agent",
            "Referer": "http://example.com",
        },
    }"""
    # chat関数を呼び出して結果を取得
    result = asyncio.run(send(test_data, []))
    print("Result:", result)
