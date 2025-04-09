from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ローカルのSQLファイルに接続するための設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

#　エンジンの作成：実際にデータベースと通信を行うためのもの
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# DBとやり取りするためのセッションクラスを作っている：個別の接続インスタンスを作れる
# FastAPIではDependsを使って、リクエストごとにセッションを作成することができる
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()