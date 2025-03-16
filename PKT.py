capacity = 75
jumlah_item = 3
item = [200,300,100]
day = []

for index,items in enumerate(item):
    while items > 0:
        delivered = min(capacity, items)
        day.append(delivered)
        items-=delivered
        
print(day)

# =============================================================================

original_word = "AB1230"
any_word = "A312B0" 
max_false = 0

for i in range(len(original_word)):
    if original_word[i] != any_word[i]:
        max_false += 1
if max_false > 2:
    print("False")
else:
    print("True")
    
# =============================================================================

kwh = int(input("Masukkan listrik: "))
harga = 0

def fisrt_1000(kwh):
    return kwh*250
def second_2000(kwh):
    return kwh*300
def third_3000(kwh):
    return kwh*325

if kwh <=1000:
    harga += fisrt_1000(kwh)
if 3000 >= kwh > 1000:
    first = min(kwh,1000)
    harga += fisrt_1000(first)
    kwh -= 1000
    harga += second_2000(kwh)
if kwh > 3000:
    first = min(kwh,1000)
    harga += fisrt_1000(first)
    kwh -= 1000
    second = min(kwh,2000)
    harga += second_2000(second)
    kwh -= 2000
    harga += third_3000(kwh)

print(harga)

# =============================================================================

angka = float(input("Masukkan angka: "))
angka = 827.14
angka = round(angka, 3)


def expanded_form(float_number):
    result = ""
    float_number = str(float_number)
    float_number = float_number.split(".")
    for i,e in enumerate(float_number[0]):
        if i == 0:
            result += e + "0"*(len(float_number[0])-1-i) + " + "
        else:
            result += e + "0"*(len(float_number[0])-1-i) + " + "
    for i,e in enumerate(float_number[1]):
        if e == '0':
            continue
        else:
            result += e + "/1" + "0"*(i+1) + " + "

    return result.strip(" + ")
    

print(expanded_form(angka))

# =============================================================================

"SELECT * FROM EmployeeInfo WHERE Department = 'HR'"

"""
SELECT 
    ei.EmpID,
    CONCAT(ei.EmpFname, ' ', ei.EmpLname) AS EmployeeName,
    ep.EmpPosition,
    ep.DateOfJoining,
    DATEDIFF(CURDATE(), ep.DateOfJoining) AS DaysInRole
FROM EmployeeInfo ei
JOIN EmployeePosition ep ON ei.EmpID = ep.EmpID
WHERE ep.EmpPosition = 'Manager';
"""

"""
SELECT 
    ei.Gender,
    ep.EmpPosition,
    MIN(ei.DOB) AS OldestDOB,
    COUNT(*) AS Count
FROM 
    EmployeeInfo ei
JOIN 
    EmployeePosition ep ON ei.EmpID = ep.EmpID
GROUP BY 
    ei.Gender, ep.EmpPosition
ORDER BY 
    ei.Gender, MIN(ei.DOB)
"""