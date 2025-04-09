from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from models import User
from database import SessionLocal, engine, Base
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
# => middlewareは、フロントとバックが別々のportで動いているときに、CORSのエラーを回避するために必要なもので、どちらも受け入れることができる

app = FastAPI()


oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")

origins = [
    "https://localhost:3000",  # もし、フロントで別のportが立った時に、こっちん3000を使うようにする
    "http://your-frontend-domain.com",
]

# 様々なタイプのリクエストを受け入れるための設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # どのオリジンを許可するか
    allow_credentials=True,
    allow_methods=["*"],  # どのメソッドを許可するか
    allow_headers=["*"],  # どのヘッダーを許可するか
)

# SessionLocalを呼び出して、セッションを作り、使ったら自動で閉じてくれる
def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

# ハッシュ化するための設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your_secret_key"  # 環境変数にすることをお勧めします
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # トークンの有効期限を30分に設定


class UserCreate(BaseModel):
    username: str
    password: str

# usernameを元にDBからユーザーを取得する関数
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# passwordをhash化して、DBに追加する関数
def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)  # パスワードをハッシュ化
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    return "complete"

# フロントから、usernameとpassword(UserCreate)を受け取り、そのユーザがもともといた場合とそうでないときの処理を分ける
# もし、もともといなかったら、create_userを呼び出して、DBに追加する
@app.post("/register")
# Depends：このエンドポイントが実行されるときに、get_db() を呼び出して、その戻り値（DBセッション）を db に自動で渡してね！
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)

# ハッシュの値と照合する
def authenticate_user(username: str, password: str, db: Session):
    user = get_user_by_username(db, username=username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

# JWTトークンを発行している（ここでどのくらいの期間一時保存できるかを定義している）
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(datetime.UTC()) + expires_delta
    else:
        expire = datetime.now(datetime.UTC()) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# トークンの検証
def verify_token(token: str = Depends(oauth2_schema)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # {"sub": user.username}が入ったデータを返している
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/verify_token/{token}")
async def verify_user_token(token: str):
    create_access_token(token = token)
    return {"message": "Token is valid"}

