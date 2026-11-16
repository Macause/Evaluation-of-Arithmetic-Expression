"""使用兩個自製 Stack 計算數值運算式。

流程：字串 -> tokenize -> classify_minus -> evaluate -> 結果。
支援四則運算、括號、一元負號、次方、實數函數及變數賦值。
直接執行本檔可逐行輸入運算式，直到 EOF。
"""

import math

from stack import Stack
from tokenizer import classify_minus, tokenize


# 數字越大，優先順序越高：-2^2 解讀為 -(2^2)。
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "NEG": 3, "^": 4}

# 三角函數採弧度，log 與 log10 都表示常用對數。
FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "ln": math.log,
    "log": math.log10,
    "log10": math.log10,
    "sqrt": math.sqrt,
}


def apply_function(name, value):
    """檢查實數定義域後計算函數，將錯誤轉成中文訊息。"""
    if name not in FUNCTIONS:
        raise ValueError(f"未知函數：{name}")
    if isinstance(value, complex):
        raise ValueError(f"{name} 目前只支援實數參數")
    if not math.isfinite(value):
        raise ValueError(f"{name} 的參數必須是有限實數")
    if name in ("ln", "log", "log10") and value <= 0:
        raise ValueError("對數的參數必須大於零")
    if name == "sqrt" and value < 0:
        raise ValueError("實數根號的參數不可小於零")
    # 浮點數不能精確表示 π/2；將非常接近奇點的輸入也視為錯誤。
    if name == "tan" and abs(math.cos(value)) < 1e-15:
        raise ValueError("tan 在此角度未定義或太接近奇點")
    return FUNCTIONS[name](value)


def apply_operator(numbers, operators):
    """取出頂端運算子及其運算元，將結果放回 numbers。

    NEG 需要一個值，二元運算子需要兩個值；本函式會修改兩個 Stack。
    """
    operator = operators.pop()
    required = 1 if operator == "NEG" else 2
    if len(numbers) < required:
        raise ValueError("運算子缺少運算元")

    # 後進先出，因此先拿到右運算元；減法與除法不可顛倒順序。
    right = numbers.pop()
    if operator == "NEG":
        numbers.push(-right)
        return

    left = numbers.pop()
    if operator == "+":
        result = left + right
    elif operator == "-":
        result = left - right
    elif operator == "*":
        result = left * right
    elif operator == "/":
        if right == 0:
            raise ValueError("不能除以零")
        result = left / right
    elif operator == "^":
        result = left ** right
        # Python 的負底數分數次方可能產生複數，例如 (-4)^0.5。
        if isinstance(result, complex):
            raise ValueError("次方結果超出實數範圍")
    else:
        raise ValueError(f"不支援的運算子：{operator}")
    numbers.push(result)


def is_variable(token):
    """只接受 a 到 z 的單字母變數名稱。"""
    return isinstance(token, str) and len(token) == 1 and "a" <= token <= "z"


