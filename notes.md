
def is_all_even(ls):
    for i in range(len(ls)):
        if (ls[i]%2)!=0:
            return False
    return True
ls1 = [10, 12, 14, 16]
ls2 = [10, 11, 14, 16]
print(is_all_even(ls)) ### True 
print(is_all_even(ls)) ### False
 