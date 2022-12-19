# AASD-Energy-Saver

## Konfiguracja
Plik config.json zawiera w sobie konfiguracje obszaru, na którym działają agenci. Ustawiana jest tam ilość pokoi.  
Każdy pokój posiada swój identyfikator. Dodatkowo należy ustawić preferowaną temperaturę. Jest ona wspólna dla wszystkich pokoi.

## Uruchamianie
Skrypt run.sh podciągnie konfigurację z pliku config.json i uruchomi dostępnych agentów do tych pokoi. Należy ten  
skrypt uruchomić następującym poleceniem:
```
sudo /etc/init.d/prosody start
```

Następnie należy uruchomić agentów:
```
python3 src/agents/sensors.py
```

### Dev

Nie uzywać środowiska python3 w wersji >=3.10 ponieważ powoduje ona błędy z biblioteką spade

Po utworzeniu agenta należy zmodyfikować konfigurację w pliku config.json i dodać tam nowy element w liście `sensors`:  
1. Name oznacza nazwe sensora  
2. min oznacza minimalna temperature, jaka chcemy by byla mozliwa do wylosowania
3. Max oznacza maksymalna temperatura, jaka moze zostac wylosowana
4. Interval oznacza jak czesto chcemy otrzymywac ta wiadomosc.

Ostatecznie należy dodać go do skryptu run.sh w pętli rooms, aby został on zarejestrowany w następujący sposób
(zmodyfikuj tylko zmienną nazwa_agenta):
```
 sudo prosodyctl register ${nazwa_agenta}{ROOM} localhost password  
```
