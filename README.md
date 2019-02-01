# NL Films
#### Isa-Ali Kirca &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 12014672
#### Gerard Noordhuis &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 11919582
#### Patrick Smit &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 11433604

### [Video](https://youtu.be/pXsLS44M2YA)
Demo video, als onderdeel van de oplevering.

### [Schetsen](https://docs.google.com/presentation/d/1Dk9pYlrxR6hi45ncdenz7bOs3y8t3Wdz3CnpoxP1xaI/edit?usp=sharing)
Bekijk de concepten/schetsen op Google Slides^.

## Samenvatting:
Nederlandse (NL) Films heeft als streven liefhebbers van Nederlandse film gemakkelijk films te laten zoeken en delen. Gebruikers kunnen films toevoegen aan bepaalde lijsten. Daarnaast is het mogelijk andere gebruikers toe te voegen als vriend en hun likes te bekijken. 

## Disclaimer:
* In de zoekresultaten kunnen per ongeluk ook niet Nederlandse films getoond worden. Omdat The Movie Database userdriven is, is niet alle data gecontroleerd en kan een film dus ook ten onrechte als Nederlands zijn bestempeld. Ook kan het voorkomen dat een Belgische film in de resultaten verschijnt vanwege de taal: Nederlands.
* Bevriende gebruikers kunnen ook uw favorietenlijst bekijken (en vice versa)

## Features

### Voor bezoekers zonder account:
  * 1.1 Vanaf iedere pagina:
    * 🔍 Zoeken naar films
      * Zoekresultaten pagina
    * Registreren
    * Inloggen
      * Wachtwoord vergeten
        * Opnieuw instellen a.d.h.v. veiligheidsvraag
  * 1.2 🏠 Homepagina:
    * Lijst met de 12 populairste Nederlandse films op The Movie Database
    * Lijst met nieuwe films: 12 Nederlandse films uit 2019, gesorteerd van populair naar minder populair.
  * 1.3 🍿 Filminformatie:
      * Omschrijving
      * Geef de rating van de film weer
        * wordt opgehaald van IMDb en anders van TMDb
      * Jaar van de release
      * Bekijk de regisseur(s), schrijver(s) en hoofdrolspelers

### Voor ingelogde gebruikers:
  * 2.1 Vanaf iedere pagina:
    * 🔍 Zoeken naar films
      * Zoekresultaten pagina
    * ❤️ Filmlijsten:
      * Lijst of gezamenlijke lijst aanmaken
      * Toevoegen aan/bekijken van favoriete films
      * Historie bekijken: films die op NL Films zijn aangeklikt
      * Aan (gezamenlijke) lijst toevoegen
      * Check-in: een film aanvinken als 'gezien' (of verwijderen uit checkins)
    * 👥 Interactie met vrienden:
      * Vriendschapsverzoeken sturen a.d.h.v. gebruikersnaam
      * Vriendschapsverzoeken accepteren of weigeren
      * Film tippen aan een vriend
      * Favorieten van vriend bekijken
      * Vriendenlijst bekijken
    * 👤 Account:
      * Profiel bekijken
      * Wachtwoord wijzigen
      * Account verwijderen
      * Uitloggen
  * 2.2 🏠 Homepage:
    * Lijst met de 12 populairste Nederlandse films op The Movie Database
    * Lijst met nieuwe films: 12 Nederlandse films uit 2019, gesorteerd van populair naar minder populair.
  * 2.3 🍿 Filminformatie:
    * Voeg film toe aan Favorieten
    * Verwijder film van Favorieten
    * Voeg film toe aan Kijklijst
    * Omschrijving
    * Geef de rating van de film weer
      * wordt opgehaald van IMDb en anders van TMDb    
    * Jaar van de release
    * Bekijk de regisseur(s), schrijver(s) en hoofdrolspelers

* Zaken die zijn overwegen maar (nog) niet op onze agenda stonden:
  * Lijst met top gebruikers bekijken
  * Vrienden berichten sturen
  * Per categorie: de beste films.
  * Een feed met films die vrienden hebben gefavoriet in chronologische volgorde.
  * Inloggen met Facebook
  
* Gebreken:
  * Tips van vrienden verwijderen
  * Op de "Tips van vrienden" pagina moet het niet mogelijk zijn vrienden de film die zij jou getipt hebben terug te tippen. Dat kan nu wel.
  * Op de mijn profiel pagina kan je zien welke films je aan mensen hebt getipt (en hoe vaak). Echter, je kan niet zien aan wíe.
  * De veiligheidsvraag is “Wat is jouw lievelingskleur”. Er wordt echter niet gevalideerd of het antwoord daadwerkelijk een kleur is. Deze vraag zou eventueel anders kunnen worden geformuleerd.

---

## Van tevoren vastgelegd:
### Wat we niet doen:
Zelf filminformatie en beoordelingen verzamelen. 

### Minimum viable product:
Er moet gezocht kunnen worden naar een specifieke film. Wanneer de film gevonden wordt, omvat de getoonde pagina in ieder geval:
 * titel van de film
 * jaar van uitkomst
 * regisseur(s)
 * acteurs
 * poster/afbeelding
 * beoordeling

--- 

#### Gebruikte diensten/afhankelijkheden

| Service        | Wat           | 
| ------------- |:-------------| 
| [The Movie Database](https://www.themoviedb.org/documentation/api) (TMDb)     | Film database  API  |
| [The Open Movie Database](http://www.omdbapi.com) (OMDb)      | Film database API      |
| [Bootstrap](https://getbootstrap.com/docs/4.2/getting-started/introduction/) | A HTML, CSS, and JS library      | 
| [Bootsnipp](https://bootsnipp.com/) | Code snippets for Bootstrap HTML/CSS/JS framework      | 


#### Alternatieve sites: wat doen zij wel wat NL Films niet doet?.

|         | NL Films           | [Filmvandaag](https://www.filmvandaag.nl)           | [TMDb](https://www.tmdb.com)           | [IMDb](https://www.imdb.com)           |  
| --- | --- | --- | --- | --- |  
| Internationale films | ☒ | ☑ | ☑ | ☑ | 
| API (en toegankelijk) | ☒ | ☒ | ☑ | ☒ | 
| Nieuws | ☒ | ☒ | ☒ | ☑ | 
| Acteur achtergrondinformatie | ☒ | ☒ | ☑ | ☑ | 
| Video games | ☒ | ☒ | ☒ | ☑ |
| Vanavond op Nl. televisie | ☒ | ☑ | ☒ | ☒ |
| Trivia vragen | ☒ | ☒ | ☒ | ☑ |
| In de bioscoop | ☒ | ☑ | ☑ | ☑ |
| Vergelijkbare films | ☒ | ☒ | ☑ | ☑ |
| Informatie uit eigen database | ☒ | ☒ | ☑ | ☑ |
