from fastapi import FastAPI, Depends, Request, Form
from sqlalchemy.orm import Session
from model import ReviewTable, UserTable, StoreTable, MenuTable
from db import session
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
import uvicorn

review_write = FastAPI()

review_write.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

review_write.add_middleware(SessionMiddleware, secret_key="your-secret-key")

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

#로그인 상태 확인, 로그인 중인 유저 아이디 반환
@review_write.get("/check_login/")
async def check_login(request: Request):
    # 세션에서 사용자 정보 확인
    if "user_id" not in request.session:
        return False
    
    return {"user_id": f"{request.session['user_id']}"}

#가게 아이디로 가게의 모든 메뉴 아이디들을 반환
@review_write.get("/menu_ids/{store_id}")
async def get_menu_ids(store_id: int, db: Session = Depends(get_db)):
    menu_ids = db.query(MenuTable.menu_id).filter(MenuTable.store_id == store_id).all()
    
    return {"menu_ids": [menu_id[0] for menu_id in menu_ids]}

#작성한 리뷰를 데이터베이스에 저장
@review_write.post("/write_review/")
async def create_review(
    user_id: str,
    menu_id: int,
    store_id: int,
    rating: float = Form(...),
    content: str = Form(...),
    photo_url: str = Form(...),
    title: str = Form(...),
    db: Session = Depends(get_db)
):
    new_review = ReviewTable(
            user_id=user_id,
            menu_id=menu_id,
            store_id=store_id,
            rating=rating,
            content=content,
            photo_url=photo_url,
            title=title,
        )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return {"review_id": new_review.review_id}

if __name__ == "__rewiew_write__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)