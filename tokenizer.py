"""輸入前處理：切分 token，再區分減法與一元負號。

數字使用 float；名稱、括號及運算子使用字串；一元負號使用 'NEG'。
本模組不計算結果，完整語法檢查交給 evaluator。
直接執行本檔可逐行查看前處理結果。
"""


def tokenize(expression):
    """從左至右掃描字串，回傳 token 串列，時間及空間為 O(n)。

    支援十進位整數與小數，尚未支援科學記號。
    遇到無效數字或未知字元時拋出 ValueError，位置以 1 起算。
    """
    tokens = []
    index = 0

    while index < len(expression):
        character = expression[index]

        if character.isspace():
            # 空白只用來分隔內容，不需要存入 token 串列。
            index += 1
            continue

        # 一次讀完整個數字，支援 12、3.14、.5 與 5.。
        if character in "0123456789.":
            start = index
            while index < len(expression) and expression[index] in "0123456789.":
                index += 1
            number = expression[start:index]
            # 單獨的小數點及多個小數點都不是合法數字。
            if number == "." or number.count(".") > 1:
                raise ValueError(f"第 {start + 1} 個字元：無效數字 {number!r}")
            tokens.append(float(number))
            continue

        # 名稱以小寫字母開頭，可包含數字，例如 log10。
        if "a" <= character <= "z":
            start = index
            while index < len(expression) and (
                "a" <= expression[index] <= "z" or expression[index] in "0123456789"
            ):
                index += 1
            tokens.append(expression[start:index])
            continue

        if character in "+-*/()=^":
            tokens.append(character)
            index += 1
            continue

        raise ValueError(f"第 {index + 1} 個字元：不支援的字元 {character!r}")

    return tokens


def classify_minus(tokens):
    """回傳新串列，將一元負號標記為 NEG，不修改原始 tokens。

    expect_operand 表示下一個位置需要運算元；此時遇到 '-' 就是負號。
    例如 2--3 會轉成 [2.0, '-', 'NEG', 3.0]。
    本函式僅分類符號，不檢查完整語法，時間及額外空間皆為 O(n)。
    """
    result = []
    expect_operand = True

    for token in tokens:
        if token == "-" and expect_operand:
            result.append("NEG")
            # 負號後仍需要運算元，因此連續負號也可以逐一辨識。
            continue

        result.append(token)
        if token in ("+", "-", "*", "/", "^", "(", "="):
            # 運算子、左括號或等號後，需要新的運算元。
            expect_operand = True
        else:
            # 數字、名稱與右括號後的減號屬於二元減法。
            expect_operand = False

    return result


def main():
    """逐行讀取直到 EOF；單行錯誤不影響下一行。"""
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            continue
        try:
            tokens = tokenize(line)
            print(classify_minus(tokens))
        except ValueError as error:
            print(f"錯誤：{error}")


if __name__ == "__main__":
    # 被其他模組 import 時不會啟動輸入迴圈。
    main()
