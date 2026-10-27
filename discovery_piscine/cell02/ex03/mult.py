#!/usr/bin/env python3
num1 = int(input("Enter first number :"))
num2 = int(input("Enter second number :"))
sum = num1 * num2
print(sum)
if sum == 0:
    print("The result is positive and negative.")
elif sum > 0:
    print("The result is positive")
elif sum < 0:
    print("The result is negative") 

