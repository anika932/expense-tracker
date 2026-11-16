# Variables: no type declaration needed
name = "Aryan"
amount = 250.75
count = 3
is_paid = True

print("Name:", name)
print("Amount:", amount)

# f-string: easy way to put variables inside text
print(f"{name} spent {amount} on {count} items")

# Conditions: indentation replaces { }, and 'elif' replaces 'else if'
if amount > 500:
    print("High expense")
elif amount > 100:
    print("Medium expense")
else:
    print("Low expense")

# Loop over a list
expenses = [120, 450, 80, 900]
total = 0
for e in expenses:
    total = total + e
print("Total:", total)

# range(): like for (int i = 0; i < 3; i++)
for i in range(3):
    print("Round", i)