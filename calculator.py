# coding: utf-8

class Message:

    def __init__(self, isOk, value=None, error=''):
        self.isOk = isOk
        self.value = value
        self.error = error


class TokenInfo:
    def __init__(self, tokenType=None, tokenValue=None, tokenEnd=None, isOk=True):
        self.tokenType = tokenType
        self.tokenValue = tokenValue
        self.tokenEnd = tokenEnd
        self.isOk = isOk

    def __str__(self):
        return f"type={self.tokenType}, value={self.tokenValue}, end={self.tokenEnd}, ok={self.isOk}"


def isLatin(c):
    return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z')

def isVariable(v):
    if (len(v) == 0):
        return False
    for c in v:
        if (not isLatin(c)):
            return False
    return True


def getNextToken(s, pos, unary_poss=False):
    while (pos < len(s) and s[pos].isspace()):
        pos += 1
    if (pos == len(s)):
        return TokenInfo(None, None, len(s), True)
    if (s[pos].isdigit() or (unary_poss and s[pos] == '-' and pos + 1 < len(s) and s[pos+1].isdigit())):
        sign = 1
        if (s[pos] == '-'):
            sign = -1
            pos += 1
        value = 0
        while (pos < len(s) and s[pos].isdigit()):
            value = value * 10 + (ord(s[pos]) - ord('0'))
            pos += 1
        if (pos < len(s) and not s[pos].isspace() and s[pos] not in ['+', '-', '*', '/', ')']):
            return TokenInfo(None, None, None, False)
        return TokenInfo("number", sign * value, pos, True)
    if (s[pos] in ['+', '-', '*', '/']):
        return TokenInfo("operation", s[pos], pos + 1, True)
    if (s[pos] in ['(', ')']):
        return TokenInfo("bracket", s[pos], pos + 1, True)
    if (isLatin(s[pos])):
        pos1 = pos
        while (pos1 < len(s) and isLatin(s[pos1])):
            pos1 += 1
        if (pos1 < len(s) and not s[pos1].isspace() and s[pos1] not in ['+', '-', '*', '/', ')']):
            return TokenInfo(None, None, None, False)
        return TokenInfo("variable", s[pos:pos1], pos1, True)
    return TokenInfo(None, None, None, False)


def parseExpression(expr, vars):
    pos = 0
    stack = []
    result = []
    lastToken = None
    while (True):
        token = getNextToken(expr, pos)
        #print(token)
        if (not token.isOk):
            return Message(False, error="Failed to get next token")
        if (token.tokenType == None):
            while (len(stack) > 0):
                if (stack[-1].tokenType == "operation"):
                    result.append(stack[-1])
                    stack.pop(-1)
                else:
                    return Message(False, error="Invalid expression")
            break
        if (token.tokenType == "number"):
            if (not (lastToken == None or lastToken.tokenValue == "(" or lastToken.tokenType == "operation")):
                return Message(False, error="Invalid expression")
            result.append(token)
        elif (token.tokenType == "variable"):
            if (not (lastToken == None or lastToken.tokenValue == "(" or lastToken.tokenType == "operation")):
                return Message(False, error="Invalid expression")
            if (token.tokenValue in vars):
                token.tokenValue = vars[token.tokenValue]
                result.append(token)
            else:
                return Message(False, error="Unknown variable")
        elif (token.tokenType == "operation"):
            if (lastToken == None or lastToken.tokenType == "operation" or lastToken.tokenValue == '('):
                if (token.tokenValue not in ['+', '-']):
                    return Message(False, error="Invalid expression")
                if (lastToken == None or lastToken.tokenValue in ['(', '*', '/']):
                    result.append(TokenInfo("number", 0))
                    stack.append(token)
                else:
                    if (token.tokenValue == '-'):
                        assert len(stack) > 0 and stack[-1].tokenType == "operation" and stack[-1].tokenValue in ['+', '-']
                        if (stack[-1].tokenValue == '+'):
                            stack[-1].tokenValue = '-'
                        elif (stack[-1].tokenValue == '-'):
                            stack[-1].tokenValue = '+'
                        else:
                            raise
            elif (lastToken.tokenType == "number" or lastToken.tokenType == "variable" or lastToken.tokenValue == ')'):
                while (len(stack) > 0 and stack[-1].tokenType == "operation" and not (token.tokenValue in ['*', '/'] and stack[-1].tokenValue in ['+', '-'])):
                    result.append(stack[-1])
                    stack.pop(-1)
                stack.append(token)
            else:
                return Message(False, error="Invalid expression")
        elif (token.tokenValue == '('):
            if (lastToken == None or lastToken.tokenType == "operation" or lastToken.tokenValue == '('):
                stack.append(token)
            else:
                return Message(False, error="Invalid expression")
        elif (token.tokenValue == ')'):
            while (len(stack) > 0 and stack[-1].tokenType == "operation"):
                result.append(stack[-1])
                stack.pop(-1)
            if (len(stack) > 0 and stack[-1].tokenValue == '('):
                stack.pop(-1)
            else:
                return Message(False, error="Invalid expression")
        else:
            assert False

        pos = token.tokenEnd
        lastToken = token

    return calculateExpression(result)


def calculateExpression(result):
    stack = []
    for item in result:
        if (item.tokenType == "number" or item.tokenType == "variable"):
            stack.append(item.tokenValue)
        elif (item.tokenType == "operation"):
            if (len(stack) < 2):
                return Message(False, error="Invalid expression")
            oper2 = stack[-1]
            stack.pop(-1)
            oper1 = stack[-1]
            stack.pop(-1)
            if (item.tokenValue == '/' and oper2 == 0):
                return Message(False, error="Division by zero")
            if (item.tokenValue == '+'):
                stack.append(oper1 + oper2)
            elif (item.tokenValue == '-'):
                stack.append(oper1 - oper2)
            elif (item.tokenValue == '*'):
                stack.append(oper1 * oper2)
            elif (item.tokenValue == '/'):
                stack.append(oper1 // oper2)
            else:
                assert False
        else:
            return Message(False, error="Invalid items")
    if (len(stack) != 1):
        return Message(False, error="Invalid expression")
    else:
        return Message(True, value=stack[0])



def parseLine(line, vars):
    if (line.strip() == ''):
        return
    elif (line.count('=') == 0):
        msg = parseExpression(line, vars)
        if (msg.isOk):
            print(msg.value)
        else:
            print(msg.error)
    elif (line.count('=') == 1):
        pos = line.find('=')
        variable = line[:pos].strip()
        expr = line[pos+1:]
        if (isVariable(variable)):
            msg = parseExpression(expr, vars)
            if (msg.isOk):
                vars[variable] = msg.value
            else:
                print(msg.error)
        else:
            print("Invalid variable name")
    else:
        print("Invalid expression")
        return


vars = {}
while (True):
    line = input()
    if (line.startswith('/')):
        if (line == '/exit'):
            print('Bye!')
            break
        else:
            print('Unknown command')
            continue
    parseLine(line, vars)
