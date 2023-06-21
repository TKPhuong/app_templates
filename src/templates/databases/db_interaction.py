from sqlalchemy import create_engine, MetaData, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine.url import URL
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from typing import Type, Optional

Base = declarative_base()

class DBHandler:
    """
    データベース操作を抽象化するためのハンドラークラス。
    SQLAlchemy ORMを用いて、データベースとのセッション管理、トランザクション処理、
    データの挿入と選択など基本的なDB操作昨日を高レベルAPIで提供する。

    Attributes
    ----------
    engine : sqlalchemy.engine.Engine
        SQLAlchemyを使用したデータベースエンジン。
    Session : sqlalchemy.orm.session.sessionmaker
        データベースセッションを作成するためのsessionmakerインスタンス。
    """

    def __init__(self, database_uri: str):
        """
        Parameters
        ----------
        database_uri : str
            データベースへの接続URI。
        """

        # データベースエンジンの作成
        self.engine = create_engine(database_uri)
        self.Session = sessionmaker(bind=self.engine)
        
    @contextmanager
    def get_session(self) -> Session:
        """
        新しいデータベースセッションを開始し、そのコンテキストを提供する。

        Yields
        ------
        Session
            新しいデータベースセッション。
        """
                
        # トランザクションの開始
        session = self.Session()
        try:
            yield session
            # トランザクションのコミット
            session.commit()
        except Exception as e:
            # エラーが起きた場合、ロールバックする
            session.rollback()
            raise e
        finally:
            # セッションを閉じる
            session.close()
            
    @contextmanager
    def custom_transaction(self):
        """
        ネストされたトランザクションのコンテキストを提供する。

        Yields
        ------
        Session
            ネストされたトランザクションのセッション。
        """

        with self.get_session() as session:
            # ネストされたトランザクションの開始
            session.begin_nested()
            try:
                yield session
                # トランザクションのコミット
                session.commit()
            except Exception as e:
                # エラーが起きた場合、ロールバックする
                session.rollback()
                raise e
    
    def add_model(self, model: Type[Base]):
        """
        モデルに対応するテーブルをデータベースに追加する。

        Parameters
        ----------
        model : Type[Base]
            データベースに追加するモデルの型。
        """

        # モデルに対応するテーブルをデータベースに追加する
        model.metadata.create_all(self.engine)

    # def delete_model(self, model: Type[Base]):
    #     # モデルに対応するテーブルをデータベースから削除する
    #     if model.__table__.exists(self.engine):
    #         model.__table__.drop(self.engine)

    def insert(self, instance: Base, session: Optional[Session] = None):
        """
        インスタンスをデータベースに追加する。

        Parameters
        ----------
        instance : Base
            データベースに追加するインスタンス。
        session : Optional[Session], optional
            追加操作を実行するセッション。指定しない場合、新しいセッションが開始されます。
        """

        # インスタンスをデータベースに追加する
        if session is None:
            with self.get_session() as session:
                session.add(instance)
        else:
            session.add(instance)
            
    def insert_many(self, instances: list[Base], session: Optional[Session] = None):
        """
        複数のインスタンスをデータベースに追加する。

        Parameters
        ----------
        instances : list[Base]
            データベースに追加するインスタンスのリスト。
        session : Optional[Session], optional
            追加操作を実行するセッション。指定しない場合、新しいセッションが開始されます。
        """
                
        # 複数のインスタンスをデータベースに追加する
        if session is None:
            with self.get_session() as session:
                session.add_all(instances)
        else:
            session.add_all(instances)
            
    def select(self, model: Type[Base], conditions=None, order_by=None, limit=None, session: Optional[Session] = None):
        """
        データベースからインスタンスを選択する。

        Parameters
        ----------
        model : Type[Base]
            選択するインスタンスのモデルの型。
        conditions : optional
            選択するインスタンスに適用する条件。
        order_by : optional
            結果を並べ替えるための順序。
        limit : optional
            取得するインスタンスの最大数。
        session : Optional[Session], optional
            選択操作を実行するセッション。指定しない場合、新しいセッションが開始されます。

        Returns
        -------
        list
            選択されたインスタンスのリスト。
        """

        # データベースからインスタンスを選択する
        if session is None:
            with self.get_session() as session:
                results = self._select(session, model, conditions, order_by, limit)
                # Load all attributes eagerly
                session.expunge_all()  # remove objects from session
                session.close()  # close session
                return results
        else:
            return self._select(session, model, conditions, order_by, limit)

    @staticmethod
    def _select(session: Session, model: Type[Base], conditions, order_by, limit):
        query = session.query(model)
        if conditions is not None:
            query = query.filter(conditions)
        if order_by is not None:
            query = query.order_by(order_by)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def update(self, model: Type[Base], conditions, update_values, session: Optional[Session] = None):
        """
        データベースのインスタンスを更新する。

        Parameters
        ----------
        model : Type[Base]
            更新するインスタンスのモデルの型。
        conditions :
            更新するインスタンスをフィルタするための条件。
        update_values :
            更新する値。
        session : Optional[Session], optional
            更新操作を実行するセッション。指定しない場合、新しいセッションが開始されます。
        """

        # データベースのインスタンスを更新する
        if session is None:
            with self.get_session() as session:
                session.query(model).filter(conditions).update(update_values)
        else:
            session.query(model).filter(conditions).update(update_values)

    def delete(self, model: Type[Base], conditions, session: Optional[Session] = None):
        """
        データベースのインスタンスを削除する。

        Parameters
        ----------
        model : Type[Base]
            削除するインスタンスのモデルの型。
        conditions :
            削除するインスタンスをフィルタするための条件。
        session : Optional[Session], optional
            削除操作を実行するセッション。指定しない場合、新しいセッションが開始されます。
        """

        # データベースのインスタンスを削除する
        if session is None:
            with self.get_session() as session:
                session.query(model).filter(conditions).delete()
        else:
            session.query(model).filter(conditions).delete()



