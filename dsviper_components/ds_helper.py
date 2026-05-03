def byte_count(value) -> str:
    ko = 1024
    mo = ko * 1024

    if value < ko:
        return f'{value}  Byte'
    elif value < mo:
        return f'{value // ko} KB'

    return f'{value // mo} MB'

