
import lib

def main() -> None:
    """選擇頁面
    """
    lib.create_table()
    while True:
        print()
        print(f"{'-' * 5} 電影管理系統 {'-' * 5}")
        print('1. 匯入電影資料檔')
        print('2. 查詢電影')
        print('3. 新增電影')
        print('4. 修改電影')
        print('5. 刪除電影')
        print('6. 匯出電影')
        print('7. 離開系統')
        print(f"{'-' * 24}")
        select = int(input('請選擇操作選項 (1-7): '))
        if select == 1:
            lib.import_movies()
        elif select == 2:
            lib.search_movie()
        elif select == 3:
            lib.add_movie()
        elif select == 4:
            lib.modify_movies()
        elif select == 5:
            lib.delete_movies()
        elif select == 6:
            lib.export_movies()
        else:
            print('系統已退出。')
            exit()
            
if __name__ == "__main__":
    main()
    