if __name__ == "__main__":
    from sqlalchemy import Column, Integer, String

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String)

    # データベースへの接続
    db = DBHandler('sqlite:///test.db')

    # モデルを追加
    db.add_model(User)
    print("テーブル 'users' をデータベースに追加しました。")

    # ユーザの作成
    alice = User(name="Alice")
    bob = User(name="Bob")
    charlie = User(name="Charlie")

    # 単一のユーザを挿入
    db.insert(alice)
    print("Aliceを追加しました")

    # ユーザを選択
    users = db.select(User)
    print("ユーザを選択しました:")
    for user in users:
        print(user.name)

    # 複数のユーザを挿入
    db.insert_many([bob, charlie])
    print("BobとCharlieを追加しました")

    # ユーザを選択
    users = db.select(User)
    print("ユーザを選択しました:")
    for user in users:
        print(user.name)

    # ユーザの名前を更新
    db.update(User, User.name == "Alice", {"name": "Alicia"})
    print("Aliceの名前をAliciaに更新しました")

    # 更新されたユーザを選択
    updated_users = db.select(User, User.name == "Alicia")
    print("更新されたユーザを選択しました:")
    for user in updated_users:
        print(user.name)

    # ユーザを削除
    db.delete(User, User.name == "Alicia")
    print("Aliciaを削除しました")

    # 削除後のユーザを選択
    deleted_users = db.select(User)
    print("削除後のユーザを選択しました:")
    for user in deleted_users:
        print(user.name)

    # カスタムトランザクションの中で操作を行う
    with db.custom_transaction() as session:
        db.insert(User(name="Daniel"), session)
        db.insert(User(name="Eve"), session)
        db.insert(User(name="Frank"), session)
    print("トランザクション内でDaniel、Eve、Frankを追加しました")

    # トランザクション後のユーザを選択
    transaction_users = db.select(User)
    print("トランザクション後のユーザを選択しました:")
    for user in transaction_users:
        print(user.name)






