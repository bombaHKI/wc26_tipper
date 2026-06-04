
# FIFA World Cup 26 tippjáték oldal

## Leírás

A projekt a 2026-os FIFA Világbajnokságra készült. A játék lényege eltalálni a meccsek pontos végkimenetelét és a jó tippekért pontokat gyűjteni.
A meccsekre kapott pontok függnek a meccs végkimenetelének előzetes esélyeitől, valamint a lőtt gólok számától.
Az oldal még nem publikus.
<!-- TODO: update az elérhetőséget -->

## Funkciók

### Felhasználók
- **Tippelés**: A "Meccsek" oldalon a felhasználók be tudják írni tippjeiket.
- **Állás**: Az összes felhasználó gyűjtött pontjai alapján felállított ranglista.
- **Tippek**: Minden felhasználó tippjeit (és az azokért járó pontokat) meg lehet nézni.
- **Követés**: Lehetséges más felhasználókat követni (egyirányú, a követett nem kap értesítést). Lehetséges csak a követettek tippjeit és ranglistáját megtekinteni.
- **Profil tevékenységek**: Be/Kijelentkezés, adatok módosítása (email, felhasználónév, jelszó).

### Admin
- **Felhasználók kezelése**: A játékra jelentkezőt elfogadása/elutasítása. A felvett jelentkezők automatikus emailt kapnak egy biztonságosan generált jelszóval.
- **Meccsek kezelése**: Meccsek automatikus frissítése (időpontok, új meccsek) egy API hívással.
- **Oddsok**: A meccsekre kapható plusz pontok frissítése valós fogadóirodák által adott oddsok alapján.

## Használt technológiák
- **Frontend**: JavaScript, Jinja (HTML), CSS. Külső könyvtárak nélkül.
- **Backend**: Python, Flask
- **Adatbázis**: SQLAlchemy, MySQL

## Média
### Login oldal
<p align="middle">
   <img src="media/login.PNG" height="250">
   <img src="media/login_filled.PNG" height="250">
</p>

### Bejelentkezés után
<p align="middle">
   <img src="media/udv.PNG" height="250">
</p>

### Szabályok oldal
<p align="middle">
   <img src="media/szabalyok.PNG" height="250">
</p>

### Meccsek oldal
<p align="middle">
   <img src="media/meccsek.PNG" height="250">
</p>

### Állás oldal
<p align="middle">
   <img src="media/allas1.PNG" height="250">
   <img src="media/allas2.PNG" height="250">
   <img src="media/allas3.PNG" height="250">
</p>

