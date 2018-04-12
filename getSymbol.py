import pandas as pd
import sys

df = pd.read_csv('./code.csv')
codes = df['code']

def form(data):
    parts = data.split('.')
    parts.reverse()
    together = parts[0] + parts[1]
    return together

def get_symbols():
    code_ls=[]
    for i in codes:
        code_ls.append(i)

    output = []
    for i in range(len(code_ls)):
        if code_ls[i][-2]=='S':#只找出倒数第二个字符为'S'的股票代码
            output.append(form(code_ls[i]))
    
    return output