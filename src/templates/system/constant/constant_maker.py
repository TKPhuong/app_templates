class ConstantMaker(type):
    """
    定数を定義するためのメタクラスです。
    クラスの属性に定数を定義することができます。
    定義された定数は "." または辞書のようなプロトコルでアクセスできます。
    """
    def __new__(cls, name, bases, dct):
        """
        定数を収集して __constants__ 属性に格納します。
        """
        constants = {}
        for key, value in dct.items():
            if not key.startswith("__") and not callable(value):
                constants[key] = value
        dct["__constants__"] = constants
        return super(ConstantMaker, cls).__new__(cls, name, bases, dct)

    def __getattr__(cls, name):
        """
        "." プロトコルで定数にアクセスするためのメソッドです。
        """
        if name in cls.__constants__:
            return cls.__constants__[name]
        else:
            raise AttributeError(f"{cls.__name__}には '{name}' という名前の定数がありません")

    def __getitem__(cls, name):
        """
        辞書のようなプロトコルで定数にアクセスするためのメソッドです。
        """
        if name in cls.__constants__:
            return cls.__constants__[name]
        else:
            raise KeyError(f"{cls.__name__}には '{name}' という名前の定数がありません")

    def __setitem__(cls, name, value):
        """
        辞書のようなプロトコルで定数に値を代入しようとするとTypeErrorが発生するようにします。
        """
        if name in cls.__constants__:
            err_msg = f"{cls.__name__}の'{name}'は定数であり、変更できません"
        else:
            err_msg = f"{cls.__name__}は定数のクラスであり、値の導入をサポートしません"
        raise TypeError(err_msg)

    def __iter__(cls):
        """
        定数をイテレーションするためのメソッドです。
        """
        return iter(cls.__constants__)

    def __setattr__(cls, name, value):
        """
        定数に値を代入しようとするとTypeErrorが発生するようにします。
        """
        cls[name] = value

    def items(cls):
        """
        定数の (名前, 値) のペアを返すメソッドです。
        """
        return cls.__constants__.items()

    def values(cls):
        """
        定数の値のリストを返すメソッドです。
        """
        return cls.__constants__.values()

if __name__ == "__main__":
    class States(metaclass=ConstantMaker):
        """
        システムの状態を表す定数を定義するクラスです。
        """
        idle = "IDLE"
        process = "PROCESSING"
        shutdown = "OFF"

    # 定数の値を取得する例
    print(States.idle)  # "IDLE"
    print(States.process)  # "PROCESSING"
    print(States.shutdown)  # "OFF"

    # 値を導入するとエラーが発生する
    try:
        States.idle = "ABC"
    except TypeError as e:
        print(f"エラーが発生しました. err:{e}")

    # 定数を辞書のようにアクセスする例
    print(States["idle"])  # "IDLE"
    print(States["process"])  # "PROCESSING"
    print(States["shutdown"])  # "OFF"

    # 定数をイテレーションする例
    for state in States:
        print(state)  # "idle", "process", "shutdown"

    # 定数の (名前, 値) のペアを取得する例
    print(States.items())  # dict_items([('idle', 'IDLE'), ('process', 'PROCESSING'), ('shutdown', 'OFF')])

    # 定数の値のリストを取得する例
    print(States.values())  # dict_values(['IDLE', 'PROCESSING', 'OFF'])


    class ErrorCode(metaclass=ConstantMaker):
        """
        エラーコードを表す定数を定義するクラスです。
        """
        NOT_FOUND = "E001"
        PERMISSION_DENIED = "E002"
        INTERNAL_ERROR = "E003"

    # 定数の値を取得する例
    print(ErrorCode.NOT_FOUND)  # "E001"
    print(ErrorCode.PERMISSION_DENIED)  # "E002"
    print(ErrorCode.INTERNAL_ERROR)  # "E003"

    # 定数を辞書のようにアクセスする例
    print(ErrorCode["NOT_FOUND"])  # "E001"
    print(ErrorCode["PERMISSION_DENIED"])  # "E002"
    print(ErrorCode["INTERNAL_ERROR"])  # "E003"

    # 値を導入するとエラーが発生する
    try:
        ErrorCode["NOT_FOUND"] = "ABC"
    except TypeError as e:
        print(f"エラーが発生しました. err:{e}")

    # 定数をイテレーションする例
    for code in ErrorCode:
        print(code)  # "NOT_FOUND", "PERMISSION_DENIED", "INTERNAL_ERROR"

    # 定数の (名前, 値) のペアを取得する例
    print(ErrorCode.items())  # dict_items([('NOT_FOUND', 'E001'), ('PERMISSION_DENIED', 'E002'), ('INTERNAL_ERROR', 'E003')])

    # 定数の値のリストを取得する例
    print(ErrorCode.values())  # dict_values(['E001', 'E002', 'E003'])
