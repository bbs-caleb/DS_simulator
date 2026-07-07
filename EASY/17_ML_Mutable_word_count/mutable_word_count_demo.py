# Демонстрация поведения словаря с ключами True, 1 и 1.0

print(True == 1)
print(1 == 1.0)
print(True == 1.0)

print(hash(True))
print(hash(1))
print(hash(1.0))

result = {True: 'yes', 1: 'no', 1.0: 'probably'}
print(result)
