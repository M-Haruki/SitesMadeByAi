from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

import ai
import db
import secrets
import string

app = FastAPI()

templates = Jinja2Templates(directory="templates")


def create_session_id():
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(8))


def parse_html_content(content: str) -> str:
    start = content.find("<!DOCTYPE html>")
    end = content.find("</html>")
    if start != -1 and end != -1:
        html = content[start : end + len("</html>")]
        return html


@app.post("/agree", response_class=JSONResponse)
async def agree():
    # 同意の処理をここに追加
    session_id = create_session_id()
    db.create_session(session_id)
    response = JSONResponse({})
    response.set_cookie(
        key="session",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="Lax",
        expires=60 * 60 * 24 * 30,  # 1ヶ月有効
    )
    return response


@app.get("/init", response_class=HTMLResponse)
def initial(request: Request):
    # 初回アクセスの画面を表示
    return templates.TemplateResponse("initial.html", {"request": request})


@app.get("/favicon.ico")
def favicon():
    # ファビコンのリクエストに対する応答
    return HTMLResponse(content="", status_code=404)


@app.get("/{path:path}", response_class=HTMLResponse)
async def root(request: Request, path: str = ""):
    if "session" in request.cookies:
        session_id = request.cookies["session"]
        if db.check_session(session_id):
            db.increment_session_count(session_id)
            # ヘッダーを辞書形式で取得
            user_data = {
                "path": path,
                "refer": request.headers.get("referer", ""),
                "query": request.query_params._dict,
            }
            res = await ai.send(str(user_data), session_id=session_id)
            content = parse_html_content(res["content"])
            return HTMLResponse(content=content, status_code=200)
        else:
            # セッションが無効または利用回数超過
            return templates.TemplateResponse("error.html", {"request": request})
    else:
        # 初回アクセス
        return templates.TemplateResponse("initial.html", {"request": request})
