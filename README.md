# huckle
huckle is a simple dynamic programming language that aims to be easy to use and similar to Python.

## Language tour
Variables behave the same as in Python: they don't have a value until one is assigned to them. The default types are numbers, strings, booleans and `None`.
```python
x = 10
y = 20
z = x * y # 200

a = 2 ^ 3 # 8
b = 5 / 3 # 1.67
c = 10 % 3 # 1

message = "Hello " + "world"
print(message)

# Chained comparison operators!
condition = 5 > 3 == 3 # True
print(not_initialized_yet) # None
```
Shortcuts exist to quickly change and delete variables.
```python
x = 10
x += 20 # 30
# Assigment operators are expressions!
print(x -= 10) # 20

del x
print(x) # None
```
After each section, indentation is needed. The conditional sections act the same as in Python. You can create loops with the while section.
```python
if 10 >= 4:
    print("This is true")
elif 10 < 0:
    print("Would be kind of weird if this is true")
else:
    print("Well I guess it's this then.")

x = 10
while x > 3:
    print(x)
    x--
```
Functions are expressions, but are defined using blocks. Putting `infix` in front of your function definition makes it an infix operator. If not enough arguments are given, the function is curried.
```python
say_hello = fn(name):
    print("Hello", name)
    
say_hello("world")

root = infix fn(r, x):
    return x ^ (1 / r)
# Infix functions are functions with two arguments.
# The function can be put between the arguments.
print(3 root 8) # 2

sqrt = root(2) # Curried function!
print(sqrt(100)) # 10
```
Matrices are the way to go for list implementation, but also for easy 2D arrays. If only one row is present, the matrix acts as a list. Split elements by using `,` and split rows using `;`.
```python
matrix = [1, 2; 3, 4]
transpose(matrix) # [1, 3; 2, 4]
```