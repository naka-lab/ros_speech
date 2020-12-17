# encoding: shift_jis
import sys

def levenshtein_distance(a, b):
    m = [ [0] * (len(b) + 1) for i in range(len(a) + 1) ]

    for i in range(len(a) + 1):
        m[i][0] = i

    for j in range(len(b) + 1):
        m[0][j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                x = 0
            else:
                x = 1
            m[i][j] = min(m[i - 1][j] + 1, m[i][ j - 1] + 1, m[i - 1][j - 1] + x)

    # 文字列のマッチングを取る
    x = len(a)
    y = len(b)
    aa = ""
    bb = ""

    # 後ろからコストが最小となる経路を探す
    while x!=0 or y!=0:
        cost = 999999
        cx = ""
        cy = ""
        #
        for i,j,ci,cj in( (x-1,y-1,a[x-1],b[y-1]) , (x-1,y,a[x-1],u"＿") , (x,y-1,u"＿",b[y-1]) ):
            if i>=0 and j>=0 and m[i][j] < cost:
                cost = m[i][j]
                x= i
                y = j
                cx = ci
                cy = cj

        aa = cx + aa
        bb = cy + bb

    #print aa
    #print bb

    return m[-1][-1],aa,bb

def DPMatching( s ):
    num = len(s)
    for i in range(num):
        for j in range(num):
            if i != j:
                d,s[i],s[j] = levenshtein_distance( s[i] , s[j] )
    return s


if __name__ == '__main__':
    pass

