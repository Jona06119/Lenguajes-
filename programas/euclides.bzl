Main |:
    <w> "Escribe dos numeros"
    <?> a
    <?> b
    Mcd a b
:|

Mcd a b |:
    if b = 0 |:
        <w> "Su MCD es" a
    :| else |:
        Mcd b (a % b)
    :|
:|