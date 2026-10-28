Main |:
    Hanoi
:|

Hanoi |:
    HanoiRec 5 C D E
:|

HanoiRec n ori dst aux |:
    if n > 0 |:
        HanoiRec (n - 1) ori aux dst
        (:) ori
        HanoiRec (n - 1) aux dst ori
    :|
:|