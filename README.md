# 使用方式

**建立字型庫**
1. 進入cvt資料夾，編輯cvt_main.py
2. 修改main裡面的src_dir，此為要掃描文字的資料夾，資料夾內所有c/cc/cpp/h/hpp的文字都會納入字庫
3. 修改main裡面的font_path，此為字型檔的路徑；cvt資料夾已經有內附一個免費的google字型。
4. 修改main裡面的font_size，此為字型的大小
5. 執行"python3 cvt_main.py"，cvt資料夾會出現"font_lib.bin"字庫檔

**測試字型庫**
1. 進入cvt資料夾
2. 執行"python3 cvt_exam.py"，會自動讀取"font_lib.bin"並把所有文字顯示一遍

**補充說明**
此字型庫是給little-endian MCU使用，esp32/arm都屬於此類，如需要big-endian請自行修改struct指令