def evaluate(tokens, variables=None):
    """計算已經過 classify_minus 處理的運算式 token。

    variables 提供已定義的變數值，省略時視為空表。求值過程只讀取變數表。

    每個 token 至多入堆疊及出堆疊一次。若將數值運算視為常數成本，
    n 個 token 的時間為 O(n)，額外空間為 O(n)。
    語法錯誤拋出 ValueError；數值運算也可能拋出 ArithmeticError。
    """
    if variables is None:
        variables = {}

    # 數值堆疊存運算元或部分結果，運算子堆疊存尚未執行的運算。
    numbers = Stack()
    operators = Stack()
    # Tokenizer 用這個狀態分類減號，這裡則用它檢查 token 的位置是否合法。
    expect_operand = True

    for index, token in enumerate(tokens):
        if isinstance(token, (int, float)) or is_variable(token):
            if not expect_operand:
                raise ValueError("運算元前缺少運算子")
            if is_variable(token):
                if token not in variables:
                    raise ValueError(f"變數 {token} 尚未定義")
                numbers.push(variables[token])
            else:
                numbers.push(token)
            expect_operand = False
        elif token in FUNCTIONS:
            if not expect_operand:
                raise ValueError("函數前缺少運算子")
            if index + 1 >= len(tokens) or tokens[index + 1] != "(":
                raise ValueError(f"函數 {token} 後必須接括號")
            # 函數名稱留在左括號下方，右括號出現時才計算函數。
            operators.push(token)
        elif token == "(":
            if not expect_operand:
                raise ValueError("左括號前缺少運算子")
            operators.push(token)
        elif token == ")":
            if expect_operand:
                raise ValueError("右括號前缺少運算元")
            # 先完成括號內的運算，左括號只作為邊界，不參與計算。
            while not operators.is_empty() and operators.peek() != "(":
                apply_operator(numbers, operators)
            if operators.is_empty():
                raise ValueError("右括號沒有對應的左括號")
            operators.pop()
            if not operators.is_empty() and operators.peek() in FUNCTIONS:
                name = operators.pop()
                numbers.push(apply_function(name, numbers.pop()))
            expect_operand = False
        elif token == "NEG":
            if not expect_operand:
                raise ValueError("負號前缺少運算子")
            # 前綴負號直接入堆疊，避免 2 ^ -2 提早執行次方。
            operators.push(token)
        elif token in PRECEDENCE:
            if expect_operand:
                raise ValueError("運算子前缺少運算元")
            # 決定舊運算子是否必須先於目前運算子執行。
            while not operators.is_empty() and operators.peek() != "(":
                top = operators.peek()
                # 次方為右結合；其餘二元運算子為左結合。
                if PRECEDENCE[top] < PRECEDENCE[token]:
                    break
                if PRECEDENCE[top] == PRECEDENCE[token] and token == "^":
                    break
                apply_operator(numbers, operators)
            operators.push(token)
            expect_operand = True
        else:
            raise ValueError(f"無法在運算式中使用：{token}")

    if expect_operand:
        raise ValueError("運算式為空或結尾缺少運算元")
    # 輸入讀完後，依堆疊順序完成尚未執行的運算。
    while not operators.is_empty():
        if operators.peek() == "(":
            raise ValueError("左括號沒有對應的右括號")
        apply_operator(numbers, operators)
    return numbers.pop()


def evaluate_expression(expression, variables=None):
    """接收純運算式字串，例如 '2*-3'，回傳計算結果。"""
    tokens = tokenize(expression)
    classified_tokens = classify_minus(tokens)
    return evaluate(classified_tokens, variables)


def evaluate_statement(line, variables):
    """接收一行運算式或賦值，回傳 (變數名稱或 None, 計算結果)。

    賦值成功後才更新傳入的 variables。純運算式回傳的名稱為 None。
    """
    tokens = tokenize(line)
    if "=" not in tokens:
        return None, evaluate(classify_minus(tokens), variables)

    # 賦值必須由單一變數、等號及至少一個右側 token 組成。
    if (
        len(tokens) < 3
        or not is_variable(tokens[0])
        or tokens[1] != "="
        or tokens.count("=") != 1
    ):
        raise ValueError("賦值格式應為單一小寫字母 = 運算式")

    name = tokens[0]
    # 右側可以讀取原值，例如 a = a + 1。計算成功後才更新。
    value = evaluate(classify_minus(tokens[2:]), variables)
    variables[name] = value
    return name, value


def main():
    """逐行讀取並計算，直到 EOF。"""
    variables = {}
    while True:
        try:
            line = input()
        except EOFError:
            # input() 讀到輸入結尾時拋出 EOFError，不需要使用 sys。
            break
        if not line.strip():
            continue
        try:
            name, value = evaluate_statement(line, variables)
            # 去除整數結果尾端的 .0，以符合題目範例的輸出格式。
            output = str(value).removesuffix(".0")
            print(output if name is None else f"{name} = {output}")
        except (ValueError, ArithmeticError) as error:
            # 本行失敗後回到迴圈，下一行仍可繼續計算。
            print(f"錯誤：{error}")


if __name__ == "__main__":
    # 匯入 evaluate_expression 時不會啟動互動輸入。
    main()
