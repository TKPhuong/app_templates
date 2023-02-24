import os

def check_file(f_name, dir_name, error_code):
    """指定されたディレクトリに指定されたファイルが存在するかどうかをチェックする。
    
    Args:
        f_name (str): チェックするファイル名。
        dir_name (str): ファイルを検索するディレクトリ名。
        error_code (int): ファイルが存在しなかった場合に発生させるエラーコード。
        
    Returns:
        bool: ファイルがディレクトリに存在する場合はTrue、それ以外はFalseを返す。
    """
    file_path = os.path.join(dir_name, f_name)
    
    if os.path.isfile(file_path):
        return True
    else:
        error_message = f"ファイル '{f_name}' がディレクトリ '{dir_name}' に見つかりませんでした。エラーコード: {error_code}"
        raise FileNotFoundError(error_message)
    